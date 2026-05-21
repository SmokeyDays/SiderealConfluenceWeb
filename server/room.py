from datetime import datetime
from server.agent.brain import Brain
from server.game import Game
from server.utils.config import get_config
from server.utils.log import logger
from server.utils.pubsub import pubsub
from typing import Dict, Any, List
import threading
import asyncio
from typing import Dict, Any, Coroutine
from server.utils.log import logger
from server.utils.runner import bot_runner
from server.charts.recorder import game_recorder

class BotTaskScheduler:
  def __init__(self, step_bots_debounce_seconds=0.1):
    # Store currently running task for each bot.
    # Key: bot_id, Value: asyncio.Task
    self.pending_tasks: Dict[str, asyncio.Task] = {}
    # Latest queued rerun per bot while current task is still running.
    # Key: bot_id, Value: Coroutine
    self.queued_tasks: Dict[str, Coroutine] = {}
    self.step_bots_debounce_seconds = step_bots_debounce_seconds
    self.step_bots_lock = threading.Lock()
    self.step_bots_timer = None
    self.step_bots_pending_get_handlers = None
    self.recorded_events = []

  def record(self, event_type: str, bot_id: str):
    timestamp = str(datetime.now())
    self.recorded_events.append({
      "event_type": event_type,
      "bot_id": bot_id,
      "timestamp": timestamp
    })

  async def schedule(self, bot_id: str, coro: Coroutine):
    """
    Schedule a new bot task.
    If a task is already running for this bot, do not cancel it.
    Queue exactly one rerun (latest wins) to avoid wasted LLM calls.
    """
    self.record("pend", bot_id)
    if bot_id in self.pending_tasks:
      existing_task = self.pending_tasks[bot_id]
      if not existing_task.done():
        logger.info(f"Bot {bot_id}: Step already running; queueing one rerun after completion.")
        self.record("queue", bot_id)
        previous_coro = self.queued_tasks.get(bot_id)
        if previous_coro is not None:
          try:
            previous_coro.close()
          except Exception:
            pass
        self.queued_tasks[bot_id] = coro
        return existing_task

    task = asyncio.create_task(self._run_task(bot_id, coro))
    self.pending_tasks[bot_id] = task
    return task

  async def _run_task(self, bot_id: str, coro: Coroutine):
    try:
      await coro
    except asyncio.CancelledError:
      logger.info(f"Bot {bot_id}: Task cancelled successfully.")
      raise
    except Exception as e:
      logger.error(f"Bot {bot_id}: Error during step execution: {e}")
    finally:
      self.record("done", bot_id)
      current_task = asyncio.current_task()
      if bot_id in self.pending_tasks and self.pending_tasks[bot_id] is current_task:
        next_coro = self.queued_tasks.pop(bot_id, None)
        if next_coro is not None:
          self.record("rerun", bot_id)
          next_task = asyncio.create_task(self._run_task(bot_id, next_coro))
          self.pending_tasks[bot_id] = next_task
        else:
          del self.pending_tasks[bot_id]

  def request_step_bots(self, get_handlers, step_bots_func):
    with self.step_bots_lock:
      self.step_bots_pending_get_handlers = get_handlers
      if self.step_bots_timer is not None and self.step_bots_timer.is_alive():
        return

      def flush():
        with self.step_bots_lock:
          pending_get_handlers = self.step_bots_pending_get_handlers
          self.step_bots_pending_get_handlers = None
          self.step_bots_timer = None
        if pending_get_handlers is not None:
          step_bots_func(pending_get_handlers)

      self.step_bots_timer = threading.Timer(self.step_bots_debounce_seconds, flush)
      self.step_bots_timer.daemon = True
      self.step_bots_timer.start()

class Room:
  def __init__(self, max_players, name, end_round, game_type = "default"):
    self.name = name
    self.end_round = end_round
    self.max_players = max_players
    self.players: Dict[str, Dict[str, Any]] = {}
    self.bots: List[str] = []
    self.bot_agents: Dict[str, Brain] = {}
    self.bot_types: Dict[str, str] = {}
    self.bots_auto_react = True
    self.game_state = "waiting"
    self.game = None
    self.game_type = game_type
    self.species = ["Caylion", "Yengii", "Im", "Eni", "Zeth", "Unity", "Faderan", "Kit", "Kjasjavikalimm"]
    self.scheduler = BotTaskScheduler(get_config("bot_step_debounce_seconds"))
    self.lock = threading.RLock()

  def enter_room(self, user_id):
    if user_id in self.players or self.game_state == "playing":
      return False
    if len(self.players) < self.max_players:
      self.players[user_id] = {
        "specie": None,
        "agreed": False
      }
      return True
    else:
      return False

  def leave_room(self, user_id):
    if user_id in self.players:
      del self.players[user_id]
      return True
    else:
      return False

  def choose_specie(self, user_id, specie):
    if user_id in self.players and specie in self.species and not self.players[user_id]["agreed"]:
      self.players[user_id]["specie"] = specie
      return True
    else:
      return False
    
  def add_bot(self, bot_id, specie, bot_type):
    self.bots.append(bot_id)
    self.enter_room(bot_id)
    self.choose_specie(bot_id, specie)
    
    self.bot_types[bot_id] = bot_type
  
  def remove_bot(self, user_id, bot_id):
    if user_id in self.players and user_id not in self.bots:
      self.leave_room(bot_id)

  def is_bot(self, user_id):
    return user_id in self.bots
  
  def toggle_bots(self):
    self.bots_auto_react = not self.bots_auto_react
    return self.bots_auto_react

  def step_bots(self, get_handlers):
    handlers_prompt, handlers_map = get_handlers(self.game.stage)
    for bot_id in self.bots:
      if self.game.waiting_player(bot_id):
        self.step_bot(bot_id, handlers_prompt, handlers_map)

  def request_step_bots(self, get_handlers):
    self.scheduler.request_step_bots(get_handlers, self.step_bots)

  def step_bot(self, bot_id, handlers_prompt, handlers_map):
    if bot_id not in self.bots:
      return
    if not self.bots_auto_react:
      logger.info(f"Bot {bot_id} in room {self.name} auto react is disabled, skipping step.")
      return
    async def async_logic():
      await self.bot_agents[bot_id].step(handlers_prompt, handlers_map)
    bot_runner.run_task(self.scheduler.schedule(bot_id, async_logic()))
    
  def get_recent_response(self, user_id, slice = 100):
    if user_id in self.bots:
      responses = self.bot_agents[user_id].recent_responses
      if len(responses) > slice:
        return responses[-slice:]
      return responses
    else:
      return []
  
  def get_calling_history(self):
    return self.scheduler.recorded_events

  def agree_to_start(self, user_id):
    if user_id in self.players:
      self.players[user_id]["agreed"] = True
      if all(player["agreed"] for player in self.players.values()) and len(self.players) >= 2:
        self.game_state = "started"
        self.start_game()
      return True
    else:
      return False
  
  def disagree_to_start(self, user_id):
    if user_id in self.players:
      self.players[user_id]["agreed"] = False
      return True
    else:
      return False
    
  def set_end_round(self, end_round):
    self.end_round = end_round
    return True
  
  def start_game(self): 
    self.game = Game(self.name, self.end_round)
    self.game.set_end_game_callback(self.on_game_end)
    for user_id, player in self.players.items():
      self.game.add_player(player["specie"], user_id)
      pubsub.publish("add_statistics", {"key": "games_played", "value": 1}, user_id)
    self.game_state = "playing"
    self.game.start_game()
    for bot in self.bots:
      bot_type = self.bot_types.get(bot, get_config('default_bot_type'))
      self.bot_agents[bot] = Brain(self.game, bot, model_name=bot_type)

  def on_game_end(self, results):
    mapped_results = []
    for res in results:
      user_id = res['user_id']
      model = self.bot_types.get(user_id, "Human")
      mapped_results.append({
        "model": model,
        "specie": res['specie'],
        "score": res['score']
      })
    
    game_recorder.add_record(self.game_type, self.name, mapped_results)
    logger.info(f"Game record saved for room {self.name} (type: {self.game_type})")

  def to_dict(self):
    return {
      "name": self.name,
      "players": self.players,
      "game_state": self.game_state,
      "max_players": self.max_players,
      "end_round": self.end_round,
      "bots": self.bots,
      "bots_auto_react": self.bots_auto_react
    }
  
  def __getstate__(self):
    state = self.__dict__.copy()
    if 'lock' in state:
      del state['lock']
    if 'scheduler' in state:
      del state['scheduler']
    return state

  def __setstate__(self, state):
    self.__dict__.update(state)
    self.lock = threading.RLock()
    self.scheduler = BotTaskScheduler(get_config("bot_step_debounce_seconds"))
