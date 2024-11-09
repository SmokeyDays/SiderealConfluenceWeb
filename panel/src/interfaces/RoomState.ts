export interface RoomPlayer {
  specie: string;
  agreed: boolean;
}

export interface RoomState {
  name: string;
  players: Record<string, RoomPlayer>;
  game_state: string;
  max_players: number;
}

export type RoomList = Record<string, RoomState>;
