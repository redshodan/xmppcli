# Copyright (C) 2009 James Newton
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import logging, re
import logging.handlers

XML = 60
FORMAT = "%(levelname)s: %(message)s"
XMPPPY_FORMAT = "%(levelname)s(%(realm)s/%(realm2)s): %(message)s"
XML_FORMAT = "%(dir)s: %(message)s"
logger = None

class MultiFormatter(logging.Formatter):
    def format(self, record):
        org = self._fmt
        if hasattr(record, "format"):
            self._fmt = record.format
        ret = logging.Formatter.format(self, record)
        self._fmt = org
        return ret

class LevelFilter(object):
    def __init__(self, lvl, invert):
        self.lvl = lvl
        self.invert = invert

    def filter(self, record):
        match = record.levelno == self.lvl
        if self.invert:
            return not match
        else:
            return match

class XMPPPYProxy(object):
    LOG_RE1 = re.compile(r"^([A-Z]+):\s+([a-z]+)\s+([a-z]+)\s+(.+)$")
    LOG_RE2 = re.compile(r"^([A-Z]+):\s+(.+)$")
    LOG_RE3 = re.compile(r"^([A-Z]+):\s+$")

    def write(self, buff):
      try:
        buff = buff.rstrip("\r\n")
        arr = self.LOG_RE1.split(buff)
        if len(arr) == 1:
            arr = self.LOG_RE2.split(buff)
        if len(arr) == 1:
            return
        lvl = logging.getLevelName(arr[1])
        if len(arr) == 6:
            logger.log(lvl, arr[4], realm=arr[2], realm2=arr[3])
        else:
            logger.log(lvl, buff[len(arr[1]):])
      except Exception, e:
          print e
    def flush(self):
        pass

xmpppy_proxy = XMPPPYProxy()

class Logger(logging.LoggerAdapter):
    def __init__(self, logger):
        logging.LoggerAdapter.__init__(self, logger, None)
        self.write_buff = []

    def process(self, msg, kwargs):
        if "realm" in kwargs:
            extra = {"realm":kwargs["realm"], "realm2":kwargs["realm2"],
                     "format":XMPPPY_FORMAT}
            kwargs["extra"] = extra
            del kwargs["realm"]
            del kwargs["realm2"]
        elif "dir" in kwargs:
            extra = {"dir":kwargs["dir"], "format":XML_FORMAT}
            kwargs["extra"] = extra
            del kwargs["dir"]
        return msg, kwargs

    def __getattr__(self, name):
        return getattr(self.logger, name)

def debug(*args, **kwargs):
    logger.debug(*args, **kwargs)

def info(*args, **kwargs):
    logger.info(*args, **kwargs)

def warn(*args, **kwargs):
    logger.warning(*args, **kwargs)

def error(*args, **kwargs):
    logger.error(*args, **kwargs)

def crit(*args, **kwargs):
    logger.critical(*args, **kwargs)

def exception(*args, **kwargs):
    logger.exception(*args, **kwargs)

def xmlIN(*args, **kwargs):
    kwargs["dir"] = "IN"
    logger.log(XML, *args, **kwargs)

def xmlOUT(*args, **kwargs):
    kwargs["dir"] = "OUT"
    logger.log(XML, *args, **kwargs)

def setup(logfile = "xmppcli.log"):
    global logger
    logging.addLevelName(XML, "xml")
    logger = Logger(logging.getLogger('xmppcli'))
    logger.setLevel(logging.DEBUG)
    handler = logging.handlers.RotatingFileHandler(logfile,
                                                   maxBytes=1024*1024,
                                                   backupCount=5)
    formatter = MultiFormatter(FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def addStreamHandler(file, lvl=0, format=FORMAT, fltr=None):
    handler = logging.StreamHandler(file)
    if lvl:
        handler.setLevel(lvl)
    if fltr:
        handler.addFilter(fltr)
    else:
        handler.addFilter(LevelFilter(XML, True))
    formatter = MultiFormatter(FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return handler

def addXMLHandler(file):
    addStreamHandler(file, XML, XML_FORMAT, LevelFilter(XML, False))
