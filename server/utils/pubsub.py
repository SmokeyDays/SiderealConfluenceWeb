from server.utils.log import logger


class PubSub:
  def __init__(self):
    self.subscribers = {}
    self.subscribers_scoped = {}

  def subscribe(self, event, callback, scope=None):
    if scope is None:
      if event not in self.subscribers:
        self.subscribers[event] = []
      self.subscribers[event].append(callback)
    else:
      if event not in self.subscribers_scoped:
        self.subscribers_scoped[event] = {}
      if scope not in self.subscribers_scoped[event]:
        self.subscribers_scoped[event][scope] = []
      self.subscribers_scoped[event][scope].append(callback)

  def publish(self, event, data=None, scope=None):
    if scope is None:
      if event in self.subscribers:
        for callback in self.subscribers[event]:
          callback(data)
    else:
      if event in self.subscribers_scoped:
        if scope in self.subscribers_scoped[event]:
          for callback in self.subscribers_scoped[event][scope]:
            callback(data, scope)

  def unsubscribe(self, event, callback, scope=None):
    if scope is None:
      if event in self.subscribers:
        self.subscribers[event] = [cb for cb in self.subscribers[event] if cb != callback]
    else:
      if event in self.subscribers_scoped:
        if scope in self.subscribers_scoped[event]:
          self.subscribers_scoped[event][scope] = [cb for cb in self.subscribers_scoped[event][scope] if cb != callback]

pubsub = PubSub()
