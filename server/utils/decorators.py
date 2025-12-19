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
