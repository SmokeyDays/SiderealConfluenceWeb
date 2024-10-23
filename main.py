import random
import json

from server.utils.connect import create_app, get_router_name
from server.game import Game, Player, Factory
# Example usage:
def load_player(json_path: str):
  data = {}
  with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)
  start_resources = data['start_resource']
  player_name = data['name']
  spice_factories = {}
  for factory_data in data['factories']:
    factory = Factory(factory_data['name'], factory_data['input_items'], factory_data['output_items'], player_name)
    spice_factories[factory.name] = factory
  start_factories = []
  for factory_name in start_resources['factories']:
    if factory_name in spice_factories:
      start_factories.append(spice_factories[factory_name])
    else:
      print("error, ", factory_name, "not found")
  player = Player(player_name, start_resources['items'], start_factories)
  return player

if __name__ == "__main__":
  game = Game()
  player = load_player('F:\Custom Games\SiderealConfluenceWeb\server\data\Kylion.json')
  game.add_player(player)
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
