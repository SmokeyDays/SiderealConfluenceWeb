import logging
from enum import Enum

class CONSOLE_COLOR(Enum):
  WHITE = 0
  RED = 31
  GREEN = 32
  YELLOW = 33
  BLUE = 34
  MAGENTA = 35
  CYAN = 36
  LIGHT_GRAY = 37
  DARK_GRAY = 90
  LIGHT_RED = 91
  LIGHT_GREEN = 92
  LIGHT_YELLOW = 93
  LIGHT_BLUE = 94
  LIGHT_MAGENTA = 95
  LIGHT_CYAN = 96
  BLACK = 97

# Create a custom logger
logger = logging.getLogger(__name__)
formatter = logging.Formatter('[%(asctime)s][%(filename)s:%(lineno)d][%(levelname)s] %(message)s')

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def set_verbose(v):
  if v:
    logger.setLevel(logging.DEBUG)
  else:
    logger.setLevel(logging.WARNING)

def set_file_log(v):
  if v:
    handler = logging.FileHandler('logs/log.txt')
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def set_file_log_path(path):
  old_handler = None
  for handler in logger.handlers:
    if type(handler) is logging.FileHandler:
      old_handler = handler
      break
  if old_handler is not None:
    logger.removeHandler(old_handler)
  handler = logging.FileHandler(path)
  handler.setLevel(logging.DEBUG)
  handler.setFormatter(formatter)
  logger.addHandler(handler)

# def log(pre, *args, file = None):
#   message = ' '.join(map(str, args))
#   if pre == "info":
#     logger.info(message)
#   elif pre == "warning":
#     logger.warning(message)
#   elif pre == "error":
#     logger.error(message)

def colored_text(text, color):
  return f"\033[{color}m{text}\033[0m"