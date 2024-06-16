# Import required libraries
from uuid import uuid4
from apps.nova_prototype.versions.Tomato.NovaMessageConstructor.get_openai_chat_response import get_openai_chat_response as gocr
from apps.nova_prototype.versions.Tomato.NovaMessageConstructor.nova_messsage_constructor import nova_message_constructor as nmc

class App:
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

# Define variables for the messages to be sent to the OpenAI API

  def construct_openai_message(self, messages):
    return nmc(messages)

  def get_openai_response(self, messages):
    return gocr(messages)