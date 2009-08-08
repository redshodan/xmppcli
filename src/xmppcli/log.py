import logging
import logging.handlers

logger = None

def debug(*args, **kwargs):
    logger.info(*args, **kwargs)

def info(*args, **kwargs):
    logger.info(*args, **kwargs)

def setup(logfile = "xmppcli.log"):
    global logger
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')
    logger = logging.getLogger('xmppcli')
    logger.setLevel(logging.DEBUG)
    handler = logging.handlers.RotatingFileHandler(logfile,
                                                   maxBytes=1024*1024,
                                                   backupCount=5)
    logger.addHandler(handler)
