from server.agent.prompt import get_prompt
from server.game import Game


class Brain:
  def __init__(self, game: Game, player_id: str):
    self.game = game
    self.player_id = player_id
    self.current_plan = "There is no specific plan for this turn."
    self.promises = []
    
  def call(self, prompt):
    return call_llm(llm_name, prompt)