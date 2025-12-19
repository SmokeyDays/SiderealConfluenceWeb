from server.agent.brain import Brain
from server.game import Game
from server.utils.log import logger
from server.utils.pubsub import pubsub
from typing import Dict, Any, List

class Room:
  def __init__(self, max_players, name, end_round):
    self.name = name
    self.end_round = end_round
    self.max_players = max_players
    self.players: Dict[str, Dict[str, Any]] = {}
    self.bots: List[str] = []
    self.bot_agents: Dict[str, Brain] = {}
    self.game_state = "waiting"
    self.game = None
    self.species = ["Caylion", "Yengii", "Im", "Eni", "Zeth", "Unity", "Faderan", "Kit", "Kjasjavikalimm"]

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

  def step_bots(self, get_handlers):
    handlers_prompt, handlers_map = get_handlers(self.game.stage)
    for bot in self.bots:
      if self.game.waiting_player(bot):
        self.bot_agents[bot].step(handlers_prompt, handlers_map)

  def step_bot(self, bot_id, get_handlers):
    if bot_id not in self.bots:
      logger.warning(f"Bot {bot_id} is not in room {self.name} as a bot.")
      return
    handlers_prompt, handlers_map = get_handlers(self.game.stage)
    logger.info(f"Stepping bot {bot_id} in room {self.name}")
    if bot_id in self.bots and self.game.waiting_player(bot_id):
      self.bot_agents[bot_id].step(handlers_prompt, handlers_map)

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
      "bots": self.bots
    }

    """
    The room state dictionary has the following structure:
    {
      "name": str,
      "players": {
        "user_id": str,
        "specie": str,
        "agreed": bool
      },
      "game_state": str,
      "max_players": int
    }
    """