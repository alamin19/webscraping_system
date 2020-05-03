
import os
import logging,datetime
from logging.handlers import RotatingFileHandler

class LogHelper():
    def __init__(self):
        self.TIME_STAMP = datetime.datetime.now() - datetime.timedelta(minutes=60)
        self.TIME_STAMP = str(self.TIME_STAMP)

    def create_rotating_log(self, foldername=None, source=None):
        """
        Creates a rotating log
        """
        if source == None:
            source = "appcast"
        if foldername == None:
            foldername = "logfiles"
        f = logging.Formatter("%(asctime)s %(levelname)-9s %(name)-8s %(thread)5s %(message)s")

        root = logging.getLogger(source)
        root.setLevel(logging.INFO)

        log_root = os.path.dirname(__file__)

        source_log = os.path.join(log_root, foldername)

        _logFileName = os.path.join(source_log, source + ".log")

        _MaxFileSize = 500000
        _MaxFiles = 50

        # h = logging.FileHandler(logFileName, 'w')
        h = logging.handlers.RotatingFileHandler(_logFileName, "a", _MaxFileSize, _MaxFiles)
        root.addHandler(h)
        h.setFormatter(f)
        h = logging.handlers.SocketHandler('localhost', logging.handlers.DEFAULT_TCP_LOGGING_PORT)
        root.addHandler(h)
        return root