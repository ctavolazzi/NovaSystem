import logging

class GameLog:
    def __init__(self):
        # create logger
        self.logger = logging.getLogger('GameLog')
        self.logger.setLevel(logging.DEBUG)  # set logger level

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        self.logger.addHandler(ch)

    def log(self, message: str):
        self.logger.info(message)
