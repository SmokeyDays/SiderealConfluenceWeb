class Config:
  singleton = None

  def __init__(self):
    self.config = {
      "auto_step_bot": True,
      'default_turn': 6,
      'load_old_saves': True,
      'default_bot_type': 'gpt-4o-mini',
      # Agent function-calling mode: "off" | "auto" | "on"
      # off: always use legacy JSON-in-prompt
      # auto: try FC first, fallback to legacy JSON if unsupported
      # on: prefer FC and still fallback on runtime errors
      "agent_function_calling_mode": "on",

      # Ablation settings here
      "prompt_converter_value_adding": True,
      # Debounce window (seconds) for coalescing repeated bot-step triggers.
      "bot_step_debounce_seconds": 0.1,
      # If no game-state update happens for this long, trigger silence recovery.
      "bot_silence_seconds": 30.0,
      # Number of consecutive silence recoveries before auto-confirming remaining bots.
      "bot_silence_force_ready_after": 3,
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


