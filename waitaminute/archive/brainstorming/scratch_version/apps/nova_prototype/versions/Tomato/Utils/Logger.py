class Logger:
  def __init__(self, target=None, log_file=None):
    self.log_file = log_file
    self.log = open(self.log_file, 'w+')
    self.log.close()

  def write(self, message):
    self.log = open(self.log_file, 'a')
    self.log.write(message)
    self.log.close()

  def read(self):
    self.log = open(self.log_file, 'r')
    return self.log.read()

  def create(self):
    self.log = open(self.log_file, 'w+')
    self.log.close()

  def __str__(self):
    return self.read()

  def __repr__(self):
    return self.read()