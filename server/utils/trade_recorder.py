class Trade:
  def __init__(self, from_player: str, to_player: str, turn: int, record: str, value: int):
    self.from_player = from_player
    self.to_player = to_player
    self.turn = turn
    self.record = record
    self.value = value

class TradeRecorder:
  def __init__(self):
    self.trades = {}
    self.trade_gap = {}

  def record_trade(self, trade: Trade):
    self.trades[trade.turn] = self.trades.get(trade.turn, []) + [trade]
    if trade.turn not in self.trade_gap:
      self.trade_gap[trade.turn] = {}
    if trade.from_player not in self.trade_gap[trade.turn]:
      self.trade_gap[trade.turn][trade.from_player] = {}
    if trade.to_player not in self.trade_gap[trade.turn][trade.from_player]:
      self.trade_gap[trade.turn][trade.from_player][trade.to_player] = 0
    self.trade_gap[trade.turn][trade.from_player][trade.to_player] += trade.value
    
  def get_value(self, turn: int, player_from: str, player_to: str):
    if turn not in self.trade_gap:
      return 0
    if player_from not in self.trade_gap[turn]:
      return 0
    return self.trade_gap[turn][player_from].get(player_to, 0)

  def get_sum_value(self, turn: int, player: str):
    total = 0
    for other_player in self.trade_gap[turn]:
      total += self.get_value(turn, player, other_player)
    return total
  
  def get_personal_trade_gap(self, player: str, turn: int = -1):
    if turn == -1:
      total = 0
      for hist_turn in self.trade_gap:
        total += self.get_sum_value(hist_turn, player)
        for other_player in self.trade_gap[hist_turn]:
          if other_player != player:
            total -= self.get_value(hist_turn, other_player, player)
      return total
    else:
      total = self.get_sum_value(turn, player)
      for other_player in self.trade_gap[turn]:
        if other_player != player:
          total -= self.get_value(turn, other_player, player)
      return total
    
  def get_pair_trade_gap(self, player_from: str, player_to: str, turn: int = -1):
    if turn == -1:
      total = 0
      for hist_turn in self.trade_gap:
        if player_from in self.trade_gap[hist_turn]:
          total += self.get_value(hist_turn, player_from, player_to)
        if player_to in self.trade_gap[hist_turn]:
          total += -self.get_value(hist_turn, player_to, player_from)
      return total
    else:
      return self.get_value(turn, player_from, player_to) - self.get_value(turn, player_to, player_from)

  def get_trades(self, turn: int = -1):
    if turn == -1:
      return [trade for trades in self.trades.values() for trade in trades]
    else:
      return self.trades.get(turn, [])
    
  def get_trades_str(self, turn: int = -1):
    return "\n".join([f"(Tune {trade.turn}) {trade.from_player} -> {trade.to_player}: {trade.record} ({trade.value})" for trade in self.get_trades(turn)])

if __name__ == "__main__":
  trade_recorder = TradeRecorder()
  trade_recorder.record_trade(Trade("A", "B", 1, "trade", 10))
  trade_recorder.record_trade(Trade("B", "C", 1, "trade", 20))
  trade_recorder.record_trade(Trade("C", "A", 1, "trade", 30))
  trade_recorder.record_trade(Trade("A", "B", 2, "trade", 15))
  trade_recorder.record_trade(Trade("B", "C", 2, "trade", -10))
  trade_recorder.record_trade(Trade("C", "A", 2, "trade", 35))
  trade_recorder.record_trade(Trade("A", "C", 2, "trade", 15))
  print(trade_recorder.get_personal_trade_gap(1, "A"))
  print(trade_recorder.get_pair_trade_gap(1, "A", "B"))
  print(trade_recorder.get_pair_trade_gap(1, "A", "C"))
  print(trade_recorder.get_pair_trade_gap(-1, "A", "B"))
  print(trade_recorder.get_pair_trade_gap(-1, "A", "C"))
  print(trade_recorder.get_personal_trade_gap(-1, "A"))
  print(trade_recorder.get_trades_str(1))
  print(trade_recorder.get_trades_str(2))
  print(trade_recorder.get_trades_str(-1))
