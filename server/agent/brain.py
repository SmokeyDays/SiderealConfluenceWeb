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
    """
    TurnPlanCall should update the current_plan of this agent.
    Should give the resoureces needed, buy, sell, borrow and factories to run and to upgrade in the plan.
    Should behave faithfully according to the promises before give proposals.
    Should give proposals according to the current plan.

    
    :param self:
    :return:
    :rtype: Any
    """
    return TurnPlanCaller.sth
  
  def EconomyMoveCall(self):
    """
    EconomyMoveCall should make economic moves based on the plan and resources.
    
    :param self: 
    :return: 
    :rtype: 
    """
    return EconomyMoveCaller.sth

  def BidMoveCall(self):
    """
    BidMoveCall should make bidding moves based on resources and species, 
    may seeing other players' resources and species.
    
    :param self: 
    :return: 
    :rtype: Any
    """
    return BidMoveCaller.sth
  
  def EvaluateTransactionCall(self, player_id, transaction):
    """
    EvaluateTransactionCall should go through all current transaction;
    return whether to accept the transaction or not.
    If accept, should send a pre-confirm request to the server.

    "For each proposal, the server should change the state of transaction from pending to lock,
    and should check and freeze the resources involved in the transaction.
    For already locked transaction, server should refuse the pre-confirm. 

    After the transaction, the game description changed, 
    it maybe should be updated after each transaction, or a fixed time interval?
    and the agent may update the current plan accordingly."


    
    :param self: 说明
    :param player_id: 说明
    :param transaction: 说明
    """
    return sth.

  

### some maybe useful functions
# def ChatCall(self, self.current_plan, self.promises):
