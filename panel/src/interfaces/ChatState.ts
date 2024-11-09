export interface Message {
  date: string;
  sender: string;
  msg: string;
  // null room stands for the message is sent to all rooms
  room: string | null;
  // null user stands for the message is sent to all users
  // if room is not null, the message is sent to all users in the room
  // if both room and user are not null, the message is sent to the specific user in the specific room
  user: string | null;
}

export const messageEqual = (a: Message, b: Message) => {
  return a.date === b.date && a.sender === b.sender && a.msg === b.msg && a.room === b.room && a.user === b.user;
}
