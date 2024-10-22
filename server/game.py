from typing import Any, Dict, List, Tuple

class Factory:
  def __init__(self, name: str, input_items: Dict[str, int], output_items: Dict[str, int], owner: str):
    self.name = name
    self.input_items = input_items
    self.output_items = output_items
    self.used = False
    self.owner = owner

  def produce(self, storage: Dict[str, int]) -> Tuple[bool, Dict[str, int]]:
    if self.used:
      return False, {}
    
    for item, quantity in self.input_items.items():
      if storage.get(item, 0) < quantity:
        return False, {}
    
    for item, quantity in self.input_items.items():
      storage[item] -= quantity
    
    for item, quantity in self.output_items.items():
      storage[item] = storage.get(item, 0) + quantity
    
    self.used = True
    return True, storage

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
  def __init__(self, name: str):
    self.name = name
    self.storage: Dict[str, int] = {}
    self.factories: Dict[str, Factory] = {}
    self.new_product_items: Dict[str, int] = {}
    self.agreed = False

  def add_factory(self, factory: Factory):
    self.factories[factory.name] = factory
    factory.owner = self.name

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
      "name": self.name,
      "storage": self.storage,
      "factories": {name: factory.to_dict() for name, factory in self.factories.items()},
    } 


class Game:
  def __init__(self):
    self.players: List[Player] = []
    self.current_round = 0
    self.stage = "trading"

  def add_player(self, player: Player):
    self.players.append(player)

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
      owner = next((p for p in self.players if p.name == factory.owner), None)
      if owner:
        current_holder = next((p for p in self.players if factory.name in p.factories), None)
        if current_holder and current_holder != owner:
          factory = current_holder.factories.pop(factory.name)
          owner.add_factory(factory)
  
  ############################
  #                          #
  # Game Interface Functions #
  #                          #
  ############################

  def trade(self, from_player: str, to_player: str, items: Dict[str, int]) -> bool:
    sender = next((p for p in self.players if p.name == from_player), None)
    receiver = next((p for p in self.players if p.name == to_player), None)

    if not sender or not receiver:
      return False

    if sender.remove_items_from_storage(items):
      receiver.add_items_to_storage(items)
      return True
    return False

  def lend_factory(self, from_player: str, to_player: str, factory_name: str) -> bool:
    sender = next((p for p in self.players if p.name == from_player), None)
    receiver = next((p for p in self.players if p.name == to_player), None)

    if not sender or not receiver or factory_name not in sender.factories:
      return False

    factory = sender.factories.pop(factory_name)
    receiver.add_factory(factory)
    return True

  def produce(self, player_name: str, factory_name: str) -> bool:
    player = next((p for p in self.players if p.name == player_name), None)

    if not player or factory_name not in player.factories:
      return False
    success, new_storage = player.factories[factory_name].produce(player.storage)

    if success:
      player.add_new_product_items(new_storage)
      return True
    return False

  def player_agree(self, player_name: str):
    player = next((p for p in self.players if p.name == player_name), None)
    if player:
      player.agree()
    if self.all_players_agreed():
      self.move_to_next_stage()
    
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
    }

    """
    The game state dictionary has the following structure:
    {
        "players": [
            {
                "name": str,
                "storage": Dict[str, int],
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
        "stage": str
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
