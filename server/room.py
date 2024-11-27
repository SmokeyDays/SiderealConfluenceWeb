from server.game import Game
from server.utils.pubsub import pubsub

class Room:
  def __init__(self, max_players, name, end_round):
    self.name = name
    self.end_round = end_round
    self.max_players = max_players
    self.players = {}
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

  def to_dict(self):
    return {
      "name": self.name,
      "players": self.players,
      "game_state": self.game_state,
      "max_players": self.max_players
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