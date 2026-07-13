from datetime import datetime
import asyncio
import threading
import time
from typing import Dict, Any, List, Coroutine, Callable

from server.agent.rule_agent import FairTradeRuleAgent
from server.game import Game
from server.utils.config import get_config
from server.utils.log import logger
from server.utils.pubsub import pubsub
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

  async def cancel_all_tasks(self):
    tasks = list(self.pending_tasks.values())
    for task in tasks:
      if not task.done():
        task.cancel()
    if tasks:
      await asyncio.gather(*tasks, return_exceptions=True)
    self.pending_tasks.clear()

    for coro in self.queued_tasks.values():
      try:
        coro.close()
      except Exception:
        pass
    self.queued_tasks.clear()


class SilenceWatchdog:
  def __init__(self, silence_seconds=30.0, silence_force_ready_after=3):
    self.silence_seconds = float(silence_seconds)
    self.silence_force_ready_after = int(silence_force_ready_after)
    self.lock = threading.Lock()
    self.timer = None
    self.last_state_update_ts = time.time()
    self.no_effective_step_count = 0
    self.callbacks = {
      "restep": None,
      "force_ready": None,
      "is_active_stage": None,
      "has_pending": None,
    }

  def notify_state_updated(self, restep_func, force_ready_func, is_active_stage_func, has_pending_func):
    with self.lock:
      self.last_state_update_ts = time.time()
      self.no_effective_step_count = 0
      self.callbacks["restep"] = restep_func
      self.callbacks["force_ready"] = force_ready_func
      self.callbacks["is_active_stage"] = is_active_stage_func
      self.callbacks["has_pending"] = has_pending_func
      if self.timer is None or not self.timer.is_alive():
        self._schedule_check_locked()

  def _schedule_check_locked(self):
    interval = max(self.silence_seconds, 1.0)
    self.timer = threading.Timer(interval, self._on_check)
    self.timer.daemon = True
    self.timer.start()

  def _on_check(self):
    action = None
    restep_func = None
    force_ready_func = None
    is_active_stage_func = None
    has_pending_func = None

    with self.lock:
      now = time.time()
      silence_duration = now - self.last_state_update_ts
      restep_func = self.callbacks.get("restep")
      force_ready_func = self.callbacks.get("force_ready")
      is_active_stage_func = self.callbacks.get("is_active_stage")
      has_pending_func = self.callbacks.get("has_pending")

      active_stage = bool(is_active_stage_func and is_active_stage_func())
      has_pending = bool(has_pending_func and has_pending_func())

      if not active_stage or not has_pending:
        self.no_effective_step_count = 0
      elif silence_duration >= self.silence_seconds and restep_func and force_ready_func:
        self.no_effective_step_count += 1
        if self.no_effective_step_count >= self.silence_force_ready_after:
          action = "force_ready"
        else:
          action = "step"

      self._schedule_check_locked()

    if action == "step":
      logger.warning(
        f"Silence watchdog triggered ({self.no_effective_step_count}/{self.silence_force_ready_after}). "
        f"Re-stepping pending bots."
      )
      restep_func()
    elif action == "force_ready":
      logger.warning(
        f"Silence watchdog triggered ({self.no_effective_step_count}/{self.silence_force_ready_after}). "
        f"Auto-confirming remaining bots."
      )
      forced = force_ready_func()
      with self.lock:
        self.no_effective_step_count = 0
        self.last_state_update_ts = time.time()
      if not forced:
        raise RuntimeError("Silence watchdog reached threshold but failed to force progress.")


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
    self.silence_watchdog = SilenceWatchdog(
      get_config("bot_silence_seconds"),
      get_config("bot_silence_force_ready_after"),
    )
    self.lock = threading.RLock()
    self.last_stage_for_tasks = None
    self.on_game_end_callback = None

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

  def clear_all_bot_tasks(self, reason: str):
    logger.info(f"Clearing bot tasks in room {self.name}. Reason: {reason}")
    bot_runner.run_task(self.scheduler.cancel_all_tasks())

  def _has_pending_bots(self):
    if not self.game:
      return False
    for bot_id in self.bots:
      player = self.game.get_player_by_id(bot_id)
      if player and not player.agreed:
        return True
    return False

  def _is_watchdog_active_stage(self):
    if not self.game:
      return False
    return self.game.stage in ("trading", "production")

  def on_state_updated(self, get_handlers, on_force_progress: Callable):
    if self.game:
      current_stage = self.game.stage
      if self.last_stage_for_tasks is None:
        self.last_stage_for_tasks = current_stage
      elif current_stage != self.last_stage_for_tasks:
        old_stage = self.last_stage_for_tasks
        self.last_stage_for_tasks = current_stage
        self.clear_all_bot_tasks(f"stage changed: {old_stage} -> {current_stage}")

    def restep_callback():
      self.request_step_bots(get_handlers)

    def force_ready_callback():
      return self.force_ready_pending_bots(on_force_progress)

    self.silence_watchdog.notify_state_updated(
      restep_callback,
      force_ready_callback,
      self._is_watchdog_active_stage,
      self._has_pending_bots,
    )

  def force_ready_pending_bots(self, on_force_progress: Callable):
    if not self.game:
      return False

    stage_before = self.game.stage
    forced_bots = []

    for bot_id in self.bots:
      if self.game.waiting_player(bot_id):
        player = self.game.get_player_by_id(bot_id)
        if player and not player.agreed:
          self.game.player_agree(bot_id)
          forced_bots.append(bot_id)

    if forced_bots:
      stage_after = self.game.stage
      self.clear_all_bot_tasks(f"watchdog force-ready at stage {stage_before}")
      logger.warning(
        f"Silence watchdog auto-confirmed bots in room {self.name} at stage {stage_before}: {forced_bots}. "
        f"Stage now: {stage_after}."
      )
      on_force_progress(stage_after != stage_before)
      return True
    else:
      logger.info(
        f"Silence watchdog force-ready triggered in room {self.name} at stage {stage_before}, "
        "but no pending bots required auto-confirm."
      )
      return False

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

  def set_on_game_end_callback(self, callback):
    self.on_game_end_callback = callback
    return True

  def _build_model_by_user(self):
    return {
      user_id: self.bot_types.get(user_id, "Human")
      for user_id in self.players
    }

  def _build_function_calling_statistics(self):
    by_model = {}

    for bot_id, agent in self.bot_agents.items():
      model = self.bot_types.get(bot_id, "Human")
      stats_getter = getattr(agent, "get_statistics", None)
      if not callable(stats_getter):
        continue

      agent_stats = stats_getter() or {}
      fc_stats = agent_stats.get("function_calling", {})
      if not fc_stats:
        continue

      model_stats = by_model.setdefault(model, {
        "attempts": 0,
        "successes": 0,
        "failures": 0,
        "failure_rate": None,
      })
      model_stats["attempts"] += int(fc_stats.get("attempts", 0) or 0)
      model_stats["successes"] += int(fc_stats.get("successes", 0) or 0)
      model_stats["failures"] += int(fc_stats.get("failures", 0) or 0)

    for model_stats in by_model.values():
      attempts = model_stats["attempts"]
      failures = model_stats["failures"]
      model_stats["failure_rate"] = failures / attempts if attempts else None

    return {
      "by_model": by_model
    }

  def _build_game_statistics(self):
    statistics = {
      "function_calling": self._build_function_calling_statistics(),
    }
    if self.game:
      statistics.update(self.game.get_trade_statistics(self._build_model_by_user()))
    return statistics

  def start_game(self):
    self.game = Game(self.name, self.end_round)
    self.game.set_end_game_callback(self.on_game_end)
    for user_id, player in self.players.items():
      self.game.add_player(player["specie"], user_id)
      pubsub.publish("add_statistics", {"key": "games_played", "value": 1}, user_id)
    self.game_state = "playing"
    self.game.start_game()
    self.last_stage_for_tasks = self.game.stage
    for bot in self.bots:
      bot_type = self.bot_types.get(bot, get_config('default_bot_type'))
      if FairTradeRuleAgent.supports_model(bot_type):
        self.bot_agents[bot] = FairTradeRuleAgent(self.game, bot, model_name=bot_type)
      else:
        from server.agent.brain import Brain
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

    game_recorder.add_record(self.game_type, self.name, mapped_results, statistics=self._build_game_statistics())
    logger.info(f"Game record saved for room {self.name} (type: {self.game_type})")
    if self.on_game_end_callback:
      try:
        self.on_game_end_callback(self.name, results)
      except Exception as e:
        logger.error(f"Game end callback failed for room {self.name}: {e}")

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
    if 'silence_watchdog' in state:
      del state['silence_watchdog']
    if 'on_game_end_callback' in state:
      del state['on_game_end_callback']
    return state

  def __setstate__(self, state):
    self.__dict__.update(state)
    self.lock = threading.RLock()
    self.scheduler = BotTaskScheduler(get_config("bot_step_debounce_seconds"))
    self.silence_watchdog = SilenceWatchdog(
      get_config("bot_silence_seconds"),
      get_config("bot_silence_force_ready_after"),
    )
    self.last_stage_for_tasks = self.game.stage if self.game else None
    self.on_game_end_callback = None
