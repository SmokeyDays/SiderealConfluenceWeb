from server.game import Converter, Factory, Game, Player, get_items_str, get_items_value
from server.utils.log import logger

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

def add_tab(str_to_process, tab_num = 1):
  tab = "  "
  tab_str = tab * tab_num
  lend_n = False
  if str_to_process.endswith("\n"):
    str_to_process = str_to_process[:-1]
    lend_n = True
  str_to_process = tab_str + str_to_process.replace("\n", f"\n{tab_str}")
  if lend_n:
    str_to_process += "\n"
  return str_to_process

def get_factory_desc(factory: Factory):
  converters_desc = ""
  for i, converter in enumerate(factory.converters):
    converters_desc += f"  - {i}: {converter}\n"
  
  upgrade_desc = ""
  if "upgrades" in factory.feature["properties"]:
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
    if upgrade_desc != "":
      upgrade_desc = f"Upgrades:\n{upgrade_desc}"
  feature_desc = ""
  if factory.description != f"":
    feature_desc = f"""Other features:
{factory.description}
"""
  res = f"""{factory.name}
Converters:
{converters_desc}{upgrade_desc}{feature_desc}"""
  return res

def get_bulletin_board_desc(player: Player):
  bb = player.bulletin_board
  message = bb.get("message", "")
  seeking = get_items_str(bb.get("seeking", {}))
  offering = get_items_str(bb.get("offering", {}))

  if not message and not seeking and not offering:
    return "  - Bulletin Board: (Empty)\n"
    
  return f"""  - Bulletin Board:
    - Message: {message}
    - Seeking: {seeking}
    - Offering: {offering}"""

def get_another_player_desc(game: Game, player: Player):
  if not player:
    logger.warning("Player not found in another_player function.")
    return "Player not found."
  player_desc = f"""
Player {player.user_id} ({player.specie}):
  - Resources: {get_items_str(player.storage)}
{get_bulletin_board_desc(player)}"""
  return player_desc
###
# Should add the player's promises into the obs later
###
def get_bid_desc(game: Game):
  colony_bid = game.colony_bid_cards
  technology_bid = game.research_bid_cards
  colony_desc = ""
  for bid_id in range(len(colony_bid)):
    bid_item = colony_bid[bid_id]
    price = bid_item["price"]
    item = bid_item["item"]
    colony_desc += f"  Number {bid_id} item, at least {price} ships are needed:\n"
    colony_desc += add_tab(get_factory_desc(item))
  technology_desc = ""
  for bid_id in range(len(technology_bid)):
    bid_item = technology_bid[bid_id]
    price = bid_item["price"]
    item = bid_item["item"]
    technology_desc += f"  Number {bid_id} item, at least {price} ships are needed for bid:\n"
    technology_desc += add_tab(get_factory_desc(item))
  return f"""Auction tracks:
There're colonies up for bid:
{colony_desc}There're technology research teams up for bid:
{technology_desc}"""

def get_pick_desc(game: Game, player: Player):
  if not game.waiting_player(player.user_id):
    logger.warning(f"Player {player.user_id} tried to get pick desc when it's not their turn.")
    return "It's not your turn to pick."
  bid_type = game.current_pick_player['type']
  cards_to_pick = game.colony_bid_cards if game.current_pick_player['type'] == 'colony' else game.research_bid_cards
  bid_bound = player.colony_bid if game.current_pick_player['type'] == 'colony' else player.research_bid

  cards = ""
  for pick_id in range(len(cards_to_pick)):
    price = cards_to_pick[pick_id]["price"]
    if price > bid_bound:
      continue
    item = cards_to_pick[pick_id]["item"]
    cards += f"  Number {pick_id} item:\n"
    if item != None:
      cards += add_tab(get_factory_desc(item))
    else:
      cards += "  - This card is picked.\n"
  return f"""Now you may pick up to one {bid_type} card from the auction track.
Auction track for {bid_type} cards:
{cards}"""
def game_obs(game: Game, player_id: str):
  player = game.get_player_by_id(player_id)
  if not player:
    return "Player not found."
  if game.stage == "discard_colony":
    factory_desc = "You are owning those colonies:\n"+"".join(
      get_factory_desc(factory) 
      for factory in player.factories.values() if factory.feature["type"] == "Colony"
    )
  else:
    factory_desc = "You are owning those factories:\n"+"".join(
      get_factory_desc(factory) 
      for factory in player.factories.values()
    )
  other_player_desc = "".join(
    get_another_player_desc(game, other_player)
    for other_player in game.players
    if other_player.user_id != player_id
  )
  bid_board_desc = ""
  if game.stage == "bid":
    bid_board_desc = get_bid_desc(game)
  pick_desc = ""
  if game.stage == "pick":
    pick_desc = get_pick_desc(game, player)
  obs = f"""You are {player.user_id} playing a specie named {player.specie} in the game.
You own those items:
{get_items_str(player.storage)}
You current Bulletin Board status:
{get_bulletin_board_desc(player)}
{factory_desc}
Other players, their species and their items are listed below. Note that anywhere you need to mention other players should use their user_id instead of specie name:
{other_player_desc}
{bid_board_desc}{pick_desc}
"""
  return obs

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
  return game_obs(game, player_id)

# def get_bulletin_board_prompt(game: Game):
#   bulletin_board_message = ""
#   for player in game.players:
#       bulletin_board_message += f"Player {player.user_id} Bulletin Board:[\n"
#       bulletin_board_message += f"Message: {player.bulletin_board['message']}\n"
#       bulletin_board_message += f"Seeking: {player.bulletin_board['seeking']}\n"
#       bulletin_board_message += f"Offering: {player.bulletin_board['offering']}\n"
#       bulletin_board_message += "]\n"
#   message = f"""
# Current bulletin board messages from all players:
# {bulletin_board_message}
# """
#   return message
