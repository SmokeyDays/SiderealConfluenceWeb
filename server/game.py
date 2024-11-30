from copy import deepcopy
import json
from typing import Any, Callable, Dict, List, Tuple
import random

from server.message import Message
from server.utils.achievement import unlock_achievement
from server.utils.pubsub import pubsub
from server.utils.trade_recorder import Trade, TradeRecorder

def get_bid_board(player_num):
  num_dict={
    3:[1,2,3],
    4:[1,1,2,3],
    5:[1,1,2,3,3],
    6:[1,1,1,2,3,3],
    7:[1,1,1,2,2,3,4],
    8:[1,1,1,1,2,2,3,4],
    9:[1,1,1,1,2,2,3,4,4],
    10:[1,1,1,1,1,2,2,3,4,4]
  }
  return num_dict[player_num]

def get_share_score(player_num,turn):
  yengii_table=[
    [3,2,2,1,1,0],
    [3,2,2,1,1,0],
    [3,2,1,1,1,0],
    [3,2,1,1,0,0],
    [2,2,1,1,0,0],
    [2,2,1,1,0,0],
    [2,2,1,1,0,0]
  ]
  normal_table=[
    [6,5,4,4,3,2],
    [6,5,4,4,3,2],
    [6,6,5,4,3,1],
    [6,6,5,4,2,1],
    [7,6,5,4,2,0],
    [7,6,5,4,2,0],
    [7,6,5,4,2,0]
  ]
  return normal_table[player_num-3][turn], yengii_table[player_num-3][turn]
    
def get_item_value(item: str):
  if item.endswith("Donation"):
    item = item.replace("Donation", "")
  item_values = {
    'Food': 1,
    'Culture': 1,
    'Industry': 1,
    'Energy': 1.5,
    'Information': 1.5,
    'Biotech': 1.5,
    'Hypertech': 3,
    'Ship': 1,
    'Score': 3,
    'WildBig': 1.5,
    'WildSmall': 1,
    'ArbitrarySmall': 1,
    'ArbitraryBig': 1.5,
  }
  return item_values.get(item, 0)

def get_items_value(items: Dict[str, Any]):
  return sum([get_item_value(item) * count for item, count in items.items()])

def get_gift_value(gift: Dict[str, Any]):
  if "items" not in gift:
    return 0
  return get_items_value(gift["items"])

def get_items_str(items: Dict[str, Any]):
  return ", ".join([f"{item}x{count}" for item, count in items.items()])

def get_gift_str(gift: Dict[str, Any]):
  factories_str = ""
  if "factories" in gift:
    factories_str = f" and Factories {', '.join(gift['factories'])}"
  tech_str = ""
  if "techs" in gift:
    tech_str = f" and Grant Techs {', '.join(gift['techs'])}"
  items_str = ""
  if "items" in gift:
    items_str = f" ({get_items_str(gift['items'])})"
  return f"{items_str}{factories_str}{tech_str}"

class TradeProposal:
  trade_proposal_id = 1
  def __init__(self, from_player: str, to_players: list[str], send_gift: Dict[str, Any], receive_gift: Dict[str, Any], message: str = ""):
    self.id = TradeProposal.trade_proposal_id
    TradeProposal.trade_proposal_id += 1
    self.from_player = from_player
    self.to_players = to_players
    self.send_gift = send_gift
    self.receive_gift = receive_gift
    self.message = message
  def to_dict(self):
    return {
      "id": self.id,
      "from_player": self.from_player,
      "to_players": self.to_players,
      "send_gift": self.send_gift,
      "receive_gift": self.receive_gift,
      "message": self.message
    }
  def get_value(self):
    return get_gift_value(self.receive_gift) - get_gift_value(self.send_gift)
  def __str__(self):
    msg_str = ""
    if self.message:
      msg_str = f" ({self.message})"
    return f"(id {self.id}) {self.from_player} -> {self.to_players}: {get_gift_str(self.send_gift)} -> {get_gift_str(self.receive_gift)}{msg_str}"

class DataManager:
  def __init__(self, path: str):
    self.specie_factories = {}
    self.specie_init_players: list[Player] = {}
    self.species_data = {}
    self.species = ["Caylion", "Yengii", "Eni", "Unity", "Im", "Kjasjavikalimm", "Kit"]
    self.load_species(path)

    self.researches_data = []
    self.research_deck = []
    self.researches = {}
    self.load_researches(path)

    self.colony_data = []
    self.colony_deck = []
    self.colonies = {}
    self.upgraded_colonies = {}
    self.load_colonies(path)
    self.generate_preview()

  def generate_preview(self):
    for specie in self.species:
      for factory in self.specie_factories[specie].values():
        if factory.feature["type"] == "Normal":
          if factory.feature["properties"].get("upgraded", False):
            continue
          upgraded_factory = self.get_factory(specie, factory.feature["properties"]["upgrades"][0]["factory"])
          if upgraded_factory:
            factory.preview = upgraded_factory.converters
        elif factory.feature["type"] == "Meta":
          unlock_factory = self.get_factory(specie, factory.feature["properties"]["unlock_factory"])
          if unlock_factory:
            factory.preview = unlock_factory.converters
    for colony in self.colony_deck:
      if colony.feature["properties"].get("upgraded", False):
        continue
      upgraded_colony = self.get_upgraded_colony(colony.name)
      if upgraded_colony:
        colony.preview = upgraded_colony.converters
        colony.feature["properties"]["upgrade_climate"] = upgraded_colony.feature["properties"]["climate"]
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
      feature = factory["feature"]
      if "upgrades" in factory["feature"]["properties"]:
        upgrades = []
        for upgrade in factory["feature"]["properties"]["upgrades"]:
          cost = upgrade["cost"]
          upgrade_factory = upgrade["factory"]
          if isinstance(cost, str):
            upgrades.append({
              "cost": cost,
              "factory": upgrade_factory
            })
          else:
            upgrades.append({
              "cost": Converter(**cost).to_dict(),
              "factory": upgrade_factory
            })
        upgrades.sort(key=lambda x: 1 if isinstance(x["cost"], str) else 0)
        feature["properties"]["upgrades"] = upgrades
      factories[factory["name"]] = Factory(
        factory["name"], 
        [Converter(**converter) for converter in factory["converters"]],
        "None" if "noOwner" in factory['feature']['properties'] else specie,
        feature
      )
    self.specie_factories[specie] = factories

  def create_init_players(self, specie: str, specie_data: dict):
    init_factories = {}
    for factory in specie_data["start_resource"]["factories"]:
      if factory in self.specie_factories[specie]:
        init_factories[factory] = self.specie_factories[specie][factory]
    specie_zh_name = specie_data["zh_name"]
    max_colony = specie_data["max_colony"]
    tie_breaker = specie_data["tie_breaker"]
    init_colony = specie_data["init_colony"]
    init_research = specie_data["init_research"]
    player = Player(
      specie, 
      specie, 
      specie_zh_name, 
      specie_data["start_resource"]["items"], 
      init_factories,
      max_colony=max_colony,
      tie_breaker=tie_breaker,
      init_colony=init_colony,
      init_research=init_research
    )
    self.specie_init_players[specie] = player
  
  def load_init_colony_and_research(self, player: "Player"):
    for i in range(player.init_colony):
      player.add_colony(self.draw_colony())
    for i in range(player.init_research):
      player.add_research(self, self.draw_research())
    return player

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
        self.researches[research["name"]] = self.load_research(research)
      random.shuffle(self.research_deck)
      self.research_deck.sort(key=lambda x: x.feature["properties"]["level"])

  def load_research(self, research_data: dict):
    factory = Factory(
      research_data["name"],
      [Converter(**converter) for converter in research_data["converters"]],
      "None",
      research_data["feature"],
    )
    return factory

  def draw_research(self):
    if len(self.research_deck) == 0:
      return None
    return self.research_deck.pop(0)

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
        self.colonies[colony["name"]] = factory
      random.shuffle(self.colony_deck)

  def load_colony(self, colony_data: dict):
    factory = Factory(
      colony_data["name"],
      [Converter(**converter) for converter in colony_data["converters"]],
      "None",
      colony_data["feature"],
    )
    return factory

  def draw_colony(self):
    if len(self.colony_deck) == 0:
      return None
    return self.colony_deck.pop(0)

  def get_upgraded_colony(self, colony_name: str):
    if colony_name in self.upgraded_colonies:
      return self.upgraded_colonies[colony_name]
    print(f"{colony_name} 的升级殖民地不存在")
    return None
  
  def add_research_preview(self, specie: str, research):
    preview = self.get_factory_by_tech(specie, research.feature["properties"]["tech"]).converters
    research.preview = preview
    return research

  def get_factory_by_name(self, specie: str, factory_name: str):
    if factory_name in self.specie_factories[specie]:
      return self.specie_factories[specie][factory_name]
    if factory_name in self.colonies:
      return self.colonies[factory_name]
    if factory_name in self.researches:
      factory = self.researches[factory_name]
      factory = self.add_research_preview(specie, factory)
      return factory
    return None

class Converter:
  def __init__(self, input_items: Dict[str, int] or List[Dict[str, int]], output_items: Dict[str, int], running_stage: str):
    self.input_items = input_items
    self.output_items = output_items
    self.running_stage = running_stage
    self.used = False

  def to_dict(self) -> Dict[str, Any]:
    return {
      "input_items": self.input_items,
      "output_items": self.output_items,
      "running_stage": self.running_stage,
      "used": self.used
    }


class Factory:
  def __init__(self, name: str,
    converters: List[Converter],
    owner: str, 
    feature = {"type": "Normal", "properties": {}},
  ):
    self.name = name
    self.converters = converters
    self.preview = None
    self.owner = owner
    self.run_count = 0

    """
    Feature is a dictionary that contains the type of the factory and its properties.

    {
      "type": "Normal",
      "properties": {
        "upgraded": bool,
        "upgrades":[
          {
            "cost": str | Converter,
            "factory": str
          }
        ]
      }
    }

    {
      "type": "Colony",
      "properties": {
        "climate": str, in ["Jungle", "Water", "Desert", "Ice"],
        "upgrade_climate": str, in ["Jungle", "Water", "Desert", "Ice"],
        "upgraded": bool,
        "upgrade_cost": Converter
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

  def on_enter_game(self, game, player):
    for index, converter in enumerate(self.converters):
      if converter.running_stage == "constant":
        game.produce_factory(player, self, index, {})
        
  def eniet_interest(self, converter, game, player, extra_properties):
    """
    extra_properties: {
      "output_type": str,
      "input_combination": Dict[str, int]
      }
    """
    output_type = extra_properties["output_type"]
    input_combination = extra_properties["input_combination"]
    small_item = ["Food", "Culture", "Industry"]
    big_item = ["Energy", "Information", "Biotech"]
    res = {}
    if converter.input_items.get("ArbitrarySmall", 0) > 0 or converter.input_items.get("ArbitraryBig", 0) > 0:
      isSmall = converter.input_items.get("ArbitrarySmall", 0) > 0
      item_list = small_item if isSmall else big_item
      if output_type not in item_list:  
        return False, "类型不正确"
      wildInput = input_combination.get("Wild" + ("Small" if isSmall else "Big"), 0)
      normalInput = input_combination.get(output_type, 0)
      if wildInput + normalInput != converter.input_items["Arbitrary" + ("Small" if isSmall else "Big")]:
        return False, "输入数量不足"
      for item in input_combination:
        if item not in ["Wild" + ("Small" if isSmall else "Big"), output_type]:
          return False, "输入多余"
      output_count = converter.output_items.get("Arbitrary" + ("Small" if isSmall else "Big"), 0)
      if not player.remove_items_from_storage(input_combination):
        return False, "玩家库存不足"
      for item, quantity in converter.output_items.items():
        if item == "Arbitrary" + ("Small" if isSmall else "Big"):
          res[output_type] = quantity - converter.input_items.get("Arbitrary" + ("Small" if isSmall else "Big"), 0)
          continue
        res[item] = quantity
      for item, quantity in input_combination.items():
        res[item] = res.get(item, 0) + quantity
    else:
      return False, "类型不正确"
    player.add_new_product_items(res)
    return True, ""

  def produce(self, game, player, converter_index: int, extra_properties: Dict[str, Any] = {}) -> Tuple[bool, Dict[str, int]]:
    converter = self.converters[converter_index]
    if converter.used:
      return False, "工厂已使用"
    if converter.running_stage != game.stage:
      return False, "当前阶段不正确"
    
    if 'MustLend' in self.feature['properties']:
      if self.owner == player.specie:
        return False, "这个转换器必须借出"
    res = {}

    special_factory = False
    for tag in ["EnietInterest"]:
      if tag in self.feature["properties"]:
        special_factory = True
        break

    if self.feature["type"] == "Research":
      assert "tech" in self.feature["properties"]
      assert "cost_type" in extra_properties
      cost_type = extra_properties["cost_type"]
      cost = converter.input_items[cost_type]
      tech = self.feature["properties"]["tech"]

      if not player.remove_items_from_storage(cost):
        return False, "玩家库存不足"

      for item, quantity in converter.output_items.items():
        res[item] = quantity

      tech_spread_bonus = game.get_tech_spread_bonus(player.user_id)
      res["Score"] += tech_spread_bonus
      game.develop_tech(player.user_id, tech)
      print(f"{player.user_id} 研发了 {tech}")
    else:
      input_items = converter.input_items.copy()
      if 'fleetCost' in self.feature['properties'] and self.run_count == 0:
        fleet_cost = self.feature['properties']['fleetCost']
        if player.storage.get('Fleet', 0) < fleet_cost:
          return False, "舰队支持不足"
        input_items['Fleet'] = fleet_cost
      if not special_factory:
        if not player.remove_items_from_storage(input_items):
          return False, "玩家库存不足"

        for item, quantity in converter.output_items.items():
          res[item] = quantity

    if self.feature["type"] == "Meta":
      unlock_factory = game.data_manager.get_factory(player.specie, self.feature["properties"]["unlock_factory"])
      player.add_factory(unlock_factory)
      unlock_factory.on_enter_game(game, player)
      player.remove_factory(self.name)

    if not special_factory:
      if converter.running_stage == 'production':
        player.add_new_product_items(res)
      else:
        player.add_items_to_storage(res)

    success = True
    if "EnietInterest" in self.feature["properties"]:
      success, msg = self.eniet_interest(converter, game, player, extra_properties)
    if not success:
      return False, msg
    self.run_count += 1
    if self.feature["type"] == "Colony" and "caylion_colony" in self.feature["properties"] and self.feature["properties"]["caylion_colony"]:
      if self.run_count >= 2:
        converter.used = True
    else:
      converter.used = True
    return True, ""

  def reset(self):
    for converter in self.converters:
      converter.used = False
    self.run_count = 0

  def to_dict(self) -> Dict[str, Any]:
    return {
      "name": self.name,
      "converters": [converter.to_dict() for converter in self.converters],
      "owner": self.owner,
      "feature": self.feature,
      "preview": [converter.to_dict() for converter in self.preview] if self.preview else None,
      "run_count": self.run_count
    }



class Player:
  def __init__(
      self, 
      user_id: str, 
      specie: str, 
      specie_zh_name: str, 
      start_storage: Dict[str, int], 
      factories: List[Factory], 
      tie_breaker: int, 
      max_colony: int,
      init_colony: int,
      init_research: int
    ):
    self.user_id = user_id
    self.specie = specie
    self.specie_zh_name = specie_zh_name
    self.storage: Dict[str, int] = {}
    self.factories: Dict[str, Factory] = {}
    self.new_product_items: Dict[str, int] = {}
    self.tie_breaker = tie_breaker
    self.max_colony = max_colony
    self.init_colony = init_colony
    self.init_research = init_research
    self.agreed = False
    self.colony_bid = 0
    self.research_bid = 0
    self.tech = []
    self.invented_tech = []
    self.score = 0
    self.item_value = 0
    
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
  
  def add_colony(self, colony: Factory):
    if self.specie == "Caylion":
      colony.feature["properties"]["caylion_colony"] = True
    self.add_factory(colony)

  def add_research(self, data_manager: DataManager, research: Factory):
    research = data_manager.add_research_preview(self.specie, research)
    self.add_factory(research)
  
  def add_tech(self, factory: Factory, tech: str):
    if tech not in self.tech:
      self.add_factory(factory)
      self.tech.append(tech)

  def remove_factory(self, factory_name: str) -> Factory:
    return self.factories.pop(factory_name)
  
  def calculate_score(self):
    self.score = self.storage.get("Score", 0) + self.storage.get("ScoreDonation", 0)
    self.item_value = 0
    for item, quantity in self.storage.items():
      if item != "Score" and item != "ScoreDonation":
        self.item_value += quantity * get_item_value(item)


  def modify_storage(self, item: str, quantity: int):
    self.storage[item] = self.storage.get(item, 0) + quantity
    self.calculate_score()
    
  def add_to_storage(self, item: str, quantity: int):
    self.modify_storage(item, quantity)
  
  def add_items_to_storage(self, items: Dict[str, int]):
    for item, quantity in items.items():
      self.modify_storage(item, quantity)

  def receive_items(self, items: Dict[str, int]):
    new_items = deepcopy(items)
    for item, quantity in items.items():
      if item.endswith('Donation'):
        new_items.pop(item)
        item = item.replace('Donation', '')
        new_items[item] = new_items.get(item, 0) + quantity
    self.add_items_to_storage(new_items)

  def check_storage(self, items: Dict[str, int]) -> bool:
    for item, quantity in items.items():
      if self.storage.get(item, 0) < quantity:
        return False
    return True

  def remove_from_storage(self, item: str, quantity: int) -> bool:
    if self.storage.get(item, 0) < quantity:
      return False
    self.modify_storage(item, -quantity)
    return True

  def remove_items_from_storage(self, items: Dict[str, int]) -> bool:
    if not self.check_storage(items):
      return False
    for item, quantity in items.items():
      if quantity == 0:
        continue
      self.modify_storage(item, -quantity)
    return True

  def add_new_product_items(self, items: Dict[str, int]):
    for item, quantity in items.items():
      self.new_product_items[item] = self.new_product_items.get(item, 0) + quantity 

  def agree(self):
    self.agreed = True

  def disagree(self):
    self.agreed = False

  def on_new_round(self):
    for factory in self.factories.values():
      for converter in factory.converters:
        if converter.running_stage == "constant":
          self.add_items_to_storage(converter.output_items)
  
  def on_end_round(self):
    expire_item_type = ['Fleet']
    for item in expire_item_type:
      self.remove_from_storage(item, self.storage.get(item, 0))

  def reset_factories(self):
    factories_to_remove = []
    for factory in self.factories.values():
      if factory.feature["type"] == "Research" or factory.feature["type"] == "Meta":
        if factory.converters[0].used:
          factories_to_remove.append(factory.name)
      else:
        factory.reset()
    for factory_name in factories_to_remove:
      self.remove_factory(factory_name)

  def has_tech(self, tech: str):
    return tech in self.tech
  
  def invent_tech(self, tech: str):
    pubsub.publish("add_statistics", {"key": "tech_invented", "value": 1}, self.user_id)
    if self.specie == "Yengii":
      pubsub.publish("add_statistics", {"key": "yengii_tech_invented", "value": 1}, self.user_id)
    self.invented_tech.append(tech)
  
  def has_invented_tech(self, tech: str):
    return tech in self.invented_tech

  def get_factory_num_by_type(self, query_type: str):
    res = 0
    for factory in self.factories.values():
      if factory.feature["type"] == query_type:
        res += 1
    return res

  def get_research_priority(self):
    return (-self.research_bid, self.get_factory_num_by_type("Research"), -self.tie_breaker)
  
  def get_colony_bid(self, split_id = None):
    if self.specie == "Caylion":
      return self.colony_bid / 2.0
    if self.specie == "Kjasjavikalimm" and split_id is not None:
      if self.colony_bid % 2 == 0:
        return self.colony_bid / 2
      else:
        return (self.colony_bid + 1) / 2 - split_id
    return self.colony_bid

  def get_colony_priority(self, split_id = None):
    return (-self.get_colony_bid(split_id), self.get_factory_num_by_type("Colony"), -self.tie_breaker)

  def to_dict(self) -> Dict[str, Any]:
    return {
      "user_id": self.user_id,
      "specie": self.specie,
      "specie_zh_name": self.specie_zh_name,
      "storage": self.storage,
      "factories": {name: factory.to_dict() for name, factory in self.factories.items()},
      "max_colony": self.max_colony,
      "tie_breaker": self.tie_breaker,
      "init_colony": self.init_colony,
      "init_research": self.init_research,
      "agreed": self.agreed,
      "colony_bid": self.colony_bid,
      "research_bid": self.research_bid,
      "tech": self.tech,
      "invented_tech": self.invented_tech,
      "score": self.score,
      "item_value": self.item_value
    }


class Game:
  def __init__(self, room_name: str, end_round: int):
    self.players: List[Player] = []
    self.current_round = 0
    self.end_round = end_round
    self.stage = ""
    self.room_name = room_name
    self.tech_spread_list = {}
    self.data_manager = DataManager("./server/data")
    self.proposals = {}

    self.research_bid_num = 0
    self.colony_bid_num = 0
    self.research_bid_cards = []
    self.colony_bid_cards = []
    self.research_bid_priority = []
    self.colony_bid_priority = []
    self.discard_colony = []
    self.endgame_score = {}
    self.trade_recorder = TradeRecorder()

    self.Kajsjavikalimm_choose_split = None
  def get_player_num(self):
    return max(len(self.players), 3)

  @property
  def current_pick_player(self):
    if self.stage == "pick":
      if self.Kajsjavikalimm_choose_split is None:
        return {
          "type": "colony",
          "player": "",
          "bid": 0
        }
      if len(self.colony_bid_priority) > 0:
        return {
          "type": "colony",
          "player": self.colony_bid_priority[0][0].user_id,
          "bid": self.colony_bid_priority[0][0].get_colony_bid(self.colony_bid_priority[0][1] if len(self.colony_bid_priority[0]) > 1 else None)
        }
      elif len(self.research_bid_priority) > 0:
        return {
          "type": "research",
          "player": self.research_bid_priority[0][0].user_id,
          "bid": self.colony_bid_priority[0][0].get_research_bid()
        }
    return {
      "type": "",
      "player": "",
      "bid": 0
    }

  @property
  def current_discard_colony_player(self):
    if self.stage == 'discard_colony':
      if len(self.discard_colony) > 0:
        return self.discard_colony[0]
    return ""

  def init_bid_cards(self):
    for i in range(self.research_bid_num):
      self.research_bid_cards.append({"price": get_bid_board(self.research_bid_num)[i], "item": None})
    for i in range(self.colony_bid_num):
      self.colony_bid_cards.append({"price": get_bid_board(self.colony_bid_num)[i], "item": None})

  def supply_bid_items(self):
    research_cards = []
    research_supply_count = 0
    for i in range(self.research_bid_num):
      if self.research_bid_cards[i]["item"] and self.research_bid_cards[i]["price"] > 1:
        research_cards.append(self.research_bid_cards[i]["item"])
      else:
        research_supply_count += 1
    for i in range(research_supply_count):
      research_cards.append(self.draw_research())
    for i in range(self.research_bid_num):
      self.research_bid_cards[i]["item"] = research_cards[i]
    colony_cards = []
    colony_supply_count = 0
    for i in range(self.colony_bid_num):
      if self.colony_bid_cards[i]["item"]:
        colony_cards.append(self.colony_bid_cards[i]["item"])
      else:
        colony_supply_count += 1
    for i in range(colony_supply_count):
      colony_cards.append(self.draw_colony())
    for i in range(self.colony_bid_num):
      self.colony_bid_cards[i]["item"] = colony_cards[i]

  def add_player(self, specie: str, user_id: str):
    player = self.data_manager.get_init_player(specie, user_id)
    player = self.data_manager.load_init_colony_and_research(player)
    self.players.append(player)

  def start_game(self):
    isKjaskavikalimmInGame = any(player.specie == "Kjasjavikalimm" for player in self.players)
    self.research_bid_num = self.get_player_num()
    self.colony_bid_num = self.get_player_num() + (1 if isKjaskavikalimmInGame else 0)
    self.init_bid_cards()

    self.current_round = 1
    self.on_new_round()
    self.stage = "trading"

  def all_players_agreed(self) -> bool:
    return all(player.agreed for player in self.players)
  
  def on_new_round(self):
    for player in self.players:
      player.on_new_round()
    self.supply_bid_items()
  
  def on_end_round(self):
    for player in self.players:
      player.on_end_round()
    self.spread_tech()
    self.return_factories_to_owners()

  def get_winner(self):
    return max(self.players, key=lambda x: x.score + 0.5 * x.item_value)

  def end_game(self):
    # check achievements
    winner = self.get_winner()
    if winner:
      pubsub.publish("add_statistics", {"key": "wins", "value": 1}, winner.user_id)
      max_trade_gap = 0
      slave_player = None
      for player in self.players:
        pubsub.publish("add_statistics", {"key": "games_completed", "value": 1}, player.user_id)
        if player.user_id != winner.user_id:
          trade_gap = self.trade_recorder.get_pair_trade_gap(winner.user_id, player.user_id)
          if trade_gap > max_trade_gap:
            max_trade_gap = trade_gap
            slave_player = player
      if slave_player:
        pubsub.publish("add_statistics", {"key": "slave", "value": 1}, slave_player.user_id)
  def production_end(self):
    self.save_new_product_items()
    #check achievements
    for player in self.players:
      if player.specie == "Im":
        if player.storage["Fleet"] == 0:
          unlock_achievement(player.user_id, "im_no_fleet")
  def move_to_next_stage(self):
    if self.stage == "trading":
      self.stage = "discard_colony"
      self.reset_player_agreements()
      self.calculate_discard_colony()
      self.proposals = {}
      if len(self.discard_colony) == 0:
        self.move_to_next_stage()
    elif self.stage == 'discard_colony':
      self.stage = 'production'
    elif self.stage == "production":
      self.production_end()
      if self.current_round == self.end_round:
        self.stage = "gameend"
        self.end_game()
      else:
        self.stage = "bid"
        self.reset_player_factories()
        self.reset_player_agreements()
    elif self.stage == "bid":
      self.stage = "pick"
      if any(player.specie == "Kjasjavikalimm" for player in self.players):
        self.Kajsjavikalimm_choose_split = None
      self.init_bid_priority()
      self.reset_player_agreements()
    elif self.stage == "pick":
      self.stage = "end"
      self.reset_player_bids()
      self.move_to_next_stage()
    elif self.stage == 'end':
      self.stage = "trading"
      self.on_end_round()
      self.current_round += 1
      self.on_new_round()

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

  def init_bid_priority(self):
    self.research_bid_priority = []
    self.colony_bid_priority = []
    for player in self.players:
      self.research_bid_priority.append([player])
      if player.specie == "Kjasjavikalimm" and self.Kajsjavikalimm_choose_split is not None and self.Kajsjavikalimm_choose_split:
        self.colony_bid_priority.append([player, 0])
        self.colony_bid_priority.append([player, 1])
      else:
        self.colony_bid_priority.append([player])
    self.calculate_bid_priority()

  def calculate_bid_priority(self):
    self.research_bid_priority.sort(key=lambda x: x[0].get_research_priority())
    self.colony_bid_priority.sort(key=lambda x: x[0].get_colony_priority(x[1] if len(x) > 1 else None))

  def calculate_discard_colony(self):
    self.discard_colony = []
    for player in self.players:
      if (player.get_factory_num_by_type("Colony") > player.max_colony):
        self.discard_colony.append(player.user_id)

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

  def get_tech(self, player: Player, tech: str):
    player.add_tech(self.data_manager.get_factory_by_tech(player.specie, tech), tech)

  def spread_tech(self):
    if self.current_round not in self.tech_spread_list:
      return
    for tech in self.tech_spread_list[self.current_round]:
      for player in self.players:
        self.get_tech(player, tech)

  def get_tech_spread_bonus(self, player_name: str):
    player = next((p for p in self.players if p.user_id == player_name), None)
    share_score, yengii_score = get_share_score(self.get_player_num(), self.current_round)
    if player and player.specie == "Yengii":
      return yengii_score
    return share_score

  def develop_tech(self, player_name: str, tech: str):
    player = next((p for p in self.players if p.user_id == player_name), None)
    if player:
      self.get_tech(player, tech)
      player.invent_tech(tech)

    if player.specie != "Yengii":
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
      player.add_colony(self.draw_colony())

  def debug_add_item(self, player_name: str, item: str, quantity: int):
    player = next((p for p in self.players if p.user_id == player_name), None)
    if player:
      player.add_to_storage(item, quantity)

  def give_items(self, sender: Player, receiver: Player, items: Dict[str, int]) -> Tuple[bool, str, Callable]:
    if sender.check_storage(items):
      def callback():
        sender.remove_items_from_storage(items)
        receiver.receive_items(items)
      return True, "", callback
    return False, "玩家库存不足", lambda: None
  
  def lend_factory(self, sender: Player, receiver: Player, factory_name: str) -> Tuple[bool, str, Callable]:
    if factory_name not in sender.factories:
      return False, "工厂不存在于发送者库存", lambda: None

    def callback():
      factory = sender.remove_factory(factory_name)
      receiver.add_factory(factory)
      #check achievements
      if sender.specie == "Eni":
        if "MustLend" in factory.feature["properties"] and factory.feature["properties"]["MustLend"]:
          unlock_achievement(sender.user_id, "eni_winwin")
    return True, "", callback
  
  def grant_tech(self, sender: Player, receiver: Player, tech: str) -> Tuple[bool, str, Callable]:
    if not sender.has_invented_tech(tech) or receiver.has_tech(tech):
      return False, "玩家没有该科技或对方已有该科技", lambda: None
    def callback():
      self.get_tech(receiver, tech)
    return True, "", callback
  ############################
  #                          #
  # Game Interface Functions #
  #                          #
  ############################
  def produce(self, player_name: str, factory_name: str, converter_index: int, extra_properties: Dict[str, Any] = {}) -> Tuple[bool, str]:
    player = next((p for p in self.players if p.user_id == player_name), None)

    if not player or factory_name not in player.factories:
      return False, "未指定玩家或工厂"

    success, msg = player.factories[factory_name].produce(self, player, converter_index, extra_properties)

    if success:
      return True, ""
    return False, msg

  def upgrade_colony(self, player_name: str, factory_name: str) -> Tuple[bool, str]:
    if self.stage != "trading":
      return False, "当前阶段不是交易阶段"
    player = next((p for p in self.players if p.user_id == player_name), None)
    if not player or factory_name not in player.factories:
      return False, "未指定玩家或工厂"
    if player.factories[factory_name].feature["type"] != "Colony":
      return False, "工厂不是殖民地"
    if player.factories[factory_name].feature["properties"]["upgraded"]:
      return False, "殖民地已经升级"
    new_factory = self.data_manager.get_upgraded_colony(factory_name)
    if not new_factory:
      return False, "升级的殖民地不存在"
    if not player.remove_items_from_storage(player.factories[factory_name].feature["properties"]["upgrade_cost"]):
      return False, "玩家库存不足"
    if "caylion_colony" in player.factories[factory_name].feature["properties"]:
      new_factory.feature["properties"]["caylion_colony"] = True
    player.remove_factory(factory_name)
    player.add_factory(new_factory)
    return True, ""

  def upgrade_normal(self, player_name: str, factory_name: str, cost_type: int) -> Tuple[bool, str]:
    if self.stage != "trading":
      return False, "当前阶段不是交易阶段"
    player = next((p for p in self.players if p.user_id == player_name), None)
    if not player or factory_name not in player.factories:
      return False, "未指定玩家或工厂"
    factory = player.factories[factory_name]
    if factory.feature["type"] != "Normal":
      return False, "工厂不是普通工厂"
    if factory.feature["properties"]["upgraded"]:
      return False, "工厂已经升级"
    if cost_type < 0 or cost_type >= len(factory.feature["properties"]["upgrades"]):
      return False, "升级费用类型不存在"
    new_factory = self.data_manager.get_factory(player.specie, factory.feature["properties"]["upgrades"][cost_type]["factory"])
    if isinstance(factory.feature["properties"]["upgrades"][cost_type]["cost"], str):
      cost_factory_name = factory.feature["properties"]["upgrades"][cost_type]["cost"]
      cost_factory = next((f for f in player.factories.values() if f.name == cost_factory_name), None)
      if not cost_factory:
        return False, "升级所需工厂不存在"
      player.remove_factory(cost_factory_name)
    else:
      # cost is to run converter
      converter = factory.feature["properties"]["upgrades"][cost_type]["cost"]
      if not player.remove_items_from_storage(converter["input_items"]):
        return False, "玩家库存不足"

      res = {}
      for item, quantity in converter["output_items"].items():
        res[item] = quantity
      player.add_items_to_storage(res)

    player.remove_factory(factory_name)
    player.add_factory(new_factory)
    #check achievements
    if player.specie == "Kit":
      if new_factory.name in ["凯特_多恒星系恒星能量利用", "凯特_心理史学目的论再设计", "凯特_微型制造的自适应架构"]:
        unlock_achievement(player.user_id, "kit_upgrade")
    return True, ""

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

  def submit_bid(self, player_name: str, colony_bid: int, research_bid: int):
    if self.stage != "bid":
      return False, "当前阶段不是拍卖阶段"
    player = next((p for p in self.players if p.user_id == player_name), None)
    if player:
      player.colony_bid = colony_bid
      player.research_bid = research_bid
      self.player_agree(player_name)
      #check achievements
      if player.specie == "Kjasjavikalimm":
        if player.research_bid >= 7:
          unlock_achievement(player.user_id, "kjas_army_on_border")
      return True, ""
    return False, "未指定玩家"

  def submit_pick(self, player_name: str, type: str, pick_id: int):
    if self.stage != "pick":
      return False, "当前阶段不是选择阶段"
    if self.current_pick_player["type"] != type:
      return False, "拍卖物品种类非法"
    if self.current_pick_player["player"] != player_name:
      return False, "当前选择阶段不是你"
    player = next((p for p in self.players if p.user_id == player_name), None)
    if not player:
      return False, "未指定玩家"
    if type == "colony":
      if pick_id != -1:
        if pick_id < 0 or pick_id >= len(self.colony_bid_cards):
          return False, "拍卖物品不存在"
        if not self.colony_bid_cards[pick_id]["item"]:
          return False, "拍卖物品不存在"
        if player.colony_bid < self.colony_bid_cards[pick_id]["price"] or player.storage.get("Ship", 0) < player.get_colony_bid():
          return False, "出价不足"
        colony = self.colony_bid_cards[pick_id]["item"]
        player.add_colony(colony)
        self.colony_bid_cards[pick_id]["item"] = None
        # 注意这里要用 player.colony_bid 因为 get_colony_bid 计算的是经过 Caylion 修正后的出价
        player.remove_from_storage("Ship", player.colony_bid)
        if player.specie == "Caylion":
          pubsub.publish("add_statistics", {"key": "caylion_colonies", "value": 1}, player.user_id)
      self.colony_bid_priority.pop(0)
    elif type == "research":
      if pick_id != -1:
        if pick_id < 0 or pick_id >= len(self.research_bid_cards):
          return False, "拍卖物品不存在"
        if not self.research_bid_cards[pick_id]["item"]:
          return False, "拍卖物品不存在"
        if player.research_bid < self.research_bid_cards[pick_id]["price"] or player.storage.get("Ship", 0) < player.research_bid:
          return False, "出价不足"
        research = self.research_bid_cards[pick_id]["item"]
        player.add_research(self.data_manager, research)
        self.research_bid_cards[pick_id]["item"] = None
        player.remove_from_storage("Ship", player.research_bid)
      self.research_bid_priority.pop(0)
    if self.colony_bid_priority == [] and self.research_bid_priority == []:
      print("拍卖结束")
      self.move_to_next_stage()
    return True, ""

  def Kajsjavikalimm_split(self, player_name: str, split: bool):
    player = next((p for p in self.players if p.user_id == player_name), None)
    if not player:
      return False, "未指定玩家"
    if player.specie != "Kjasjavikalimm":
      return False, "玩家不是贾斯"
    if self.stage != "pick":
      return False, "当前阶段不是选择阶段"
    if self.Kajsjavikalimm_choose_split is not None:
      return False, "贾斯已经做出选择"
    self.Kajsjavikalimm_choose_split = split
    self.init_bid_priority()
    return True, ""

  def exchange_colony(self, player_name: str, colony_name: str):
    player = next((p for p in self.players if p.user_id == player_name), None)
    if not player:
      return False, "未指定玩家"
    colony = player.remove_factory(colony_name)
    player.add_to_storage(colony.feature["properties"]["climate"], 1)
    return True, ""
  
  def exchange_arbitrary(self, player_name: str, items: Dict[str, int]):
    player = next((p for p in self.players if p.user_id == player_name), None)
    if not player:
      return False, "未指定玩家"
    new_items = {}
    small_item = ["Food", "Culture", "Industry", "WildSmall"]
    big_item = ["Energy", "Information", "Biotech", "WildBig"]
    world_item = ["Jungle", "Ice", "Desert", "Water"]
    for item, quantity in items.items():
      if item in small_item:
        new_items["ArbitrarySmall"] = new_items.get("ArbitrarySmall", 0) + quantity
      elif item in big_item:
        new_items["ArbitraryBig"] = new_items.get("ArbitraryBig", 0) + quantity
      elif item in world_item:
        new_items["ArbitraryWorld"] = new_items.get("ArbitraryWorld", 0) + quantity
      else:
        return False, "非法物品"
    if player.remove_items_from_storage(items):
      player.add_items_to_storage(new_items)
      return True, ""
    return False, "玩家库存不足"
  
  def exchange_wild(self, player_name: str, items: Dict[str, int]):
    player = next((p for p in self.players if p.user_id == player_name), None)
    if not player:
      return False, "未指定玩家"
    new_items = {}
    small_item = ["Food", "Culture", "Industry", "ArbitrarySmall"]
    big_item = ["Energy", "Information", "Biotech", "ArbitraryBig"]
    for item, quantity in items.items():
      if item in small_item:
        new_items["WildSmall"] = new_items.get("WildSmall", 0) + quantity
      elif item in big_item:
        new_items["WildBig"] = new_items.get("WildBig", 0) + quantity
      else:
        return False, "非法物品"
    if player.remove_items_from_storage(new_items):
      player.add_items_to_storage(items)
      #check achievements
      if player.specie == "Unity":
        unlock_achievement(player.user_id, "unity_exchange")
      return True, ""
    return False, "玩家库存不足"
  
  def discard_colonies(self, player_name: str, colonies: list[str]):
    if self.stage != "discard_colony": 
      return False, "当前阶段不是弃置殖民地阶段"
    if self.discard_colony[0] != player_name:
      return False, "当前弃置殖民地的不是你"
    player = next((p for p in self.players if p.user_id == player_name), None)
    if not player:
      return False, "未指定玩家"
    discard_num = player.get_factory_num_by_type("Colony") - player.max_colony
    if len(colonies) != discard_num:
      return False, "需要弃置的殖民地数量不符"
    for colony in colonies:
      player.remove_factory(colony)
    self.discard_colony.pop(0)
    if len(self.discard_colony) == 0:
      self.move_to_next_stage()
    return True, ""
  
  def give_many_things(self, from_player: str, to_player: str, gift: Dict[str, Any]):
    items = gift.get("items", {})
    factories = gift.get("factories", [])
    techs = gift.get("techs", [])
    if self.stage != "trading":
      return False, "当前阶段不是交易阶段", []
    sender = next((p for p in self.players if p.user_id == from_player), None)
    receiver = next((p for p in self.players if p.user_id == to_player), None)
    if not sender or not receiver:
      return False, "未指定玩家", []
    
    msg, callbacks = "", []
    give_items_res = self.give_items(sender, receiver, items)
    if not give_items_res[0]:
      return give_items_res
    msg += give_items_res[1]
    callbacks.append(give_items_res[2])

    for factory in factories:
      lend_factory_res = self.lend_factory(sender, receiver, factory)
      if not lend_factory_res[0]:
        return lend_factory_res
      msg += lend_factory_res[1]
      callbacks.append(lend_factory_res[2])
    
    for tech in techs:
      grant_tech_res = self.grant_tech(sender, receiver, tech)
      if not grant_tech_res[0]:
        return grant_tech_res
      msg += grant_tech_res[1]
      callbacks.append(grant_tech_res[2])

    return True, msg, callbacks
  
  def gift(self, from_player: str, to_player: str, gift: Dict[str, Any]):
    success, msg, callbacks = self.give_many_things(from_player, to_player, gift)
    if not success:
      return success, msg
    for callback in callbacks:
      callback()
    self.trade_recorder.record_trade(Trade(from_player, to_player, self.current_round, "Gift" + get_gift_str(gift), -get_gift_value(gift)))
    return True, ""
  
  def trade_proposal(self, from_player: str, to_players: list[str], send_gift: Dict[str, Any], receive_gift: Dict[str, Any], message: str = ""):
    proposal = TradeProposal(from_player, to_players, send_gift, receive_gift, message)
    self.proposals[from_player] = self.proposals.get(from_player, []) + [proposal]
    return True, "", proposal.id

  def decline_trade_proposal(self, from_player: str, id: int):
    if from_player in self.proposals:
      for proposal in self.proposals[from_player]:
        if proposal.id == id:
          self.proposals[from_player].remove(proposal)
          return True, ""
    return False, "交易提案不存在"
  
  def accept_trade_proposal(self, accept_player: str, id: int):
    for sender, proposals in self.proposals.items():
      for proposal in proposals:
        if proposal.id == id:
          success, msg = self.trade(sender, accept_player, proposal.send_gift, proposal.receive_gift)
          if success:
            self.proposals[sender].remove(proposal)
            self.trade_recorder.record_trade(Trade(sender, accept_player, self.current_round, "Trade " + str(proposal), proposal.get_value()))
            pubsub.publish("new-message", Message("OP", "交易达成：" + str(proposal), None, self.room_name, None))
            return True, msg
          return success, msg
    return False, "交易提案不存在"

  def trade(self, from_player: str, to_player: str, send_gift: Dict[str, Any], receive_gift: Dict[str, Any]):
    success, msg, send_callbacks = self.give_many_things(from_player, to_player, send_gift)
    if not success:
      return success, msg
    success, msg, receive_callbacks = self.give_many_things(to_player, from_player, receive_gift)
    if not success:
      return success, msg
    for callback in send_callbacks:
      callback()
    for callback in receive_callbacks:
      callback()
    return True, ""
  
  
  ###########################
  #                         #
  #     Query Functions     #
  #                         #
  ###########################

  def get_factory(self, username: str, factory_name: str) -> Factory:
    specie = next((p for p in self.players if p.user_id == username), None).specie
    return self.data_manager.get_factory_by_name(specie, factory_name)
  
  def get_trade_log(self):
    return self.trade_recorder.get_trades_str()

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
    research_bid_priority = []
    for x in self.research_bid_priority:
      research_bid_priority.append({"player": x[0].user_id, "bid": x[0].get_research_priority()})
    colony_bid_priority = []
    for x in self.colony_bid_priority:
      colony_bid_priority.append({"player": x[0].user_id, "bid": x[0].get_colony_priority(x[1] if len(x) > 1 else None)})
    return {
      "players": [player.to_dict() for player in self.players],
      "current_round": self.current_round,
      "end_round": self.end_round,
      "stage": self.stage,
      "room_name": self.room_name,
      "research_bid_cards": research_bid_cards_dict,
      "colony_bid_cards": colony_bid_cards_dict,
      "research_bid_priority": research_bid_priority,
      "colony_bid_priority": colony_bid_priority,
      "current_pick": self.current_pick_player,
      "current_discard_colony_player": self.current_discard_colony_player,
      "proposals": {sender: [proposal.to_dict() for proposal in proposals] for sender, proposals in self.proposals.items()},
      "Kajsjavikalimm_choose_split": self.Kajsjavikalimm_choose_split
    }

    """
    The game state dictionary has the following structure:
    {
        "players": [
            {
                "specie": str,
                "specie_zh_name": str,
                "user_id": str,
                "storage": Dict[str, int],
                "factories": {
                    "factory_name": {
                        "name": str,
                        "converter": [
                          {
                            "input_items": Dict[str, int] | List[Dict[str, int]],
                            "output_items": Dict[str, int],
                            "running_stage": str,
                            "used": bool
                          },
                        ...],
                        "owner": str,
                        "feature": {
                          "type": str,
                          "properties": Dict[str, Any]
                        },
                        "preview": Converter[] | None,
                        "run_count": int
                    },
                    ...
                },
                "max_colony": number,
                "tie_breaker": number,
                "agreed": bool,
                "tech": [str, ...],
                "invented_tech": [str, ...],
                "score": number
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
        ],
        "research_bid_priority": [
          {
            "player": str,
            "bid": [number, number, number]
          },
          ...
        ],
        "colony_bid_priority": [
          {
            "player": str,
            "bid": [number, number, number]
          },
          ...
        ],
        "current_pick": {
          "type": str,
          "player": str,
          "bid": number
        },
        "current_discard_colony_player": str,
        "proposals": {
          "sender": [
            {
              "id": int,
              "from_player": str,
              "to_players": [str, ...],
              "send_gift": Dict[str, Any],
              "receive_gift": Dict[str, Any]
            },
            ...
          ],
        },
        "Kajsjavikalimm_choose_split": bool | None  
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

      - WildSmall / Gray Small Cube
      - WildBig / Gray Big Cube

      - Ship / Red Triangle
      - Score
    """
