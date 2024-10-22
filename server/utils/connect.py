from flask import Flask, render_template
from flask_socketio import SocketIO, emit

# pip install flask-socketio
# Flask==2.1.1
# Flask-SocketIO==5.1.1
# greenlet==1.1.2
# Jinja2==3.1.1
# python-engineio==4.3.1
# python-socketio==5.5.2
# Werkzeug==2.1.1

router_name = '/backend'

def get_router_name():
  return router_name

def create_app():
  app = Flask(__name__)

  socketio = SocketIO()
  socketio.init_app(app, cors_allowed_origins='*', async_mode="threading")

  @app.route('/test')
  def hello():
      # How can I send a WebSocket message from here?
      return 'Hello World!'


  @app.route('/')
  def index():
      return render_template("./index.html")

  @socketio.on('disconnect', namespace=router_name)
  def disconnect_msg():
    print('client disconnected.')

  return app, socketio


if __name__ == '__main__':
  app, socketio = create_app()
  socketio.run(app, host='0.0.0.0', port=2357, debug=True)
    
