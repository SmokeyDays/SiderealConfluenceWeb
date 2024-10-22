import random
import json

from server.utils.connect import create_app, get_router_name
from server.game import Game
# Example usage:
if __name__ == "__main__":
  game = Game()
  app, socketio = create_app()
  @socketio.on('connect', namespace=get_router_name())
  def connected_success():
    print('client connected.')
    socketio.emit("update-state", {"state": game.to_dict()}, namespace=get_router_name())
    socketio.emit('alert-message', {
      "type": "success",
      "title": "Connected",
      "str": "Connected to the server successfully."
    }, namespace=get_router_name())

  socketio.run(app, host='0.0.0.0', port=2357, debug=False)
