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

###
# Should add the player's promises into the obs later
###
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


###
# Maybe add the promise thing, like borrow bulabula?
###

# def game_plan():
#   return """
# Now is the beginning stage of this turn.
# Reviewing the instructions below, please make a plan for this turn.
# Your plan may containing following parts:
# 1. What factories (and its converters) to run.
# 2. What resources are needed to run the factories or to upgrade the factories.
# 3. What resources are not needed in this turn and can be used to trade with other players.
# 4. What resources you want to buy from other players.
# Your response must be a json object with the following format:
# {
#   "reasoning": <reasoning>,
#   "factories": [{"factory_name": <factory_name>, "converters": [<converter_id>, ...]}, ...],
#   "resources": {"<resource_name>": <resource_quantity>, ...},
#   "sell": {"<resource_name>": <resource_quantity>, ...},
#   "buy": {"<resource_name>": <resource_quantity>, ...}
# }
# """

### borrow may need complicated logic, need to think more carefully
def turn_plan_prompt():
    return """
Now is the planning stage of this turn.
Reviewing the game state and your history, please update your current plan.
Your task involves planning resource management, factory operations, and formulating proposals for other players.

Please follow these instructions:
1. **Check Promises**: Review previous agreements. You must behave faithfully according to promises made in earlier turns.
2. **Factory Planning**: Decide which factories to run and which to upgrade based on efficiency and needs.
3. **Resource Calculation**: Calculate the net resources needed. Determine what should be bought, sold, or borrowed.
4. **Proposals**: Based on your plan, formulate specific proposals (trades/deals) you intend to offer to other players.

Your response must be a json object with the following format:
{
  "reasoning": "Detailed analysis of promises, strategy, and resource gaps...",
  "faithful_check": "Confirmation that this plan adheres to previous promises",
  "factories_run": [{"factory_name": <string>, "converters": [<converter_id>, ...]}, ...],
  "factories_upgrade": [{"factory_name": <string>, "converter_id": [<converter_id>, ...]}, ...],
  "resources_needed": {"<resource_name>": <quantity>, ...},
  "trade_strategy": {
      "buy": {"<resource_name>": <quantity>, ...},
      "sell": {"<resource_name>": <quantity>, ...},
      "borrow": {"<resource_name>": <quantity>, ...}
  },
  "proposals": [
      {"target_player_id": <id>, "offer": {...}, "request": {...}, "note": "..."},
      ...
  ]
}
"""


### It maybe easier to implement if the upgrade action can be shifted here for AI, 
### or we may should add some upgrade actions to turn_plan_prompt or make a new call for upgrade?
def economy_move_prompt():
    return """
Now is the economic action stage.
Based on your established plan and current resource holdings, you need to execute specific economic moves.

Please follow these instructions:
1. **Review Plan**: Look at your current plan for factories_run.
2. **Execute Actions**: Generate specific operational commands.
   - Run factories to convert resources if resources allowed, try to maximize your utility.
   - Upgrade factories if resources allow.


Your response must be a json object with the following format:
{
  "reasoning": "Explanation of why these specific moves are being taken now...",
  "factory_actions": [
      {"action": "run", "factory_name": <string>, "converter_id": <id>, "times": <int>},
      {"action": "upgrade", "factory_name": <string>, "converter_id": <id>}
  ]
}
"""

def bid_move_prompt():
    return """
Now is the bidding/auction stage.
You need to make a decision on the current item up for bid, **Ships** are used as currency. There are two separate auction tracks: **Colony** and **Technology**.

**Bidding Rules:**
1. **Allocation**: You must decide how to distribute your available ships between the 'Colony' bid and the 'Technology' bid. You can bid 0 on a track.
2. **Priority**: In each track, players with higher bids select items first.
3. **Capacity Limit**: Your bid amount acts as a budget cap. **You cannot select an item with a value higher than the number of ships you bid for that track**, even if it is your turn to pick.
4. **Payment & Refund**: 
   - If you pick an item: You pay your **FULL BID AMOUNT**. Any excess ships (Bid - Item Value) are **NOT** returned.
   - If you pick nothing: Your full bid is returned to you.

Please follow these instructions:
1. **Analyze Items**: Review available Colonies and Technologies. Note the value of items you want.
2. **Competitor Analysis**: Observe other players' resources(ships) and likely needs. Anticipate their bids.
3. **Strategic Allocation**: 
   - Trade-off: Bidding high guarantees priority, but you will lose the difference if the item's value is lower than your bid.
   - You must calculate: Is the priority worth the extra cost?
   - If you bid exactly the item's value, you save ships but risk being picked after opponents.
4. **Feasibility**: Ensure (Colony Bid + Technology Bid) <= Total Available Ships.

Your response must be a json object with the following format:
{
  "reasoning": "Strategy explanation: Balancing priority vs. overpaying. Why is this specific bid amount chosen?",
  "current_total_ships": <int>,
  "intended_targets": {
      "colony": "Name/ID of the colony you plan to pick",
      "technology": "Name/ID of the tech you plan to pick"
  },
  "bid_allocation": {
      "colony_bid": <int amount of ships>,
      "technology_bid": <int amount of ships>
  }
}
"""

def evaluate_transaction_prompt(transactions_list):
    return f"""
You are now viewing the list of currently available transactions.
You need to evaluate all pending proposals and decide which ones to accept.

Current Transactions:
{transactions_list}

**Crucial Context:**
1. **Competition (Urgency)**: Some transactions are public offers visible to multiple players. These are **first-come, first-served**. If you see a highly beneficial public deal, you must accept it quickly before other players snatch it.
2. **Resource Locking**: Accepting a transaction triggers a pre-confirm request to the server, which will try to **lock/freeze** your resources. You cannot accept multiple trades that require the same resources if you don't have enough (no double-spending).
3. **Plan Alignment**: Only trade if it advances your current turn plan or provides profit without jeopardizing critical operations.

Please follow these instructions:
1. **Screening**: Filter out transactions you cannot afford or do not need.
2. **Prioritization**: 
   - If a deal is **Public and High Value**, prioritize it to beat competitors.
   - If a deal is Private, check if it aligns with your diplomatic promises.
3. **Conflict Check**: Ensure that the total resources required for *all* accepted transactions do not exceed your current holdings.
4. **Decision**: Return the IDs of the transactions you wish to accept.

Your response must be a json object with the following format:
{{
  "reasoning": "Analysis of the market. Which deals are urgent? How do you resolve resource conflicts between multiple good deals?",
  "accepted_transaction_ids": ["<transaction_id_1>", "<transaction_id_2>", ...],
  "rejected_analysis": "Brief explanation of why others were rejected (e.g., 'insufficient funds', 'bad price', 'saving resources')"
}}
"""


###
# Should add description of species into the prompt later, 
# such as allowed max colonies number, special abilities ... 
###
def get_prompt(game: Game, player_id: str):
  return game_desc() + game_obs(game, player_id) + game_plan()

