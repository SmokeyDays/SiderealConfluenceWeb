from datetime import datetime
from server.agent.brain import Brain
from server.game import Game
from server.utils.log import logger
from server.utils.pubsub import pubsub
from typing import Dict, Any, List
import threading
import asyncio
from typing import Dict, Any, Coroutine
from server.utils.log import logger
from server.utils.runner import bot_runner

class BotTaskScheduler:
  def __init__(self):
    # 存储每个 Bot 当前正在运行的任务
    # Key: bot_id, Value: asyncio.Task
    self.pending_tasks: Dict[str, asyncio.Task] = {}
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
    调度一个新的 Bot 任务。
    如果该 Bot 已经有正在进行的任务，取消旧任务，执行新任务。
    """
    # 1. 检查是否有旧任务
    self.record("pend", bot_id)
    if bot_id in self.pending_tasks:
      existing_task = self.pending_tasks[bot_id]
      if not existing_task.done():
        logger.info(f"Bot {bot_id}: Cancelling outdated step task due to new event.")
        self.record("cancel", bot_id)
        existing_task.cancel() # 发送取消信号
        try:
          # 等待旧任务清理完成（可选，防止资源竞争，通常 await 即可）
          await existing_task
        except asyncio.CancelledError:
          # 预期内的取消，忽略报错
          pass
    
    # 2. 创建新任务
    # 我们把这个任务包装一下，以便在完成时从字典中移除自己
    task = asyncio.create_task(self._run_task(bot_id, coro))
    self.pending_tasks[bot_id] = task
    return task

  async def _run_task(self, bot_id: str, coro: Coroutine):
    try:
      await coro
    except asyncio.CancelledError:
      logger.info(f"Bot {bot_id}: Task cancelled successfully.")
      raise # 重新抛出，让 asyncio 知道它被取消了
    except Exception as e:
      logger.error(f"Bot {bot_id}: Error during step execution: {e}")
    finally:
      # 任务结束（无论成功、失败还是取消），清理字典
      # 只有当字典里的任务是当前这个任务时才删除（防止删除了后来覆盖的新任务）
      self.record("done", bot_id)
      if bot_id in self.pending_tasks and self.pending_tasks[bot_id] is asyncio.current_task():
          del self.pending_tasks[bot_id]

class Room:
  def __init__(self, max_players, name, end_round):
    self.name = name
    self.end_round = end_round
    self.max_players = max_players
    self.players: Dict[str, Dict[str, Any]] = {}
    self.bots: List[str] = []
    self.bot_agents: Dict[str, Brain] = {}
    self.bots_auto_react = True
    self.game_state = "waiting"
    self.game = None
    self.species = ["Caylion", "Yengii", "Im", "Eni", "Zeth", "Unity", "Faderan", "Kit", "Kjasjavikalimm"]
    self.scheduler = BotTaskScheduler()
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
    
  def add_bot(self, user_id, bot_id, specie):
    if user_id in self.players and user_id not in self.bots:
      self.bots.append(bot_id)
      self.enter_room(bot_id)
      self.choose_specie(bot_id, specie)
  
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

  def step_bot(self, bot_id, handlers_prompt, handlers_map):
    if bot_id not in self.bots:
      return
    if not self.bots_auto_react:
      logger.info(f"Bot {bot_id} in room {self.name} auto react is disabled, skipping step.")
      return
    async def async_logic():
      # 这里调用的是 Brain.step (它是 async 的)
      # 注意：handlers_map 里的函数已经被 registry 包装了锁，所以是安全的
      await self.bot_agents[bot_id].step(handlers_prompt, handlers_map)
    bot_runner.run_task(self.scheduler.schedule(bot_id, async_logic()))
    
  def get_recent_response(self, user_id):
    if user_id in self.bots:
      return self.bot_agents[user_id].recent_responses
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
    for user_id, player in self.players.items():
      self.game.add_player(player["specie"], user_id)
      pubsub.publish("add_statistics", {"key": "games_played", "value": 1}, user_id)
    self.game_state = "playing"
    self.game.start_game()
    for bot in self.bots:
      self.bot_agents[bot] = Brain(self.game, bot)

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
    self.scheduler = BotTaskScheduler()