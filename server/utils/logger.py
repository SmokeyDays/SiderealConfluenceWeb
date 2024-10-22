from enum import Enum

verbose = True

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
  


def set_verbose(v):
  global verbose
  verbose = v

prefix = {
  # info is default, warning is yellow, error is red
  "info": "\033[0m[Info]\033[0m ",
  "warning": "\033[33m[Warning]\033[0m ",
  "error": "\033[31m[Error]\033[0m ",
}

def log(pre, *args):
  if verbose:
    print(prefix[pre], *args)

def colored_text(text, color):
  return f"\033[{color}m{text}\033[0m"