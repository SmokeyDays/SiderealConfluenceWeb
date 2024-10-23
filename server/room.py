from server.game import Game

class Room:
  def __init__(self, max_players, name):
    self.name = name
    self.max_players = max_players
    self.players = {}
    self.game_state = "waiting"
    self.game = None
    self.spices = ["Kylion", "Eni", "Im", "Yengii", "Zeth", "Unity", "Faderan"]

  def enter_room(self, user_id):
    if user_id in self.players:
      return False
    if len(self.players) < self.max_players:
      self.players[user_id] = {
        "spice": None,
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

  def choose_spice(self, user_id, spice):
    if user_id in self.players and spice in self.spices:
      self.players[user_id]["spice"] = spice
      return True
    else:
      return False

  def agree_to_start(self, user_id):
    if user_id in self.players:
      self.players[user_id]["agreed"] = True
      if all(player["agreed"] for player in self.players.values()):
        self.game_state = "started"
        self.start_game()
      return True
    else:
      return False
    
  def start_game(self):
    self.game = Game()
    for player in self.players.values():
      self.game.add_player(player["spice"], player["user_id"])
    self.game_state = "playing"

  def to_dict(self):
    return {
      "name": self.name,
      "players": self.players,
      "game_state": self.game_state,
    }

    """
    The room state dictionary has the following structure:
    {
      "name": str,
      "players": {
        "user_id": str,
        "spice": str,
        "agreed": bool
      },
      "game_state": str
    }
    """