from datetime import datetime
import asyncio
from server.agent.prompt import get_prompt
from server.game import Game
from server.agent.llm_caller import BasicCaller, TradeCaller, TurnPlanCaller, EconomyCaller, BidCaller, PickCaller, DiscardColonyCaller
from server.utils.config import get_config
from server.utils.log import logger
from server.agent.prompt_template import load_prompt
from server.agent.interface import llm_manager

class PlannerFactory:
  _instances = {}
  planners = {
    "turn_plan": TurnPlanCaller,
    "trade": TradeCaller,
    "economy": EconomyCaller,
    "bid": BidCaller,
    "pick": PickCaller,
    "discard_colony": DiscardColonyCaller
  }

  @classmethod
  def get_planner(cls, model_name, planner):
    planner_class = cls.planners.get(planner)
    if planner_class is None:
      raise ValueError(f"Planner {planner} not found in PlannerFactory.")
    key = (model_name, planner_class.__name__)
    if key not in cls._instances:
      vlm = llm_manager.get_api(model_name)
      # Assume callers accept vlm and model_name
      cls._instances[key] = planner_class(model_name=model_name, vlm=vlm)
    return cls._instances[key]

class Brain:
  def __init__(self, game: Game, player_id: str, model_name: str = get_config('default_bot_type')):
    self.game = game
    self.player_id = player_id
    self.model_name = model_name

    self.current_plan = None
    self.promises = []
    self.recent_responses = []
    self._step_id = 0
    self.trading_step_count = 0
    self.last_trading_round = -1

  def get_planner(self, planner_name: str) -> BasicCaller:
    return PlannerFactory.get_planner(self.model_name, planner_name)

  def record_response(self, prompt, response, special_call=None):
    # logger.info(f"Bot {self.player_id} record response: {prompt}, {response}")
    self.recent_responses.append({
      "timestamp": str(datetime.now()),
      "round": self.game.current_round,
      "stage": self.game.stage if special_call is None else special_call,
      "prompt": prompt,
      "response": response
    })

  def ensure_confirm(self, response):
    actions = response.get("actions", [])
    has_confirm = any(action.get("func") == "confirm_ready" for action in actions)
    if not has_confirm:
      logger.info(f"Bot {self.player_id} adding confirm_ready to actions.")
      actions.append({"func": "confirm_ready", "data": {}})
      response["actions"] = actions
    return response

  async def step(self, handlers_prompt, handlers_map):
    self._step_id = self._step_id + 1
    current_id = self._step_id

    await asyncio.sleep(1)
    if self._step_id != current_id:
      return

    obs = get_prompt(self.game, self.player_id)
    # 定义一个通用的回调处理函数，避免代码重复
    def execute_callbacks(response, caller_name):
      if not response or "actions" not in response.keys():
        logger.warning(f"Bot {self.player_id} {caller_name} returned no callbacks: {response}")
        return
      if self._step_id != current_id:
        logger.warning(f"Bot {self.player_id}: Discarding outdated callbacks from {current_id} (Race Condition Prevented)")
        return

      
      callbacks = response.get("actions", [])
      try:
        for callback in callbacks:
          func_name, data = callback['func'], callback['data']
          data['room_name'] = self.game.room_name
          data['username'] = self.player_id
          
          if func_name in handlers_map:
            func = handlers_map[func_name]
            # 假设 func 是同步的，如果是异步的需要 await
            func(data)
          else:
            logger.error(f"Function {func_name} not found in handlers_map")

      except Exception as e:
        import traceback
        logger.error(f"Bot {self.player_id} {caller_name} execute callback error: {e}, {traceback.format_exc()}")

    # === 逻辑分支 ===
    player = self.game.get_player_by_id(self.player_id)
    specie = player.specie if player else None
    specie_desc = load_prompt(f"species_intro/{specie}.txt") if specie else "Unknown specie"
    

    if self.game.stage == "trading":
      if self.last_trading_round != self.game.current_round:
        self.trading_step_count = 0
        self.current_plan = None
        self.last_trading_round = self.game.current_round
      self.trading_step_count += 1

      if self.current_plan is None:
        prompt = [
          ("Specie description", specie_desc), 
          ("Observation", obs)
        ]
        response = await self.get_planner("turn_plan").aplan(prompt)
        self.record_response(prompt, response, special_call="turn_plan")
        if "reasoning" in response:
          response.pop("reasoning") # 清理不需要存储的字段
        self.current_plan = response

      # 2. Trade Plan
      prompt = [
        ("Specie description", specie_desc),
        ("Plan", str(self.current_plan)),
        ("Observation", obs),
        ("Actions", handlers_prompt)
      ]
      # AWAIT 调用
      response = await self.get_planner("trade").aplan(prompt)

      if self.trading_step_count > 100 and response and "actions" in response:
        response = self.ensure_confirm(response)
      self.record_response(prompt, response)
      execute_callbacks(response, "trade caller")
      # Apply updated plan
      new_plan = response.get("updated_plan", None)
      if new_plan is not None:
        self.current_plan = new_plan
        
    elif self.game.stage == "discard_colony":
      prompt = [
        ("Specie description", specie_desc),
        ("Observation", obs),
        ("Actions", handlers_prompt)
      ]
      response = await self.get_planner("discard_colony").aplan(prompt)
      self.record_response(prompt, response)
      execute_callbacks(response, "discard_colony caller")

    elif self.game.stage == "production":
      prompt = [
        ("Specie description", specie_desc),
        ("Plan", str(self.current_plan)),
        ("Observation", obs),
        ("Actions", handlers_prompt)
      ]
      response = await self.get_planner("economy").aplan(prompt)
      self.record_response(prompt, response)
      response = self.ensure_confirm(response)
      execute_callbacks(response, "economy caller")

    elif self.game.stage == "bid":
      prompt = [
        ("Specie description", specie_desc),
        ("Plan", str(self.current_plan)),
        ("Observation", obs),
        ("Actions", handlers_prompt)
      ]
      response = await self.get_planner("bid").aplan(prompt)
      self.record_response(prompt, response)
      execute_callbacks(response, "bid caller")

    elif self.game.stage == "pick":
      prompt = [
        ("Specie description", specie_desc),
        ("Plan", str(self.current_plan)),
        ("Observation", obs),
        ("Actions", handlers_prompt)
      ]
      response = await self.get_planner("pick").aplan(prompt)
      self.record_response(prompt, response)
      execute_callbacks(response, "pick caller")

    elif self.game.stage == "end": 
      self.current_plan = None