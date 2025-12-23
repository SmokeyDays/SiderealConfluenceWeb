export class Gift {
  constructor(
    public items: { [key: string]: number },
    public factories: string[],
    public techs: string[]
  ) {}
}

export class TradeProposal {
  constructor(
    public id: number,
    public from_player: string,
    public to_players: string[],
    public send_gift: Gift,
    public receive_gift: Gift,
    public message: string
  ) {}
}

export class Converter {
  constructor(
    public input_items: { [key: string]: number } | [{ [key: string]: number }],
    public output_items: { [key: string]: number },
    public running_stage: string,
    public used: boolean
  ) {}
}

export class Factory {
  constructor(
    public name: string,
    public converters: Converter[],
    public preview: Converter[] | null,
    public owner: string,
    public feature: { type: string, properties: { [key: string]: any } },
    public run_count: number,
    public description: string
  ) {}
}

export class Player {
  constructor(
    public user_id: string,
    public specie: string,
    public specie_zh_name: string,
    public storage: { [key: string]: number },
    public factories: { [key: string]: Factory },
    public max_colony: number,
    public tie_breaker: number,
    public agreed: boolean,
    public colony_bid: number,
    public research_bid: number,
    public tech: string[],
    public invented_tech: string[],
    public score: number,
    public item_value: number,
    public bulletin_board: {
      message: string,
      seeking: { [key: string]: number },
      offering: { [key: string]: number }
    }
  ) {}
}

export function getStorage(player: Player, item: string): number {
  return (player.storage[item] || 0);
}

export class GameState {
  constructor(
    public players: Player[],
    public current_round: number,
    public end_round: number,
    public stage: string,
    public room_name: string,
    public research_bid_cards: { price: number, item: Factory | null }[],
    public colony_bid_cards: { price: number, item: Factory | null }[],
    public research_bid_priority: { player: string, bid: [number, number, number] }[],
    public colony_bid_priority: { player: string, bid: [number, number, number] }[],
    public current_pick: { type: string, player: string, bid: number },
    public current_discard_colony_player: string,
    public proposals: { [key: string]: TradeProposal[] },
    public Kajsjavikalimm_choose_split: boolean | null,
    public favor_buff_in_game: boolean,
    public faderan_relic_world_deck_size: number
  ) {}
}

export function isOnFavorBuff(gameState: GameState, player_id: string): boolean {
  const player = gameState.players.find(player => player.user_id === player_id);
  if (gameState.favor_buff_in_game && player && player.specie !== "Faderan" && getStorage(player, "Favor") > 0) {
    return true;
  }
  return false;
}

export function getFavorCost(gameState: GameState, player_id: string, item: string, cost: number): number {
  if (isOnFavorBuff(gameState, player_id) && item !== "Hypertech") {
    return cost - 1;
  }
  return cost;
}

export function isColony(factory: Factory): boolean {
  return factory.feature["type"] === "Colony" || factory.feature["properties"]["isColony"] === true;
}

export function getPlayerScore(player: Player): number{
  return (player.score + player.item_value * 0.5 / 3);
}