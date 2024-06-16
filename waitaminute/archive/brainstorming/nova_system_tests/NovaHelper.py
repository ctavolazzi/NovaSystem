import time

class NovaHelper():
  _default_delay = 0.022

  def __init__(self):
    self.classification = 'NovaHelper'

  def test(self):
    self.stc(f'Testing NovaHelper...\n')
    self.stc(f'classification: {self.classification}\n')
    self.stc(f'{self.classification} class instantiated successfully.')

  def stream_to_console(self, message, delay=_default_delay):
    for char in message:
      print(char, end='', flush=True)
      time.sleep(delay)

  def stc(self, message, delay=_default_delay):
    self.stream_to_console(message, delay)

def stc(message, delay=0.022):
  helper = NovaHelper()
  helper.stream_to_console(message, delay)

if __name__ == "__main__":
  helper = NovaHelper()
  helper.test()
