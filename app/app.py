from uuid import uuid4

class App():
  def __init__(self):
    self.id = str(uuid4())

  def get(self, attr):
    return getattr(self, attr)

  def set(self, attr, value):
      if not attr.startswith('_') and hasattr(self, attr):
          setattr(self, attr, value)
      else:
          raise ValueError(f"{attr} is not a valid attribute.")

  def __str__(self) -> str:
    self_string = ''
    for attr in dir(self):
      if not attr.startswith('__') or not attr.startswith('_'):
        self_string += '{}: {}\n'.format(attr, getattr(self, attr))
        print(attr, getattr(self, attr))
    return self_string