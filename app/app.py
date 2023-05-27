from uuid import uuid4

class App():
  def __init__(self):
    self.id = str(uuid4())

  def get(self, attr):
    return getattr(self, attr)

  def set(self, attr, value):
    if attr.startswith('_'):
      raise ValueError(f"Cannot set private attribute: {attr}")
    elif not hasattr(self, attr):
      raise ValueError(f"Attribute {attr} does not exist.")
    else:
      setattr(self, attr, value)

  def __str__(self) -> str:
    self_string = ''
    for attr in dir(self):
      if not attr.startswith('__') or not attr.startswith('_'):
        self_string += '{}: {}\n'.format(attr, getattr(self, attr))
    return self_string