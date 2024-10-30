export class Converter {
  constructor(
    public input_items: { [key: string]: number } | [{ [key: string]: number }],
    public output_items: { [key: string]: number },
    public donation_items: { [key: string]: number },
    public running_stage: string,
    public used: boolean
  ) {}
}

export class Factory {
  constructor(
    public name: string,
    public converter: Converter,
    public preview: Converter | null,
    public owner: string,
    public feature: { type: string, properties: { [key: string]: any } },
    public run_count: number
  ) {}
}

export class Player {
  constructor(
    public user_id: string,
    public specie: string,
    public specie_zh_name: string,
    public storage: { [key: string]: number },
    public donation_items: { [key: string]: number },
    public factories: { [key: string]: Factory },
    public max_colony: number,
    public tie_breaker: number,
    public agreed: boolean,
    public colony_bid: number,
    public research_bid: number,
    public tech: string[],
    public invented_tech: string[]
  ) {}
}

export class GameState {
  constructor(
    public players: Player[],
    public current_round: number,
    public stage: string,
    public room_name: string,
    public research_bid_cards: { price: number, item: Factory | null }[],
    public colony_bid_cards: { price: number, item: Factory | null }[],
    public current_pick: { type: string, player: string },
    public current_discard_colony_player: string
  ) {}
}
