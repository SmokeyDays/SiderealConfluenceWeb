export interface Factory {
  name: string;
  input_items: { [key: string]: number };
  output_items: { [key: string]: number };
  used: boolean;
  owner: string;
}

export interface Player {
  name: string;
  storage: { [key: string]: number };
  factories: { [key: string]: Factory };
  agreed: boolean;
}

export interface GameState {
  players: Player[];
  current_round: number;
  stage: string;
}


