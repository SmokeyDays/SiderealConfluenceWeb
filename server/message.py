class Message:
  def __init__(self, sender, msg, date, room = None, user = None):
    self.date = date
    self.sender = sender
    self.msg = msg
    self.room = room
    self.user = user

  def to_dict(self):
    return {
      "date": self.date,
      "sender": self.sender,
      "msg": self.msg,
      "room": self.room,
      "user": self.user
    }

class MessageManager:
  def __init__(self, max_length = 500, on_new_msg = lambda msg : None):
    self.max_length = max_length
    self.msgs = []
    self.on_new_msg = on_new_msg

  def get_msgs_by_user(self, user_id):
    res = []
    for msg in self.msgs:
      if msg.user is None or msg.user == user_id or msg.sender == user_id:
        res.append(msg)
    return res
  
  def new_msg(self, msg):
    self.msgs.append(msg)
    if len(self.msgs) > self.max_length:
      self.msgs.pop(0)
    return self.on_new_msg(msg)
