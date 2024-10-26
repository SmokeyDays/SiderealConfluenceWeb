import json
from typing import Any, Dict, List, Tuple

class SpecieManager:
  def __init__(self, path: str):
    self.specie_factories = {}
    self.specie_init_players = {}
    self.load_species(path)

  def load_species(self, path: str):
    species = ["Caylion", "Yengii"]
    for specie in species:
      self.load_specie_data(specie, path)

  def load_specie_data(self, specie: str, path: str):
    with open(f"{path}/{specie}.json", "r", encoding="utf-8") as f:
      specie_data = json.load(f)
      self.create_factories(specie, specie_data)
      self.create_init_players(specie, specie_data)

  def create_factories(self, specie: str, specie_data: dict):
    factories = {}
    for factory in specie_data["factories"]:
      factories[factory["name"]] = Factory(factory["name"], factory["input_items"], factory["output_items"], specie)
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

class Factory:
  def __init__(self, name: str, input_items: Dict[str, int], output_items: Dict[str, int], owner: str):
    self.name = name
    self.input_items = input_items
    self.output_items = output_items
    self.used = False
    self.owner = owner

  def produce(self, input_items: Dict[str, int]) -> Tuple[bool, Dict[str, int]]:
    if self.used:
      return False, {}

    res = {}
    
    for item, quantity in self.input_items.items():
      if input_items.get(item, 0) < quantity:
        return False, {}
    
    for item, quantity in self.input_items.items():
      input_items[item] -= quantity

    for item, quantity in self.output_items.items():
      res[item] = quantity
    
    self.used = True
    return True, res

  def reset(self):
    self.used = False

  def to_dict(self) -> Dict[str, Any]:
    return {
      "name": self.name,
      "input_items": self.input_items,
      "output_items": self.output_items,
      "used": self.used,
      "owner": self.owner,
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

    self.add_items_to_storage(start_storage)
    for factory_name, factory in factories.items():
      self.factories[factory_name] = factory

  def add_factory(self, factory: Factory):
    self.factories[factory.name] = factory
    factory.owner = self.specie

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

  def to_dict(self) -> Dict[str, Any]:
    return {
      "user_id": self.user_id,
      "specie": self.specie,
      "storage": self.storage,
      "donation_items": self.donation_items,
      "factories": {name: factory.to_dict() for name, factory in self.factories.items()},
      "agreed": self.agreed
    } 


class Game:
  def __init__(self, room_name: str):
    self.players: List[Player] = []
    self.current_round = 0
    self.stage = "trading"
    self.room_name = room_name
    self.specie_manager = SpecieManager("./server/data/species")

  def add_player(self, specie: str, user_id: str):
    self.players.append(self.specie_manager.get_init_player(specie, user_id))

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
      self.stage = "trading"
      self.current_round += 1
      self.reset_player_agreements()
      self.reset_player_factories()
      self.save_new_product_items()
      self.return_factories_to_owners()

  def reset_player_agreements(self):
    for player in self.players:
      player.disagree()

  def reset_player_factories(self):
    for player in self.players:
      player.reset_factories()

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

  def produce(self, player_name: str, factory_name: str) -> Tuple[bool, str]:
    if self.stage != "production":
      return False, "当前阶段不是生产阶段"
    player = next((p for p in self.players if p.user_id == player_name), None)

    if not player or factory_name not in player.factories:
      return False, "未指定玩家或工厂"
    success, new_storage = player.factories[factory_name].produce(player.storage)

    if success:
      player.add_new_product_items(new_storage)
      return True, ""
    return False, "工厂无法生产"

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
    return {
      "players": [player.to_dict() for player in self.players],
      "current_round": self.current_round,
      "stage": self.stage,
      "room_name": self.room_name
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
                        "owner": str
                    },
                    ...
                },
                "agreed": bool
            },
            ...
        ],
        "current_round": int,
        "stage": str,
        "room_name": str
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
