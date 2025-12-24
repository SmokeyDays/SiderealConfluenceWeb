from datetime import datetime
from server.agent.prompt import get_prompt
from server.game import Game
from server.agent.llm_caller import BasicCaller, TradeCaller, TurnPlanCaller, EconomyCaller, BidCaller, PickCaller, DiscardColonyCaller
from server.utils.log import logger

turn_plan_caller = TurnPlanCaller()
trade_caller = TradeCaller()
economy_caller = EconomyCaller()
bid_caller = BidCaller()
pick_caller = PickCaller()
discard_colony_caller = DiscardColonyCaller()

class Brain:
  def __init__(self, game: Game, player_id: str):
    self.game = game
    self.player_id = player_id
    self.current_plan = None
    self.promises = []
    self.recent_responses = []

  def record_response(self, prompt, response, special_call=None):
    logger.info(f"Bot {self.player_id} record response: {prompt}, {response}")
    self.recent_responses.append({
      "timestamp": str(datetime.now()),
      "round": self.game.current_round,
      "stage": self.game.stage if special_call is None else special_call,
      "prompt": prompt,
      "response": response
    })

  async def step(self, handlers_prompt, handlers_map):
    obs = get_prompt(self.game, self.player_id)
    
    # 定义一个通用的回调处理函数，避免代码重复
    def execute_callbacks(response, caller_name):
      if not response or "actions" not in response.keys():
        logger.warning(f"Bot {self.player_id} {caller_name} returned no callbacks: {response}")
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
    
    if self.game.stage == "trading":
      # 1. Turn Plan (如果还没有 Plan)
      if self.current_plan is None:
        prompt = {"Observation": obs}
        # AWAIT 调用
        response = await turn_plan_caller.aplan(prompt)
        
        self.record_response(prompt, response, special_call="turn_plan")
        if "reasoning" in response:
          response.pop("reasoning") # 清理不需要存储的字段
        self.current_plan = response

      # 2. Trade Plan
      prompt = {
        "Plan": str(self.current_plan),
        "Observation": obs,
        "Actions": handlers_prompt
      }
      # AWAIT 调用
      response = await trade_caller.aplan(prompt)
      self.record_response(prompt, response)
      execute_callbacks(response, "trade caller")
        
    elif self.game.stage == "discard_colony":
      prompt = {
        "Plan": str(self.current_plan),
        "Observation": obs,
        "Actions": handlers_prompt
      }
      response = await discard_colony_caller.aplan(prompt)
      self.record_response(prompt, response)
      execute_callbacks(response, "discard_colony caller")

    elif self.game.stage == "production":
      prompt = {
        "Plan": str(self.current_plan),
        "Observation": obs,
        "Actions": handlers_prompt
      }
      response = await economy_caller.aplan(prompt)
      self.record_response(prompt, response)
      execute_callbacks(response, "economy caller")

    elif self.game.stage == "bid":
      prompt = {
        "Plan": str(self.current_plan),
        "Observation": obs,
        "Actions": handlers_prompt
      }
      response = await bid_caller.aplan(prompt)
      self.record_response(prompt, response)
      execute_callbacks(response, "bid caller")

    elif self.game.stage == "pick":
      prompt = {
        "Plan": str(self.current_plan),
        "Observation": obs,
        "Actions": handlers_prompt
      }
      response = await pick_caller.aplan(prompt)
      self.record_response(prompt, response)
      execute_callbacks(response, "pick caller")

    elif self.game.stage == "end": 
      self.current_plan = None