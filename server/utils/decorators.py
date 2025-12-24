from functools import wraps
import threading
from server.utils.log import logger

def add_info(info):
  def wrapper(func):
    func.info = info
    return func
  return wrapper

def add_para_desc(para, desc):
  def wrapper(func):
    if not hasattr(func, 'para_desc'):
      func.para_desc = {}
    func.para_desc[para] = desc
    return func
  return wrapper

def set_attr(attr, value):
  def wrapper(func):
    if not hasattr(func, 'attrs'):
      func.attrs = {}
    func.attrs[attr] = value
    return func
  return wrapper

class Registry:
  def __init__(self):
    self._registry = {}

  def __call__(self, tags):
    def inner(func):
      for tag in tags:
        if tag in self._registry:
          self._registry[tag].append(func)
        else:
          self._registry[tag] = [func]
      return func
    return inner

  def get(self, tag):
    return self._registry.get(tag, [])
  
  def get_all_tags(self):
    return list(self._registry.keys())

class RoomLockedRegistry:
  def __init__(self, server):
    self._registry = {}
    self.server = server

  def __call__(self, tags):
    def inner(func):
      @wraps(func)
      def wrapper(data, *args, **kwargs):
        room_name = None
        if self.server and isinstance(data, dict):
          room_name = data.get('room_name')
          if room_name and hasattr(self.server, 'rooms') and room_name in self.server.rooms:
            room = self.server.rooms[room_name]
            if hasattr(room, 'lock'):
              # === 核心：在这里加锁 ===
              with room.lock:
                return func(data, *args, **kwargs)
        return func(data, *args, **kwargs)
      for tag in tags:
        if tag in self._registry:
          self._registry[tag].append(wrapper)
        else:
          self._registry[tag] = [wrapper]
      return wrapper
      
    return inner

  def get(self, tag):
    return self._registry.get(tag, [])
  
  def get_all_tags(self):
    return list(self._registry.keys())