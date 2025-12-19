import random
import json

from server.server import Server
from server.utils.connect import create_app, get_router_name
from server.game import Game
from server.utils.log import set_file_log, set_verbose

if __name__ == "__main__":
  set_verbose(True)
  set_file_log(True)
  server = Server()
  server.run(host='0.0.0.0', port=2359, debug=False)
