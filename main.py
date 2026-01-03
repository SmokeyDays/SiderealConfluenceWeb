from datetime import datetime
import random
import json

from server.server import Server
from server.utils.connect import create_app, get_router_name
from server.game import Game
from server.utils.log import set_file_log, set_file_log_path, set_verbose

if __name__ == "__main__":
  set_verbose(True)
  set_file_log(True)
  save_path = f"logs/log_{datetime.now().timestamp()}.txt"
  set_file_log_path(save_path)
  server = Server()
  server.run(host='0.0.0.0', port=2359, debug=False)
