from flask_socketio import join_room
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
    self.rooms["test"].choose_specie("Alice", "Caylion")
    self.rooms["test"].choose_specie("Bob", "Yengii")
    self.rooms["test"].agree_to_start("Alice")
    self.rooms["test"].agree_to_start("Bob")
  
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
      self.socketio.emit('alert-message', {
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
      self.socketio.emit('alert-message', {
        "type": "success",
        "title": "Logged in",
        "str": f"Welcome, {username}!"
      }, namespace=get_router_name())
      self.socketio.emit('login-success', {
        "username": username
      }, namespace=get_router_name())

  def bind_lobby_events(self):
    @self.socketio.on('get-room-list', namespace=get_router_name())
    def get_room_list():
      rooms = {}
      for room_name, room in self.rooms.items():
        rooms[room_name] = room.to_dict()
      self.socketio.emit("room-list", {"rooms": rooms}, namespace=get_router_name())

    @self.socketio.on('create-room', namespace=get_router_name())
    def create_room(data):
      room_name = data['room_name']
      max_players = 9
      if room_name in self.rooms:
        self.socketio.emit('alert-message', {
          "type": "error",
          "title": "Room already exists",
          "str": f"Room {room_name} already exists."
        }, namespace=get_router_name())
        return
      self.rooms[room_name] = Room(max_players, room_name)
      self.socketio.emit('alert-message', {
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
        self.socketio.emit('alert-message', {
          "type": "success",
          "title": "Joined room",
          "str": f"You have joined room {room_name}."
        }, namespace=get_router_name())
        self.update_rooms()
      else:
        self.socketio.emit('alert-message', {
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
        self.socketio.emit('alert-message', {
          "type": "success",
          "title": "Left room",
          "str": f"You have left room {room_name}."
        }, namespace=get_router_name())
        self.update_rooms()
      else:
        self.socketio.emit('alert-message', {
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
          self.socketio.emit('alert-message', {
            "type": "error",
            "title": "Invalid specie",
            "str": f"specie {specie} is not a valid specie."
          }, namespace=get_router_name())
      else:
        self.socketio.emit('alert-message', {
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

  def update_game_state(self, room_name):
    if room_name in self.rooms:
      for user_id in self.rooms[room_name].players:
        self.socketio.emit("game-state", {"state": self.rooms[room_name].game.to_dict()}, namespace=get_router_name(), to=user_id)

  def bind_game_events(self):
    @self.socketio.on('get-game-state', namespace=get_router_name())
    def get_game_state(data):
      room_name = data['room_name']
      username = data['username']
      self.socketio.emit("game-state", {"state": self.rooms[room_name].game.to_dict()}, namespace=get_router_name())

