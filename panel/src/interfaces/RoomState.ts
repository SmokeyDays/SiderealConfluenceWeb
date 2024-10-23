export interface RoomPlayer {
  spice: string;
  agreed: boolean;
}

export interface RoomState {
  name: string;
  players: Record<string, RoomPlayer>;
  game_state: string;
}

export type RoomList = Record<string, RoomState>;

