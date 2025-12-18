class Config:
  singleton = None

  def __init__(self):
    self.config = {
      "auto_step_bot": False,
      'default_turn': 6,
    }


  @classmethod
  def instance(cls):
    if cls.singleton is None:
      cls.singleton = Config()
    return cls.singleton

  def set(self, key, value):
    self.config[key] = value

  def get(self, key):
    return self.config[key]


def get_config(key):
  return Config.instance().get(key)

def set_config(key, value):
  Config.instance().set(key, value)


