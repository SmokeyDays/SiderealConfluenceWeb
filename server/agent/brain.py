from server.agent.prompt import get_prompt
from server.game import Game
from server.agent.llm_caller import BasicCaller, TradeCaller, TurnPlanCaller

turn_plan_caller = TurnPlanCaller()
trade_caller = TradeCaller()

class Brain:
  def __init__(self, game: Game, player_id: str):
    self.game = game
    self.player_id = player_id
    self.current_plan = "There is no specific plan for this turn."
    self.promises = []  

  def step(self, handlers_prompt, handlers_map):
    """
    Auto detect the current stage of the game and call the corresponding function.
    """
    rule, obs = get_prompt(self.game, self.player_id)
    if self.game.stage == "trading":
      if self.current_plan == None:
        turn_plan_caller.plan(rule, obs)
      callbacks = trade_caller.plan(rule, obs, handlers_prompt)
      for callback in callbacks:
        func, data = callback['func'], callback['data']
        func(data)
    # elif self.game.stage == "production":
    #   self.EconomyMoveCall()
    # elif self.game.stage == "bid":
    #   self.BidMoveCall()
