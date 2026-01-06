
import os
import pickle
import time
import glob
from server.room import Room
from server.utils.log import logger

def save_room(room: Room, path: str = "./saves"):
  if not os.path.exists(path):
    os.makedirs(path)
  
  if room.game:
    round_num = room.game.current_round
    stage = room.game.stage
    # Sanitize stage name just in case
    stage_safe = "".join([c for c in stage if c.isalnum() or c in ('-', '_')])
    
    timestamp = int(time.time())
    filename = f"room_{room.name}_r{round_num}_s{stage_safe}_{timestamp}.pkl"
    
    # Check for existing saves for this round and stage
    pattern = f"room_{room.name}_r{round_num}_s{stage_safe}_*.pkl"
    search_path = os.path.join(path, pattern)
    existing_files = glob.glob(search_path)
    
    # Filter out any non-save files if necessary, though pattern is specific
    existing_files = [f for f in existing_files if f.endswith(".pkl")]
    
    if len(existing_files) >= 3:
      # Sort by modification time (oldest first)
      existing_files.sort(key=os.path.getmtime)
      
      # Delete oldest until we have < 3
      while len(existing_files) >= 3:
        try:
          os.remove(existing_files[0])
          existing_files.pop(0)
        except OSError as e:
          print(f"Error deleting old save {existing_files[0]}: {e}")
  else:
    filename = f"room_{room.name}.pkl"
    filepath = f"{path}/{filename}"
    if os.path.exists(filepath):
      os.rename(filepath, f"{filepath}_{time.time()}.bak.pkl")

  filepath = f"{path}/{filename}"
  with open(filepath, "wb") as f:
    pickle.dump(room, f)

def load_room(room_name: str, path: str = "./saves"):
  try:
    # Find all files for this room
    # Match room_{room_name}.pkl or room_{room_name}_*.pkl
    # Be careful not to match room_{room_name}suffix.pkl
    
    candidates = []
    if os.path.exists(path):
      for file in os.listdir(path):
        if not file.endswith(".pkl") or file.endswith(".bak.pkl"):
          continue
        
        # Check if file starts with room_{room_name}
        prefix = f"room_{room_name}"
        if file == f"{prefix}.pkl" or file.startswith(f"{prefix}_"):
           candidates.append(os.path.join(path, file))
    
    if not candidates:
      return None
      
    # Sort by mtime descending
    candidates.sort(key=os.path.getmtime, reverse=True)
    filepath = candidates[0]
    
    with open(filepath, "rb") as f:
      return pickle.load(f)
  except Exception as e:
    print(f"Error loading room {room_name}: {e}")
    return None

def load_all_rooms(path: str = "./saves"):
  if not os.path.exists(path):
    return {}
  rooms = {}
  
  # Group files by room name
  room_files = {} # name -> list of (filepath, mtime)
  
  for file in os.listdir(path):
    if file.endswith(".pkl") and not file.endswith(".bak.pkl"):
      logger.info(f"Found save file: {file}")
      parts = file.split("_")
      if len(parts) >= 2 and parts[0] == "room":
        # Assuming room name is the second part and doesn't contain underscores
        room_name = parts[1]
        # If filename is room_Name.pkl, parts=['room', 'Name.pkl'] -> room_name='Name.pkl' -> split('.')[0] -> 'Name'
        # If filename is room_Name_r1...pkl, parts=['room', 'Name', 'r1'...] -> room_name='Name'
        
        if room_name.endswith(".pkl"):
            room_name = room_name.split(".")[0]
            
        filepath = os.path.join(path, file)
        mtime = os.path.getmtime(filepath)
        
        if room_name not in room_files:
          room_files[room_name] = []
        room_files[room_name].append((filepath, mtime))
        
  for room_name, files in room_files.items():
    # Sort by mtime descending
    files.sort(key=lambda x: x[1], reverse=True)
    if files:
      latest_file = files[0][0]
      try:
        with open(latest_file, "rb") as f:
          rooms[room_name] = pickle.load(f)
          rooms[room_name].name = room_name  # Ensure the room name is set correctly
          if rooms[room_name].game is not None:
            rooms[room_name].game.room_name = room_name  # Re-link room reference in game
            logger.info(f"Room {room_name} loaded at round {rooms[room_name].game.current_round}, stage {rooms[room_name].game.stage}")
      except Exception as e:
        print(f"Error loading room {room_name} from {latest_file}: {e}")
      

  return rooms
