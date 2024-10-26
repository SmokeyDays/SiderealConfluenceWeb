export class Factory {
  constructor(
    public name: string,
    public input_items: { [key: string]: number },
    public output_items: { [key: string]: number },
    public used: boolean,
    public owner: string
  ) {}
}

export class Player {
  constructor(
    public user_id: string,
    public specie: string,
    public storage: { [key: string]: number },
    public donation_items: { [key: string]: number },
    public factories: { [key: string]: Factory },
    public agreed: boolean
  ) {}
}

export class GameState {
  constructor(
    public players: Player[],
    public current_round: number,
    public stage: string,
    public room_name: string
  ) {}
}
