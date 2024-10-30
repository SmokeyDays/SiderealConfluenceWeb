from flask_socketio import emit, join_room, leave_room
from server.game import Game
from server.room import Room
from server.utils.connect import create_app, get_router_name

class Server:
  def __init__(self):
    self.app, self.socketio = create_app()
    
    self.rooms = {}
    
    self.mock()
    self.bind_basic_events()
    self.bind_lobby_events()
    self.bind_game_events()
  
  def mock(self):
    self.rooms["test"] = Room(2, "test")
    self.rooms["test"].enter_room("Alice")
    self.rooms["test"].enter_room("Bob")
    self.rooms["test"].choose_specie("Alice", "Eni")
    self.rooms["test"].choose_specie("Bob", "Yengii")
    self.rooms["test"].agree_to_start("Alice")
    self.rooms["test"].agree_to_start("Bob")
    self.rooms["test"].game.develop_tech("Alice", "跨种族道德平等")
    self.rooms["test"].game.develop_tech("Alice", "基因工程学")
    self.rooms["test"].game.debug_draw_colony("Alice")
    self.rooms["test"].game.debug_add_item("Alice", "Ship", 5)
    self.rooms["test"].game.debug_add_item("Bob", "Ship", 5)
    self.rooms["test"].game.debug_add_item("Alice", "Score", 5)
    self.rooms["test"].game.debug_add_item("Alice", "ScoreDonation", 1)
    # skip trading
    self.rooms["test"].game.player_agree("Alice")
    self.rooms["test"].game.player_agree("Bob")
    # skip production
    self.rooms['test'].game.player_agree("Alice")
    self.rooms['test'].game.player_agree("Bob")
    self.rooms['test'].game.submit_bid("Alice", 3, 2)
    self.rooms['test'].game.submit_bid("Bob", 1, 3)
    self.rooms['test'].game.submit_pick("Alice", "colony", 0)
    self.rooms['test'].game.submit_pick("Bob", "colony", 1)
    self.rooms['test'].game.submit_pick("Bob", "research", 0)
    self.rooms['test'].game.submit_pick("Alice", "research", 1)
    


  def run(self, **kwargs):
    self.socketio.run(self.app, **kwargs)

  def update_rooms(self):
    rooms = {}
    for room_name, room in self.rooms.items():
      rooms[room_name] = room.to_dict()
    self.socketio.emit("room-list", {"rooms": rooms}, namespace=get_router_name())

  def bind_basic_events(self):
    @self.socketio.on('connect', namespace=get_router_name())
    def connected_success():
      print('client connected.')
      emit('alert-message', {
        "type": "success",
        "title": "Connected",
        "str": "Connected to the server successfully."
      }, namespace=get_router_name())

    @self.socketio.on('login', namespace=get_router_name())
    def login(data):
      username = data['username']
      # Note that the 'join_room' here is just for the socketio usage, not the room object in the server.
      # Whenever we send a message to a user, we should use the 'to' parameter and specify the username as the room name.
      join_room(username)
      emit('alert-message', {
        "type": "success",
        "title": "Logged in",
        "str": f"Welcome, {username}!"
      }, namespace=get_router_name())
      emit('login-success', {
        "username": username
      }, namespace=get_router_name())
    
    @self.socketio.on('logout', namespace=get_router_name())
    def logout(data):
      username = data['username']
      leave_room(username)

  def bind_lobby_events(self):
    @self.socketio.on('get-room-list', namespace=get_router_name())
    def get_room_list():
      rooms = {}
      for room_name, room in self.rooms.items():
        rooms[room_name] = room.to_dict()
      emit("room-list", {"rooms": rooms}, namespace=get_router_name())

    @self.socketio.on('create-room', namespace=get_router_name())
    def create_room(data):
      room_name = data['room_name']
      max_players = 9
      if room_name in self.rooms:
        emit('alert-message', {
          "type": "error",
          "title": "Room already exists",
          "str": f"Room {room_name} already exists."
        }, namespace=get_router_name())
        return
      self.rooms[room_name] = Room(max_players, room_name)
      self.rooms[room_name].enter_room(data['username'])
      emit('alert-message', {
        "type": "success",
        "title": "Room created",
        "str": f"Room {room_name} created successfully."
      }, namespace=get_router_name())
      self.update_rooms()

    @self.socketio.on('enter-room', namespace=get_router_name())
    def enter_room(data):
      room_name = data['room_name']
      username = data['username']
      if room_name in self.rooms:
        self.rooms[room_name].enter_room(username)
        emit('alert-message', {
          "type": "success",
          "title": "Joined room",
          "str": f"You have joined room {room_name}."
        }, namespace=get_router_name())
        self.update_rooms()
      else:
        emit('alert-message', {
          "type": "error",
          "title": "Room not found",
          "str": f"Room {room_name} not found."
        }, namespace=get_router_name())

    @self.socketio.on('leave-room', namespace=get_router_name())
    def leave_room(data):
      room_name = data['room_name']
      username = data['username']
      if room_name in self.rooms:
        self.rooms[room_name].leave_room(username)
        emit('alert-message', {
          "type": "success",
          "title": "Left room",
          "str": f"You have left room {room_name}."
        }, namespace=get_router_name())
        self.update_rooms()
      else:
        emit('alert-message', {
          "type": "error",
          "title": "Room not found",
          "str": f"Room {room_name} not found."
        }, namespace=get_router_name())
    
    @self.socketio.on('choose-specie', namespace=get_router_name())
    def choose_specie(data):
      room_name = data['room_name']
      username = data['username']
      specie = data['specie']
      print(f"choose_specie: {room_name}, {username}, {specie}")
      if room_name in self.rooms:
        if specie in self.rooms[room_name].species:
          self.rooms[room_name].choose_specie(username, specie)
          self.update_rooms()
        else:
          emit('alert-message', {
            "type": "error",
            "title": "Invalid specie",
            "str": f"specie {specie} is not a valid specie."
          }, namespace=get_router_name())
      else:
        emit('alert-message', {
          "type": "error",
          "title": "Room not found",
          "str": f"Room {room_name} not found."
        }, namespace=get_router_name())

    @self.socketio.on('agree-to-start', namespace=get_router_name())
    def agree_to_start(data):
      room_name = data['room_name']
      username = data['username']
      if room_name in self.rooms:
        self.rooms[room_name].agree_to_start(username)
        self.update_rooms()
        if self.rooms[room_name].game_state == "playing":
          self.update_game_state(room_name)
    
    @self.socketio.on('disagree-to-start', namespace=get_router_name())
    def disagree_to_start(data):
      room_name = data['room_name']
      username = data['username']
      if room_name in self.rooms:
        self.rooms[room_name].disagree_to_start(username)
        self.update_rooms()

  def update_game_state(self, room_name):
    if room_name in self.rooms:
      for user_id in self.rooms[room_name].players:
        self.socketio.emit("game-state", {"state": self.rooms[room_name].game.to_dict()}, namespace=get_router_name(), to=user_id)

  def bind_game_events(self):
    @self.socketio.on('get-game-state', namespace=get_router_name())
    def get_game_state(data):
      room_name = data['room_name']
      username = data['username']
      emit("game-state", {"state": self.rooms[room_name].game.to_dict()}, namespace=get_router_name())

    @self.socketio.on('trade-items', namespace=get_router_name())
    def trade(data):
      room_name = data['room_name']
      username = data['username']
      success, message = self.rooms[room_name].game.trade(username, data['to'], data['items'])
      emit('alert-message', {
        "type": "success" if success else "error",
        "title": "Trade Success" if success else "Trade Failed",
        "str": message
      }, namespace=get_router_name())
      self.update_game_state(room_name)

    @self.socketio.on('lend-factory', namespace=get_router_name())
    def lend_factory(data):
      room_name = data['room_name']
      username = data['username']
      success, message = self.rooms[room_name].game.lend_factory(username, data['to'], data['factory_name'])
      emit('alert-message', {
        "type": "success" if success else "error",
        "title": "Lend Factory Success" if success else "Lend Factory Failed",
        "str": message
      }, namespace=get_router_name())
      self.update_game_state(room_name)

    @self.socketio.on('lend-factories', namespace=get_router_name())
    def lend_factories(data):
      room_name = data['room_name']
      username = data['username']
      factories = data['factories']
      to = data['to']
      for factory in factories:
        success, message = self.rooms[room_name].game.lend_factory(username, to, factory)
        if not success:
          emit('alert-message', {
            "type": "error",
            "title": "Lend Factory Failed",
            "str": message
          }, namespace=get_router_name())
      self.update_game_state(room_name)

    @self.socketio.on('produce', namespace=get_router_name())
    def produce(data):
      room_name = data['room_name']
      username = data['username']
      extra_properties = data['extra_properties'] if 'extra_properties' in data else {}
      print(f"produce: {room_name}, {username}, {data['factory_name']}, {extra_properties}")
      success, message = self.rooms[room_name].game.produce(username, data['factory_name'], extra_properties)
      emit('alert-message', {
        "type": "success" if success else "error",
        "title": "Produce Success" if success else "Produce Failed",
        "str": message
      }, namespace=get_router_name())
      self.update_game_state(room_name)

    @self.socketio.on('agree', namespace=get_router_name())
    def agree(data):
      room_name = data['room_name']
      username = data['username']
      self.rooms[room_name].game.player_agree(username)
      self.update_game_state(room_name)

    @self.socketio.on('disagree', namespace=get_router_name())
    def disagree(data):
      room_name = data['room_name']
      username = data['username']
      self.rooms[room_name].game.player_disagree(username)
      self.update_game_state(room_name)

    @self.socketio.on('submit-bid', namespace=get_router_name())
    def submit_bid(data):
      room_name = data['room_name']
      username = data['username']
      self.rooms[room_name].game.submit_bid(username, data['colony_bid'], data['research_bid'])
      self.update_game_state(room_name)
      print(f"submit-bid: {room_name}, {username}, {data['colony_bid']}, {data['research_bid']}")

    @self.socketio.on('submit-pick', namespace=get_router_name())
    def pick_item(data):
      room_name = data['room_name']
      username = data['username']
      self.rooms[room_name].game.submit_pick(username, data['type'], data['pick_id'])
      self.update_game_state(room_name)

    @self.socketio.on('upgrade-colony', namespace=get_router_name())
    def upgrade_colony(data):
      room_name = data['room_name']
      username = data['username']
      self.rooms[room_name].game.upgrade_colony(username, data['factory_name'])
      self.update_game_state(room_name)

    @self.socketio.on('upgrade-normal', namespace=get_router_name())
    def upgrade_normal(data):
      room_name = data['room_name']
      username = data['username']
      success, message = self.rooms[room_name].game.upgrade_normal(username, data['factory_name'], data['cost_type'])
      emit('alert-message', {
        "type": "success" if success else "error",
        "title": "Upgrade Success" if success else "Upgrade Failed",
        "str": message
      }, namespace=get_router_name())
      self.update_game_state(room_name)

    @self.socketio.on('exchange-colony', namespace=get_router_name())
    def exchange_colony(data):
      room_name = data['room_name']
      username = data['username']
      self.rooms[room_name].game.exchange_colony(username, data['colony_name'])
      self.update_game_state(room_name)

    @self.socketio.on('exchange-arbitrary', namespace=get_router_name())
    def exchange_arbitrary(data):
      room_name = data['room_name']
      username = data['username']
      self.rooms[room_name].game.exchange_arbitrary(username, data['items'])
      self.update_game_state(room_name)
    
    @self.socketio.on('exchange-wild', namespace=get_router_name())
    def exchange_wild(data):
      room_name = data['room_name']
      username = data['username']
      self.rooms[room_name].game.exchange_wild(username, data['items'])
      self.update_game_state(room_name)

    @self.socketio.on('grant-techs', namespace=get_router_name())
    def grant_tech(data):
      room_name = data['room_name']
      username = data['username']
      for tech in data['techs']:
        success, message = self.rooms[room_name].game.grant_tech(username, data['to'], tech)
        emit('alert-message', {
          "type": "success" if success else "error",
          "title": "Grant Tech Success" if success else "Grant Tech Failed",
          "str": message
        }, namespace=get_router_name())
      self.update_game_state(room_name)

    @self.socketio.on('discard-colonies', namespace=get_router_name())
    def discard_colonies(data):
      room_name = data['room_name']
      username = data['username']
      self.rooms[room_name].game.discard_colonies(username, data['colonies'])
      self.update_game_state(room_name)
    