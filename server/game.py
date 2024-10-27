import json
from typing import Any, Dict, List, Tuple
import random

class DataManager:
  def __init__(self, path: str):
    self.specie_factories = {}
    self.specie_init_players = {}
    self.species_data = {}
    self.species = ["Caylion", "Yengii"]
    self.load_species(path)

    self.researches_data = []
    self.research_deck = []
    self.load_researches(path)

    self.colony_data = []
    self.colony_deck = []
    self.upgraded_colonies = {}
    self.load_colonies(path)

  def load_species(self, path: str):
    for specie in self.species:
      self.load_specie_data(specie, path)

  def load_specie_data(self, specie: str, path: str):
    with open(f"{path}/species/{specie}.json", "r", encoding="utf-8") as f:
      specie_data = json.load(f)
      self.create_factories(specie, specie_data)
      self.create_init_players(specie, specie_data)
      self.species_data[specie] = specie_data

  def create_factories(self, specie: str, specie_data: dict):
    factories = {}
    for factory in specie_data["factories"]:
      factories[factory["name"]] = Factory(factory["name"], factory["input_items"], factory["output_items"], factory["donation_items"], specie)
    self.specie_factories[specie] = factories

  def create_init_players(self, specie: str, specie_data: dict):
    self.init_factories = {}
    for factory in specie_data["start_resource"]["factories"]:
      if factory in self.specie_factories[specie]:
        self.init_factories[factory] = self.specie_factories[specie][factory]
    self.specie_init_players[specie] = Player(specie, specie, specie_data["start_resource"]["items"], self.init_factories)

  def get_init_player(self, specie: str, user_id: str):
    player = self.specie_init_players[specie]
    player.user_id = user_id
    return player

  def get_factories(self, specie: str):
    return self.specie_factories[specie]

  def get_factory(self, specie: str, factory_name: str):
    return self.specie_factories[specie][factory_name]

  def get_zh_name(self, specie: str):
    return self.species_data[specie]["zh_name"]

  def get_factory_by_tech(self, specie: str, tech: str):
    factory_name = self.get_zh_name(specie) + "_" + tech
    return self.get_factory(specie, factory_name)

  def load_researches(self, path: str):
    with open(f"{path}/researches.json", "r", encoding="utf-8") as f:
      researches_data = json.load(f)
      self.researches_data = researches_data
      for research in researches_data:
        self.research_deck.append(self.load_research(research))
      random.shuffle(self.research_deck)
      self.research_deck.sort(key=lambda x: x.feature["properties"]["level"])

  def load_research(self, research_data: dict):
    factory = Factory(
      research_data["name"],
      research_data["input_items"],
      research_data["output_items"],
      {},
      "None",
      research_data["feature"],
      True
    )
    return factory

  def draw_research(self):
    return self.research_deck.pop()

  def load_colonies(self, path: str):
    with open(f"{path}/colonies.json", "r", encoding="utf-8") as f:
      colonies_data = json.load(f)
      self.colonies_data = colonies_data
      for colony in colonies_data:
        factory = self.load_colony(colony)
        if colony["name"].endswith('+'):
          self.upgraded_colonies[colony["name"][:-1]] = factory
        else:
          self.colony_deck.append(factory)
      random.shuffle(self.colony_deck)

  def load_colony(self, colony_data: dict):
    factory = Factory(
      colony_data["name"],
      colony_data["input_items"],
      colony_data["output_items"],
      colony_data["donation_items"],
      "None",
      colony_data["feature"],
      False
    )
    return factory

  def draw_colony(self):
    return self.colony_deck.pop()

class Factory:
  def __init__(self, name: str, input_items: Dict[str, int], output_items: Dict[str, int], donation_items: Dict[str, int], owner: str, feature = {"type": "Normal", "properties": {}}, run_in_trading = False):
    self.name = name
    self.input_items = input_items
    self.output_items = output_items
    self.donation_items = donation_items
    self.used = False
    self.owner = owner

    """
    Feature is a dictionary that contains the type of the factory and its properties.

    {
      "type": "Normal",
      "properties": {}
    }

    {
      "type": "Colony",
      "properties": {
        "climate": str, in ["Jungle", "Water", "Desert", "Ice"],
        "upgraded": bool,
        "upgrade_cost": Dict[str, int]
      }
    }

    {
      "type": "Research",
      "properties": {
        "tech": str,
        "level": int,
        "research_cost": List[Dict[str, int]]
      }
    }
    """
    self.feature = feature
    self.run_in_trading = run_in_trading

  def produce(self, game, player, extra_properties: Dict[str, Any] = {}) -> Tuple[bool, Dict[str, int]]:
    if self.used:
      return False, "工厂已使用"

    if self.feature["type"] == "Normal":
      res = {}
      for item, quantity in self.input_items.items():
        if player.storage.get(item, 0) < quantity:
          return False, "玩家库存不足"
    
      for item, quantity in self.input_items.items():
        player.storage[item] -= quantity

      for item, quantity in self.output_items.items():
        res[item] = quantity
      
      player.add_new_product_items(res)

    elif self.feature["type"] == "Research":
      assert "tech" in self.feature["properties"]
      assert "research_cost" in self.feature["properties"]
      assert "cost_type" in extra_properties
      cost_type = extra_properties["cost_type"]
      cost = self.feature["properties"]["research_cost"][cost_type]
      tech = self.feature["properties"]["tech"]

      for item, quantity in cost.items():
        if player.storage.get(item, 0) < quantity:
          return False, "玩家库存不足"

      for item, quantity in cost.items():
        player.storage[item] -= quantity

      res = {}
      for item, quantity in self.output_items.items():
        res[item] = quantity

      tech_spread_bonus = game.get_tech_spread_bonus(player.user_id)
      res["Score"] += tech_spread_bonus
      player.add_new_product_items(res)

      game.develop_tech(player.user_id, tech)
      print(f"{player.user_id} 研发了 {tech}")


    self.used = True
    return True, ""

  def reset(self):
    self.used = False

  def to_dict(self) -> Dict[str, Any]:
    return {
      "name": self.name,
      "input_items": self.input_items,
      "output_items": self.output_items,
      "used": self.used,
      "owner": self.owner,
      "feature": self.feature,
      "run_in_trading": self.run_in_trading
    }



class Player:
  def __init__(self, user_id: str, specie: str, start_storage: Dict[str, int], factories: List[Factory]):
    self.user_id = user_id
    self.specie = specie
    self.storage: Dict[str, int] = {}
    self.donation_items: Dict[str, int] = {}
    self.factories: Dict[str, Factory] = {}
    self.new_product_items: Dict[str, int] = {}
    self.agreed = False
    self.colony_bid = 0
    self.research_bid = 0
    self.tie_breaker = 0

    self.add_items_to_storage(start_storage)
    for factory_name, factory in factories.items():
      self.new_factory(factory)

  def new_factory(self, factory: Factory):
    self.factories[factory.name] = factory
    factory.owner = self.specie

  def add_factory(self, factory: Factory):
    if factory.name in self.factories:
      print(f"工厂 {factory.name} 已存在")
      return False
    self.factories[factory.name] = factory
    return True

  def remove_factory(self, factory_name: str) -> Factory:
    return self.factories.pop(factory_name)

  def add_to_storage(self, item: str, quantity: int):
    self.storage[item] = self.storage.get(item, 0) + quantity
  
  def add_items_to_storage(self, items: Dict[str, int]):
    for item, quantity in items.items():
      self.storage[item] = self.storage.get(item, 0) + quantity

  def remove_from_storage(self, item: str, quantity: int) -> bool:
    if self.storage.get(item, 0) < quantity:
      return False
    self.storage[item] -= quantity
    return True

  def remove_items_from_storage(self, items: Dict[str, int]) -> bool:
    for item, quantity in items.items():
      if self.storage.get(item, 0) < quantity:
        return False
      self.storage[item] -= quantity
    return True
  
  def add_new_product_items(self, items: Dict[str, int]):
    for item, quantity in items.items():
      self.new_product_items[item] = self.new_product_items.get(item, 0) + quantity 

  def agree(self):
    self.agreed = True

  def disagree(self):
    self.agreed = False

  def reset_factories(self):
    for factory in self.factories.values():
      factory.reset()

  def get_research_priority(self):
    research_count = 0
    for factory in self.factories.values():
      if factory.feature["type"] == "Research":
        research_count += 1
    return (-self.research_bid, research_count, -self.tie_breaker)
  
  def get_colony_priority(self):
    colony_count = 0
    for factory in self.factories.values():
      if factory.feature["type"] == "Colony":
        colony_count += 1
    return (-self.colony_bid, colony_count, -self.tie_breaker)

  def to_dict(self) -> Dict[str, Any]:
    return {
      "user_id": self.user_id,
      "specie": self.specie,
      "storage": self.storage,
      "donation_items": self.donation_items,
      "factories": {name: factory.to_dict() for name, factory in self.factories.items()},
      "agreed": self.agreed
    }

bid_price_list = [1, 1, 2, 3]

class Game:
  def __init__(self, room_name: str):
    self.players: List[Player] = []
    self.current_round = 0
    self.stage = "trading"
    self.room_name = room_name
    self.tech_spread_list = {}
    self.data_manager = DataManager("./server/data")

    self.research_bid_num = 4
    self.colony_bid_num = 4
    self.research_bid_cards = []
    self.colony_bid_cards = []
    self.init_bid_cards()
    self.supply_bid_items()
    self.research_bid_priority = []
    self.colony_bid_priority = []

  def init_bid_cards(self):
    for i in range(self.research_bid_num):
      self.research_bid_cards.append({"price": bid_price_list[i], "item": None})
    for i in range(self.colony_bid_num):
      self.colony_bid_cards.append({"price": bid_price_list[i], "item": None})

  def supply_bid_items(self):
    for i in range(self.research_bid_num):
      self.research_bid_cards[i]["item"] = self.draw_research()
    for i in range(self.colony_bid_num):
      self.colony_bid_cards[i]["item"] = self.draw_colony()

  def add_player(self, specie: str, user_id: str):
    self.players.append(self.data_manager.get_init_player(specie, user_id))

  def start_game(self):
    self.current_round = 1
    self.stage = "trading"

  def all_players_agreed(self) -> bool:
    return all(player.agreed for player in self.players)

  def move_to_next_stage(self):
    if self.stage == "trading":
      self.stage = "production"
      self.reset_player_agreements()
    elif self.stage == "production":
      self.stage = "bid"
      self.save_new_product_items()
      self.reset_player_factories()
      self.reset_player_agreements()
    elif self.stage == "bid":
      self.stage = "pick"
      self.calculate_bid_priority()
    elif self.stage == "pick":
      self.stage = "end"
      self.supply_bid_items()
      self.move_to_next_stage()
      self.reset_player_bids()
    elif self.stage == 'end':
      self.stage = "trading"
      self.spread_tech()
      self.return_factories_to_owners()
      self.current_round += 1

  def reset_player_agreements(self):
    for player in self.players:
      player.disagree()

  def reset_player_factories(self):
    for player in self.players:
      player.reset_factories()

  def reset_player_bids(self):
    for player in self.players:
      player.colony_bid = 0
      player.research_bid = 0

  def calculate_bid_priority(self):
    self.research_bid_priority = []
    self.colony_bid_priority = []
    for player in self.players:
      self.research_bid_priority.append(player)
      self.colony_bid_priority.append(player)
    self.research_bid_priority.sort(key=lambda x: x.get_research_priority())
    self.colony_bid_priority.sort(key=lambda x: x.get_colony_priority())

  def save_new_product_items(self):
    for player in self.players:
      player.add_items_to_storage(player.new_product_items)
      player.new_product_items = {}

  def return_factories_to_owners(self):
    all_factories = [factory for player in self.players for factory in player.factories.values()]
    for factory in all_factories:
      owner = next((p for p in self.players if p.specie == factory.owner), None)
      if owner:
        current_holder = next((p for p in self.players if factory.name in p.factories), None)
        if current_holder and current_holder != owner:
          factory = current_holder.remove_factory(factory.name)
          owner.add_factory(factory)

  def spread_tech(self):
    for tech in self.tech_spread_list[self.current_round]:
      for player in self.players:
        player.new_factory(self.data_manager.get_factory_by_tech(player.specie, tech))

  def get_tech_spread_bonus(self, player_name: str):
    return 7 - self.current_round

  def develop_tech(self, player_name: str, tech: str):
    player = next((p for p in self.players if p.user_id == player_name), None)
    if player:
      player.new_factory(self.data_manager.get_factory_by_tech(player.specie, tech))
    if self.current_round not in self.tech_spread_list:
      self.tech_spread_list[self.current_round] = []
    self.tech_spread_list[self.current_round].append(tech)

  def draw_research(self):
    return self.data_manager.draw_research()

  def debug_draw_research(self, player_name: str):
    player = next((p for p in self.players if p.user_id == player_name), None)
    if player:
      player.add_factory(self.draw_research())

  def draw_colony(self):
    return self.data_manager.draw_colony()
    
  def debug_draw_colony(self, player_name: str):
    player = next((p for p in self.players if p.user_id == player_name), None)
    if player:
      player.add_factory(self.draw_colony())

  def debug_add_item(self, player_name: str, item: str, quantity: int):
    player = next((p for p in self.players if p.user_id == player_name), None)
    if player:
      player.add_to_storage(item, quantity)
  
  ############################
  #                          #
  # Game Interface Functions #
  #                          #
  ############################

  def trade(self, from_player: str, to_player: str, items: Dict[str, int]) -> Tuple[bool, str]:
    if self.stage != "trading":
      return False, "当前阶段不是交易阶段"
    sender = next((p for p in self.players if p.user_id == from_player), None)
    receiver = next((p for p in self.players if p.user_id == to_player), None)

    if not sender or not receiver:
      return False, "未指定玩家"

    if sender.remove_items_from_storage(items):
      receiver.add_items_to_storage(items)
      return True, ""
    return False, "玩家库存不足"

  def lend_factory(self, from_player: str, to_player: str, factory_name: str) -> Tuple[bool, str]:
    if self.stage != "trading":
      return False, "当前阶段不是交易阶段"
    sender = next((p for p in self.players if p.user_id == from_player), None)
    receiver = next((p for p in self.players if p.user_id == to_player), None)

    if not sender or not receiver or factory_name not in sender.factories:
      return False, "未指定玩家或工厂"

    factory = sender.remove_factory(factory_name)
    receiver.add_factory(factory)
    return True, ""

  def produce(self, player_name: str, factory_name: str, extra_properties: Dict[str, Any] = {}) -> Tuple[bool, str]:
    player = next((p for p in self.players if p.user_id == player_name), None)

    if not player or factory_name not in player.factories:
      return False, "未指定玩家或工厂"

    if self.stage != "production" and not player.factories[factory_name].run_in_trading:
      return False, "当前阶段不是生产阶段"

    success, msg = player.factories[factory_name].produce(self, player, extra_properties)

    if success:
      return True, ""
    return False, msg

  def player_agree(self, player_name: str):
    player = next((p for p in self.players if p.user_id == player_name), None)
    if player:
      player.agree()
    if self.all_players_agreed():
      self.move_to_next_stage()
  
  def player_disagree(self, player_name: str):
    player = next((p for p in self.players if p.user_id == player_name), None)
    if player:
      player.disagree()

  ###########################
  #                         #
  #     Other Functions     #
  #                         #
  ###########################

  def to_dict(self) -> Dict[str, Any]:
    research_bid_cards_dict = []
    for card in self.research_bid_cards:
      if card["item"]:
        research_bid_cards_dict.append({"price": card["price"], "item": card["item"].to_dict()})
      else:
        research_bid_cards_dict.append({"price": card["price"], "item": None})
    colony_bid_cards_dict = []
    for card in self.colony_bid_cards:
      if card["item"]:
        colony_bid_cards_dict.append({"price": card["price"], "item": card["item"].to_dict()})
      else:
        colony_bid_cards_dict.append({"price": card["price"], "item": None})
    return {
      "players": [player.to_dict() for player in self.players],
      "current_round": self.current_round,
      "stage": self.stage,
      "room_name": self.room_name,
      "research_bid_cards": research_bid_cards_dict,
      "colony_bid_cards": colony_bid_cards_dict
    }

    """
    The game state dictionary has the following structure:
    {
        "players": [
            {
                "specie": str,
                "user_id": str,
                "storage": Dict[str, int],
                "donation_items": Dict[str, int],
                "factories": {
                    "factory_name": {
                        "name": str,
                        "input": Dict[str, int],
                        "output": Dict[str, int],
                        "owner": str,
                        "feature": {
                          "type": str,
                          "properties": Dict[str, Any]
                        },
                        "run_in_trading": bool
                    },
                    ...
                },
                "agreed": bool
            },
            ...
        ],
        "current_round": int,
        "stage": str,
        "room_name": str,
        "research_bid_cards": [
          {
            "price": int,
            "item": Factory | None
          },
          ...
        ],
        "colony_bid_cards": [
          {
            "price": int,
            "item": Factory | None
          },
          ...
        ]
    }
    """
    """
    Items:
      - Food / Small Green Cube
      - Culture / Small White Cube
      - Industry / Small Black Cube
      - Information / Big Black Cube
      - Biotech / Big Blue Cube
      - Energy / Big Yellow Cube
      - Hypertech / Brown Column

      - AnySmall / Gray Small Cube
      - AnyBig / Gray Big Cube

      - Ship / Red Triangle
      - Score
    """
