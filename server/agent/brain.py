from datetime import datetime
from server.agent.prompt import get_prompt
from server.game import Game
from server.agent.llm_caller import BasicCaller, TradeCaller, TurnPlanCaller, EconomyCaller, BidCaller, PickCaller
from server.utils.log import logger

turn_plan_caller = TurnPlanCaller()
trade_caller = TradeCaller()
economy_caller = EconomyCaller()
bid_caller = BidCaller()
pick_caller = PickCaller()

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

  def step(self, handlers_prompt, handlers_map):
    """
    Auto detect the current stage of the game and call the corresponding function.
    """
    obs = get_prompt(self.game, self.player_id)
    if self.game.stage == "trading":
      if self.current_plan == None:
        prompt = {"Observation": obs}
        response = turn_plan_caller.plan(prompt)
        self.record_response(prompt, response, special_call="turn_plan")
        response.pop("reasoning")
        self.current_plan = response

      prompt = {
        "Plan": str(self.current_plan),
        "Observation": obs,
        "Actions": handlers_prompt
      }
      response = trade_caller.plan(prompt)
      self.record_response(prompt, response)
      if "actions" not in response.keys():
        logger.warning(f"Bot {self.player_id} trade caller returned no callbacks: {response}")
        return
      callbacks = response.get("actions", [])
      try:
        for callback in callbacks:
          func_name, data = callback['func'], callback['data']
          data['room_name'] = self.game.room_name
          data['username'] = self.player_id
          func = handlers_map[func_name]
          func(data)
      except Exception as e:
        import traceback
        logger.error(f"Bot {self.player_id} trade caller execute callback error: {e}, {traceback.format_exc()}")
    
    elif self.game.stage == "production":
      prompt = {
        "Plan": str(self.current_plan),
        "Observation": obs,
        "Actions": handlers_prompt
      }

      response = economy_caller.plan(prompt)
      self.record_response(prompt, response)
      if "actions" not in response.keys():
        logger.warning(f"Bot {self.player_id} trade caller returned no callbacks: {response}")
        return
      callbacks = response.get("actions", [])
      try:
        for callback in callbacks:
          func_name, data = callback['func'], callback['data']
          data['room_name'] = self.game.room_name
          data['username'] = self.player_id
          func = handlers_map[func_name]
          func(data)
      except Exception as e:
        import traceback
        logger.error(f"Bot {self.player_id} trade caller execute callback error: {e}, {traceback.format_exc()}")

    elif self.game.stage == "bid":
      prompt = {
        "Plan": str(self.current_plan),
        "Observation": obs,
        "Actions": handlers_prompt
      }

      response = bid_caller.plan(prompt)
      self.record_response(prompt, response)
      if "actions" not in response.keys():
        logger.warning(f"Bot {self.player_id} bid caller returned no callbacks: {response}")
        return
      callbacks = response.get("actions", [])
      try:
        for callback in callbacks:
          func_name, data = callback['func'], callback['data']
          data['room_name'] = self.game.room_name
          data['username'] = self.player_id
          func = handlers_map[func_name]
          func(data)
      except Exception as e:
        import traceback
        logger.error(f"Bot {self.player_id} bid caller execute callback error: {e}, {traceback.format_exc()}")

    elif self.game.stage == "pick":
      prompt = {
        "Plan": str(self.current_plan),
        "Observation": obs,
        "Actions": handlers_prompt
      }
      response = pick_caller.plan(prompt)
      self.record_response(prompt, response)
      if "actions" not in response.keys():
        logger.warning(f"Bot {self.player_id} pick caller returned no callbacks: {response}")
        return
      callbacks = response.get("actions", [])
      try:
        for callback in callbacks:
          func_name, data = callback['func'], callback['data']
          data['room_name'] = self.game.room_name
          data['username'] = self.player_id
          func = handlers_map[func_name]
          func(data)
      except Exception as e:
        import traceback
        logger.error(f"Bot {self.player_id} pick caller execute callback error: {e}, {traceback.format_exc()}")

    elif self.game.stage == "end": 
       self.current_plan = None

  def get_recent_responses(self):
    return self.recent_responses
