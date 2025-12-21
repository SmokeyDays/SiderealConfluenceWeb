from server.agent.prompt import get_prompt
from server.game import Game
from server.agent.llm_caller import BasicCaller, TradeCaller, TurnPlanCaller
from server.utils.log import logger

turn_plan_caller = TurnPlanCaller()
trade_caller = TradeCaller()

class Brain:
  def __init__(self, game: Game, player_id: str):
    self.game = game
    self.player_id = player_id
    self.current_plan = None
    self.promises = []
    self.recent_responses = []

  def record_response(self, prompt, response):
    logger.info(f"Bot {self.player_id} record response: {prompt}, {response}")
    self.recent_responses.append({
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
        self.record_response(prompt, response)
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
    # elif self.game.stage == "production":
    #   self.EconomyMoveCall()
    # elif self.game.stage == "bid":
    #   self.BidMoveCall()

  def get_recent_responses(self):
    return self.recent_responses
