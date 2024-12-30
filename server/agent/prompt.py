from server.game import Converter, Factory, Game, Player, get_items_str, get_items_value

# First stage: provide game obs and factories, and ask llms to provide a plan
# Second stage: provide the plan and chat history, llms must react players' trade request

items_abbr = {
  "Food": "f",
  "Industry": "i",
  "Culture": "c",
  "Biotech": "B",
  "Energy": "E",
  "Information": "I",
  "Ship": "*",
  "Hypertech": "H",
  "Score": "$",
  "WildSmall": "w",
  "WildBig": "W",
  "ArbitrarySmall": "a",
  "ArbitraryBig": "A",
}
def factory_abbr(factory: Factory):
  converters_desc = ""
  for i, converter in enumerate(factory.converters):
    converters_desc += f"  - {i}: {converter}\n"
  
  upgrade_desc = ""
  if "upgrades" in factory.feature["properties"]:
    upgrade_desc = "Upgrades:\n"
    upgrade_targets = {}
    for i, upgrade in enumerate(factory.feature["properties"]["upgrades"]):
      cost = upgrade["cost"]
      target = upgrade["factory"]
      if isinstance(cost, str):
        upgrade_desc += f"  - {i}: By removing {cost}, you can upgrade {factory.name} to {target}\n"
      else:
        if isinstance(cost, dict):
          cost = Converter(**cost)
        upgrade_desc += f"  - {i}: By running the specific converter {cost}, you can upgrade {factory.name} to {target}\n"
  res = f"""{factory.name}
Converters:
{converters_desc}{upgrade_desc}"""
  return res

def game_desc():
  # resource_list = "\n".join([f"{item}({item_abbr})" for item, item_abbr in items_abbr.items()])
  desc = f"""
You are playing a game named "Sidereal Confluence".
This is a game of production and trade. You own some factories, each factory contains some converters, each converter receives some resources and produces some resources.
The game is turn-based, and each turn contains following stages:
Beginning stage:
  - You must plan for this turn.
Trade stage:
  - You can trade resources with other players to prepare for production.
  - You can upgrade factories to get more efficient converters.
Production stage:
  - You can run factories to produce resources.
  - You can only run a converter once in a turn.
  - You must run factories simultaneously. That means you must prepare all needed resources for all factories you want to run in advance.
Your final goal is to be the richest player.
Here are introduction of resources:
And as suggesting, each item has a estimated value, you can use it to estimate the value of the item to help you make trade decision.
Note that the value is only a rough estimation, and you should not rely on it too much:
Food, Industry and Culture, sometimes called "small block", each has a estimated value of 1
Biotech, Energy, Information, sometimes called "big block", each has a estimated value of 1.5
Ship has a estimated value of 1, and its value is very changeable.
Hypertech, Score, each has a estimated value of 3
WildSmall may replace any small block as input item, and WildBig may replace any big block as input item.
w and W each has a value of 1, but sometimes they may become more valuable.
ArbitrarySmall and ArbitraryBig are only used to describe the converter's input. It means you can use any small block or big block as input item.
"""
  return desc

def game_obs(game: Game, player_id: str):
  player = game.get_player_by_id(player_id)
  if not player:
    return "Player not found."
  factory_desc = ""
  for factory in player.factories.values():
    factory_desc += f"{factory_abbr(factory)}"
  obs = f"""
You are {player.user_id} playing a specie named {player.specie} in the game.
You are owning those items:
{get_items_str(player.storage)}
You are owning those factories:
{factory_desc}
"""
  return obs

def game_plan():
  return """
Now is the beginning stage of this turn.
Reviewing the instructions below, please make a plan for this turn.
Your plan may containing following parts:
1. What factories (and its converters) to run.
2. What resources are needed to run the factories or to upgrade the factories.
3. What resources are not needed in this turn and can be used to trade with other players.
4. What resources you want to buy from other players.
Your response must be a json object with the following format:
{
  "reasoning": <reasoning>,
  "factories": [{"factory_name": <factory_name>, "converters": [<converter_id>, ...]}, ...],
  "resources": {"<resource_name>": <resource_quantity>, ...},
  "sell": {"<resource_name>": <resource_quantity>, ...},
  "buy": {"<resource_name>": <resource_quantity>, ...}
}
"""

def get_prompt(game: Game, player_id: str):
  return game_desc() + game_obs(game, player_id) + game_plan()


