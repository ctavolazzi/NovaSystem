from uuid import uuid4
from nova_prototype.versions.Tomato.get_ai_response import get_ai_response
from Utils import Logger

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

  def get_ai_response(self, message):
    return get_ai_response(message)

  def add_test(self, test_name, func):
    self[test_name] = func
    assert self[test_name] == func
    print(f"Added test: {test_name}")

    return self[test_name]

  def __str__(self) -> str:
    self_string = ''
    for attr in dir(self):
      if not attr.startswith('__') or not attr.startswith('_'):
        self_string += '{}: {}\n'.format(attr, getattr(self, attr))
    return self_string

if __name__ == '__main__':
  app = App()
  app.test = 'Nova_test'