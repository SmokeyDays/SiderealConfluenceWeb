import datetime
import textwrap
from flask_socketio import emit, join_room, leave_room
from server.agent.prompt import get_prompt
from server.game import Game
from server.room import Room
from server.utils.decorators import Registry, add_para_desc, set_attr
from server.utils.pubsub import pubsub
from server.utils.connect import create_app, get_router_name
from server.utils.logger import log
from server.message import Message, MessageManager
from server.utils.achievement import unlock_achievement, achievement_manager
from server.user import user_manager
from server.utils.saver_loader import load_all_rooms, save_room

class Server:
  def __init__(self):
    self.app, self.socketio = create_app()
    
    self.online_users = {}
    # self.rooms: dict[str, Room] = {}
    self.rooms = load_all_rooms()
    self.message_manager = MessageManager(on_new_msg=self.on_new_msg)
    
    self.mock1()
    self.mock2()
    self.mock3()
    
    self.bind_basic_events()
    self.bind_lobby_events()
    self.bind_game_events()
    self.bind_query_events()
    
  
  def mock1(self):
    user_manager.get_user("Alice")
    user_manager.get_user("Bob")
    user_manager.get_user("Charlie")
    user_manager.get_user("David")
    self.rooms["test"] = Room(4, "test", 2)
    test_room = self.rooms['test']
    test_room.enter_room("Alice")
    test_room.enter_room("Bob")
    test_room.enter_room("Charlie")
    test_room.enter_room("David")

    self.new_msg(Message("Alice", "HelloGlobal", str(datetime.datetime.now()), None, None))
    self.new_msg(Message("Bob", "HelloGlobal", str(datetime.datetime.now()), None, None))
    self.new_msg(Message("Alice", "HelloRoom", str(datetime.datetime.now()), "test"))
    self.new_msg(Message("Bob", "HelloRoom", str(datetime.datetime.now()), "test"))
    self.new_msg(Message("Alice", "HelloBob", str(datetime.datetime.now()), None, "Bob"))
    self.new_msg(Message("Bob", "HelloAlice", str(datetime.datetime.now()), None, "Alice"))

    test_room.choose_specie("Alice", "Faderan")
    test_room.choose_specie("Bob", "Eni")
    test_room.choose_specie("Charlie", "Unity")
    test_room.choose_specie("David", "Yengii")
    test_room.agree_to_start("Alice")
    test_room.agree_to_start("Bob")
    test_room.agree_to_start("Charlie")
    test_room.agree_to_start("David")
    test_room.game.develop_tech("Alice", "纳米科技")
    test_room.game.develop_tech("Alice", "反物质能源")
    test_room.game.develop_tech("David", "跨种族道德平等")
    test_room.game.debug_draw_colony("Bob")
    test_room.game.debug_add_item("Alice", "Ship", 5)
    test_room.game.debug_add_item("Bob", "Ship", 5)
    test_room.game.debug_add_item("Alice", "Score", 5)
    test_room.game.debug_add_item("Alice", "ScoreDonation", 10)
    test_room.game.debug_add_item("Alice", "Hypertech", 5)
    test_room.game.debug_add_item("Alice", "Industry", 5)
    test_room.game.debug_add_item("David", "Culture", 5)
    test_room.game.debug_add_item("Alice", "Ice", 5)
    test_room.game.debug_add_item("Alice", "WildSmall", 5)
    test_room.game.debug_add_item("Alice", "WildBig", 5)
    test_room.game.debug_add_item("David", "WildBig", 6)
    test_room.game.gift("Bob", "Alice", {"factories": ["恩尼艾特_相互理解"]})
    test_room.game.gift("Alice", "Bob", {"items": {"Favor": 10}})
    for _ in range(10):
      test_room.game.trade_proposal("Alice", 
                                  ["Bob"], 
                                  {"items": {"Food": 1}, "factories": ["凯利安_跨种族道德平等"], "techs": ["跨种族道德平等"]}, 
                                  {"items": {"Culture": 1}, "factories": ["恩尼艾特_文化包容"]})
    suc, msg, id = test_room.game.trade_proposal("David", ["Alice"], {"items": {"Culture": 2}, "factories": ["岩基艾_跨种族道德平等"], "techs": ["跨种族道德平等"]}, {"items": {"ScoreDonation": 1}})
    suc, msg = test_room.game.accept_trade_proposal("Alice", id)
    for _ in range(12):
      test_room.game.draw_special_deck(test_room.game.players[0], "FaderanRelicWorld")
    suc, msg, id = test_room.game.trade_proposal("Alice", ["David"], {"items": {"Favor": 10}, "factories": ["法德澜_杜伦泰的赠礼"], "techs": []}, {"items": {}, "factories": []})
    suc, msg = test_room.game.accept_trade_proposal("David", id)
    return
    # skip trading
    test_room.game.player_agree("Alice")
    test_room.game.player_agree("Bob")
    # skip production
    test_room.game.player_agree("Alice")
    test_room.game.player_agree("Bob")
    # skip bidding
    test_room.game.submit_bid("Alice", 4, 2)
    test_room.game.submit_bid("Bob", 2, 3)
    test_room.game.submit_pick("Bob", "colony", 0)
    test_room.game.submit_pick("Alice", "colony", 1)
    test_room.game.submit_pick("Bob", "research", 0)
    test_room.game.submit_pick("Alice", "research", 1)
    # skip t1 trading
    test_room.game.player_agree("Alice")
    test_room.game.player_agree("Bob")
    # skip t1 production
    # test_room.game.player_agree("Alice")
    test_room.game.player_agree("Bob")
    return
  
  def mock2(self):
    self.rooms["test2"] = Room(4, "test2", 4)
    test_room = self.rooms['test2']
    test_room.enter_room("Alice")
    test_room.enter_room("Bob")
    test_room.enter_room("Charlie")
    test_room.enter_room("David")

    self.new_msg(Message("Alice", "HelloRoom", str(datetime.datetime.now()), "test2"))
    self.new_msg(Message("Bob", "HelloRoom", str(datetime.datetime.now()), "test2"))
    self.new_msg(Message("Charlie", "HelloRoom", str(datetime.datetime.now()), "test2"))
    self.new_msg(Message("David", "HelloRoom", str(datetime.datetime.now()), "test2"))

    test_room.choose_specie("Alice", "Kjasjavikalimm")
    test_room.choose_specie("Bob", "Eni")
    test_room.choose_specie("Charlie", "Unity")
    test_room.choose_specie("David", "Yengii")

    test_room.agree_to_start("Alice")
    test_room.agree_to_start("Bob")
    test_room.agree_to_start("Charlie")
    test_room.agree_to_start("David")
    # add debug items
    test_room.game.debug_add_item("Alice", "Ship", 10)
    test_room.game.debug_add_item("Bob", "Ship", 10)
    test_room.game.debug_add_item("Charlie", "Ship", 10)
    test_room.game.debug_add_item("David", "Ship", 10)
    # skip trading
    test_room.game.player_agree("Alice")
    test_room.game.player_agree("Bob")
    test_room.game.player_agree("Charlie")
    test_room.game.player_agree("David")
    # skip production
    test_room.game.player_agree("Alice")
    test_room.game.player_agree("Bob")
    test_room.game.player_agree("Charlie")
    test_room.game.player_agree("David")
    # skip bidding
    test_room.game.submit_bid("Alice", 4, 2)
    test_room.game.submit_bid("Bob", 2, 3)
    test_room.game.submit_bid("Charlie", 1, 1)
    test_room.game.submit_bid("David", 1, 5)

    test_room.game.Kajsjavikalimm_split("Alice", True)

    test_room.game.submit_pick("Bob", "colony", 0)
    test_room.game.submit_pick("Alice", "colony", 1)
    test_room.game.submit_pick("Alice", "colony", 2)
    test_room.game.submit_pick("David", "colony", -1)
    test_room.game.submit_pick("Charlie", "colony", -1)
    return
  
  def mock3(self):
    print(get_prompt(self.rooms["test2"].game, "Alice"))
    return
    
  def run(self, **kwargs):
    self.socketio.run(self.app, **kwargs)

  def send_new_msg(self, user_id, msg):
    self.socketio.emit("new-message", {"msg": msg.to_dict()}, namespace=get_router_name(), to=user_id)

  def on_new_msg(self, msg: Message):
    room = msg.room
    user = msg.user
    receivers = []
    if room is None:
      if user is None:
        for online_user, _ in self.online_users.items():
          receivers.append(online_user)
      else:
        receivers.append(user)
    else:
      if room not in self.rooms:
        log('error', f"Room {room} not found")
      if user is None:
        for user_id in self.rooms[room].players:
          receivers.append(user_id)
      else:
        if user not in self.rooms[room].players:
          log('error', f"User {user} not found in room {room}")
          return
        receivers.append(user)
      for receiver in receivers:
        if receiver != msg.sender:
          self.send_new_msg(receiver, msg)
  
  def new_msg(self, msg: Message):
    self.message_manager.new_msg(msg)

  def bind_basic_events(self):
    @self.socketio.on('connect', namespace=get_router_name())
    def connected_success():
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
      self.online_users[username] = self.online_users.get(username, 0) + 1
      user = user_manager.get_user(username)
      msgs = self.message_manager.get_msgs_by_user(username)
      emit('sync-chat', {"msgs": [msg.to_dict() for msg in msgs]}, namespace=get_router_name())
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
      self.online_users[username] = self.online_users.get(username, 0) - 1
      if self.online_users[username] <= 0:
        self.online_users.pop(username)

    @self.socketio.on('send-message', namespace=get_router_name())
    def send_msg(data):
      msg = Message(
        data['sender'],
        data['msg'], 
        data['date'], 
        data['room'] if 'room' in data else None, 
        data['user'] if 'user' in data else None
      )
      self.new_msg(msg)

    @self.socketio.on('admin-command', namespace=get_router_name())
    def admin_command(data):
      command = data['command']
      try:
        eval(command, {"self": self})
      except Exception as e:
        emit('alert-message', {
          "type": "error",
          "title": "Admin Command Failed",
          "str": f"Command failed: {e}"
        }, namespace=get_router_name())

  def update_rooms(self):
    rooms = {}
    for room_name, room in self.rooms.items():
      rooms[room_name] = room.to_dict()
    self.socketio.emit("room-list", {"rooms": rooms}, namespace=get_router_name())

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
      self.rooms[room_name] = Room(max_players, room_name, 5)
      self.rooms[room_name].enter_room(data['username'])
      unlock_achievement(data['username'], "create_room")
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
    
    @self.socketio.on('delete-room', namespace=get_router_name())
    def delete_room(data):
      room_name = data['room_name']
      if room_name in self.rooms:
          room = self.rooms[room_name]
          
          if len(room.players) == 0:
              del self.rooms[room_name]
              self.update_rooms()
              emit('alert-message', {
                "type": "success",
                "title": "Delete room",
                "str": f"You have delete room {room_name}."
              }, namespace=get_router_name())
          else:
              emit('alert-message', {
                "type": "error",
                "title": "Can not delete room",
                "str": f"Room {room_name} is not empty."
              }, namespace=get_router_name())
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
    
    @self.socketio.on('set-end-round', namespace=get_router_name())
    def handle_set_end_round(data):
        room_name = data['room_name']
        end_round = data['end_round']
        
        if room_name in self.rooms:
          self.rooms[room_name].set_end_round(end_round)
          self.update_rooms()
          emit('alert-message', {
            "type": "success",
            "title": "End round changed",
            "str": f"You have changed end round of room {room_name} to {end_round}."
          }, namespace=get_router_name())

  def update_game_state(self, room_name):
    if room_name in self.rooms:
      for user_id in self.rooms[room_name].players:
        self.socketio.emit("game-state", {"state": self.rooms[room_name].game.to_dict()}, namespace=get_router_name(), to=user_id)
      save_room(self.rooms[room_name])
  def bind_game_events(self):

    registry = Registry()
    
    @self.socketio.on('get-game-state', namespace=get_router_name())
    def get_game_state(data):
      room_name = data['room_name']
      username = data['username']
      emit("game-state", {"state": self.rooms[room_name].game.to_dict()}, namespace=get_router_name())

    @self.socketio.on('gift', namespace=get_router_name())
    def gift(data):
      room_name = data['room_name']
      username = data['username']
      success, message = self.rooms[room_name].game.gift(username, data['to'], data['gift'])
      emit('alert-message', {
        "type": "success" if success else "error",
        "title": "Gift Success" if success else "Gift Failed",
        "str": message
      }, namespace=get_router_name())
      self.update_game_state(room_name)
    
    @registry("game-interface")
    @set_attr("stage", ["trading"])
    @self.socketio.on('trade-proposal', namespace=get_router_name())
    def trade_proposal(data):
      """
      trade_proposal: Propose a trade to the other players in the game.
        - to: [player1, player2, ...], players you propose to trade with.
        - send: {items: Dict[item_name, item_count], factories: [factory1, factory2, ...], techs: [tech1, tech2, ...]}, items, factories and techs that you send to the other players in the trade.
        - receive: {items: Dict[item_name, item_count], factories: [factory1, factory2, ...], techs: [tech1, tech2, ...]}, items, factories and techs that you receive from the other players in the trade.
        - message: str, any other notes you want to attach to the trade proposal.
      """
      room_name = data['room_name']
      username = data['username']
      success, message, id = self.rooms[room_name].game.trade_proposal(username, data['to'], data['send'], data['receive'], data['message'])
      emit('alert-message', {
        "type": "success" if success else "error",
        "title": "Trade Proposal Success" if success else "Trade Proposal Failed",
        "str": message
      }, namespace=get_router_name())
      self.update_game_state(room_name)

    @registry("game-interface")
    @set_attr("stage", ["trading"])
    @self.socketio.on('decline-trade-proposal', namespace=get_router_name())
    def decline_trade_proposal(data):
      """
      decline_trade_proposal: Decline a trade proposal you proposed.
        - id: int, the id of the trade proposal to decline.
      """
      room_name = data['room_name']
      username = data['username']
      success, message = self.rooms[room_name].game.decline_trade_proposal(username, data['id'])
      emit('alert-message', {
        "type": "success" if success else "error",
        "title": "Decline Trade Proposal Success" if success else "Decline Trade Proposal Failed",
        "str": message
      }, namespace=get_router_name())
      self.update_game_state(room_name)

    @registry("game-interface")
    @set_attr("stage", ["trading"])
    @self.socketio.on('accept-trade-proposal', namespace=get_router_name())
    def accept_trade_proposal(data):
      """
      accept_trade_proposal: Accept a trade proposal you received.
        - id: int, the id of the trade proposal to accept.
      """
      room_name = data['room_name']
      username = data['username']
      success, message = self.rooms[room_name].game.accept_trade_proposal(username, data['id'])
      emit('alert-message', {
        "type": "success" if success else "error",
        "title": "Accept Trade Proposal Success" if success else "Accept Trade Proposal Failed",
        "str": message
      }, namespace=get_router_name())
      self.update_game_state(room_name)

    @registry("game-interface")
    @set_attr("stage", ["production"])
    @self.socketio.on('produce', namespace=get_router_name())
    def produce(data):
      """
      produce: Select a converter of a factory to produce.
        - factory_name: str, the name of the factory to produce.
        - converter_index: int, the index of the converter to produce.
        - extra_properties: Dict[str, Any], at most of time, this is {}. When cost type must be specified (e.g. when converter input is described as "item_a / item_b"), there should be {cost_type: "item_a"}.
      """
      room_name = data['room_name']
      username = data['username']
      extra_properties = data['extra_properties'] if 'extra_properties' in data else {}
      converter_index = data['converter_index'] if 'converter_index' in data else 0
      log("info", f"produce: {room_name}, {username}, {data['factory_name']}, {extra_properties}")
      success, message = self.rooms[room_name].game.produce(username, data['factory_name'], converter_index, extra_properties)
      emit('alert-message', {
        "type": "success" if success else "error",
        "title": "Produce Success" if success else "Produce Failed",
        "str": message
      }, namespace=get_router_name())
      self.update_game_state(room_name)

    @registry("game-interface")
    @set_attr("stage", ["trading", "production"])
    @self.socketio.on('agree', namespace=get_router_name())
    def agree(data):
      """
      agree: Agree to continue the game and go to the next stage.
      """
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

    @registry("game-interface")
    @set_attr("stage", ["bid"])
    @self.socketio.on('submit-bid', namespace=get_router_name())
    def submit_bid(data):
      """
      submit_bid: Submit a bid for bidding cards.
        - colony_bid: int, your bid for the colony.
        - research_bid: int, your bid for the research.
      """
      room_name = data['room_name']
      username = data['username']
      self.rooms[room_name].game.submit_bid(username, data['colony_bid'], data['research_bid'])
      self.update_game_state(room_name)

    @self.socketio.on('submit-kajsjavikalimm-choose-split', namespace=get_router_name())
    def submit_kajsjavikalimm_choose_split(data):
      room_name = data['room_name']
      username = data['username']
      self.rooms[room_name].game.Kajsjavikalimm_split(username, data['choose_split'])
      self.update_game_state(room_name)

    @registry("game-interface")
    @set_attr("stage", ["pick"])
    @self.socketio.on('submit-pick', namespace=get_router_name())
    def pick_item(data):
      """
      submit_pick: Pick an item from the deck.
        - type: str, the type of the item to pick. It can be "colony" or "research".
        - pick_id: int, the id of the item to pick.
      """
      room_name = data['room_name']
      username = data['username']
      self.rooms[room_name].game.submit_pick(username, data['type'], data['pick_id'])
      self.update_game_state(room_name)

    @registry("game-interface")
    @set_attr("stage", ["trading"])
    @self.socketio.on('upgrade-colony', namespace=get_router_name())
    def upgrade_colony(data):
      """
      upgrade_colony: Upgrade a colony.
        - factory_name: str, the name of the colony to upgrade.
      """
      room_name = data['room_name']
      username = data['username']
      self.rooms[room_name].game.upgrade_colony(username, data['factory_name'])
      self.update_game_state(room_name)

    @registry("game-interface")
    @set_attr("stage", ["trading"])
    @self.socketio.on('upgrade-normal', namespace=get_router_name())
    def upgrade_normal(data):
      """
      upgrade_normal: Upgrade a normal factory.
        - factory_name: str, the name of the factory to upgrade.
        - cost_type: str, id of the cost type you choose to upgrade.
      """
      room_name = data['room_name']
      username = data['username']
      success, message = self.rooms[room_name].game.upgrade_normal(username, data['factory_name'], data['cost_type'])
      emit('alert-message', {
        "type": "success" if success else "error",
        "title": "Upgrade Success" if success else "Upgrade Failed",
        "str": message
      }, namespace=get_router_name())
      self.update_game_state(room_name)

    @registry("game-interface")
    @set_attr("stage", ["trading"])
    @self.socketio.on('exchange-colony', namespace=get_router_name())
    def exchange_colony(data):
      """
      exchange_colony: Exchange a colony for a material.
        - colony_name: str, the name of the colony you spend to exchange.
      """
      room_name = data['room_name']
      username = data['username']
      self.rooms[room_name].game.exchange_colony(username, data['colony_name'])
      self.update_game_state(room_name)

    @registry("game-interface")
    @set_attr("stage", ["trading"])
    @self.socketio.on('exchange-arbitrary', namespace=get_router_name())
    def exchange_arbitrary(data):
      """
      exchange_arbitrary: If a converter requires "AnySmall" or "AnyBig", you can use this to exchange your blocks for the converter. Industry, Culture and Food will be exchanged for "AnySmall" and Biotech, Energy and Information will be exchanged for "AnyBig".
        - items: Dict[str, int], the items you want to exchange.
      """
      room_name = data['room_name']
      username = data['username']
      self.rooms[room_name].game.exchange_arbitrary(username, data['items'])
      self.update_game_state(room_name)
    
    @registry("game-interface")
    @set_attr("stage", ["trading"])
    @self.socketio.on('exchange-wild', namespace=get_router_name())
    def exchange_wild(data):
      """
      exchange_wild: If you have "WildSmall" or "WildBig" in your hand, you can use this to exchange them for any blocks. WildSmall will be exchanged for Industry, Culture or Food. WildBig will be exchanged for Biotech, Energy or Information.
        - items: Dict[str, int], the items you want to exchange. e.g. {"Industry": 1, "Culture": 1, "Biotech": 1} will spend 2 WildSmall and 1 WildBig automatically.
      """
      room_name = data['room_name']
      username = data['username']
      self.rooms[room_name].game.exchange_wild(username, data['items'])
      self.update_game_state(room_name)

    @registry("game-interface")
    @set_attr("stage", ["trading"])
    @self.socketio.on('discard-colonies', namespace=get_router_name())
    def discard_colonies(data):
      room_name = data['room_name']
      username = data['username']
      self.rooms[room_name].game.discard_colonies(username, data['colonies'])
      self.update_game_state(room_name)

    def gen_prompt(stage):
      handles = self.registry.get("game-interface")
      handle_map = {}
      prompt = ""
      for handle in handles:
        if handle.attrs.get("stage") == stage:
          desc = textwrap.dedent(handle.__doc__)
          prompt += f"{desc}\n"
        if handle.attrs.get("name"):
          handle_map[handle.attrs.get("name")] = handle
      return prompt, handle_map


    def parse(func, data):
      func(data)
    
  def update_achievements(self, user_id: str):
    user = user_manager.get_user(user_id)
    achievements = user.achievements
    achievements_dict = {}
    for achievement_id in achievements:
      achievements_dict[achievement_id] = achievement_manager.get_achievement(achievement_id).to_dict()
      achievements_dict[achievement_id]["unlocked"] = achievements[achievement_id]
    emit('sync-achievements', {
      "achievements": achievements_dict
    }, namespace=get_router_name(), to=user_id)

  def add_achievement(self, user_id: str, achievement_id: str):
    emit('add-achievement', {
      "achievement": achievement_manager.get_achievement(achievement_id).to_dict(),
      "username": user_id
    }, namespace=get_router_name(), to=user_id)
    self.update_achievements(user_id)
    user_manager.save_users()

  def bind_query_events(self):
    @self.socketio.on('query-factory', namespace=get_router_name())
    def query_factory(data):
      room_name = data['room_name']
      username = data['username']
      factory_name = data['factory_name']
      factory = self.rooms[room_name].game.get_factory(username, factory_name)
      emit('factory-data', {
        "room_name": room_name,
        "factory": factory.to_dict()
      }, namespace=get_router_name())

    @self.socketio.on('query-achievement', namespace=get_router_name())
    def query_achievement(data):
      username = data['username']
      self.update_achievements(username)

    @self.socketio.on('query-prompt', namespace=get_router_name())
    def query_prompt(data):
      room_name = data['room_name']
      username = data['username']
      prompt = get_prompt(self.rooms[room_name].game, username)
      emit('prompt', {
        "prompt": prompt
      }, namespace=get_router_name())
    
    def add_achievement_listener(data):
      self.add_achievement(data['username'], data['id'])
    pubsub.subscribe("add_achievement", add_achievement_listener)
