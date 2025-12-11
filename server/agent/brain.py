from server.agent.prompt import get_prompt
from server.game import Game
from server.agent.llm_caller import BasicCaller, TurnPlanCaller

class Brain:
  def __init__(self, game: Game, player_id: str):
    self.game = game
    self.player_id = player_id
    self.current_plan = "There is no specific plan for this turn."
    self.promises = []  
    self.turn_plan_caller = TurnPlanCaller()



     
  def TurnPlanCall(self):
    return TurnPlanCaller.sth
  
  def EconomyMoveCall(self):
    return EconomyMoveCaller.sth

  def BidMoveCall(self):
    return BidMoveCaller.sth
  

### some maybe useful functions
# def ChatCall(self, self.current_plan, self.promises):
# def EvaluateTransactionCall(self, player_id, transaction):