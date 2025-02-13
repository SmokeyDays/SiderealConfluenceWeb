
import os
import pickle
import time
from server.room import Room


def save_room(room: Room, path: str = "./saves"):
  if not os.path.exists(path):
    os.makedirs(path)
  filename = f"room_{room.name}.pkl"
  filepath = f"{path}/{filename}"
  if os.path.exists(filepath):
    os.rename(filepath, f"{filepath}_{time.time()}.bak.pkl")
  with open(filepath, "wb") as f:
    pickle.dump(room, f)

def load_room(room_name: str, path: str = "./saves"):
  try:
    filename = f"room_{room_name}.pkl"
    filepath = f"{path}/{filename}"
    with open(filepath, "rb") as f:
      return pickle.load(f)
  except Exception as e:
    print(f"Error loading room {room_name}: {e}")
    return None

def load_all_rooms(path: str = "./saves"):
  if not os.path.exists(path):
    return {}
  rooms = {}
  for file in os.listdir(path):
    if file.endswith(".pkl"):
      with open(os.path.join(path, file), "rb") as f:
        rooms[file.split("_")[1].split(".")[0]] = pickle.load(f)
  return rooms
