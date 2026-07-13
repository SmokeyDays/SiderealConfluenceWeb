from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from server.game import Converter, Game, Player, TradeProposal, get_gift_value, get_item_value, get_items_value
from server.utils.config import get_config
from server.utils.log import logger


@dataclass
class ConverterCandidate:
  factory_name: str
  converter_index: int
  gain: float
  input_items: Dict[str, int]
  output_items: Dict[str, int]
  extra_properties: Dict[str, Any]


class FairTradeRuleAgent:
  """A deterministic baseline agent using simple fair-trade and greedy production rules."""

  MODEL_NAMES = {"rule-fair"}

  def __init__(self, game: Game, player_id: str, model_name: str = "rule-fair"):
    self.game = game
    self.player_id = player_id
    self.model_name = model_name
    self.recent_responses = []
    self.proposed_rounds = set()
    self.stage_key = None
    self.stage_started_at = time.monotonic()
    self.stage_step_count = 0
    self.stage_start_trade_count = 0

  @classmethod
  def supports_model(cls, model_name: str) -> bool:
    return model_name in cls.MODEL_NAMES

  async def step(self, handlers_prompt, handlers_map):
    stage = self.game.stage
    try:
      self._update_stage_counters(stage)
      player = self._player()
      if self._should_pass(stage) or self._already_passed(player, stage):
        self._pass_step(handlers_map, stage)
        return

      if stage == "trading":
        self._trading_step(handlers_map)
      elif stage == "discard_colony":
        self._discard_colony_step(handlers_map)
      elif stage == "production":
        self._production_step(handlers_map)
      elif stage == "bid":
        self._bid_step(handlers_map)
      elif stage == "pick":
        self._pick_step(handlers_map)
    except Exception as exc:
      logger.error(f"Rule agent {self.player_id} failed in stage {stage}: {exc}")

  def _call(self, handlers_map, func_name: str, data: Optional[Dict[str, Any]] = None):
    if func_name not in handlers_map:
      logger.warning(f"Rule agent {self.player_id}: handler {func_name} is not available.")
      return
    payload = dict(data or {})
    payload["room_name"] = self.game.room_name
    payload["username"] = self.player_id
    handlers_map[func_name](payload)

  def _get_config(self, key: str, default):
    try:
      return get_config(key)
    except KeyError:
      return default

  def _trade_count(self) -> int:
    return len(self.game.trade_recorder.get_trades())

  def _update_stage_counters(self, stage: str):
    current_key = (self.game.current_round, stage)
    if current_key != self.stage_key:
      self.stage_key = current_key
      self.stage_started_at = time.monotonic()
      self.stage_step_count = 0
      self.stage_start_trade_count = self._trade_count()
    self.stage_step_count += 1

  def _should_pass(self, stage: str) -> bool:
    max_steps = int(self._get_config("rule_agent_stage_max_steps", 200))
    timeout_minutes = float(self._get_config("rule_agent_stage_timeout_minutes", 5.0))
    elapsed_minutes = (time.monotonic() - self.stage_started_at) / 60.0

    if max_steps > 0 and self.stage_step_count > max_steps:
      logger.info(
        f"Rule agent {self.player_id} auto-passing {stage}: "
        f"stage steps {self.stage_step_count} > {max_steps}."
      )
      return True

    if timeout_minutes > 0 and elapsed_minutes > timeout_minutes:
      logger.info(
        f"Rule agent {self.player_id} auto-passing {stage}: "
        f"elapsed minutes {elapsed_minutes:.2f} > {timeout_minutes:.2f}."
      )
      return True

    if stage == "trading":
      max_trades = int(self._get_config("rule_agent_trading_max_trades", 5))
      stage_trades = self._trade_count() - self.stage_start_trade_count
      if max_trades > 0 and stage_trades >= max_trades:
        logger.info(
          f"Rule agent {self.player_id} auto-passing trading: "
          f"stage trades {stage_trades} >= {max_trades}."
        )
        return True

    return False

  def _already_passed(self, player: Optional[Player], stage: str) -> bool:
    return bool(player and player.agreed and stage in ("trading", "production", "bid"))

  def _pass_step(self, handlers_map, stage: str):
    if stage in ("trading", "production"):
      self._call(handlers_map, "confirm_ready")
    elif stage == "bid":
      self._call(handlers_map, "submit_bid", {
        "colony_bid": 0,
        "research_bid": 0,
      })
    elif stage == "pick":
      current_pick = self.game.current_pick_player
      if current_pick.get("player") == self.player_id and current_pick.get("type") in ("colony", "research"):
        self._call(handlers_map, "submit_pick", {
          "type": current_pick["type"],
          "pick_id": -1,
        })
    elif stage == "discard_colony":
      self._discard_colony_step(handlers_map)

  def _player(self) -> Optional[Player]:
    return self.game.get_player_by_id(self.player_id)

  def _normalize_items(self, items: Dict[str, Any]) -> Dict[str, int]:
    normalized = {}
    for item, quantity in (items or {}).items():
      if isinstance(quantity, (int, float)) and quantity > 0:
        normalized[item] = int(quantity)
    return normalized

  def _can_pay(self, player: Player, items: Dict[str, int]) -> bool:
    return all(player.storage.get(item, 0) >= quantity for item, quantity in items.items())

  def _input_options(self, converter: Converter) -> List[Tuple[Dict[str, int], Dict[str, Any]]]:
    if isinstance(converter.input_items, list):
      return [
        (self._normalize_items(input_items), {"cost_type": index})
        for index, input_items in enumerate(converter.input_items)
      ]
    return [(self._normalize_items(converter.input_items), {})]

  def _converter_candidates(self, player: Player, stage: str) -> List[ConverterCandidate]:
    candidates = []
    for factory in player.factories.values():
      for index, converter in enumerate(factory.converters):
        if converter.used:
          continue
        if converter.running_stage not in (stage, "instant", "constant"):
          continue
        for input_items, extra_properties in self._input_options(converter):
          if not self._can_pay(player, input_items):
            continue
          output_items = self._normalize_items(converter.output_items)
          gain = get_items_value(output_items) - get_items_value(input_items)
          candidates.append(ConverterCandidate(
            factory_name=factory.name,
            converter_index=index,
            gain=gain,
            input_items=input_items,
            output_items=output_items,
            extra_properties=extra_properties,
          ))
    candidates.sort(key=lambda candidate: candidate.gain, reverse=True)
    return candidates

  def _best_candidate(self, player: Player, stage: str) -> Optional[ConverterCandidate]:
    candidates = self._converter_candidates(player, stage)
    return candidates[0] if candidates else None

  def _needed_items_for_best_converter(self, player: Player) -> Dict[str, int]:
    best_missing = None
    best_gain = float("-inf")
    for factory in player.factories.values():
      for converter in factory.converters:
        if converter.used or converter.running_stage not in ("production", "trading"):
          continue
        for input_items, _ in self._input_options(converter):
          missing = {
            item: quantity - player.storage.get(item, 0)
            for item, quantity in input_items.items()
            if quantity > player.storage.get(item, 0)
          }
          if not missing:
            continue
          gain = get_items_value(self._normalize_items(converter.output_items)) - get_items_value(input_items)
          if gain > best_gain:
            best_gain = gain
            best_missing = missing
    return best_missing or {}

  def _surplus_items(self, player: Player, protected_items: Dict[str, int]) -> Dict[str, int]:
    surplus = {}
    for item, quantity in player.storage.items():
      if item in ("Score", "ScoreDonation"):
        continue
      spare = quantity - protected_items.get(item, 0)
      if spare > 1:
        surplus[item] = spare - 1
    return surplus

  def _trim_to_value(self, items: Dict[str, int], target_value: float) -> Dict[str, int]:
    selected = {}
    total = 0.0
    for item, quantity in sorted(items.items(), key=lambda pair: get_item_value(pair[0])):
      for _ in range(quantity):
        item_value = get_item_value(item)
        if total >= target_value:
          return selected
        selected[item] = selected.get(item, 0) + 1
        total += item_value
    return selected

  def _proposal_value_for_acceptor(self, proposal: TradeProposal) -> float:
    return get_gift_value(proposal.send_gift) - get_gift_value(proposal.receive_gift)

  def _incoming_proposals(self) -> List[TradeProposal]:
    incoming = []
    for proposals in self.game.proposals.values():
      for proposal in proposals:
        if self.player_id in proposal.to_players:
          incoming.append(proposal)
    return incoming

  def _trading_step(self, handlers_map):
    player = self._player()
    if not player:
      return

    accepted_any = False
    for proposal in self._incoming_proposals():
      receive_items = self._normalize_items(proposal.receive_gift.get("items", {}))
      if not self._can_pay(player, receive_items):
        continue
      if self._proposal_value_for_acceptor(proposal) >= 0:
        self._call(handlers_map, "accept_trade_proposal", {"id": proposal.id})
        accepted_any = True
        break

    round_key = (self.game.current_round, self.player_id)
    if not accepted_any and round_key not in self.proposed_rounds:
      needed = self._needed_items_for_best_converter(player)
      if needed:
        protected = {}
        best_candidate = self._best_candidate(player, "production")
        if best_candidate:
          protected = best_candidate.input_items
        surplus = self._surplus_items(player, protected)
        ask_value = get_items_value(needed)
        offer = self._trim_to_value(surplus, ask_value)
        if offer and get_items_value(offer) >= max(0.5, ask_value * 0.8):
          targets = [other.user_id for other in self.game.players if other.user_id != self.player_id]
          self._call(handlers_map, "trade_proposal", {
            "to": targets,
            "message": "Rule baseline fair-value resource swap.",
            "send": {"items": offer, "factories": [], "techs": []},
            "receive": {"items": needed, "factories": [], "techs": []},
          })
          self.proposed_rounds.add(round_key)

    seeking = self._needed_items_for_best_converter(player)
    offering = self._surplus_items(player, seeking)
    self._call(handlers_map, "update_bulletin_board", {
      "message": "Rule baseline: fair resource trades.",
      "seeking": seeking,
      "offering": offering,
    })
    self._call(handlers_map, "confirm_ready")

  def _discard_colony_step(self, handlers_map):
    player = self._player()
    if not player:
      return
    excess = player.get_factory_num_by_type("Colony") - player.get_max_colony()
    if excess <= 0:
      return
    colonies = [
      factory.name
      for factory in player.factories.values()
      if factory.is_colony()
    ][:excess]
    self._call(handlers_map, "discard_colonies", {"colonies": colonies})

  def _production_step(self, handlers_map):
    player = self._player()
    if not player:
      return

    while True:
      candidate = self._best_candidate(player, "production")
      if not candidate or candidate.gain < 0:
        break
      before_used = player.factories[candidate.factory_name].converters[candidate.converter_index].used
      self._call(handlers_map, "produce", {
        "factory_name": candidate.factory_name,
        "converter_index": candidate.converter_index,
        "extra_properties": candidate.extra_properties,
      })
      after_used = player.factories.get(candidate.factory_name)
      if before_used or not after_used or not after_used.converters[candidate.converter_index].used:
        break

    self._call(handlers_map, "confirm_ready")

  def _bid_step(self, handlers_map):
    player = self._player()
    if not player:
      return
    ships = int(player.storage.get("Ship", 0))
    if ships <= 0:
      colony_bid = 0
      research_bid = 0
    elif ships == 1:
      colony_bid = 1
      research_bid = 0
    else:
      colony_bid = max(1, int(ships * 0.6))
      research_bid = max(0, min(ships - colony_bid, int(ships * 0.3)))
    self._call(handlers_map, "submit_bid", {
      "colony_bid": colony_bid,
      "research_bid": research_bid,
    })

  def _pick_step(self, handlers_map):
    player = self._player()
    if not player:
      return
    if player.specie == "Kjasjavikalimm" and self.game.Kajsjavikalimm_choose_split is None:
      self._call(handlers_map, "submit_kjasjavikalimm_split", {"choose_split": False})
      return

    current_pick = self.game.current_pick_player
    pick_type = current_pick.get("type")
    if current_pick.get("player") != self.player_id or pick_type not in ("colony", "research"):
      return

    cards = self.game.colony_bid_cards if pick_type == "colony" else self.game.research_bid_cards
    bid = player.colony_bid if pick_type == "colony" else player.research_bid
    affordable_ids = [
      index for index, card in enumerate(cards)
      if card["item"] is not None and card["price"] <= bid
    ]
    pick_id = affordable_ids[0] if affordable_ids else -1
    self._call(handlers_map, "submit_pick", {
      "type": pick_type,
      "pick_id": pick_id,
    })
