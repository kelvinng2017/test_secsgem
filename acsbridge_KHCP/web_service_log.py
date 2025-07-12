import logging
import logging.handlers as log_handler
import os
from colorlog import ColoredFormatter as cl #ggg
print("web_serbice_log_version_241119")

def addLoggingLevel(levelName, levelNum, methodName=None):
    if not methodName:
        methodName = levelName.lower()
    
    if hasattr(logging, levelName):
        raise AttributeError('{} already defined in logging module'.format(levelName))
    if hasattr(logging, methodName):
        raise AttributeError('{} already defined in logging module'.format(methodName))
    if hasattr(logging.getLoggerClass(), methodName):
        raise AttributeError('{} already defined in logger class'.format(methodName))
    
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)
    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)
    
    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)

if not os.path.isdir("./log"):
    print("no file log")
    os.mkdir("./log")

format_str = "%(asctime)s-[%(funcName)s]-[line:%(lineno)d]-[%(levelname)s]-[%(threadName)s]:%(message)s"
date_format = '%Y-%m-%d %H:%M:%S'
cformat = '%(log_color)s' + format_str
colors = {'DEBUG': 'green',
          'INFO': 'cyan',
          'INFO2':'yellow',
          'WARNING': 'bold_yellow',
          'ERROR': 'bold_red',
          'CRITICAL': 'bg_purple'}
formatter = cl(cformat, date_format, log_colors=colors)
SERIOUS = 51
logging.addLevelName(35, "INFO2")
logging.addLevelName(9, "*")

def info2(self, message, *args, **kwargs):
    if self.isEnabledFor(35):
        self._log(35, message, args, **kwargs)

    logging.Logger.INFO2 = info2
# logging.addLevelName(35, 'MINOR')
print(logging.getLevelName(0))


################################################################################################
acsbridge_logger = logging.getLogger("acsbridge")
acsbridge_logger.setLevel(logging.DEBUG)

streamLogHandler = logging.StreamHandler()
streamLogHandler.setLevel(logging.DEBUG)
streamLogHandler.setFormatter(formatter)
acsbridge_logger.addHandler(streamLogHandler)

filename = os.path.join("log", "acsbridge.log")
LogFileHandler = log_handler.TimedRotatingFileHandler(filename, when='midnight', interval=1, backupCount=30, encoding="utf-8")
LogFileHandler.setLevel(logging.DEBUG)
LogFileHandler.setFormatter(logging.Formatter("%(asctime)s-[%(funcName)s]-[line:%(lineno)d]-[%(levelname)s]-[%(threadName)s]-%(processName)s: %(message)s"))
acsbridge_logger.addHandler(LogFileHandler)
######################################################################################
global_variables_logger = logging.getLogger("global_variables")
global_variables_logger.setLevel(logging.DEBUG)
streamLogHandler = logging.StreamHandler()
streamLogHandler.setLevel(logging.DEBUG)
streamLogHandler.setFormatter(formatter)
global_variables_logger.addHandler(streamLogHandler)

filename = os.path.join("log", "global_variables.log")
LogFileHandler = log_handler.TimedRotatingFileHandler(filename, when='midnight', interval=1, backupCount=30, encoding="utf-8")
LogFileHandler.setLevel(logging.DEBUG)
LogFileHandler.setFormatter(logging.Formatter("%(asctime)s-[%(funcName)s]-[line:%(lineno)d]-[%(levelname)s]-[%(threadName)s]: %(message)s"))
global_variables_logger.addHandler(LogFileHandler)
######################################################################################
mythread_logger = logging.getLogger("mythread")
mythread_logger.setLevel(logging.DEBUG)
streamLogHandler = logging.StreamHandler()
streamLogHandler.setLevel(logging.DEBUG)
streamLogHandler.setFormatter(formatter)
mythread_logger.addHandler(streamLogHandler)

filename = os.path.join("log", "mythread.log")
LogFileHandler = log_handler.TimedRotatingFileHandler(filename, when='midnight', interval=1, backupCount=30, encoding="utf-8")
LogFileHandler.setLevel(logging.DEBUG)
LogFileHandler.setFormatter(logging.Formatter("%(asctime)s-[%(funcName)s]-[line:%(lineno)d]-[%(levelname)s]-[%(threadName)s]: %(message)s"))
mythread_logger.addHandler(LogFileHandler)
######################################################################################
test_K11_logger = logging.getLogger("test_K11")
test_K11_logger.setLevel(logging.DEBUG)
streamLogHandler = logging.StreamHandler()
streamLogHandler.setLevel(logging.DEBUG)
streamLogHandler.setFormatter(formatter)
test_K11_logger.addHandler(streamLogHandler)

filename = os.path.join("log", "test_K11.log")
LogFileHandler = log_handler.TimedRotatingFileHandler(filename, when='midnight', interval=1, backupCount=30, encoding="utf-8")
LogFileHandler.setLevel(logging.DEBUG)
LogFileHandler.setFormatter(logging.Formatter("%(asctime)s-[%(funcName)s]-[line:%(lineno)d]-[%(levelname)s]-[%(threadName)s]: %(message)s"))
test_K11_logger.addHandler(LogFileHandler)
######################################################################################
AMR01_route_logger = logging.getLogger("AMR01_route")
AMR01_route_logger.setLevel(logging.DEBUG)

streamLogHandler = logging.StreamHandler()
streamLogHandler.setLevel(logging.DEBUG)
streamLogHandler.setFormatter(formatter)
AMR01_route_logger.addHandler(streamLogHandler)

filename = os.path.join("log", "AMR01_route.log")
LogFileHandler = log_handler.TimedRotatingFileHandler(filename, when='midnight', interval=1, backupCount=5, encoding="utf-8")
LogFileHandler.setLevel(logging.DEBUG)
LogFileHandler.setFormatter(logging.Formatter("%(asctime)s-[%(funcName)s]-[line:%(lineno)d]-[%(levelname)s]-[%(threadName)s]: %(message)s"))
AMR01_route_logger.addHandler(LogFileHandler)
######################################################################################
error_logger = logging.getLogger("error")
error_logger.setLevel(logging.DEBUG)

streamLogHandler = logging.StreamHandler()
streamLogHandler.setLevel(logging.DEBUG)
streamLogHandler.setFormatter(formatter)
error_logger.addHandler(streamLogHandler)

filename = os.path.join("log", "error.log")
LogFileHandler = log_handler.TimedRotatingFileHandler(filename, when='midnight', interval=1, backupCount=5, encoding="utf-8")
LogFileHandler.setLevel(logging.DEBUG)
LogFileHandler.setFormatter(logging.Formatter("%(asctime)s-[%(funcName)s]-[line:%(lineno)d]-[%(levelname)s]-[%(threadName)s]: %(message)s"))
error_logger.addHandler(LogFileHandler)
######################################################################################
alarm_logger = logging.getLogger("alarm")
alarm_logger.setLevel(logging.DEBUG)

streamLogHandler = logging.StreamHandler()
streamLogHandler.setLevel(logging.DEBUG)
streamLogHandler.setFormatter(formatter)
alarm_logger.addHandler(streamLogHandler)

filename = os.path.join("log", "alarm.log")
LogFileHandler = log_handler.TimedRotatingFileHandler(filename, when='midnight', interval=1, backupCount=5, encoding="utf-8")
LogFileHandler.setLevel(logging.DEBUG)
LogFileHandler.setFormatter(logging.Formatter("%(asctime)s-[%(funcName)s]-[line:%(lineno)d]-[%(levelname)s]-[%(threadName)s]: %(message)s"))
alarm_logger.addHandler(LogFileHandler)
#####################################################################################
vibration_logger = logging.getLogger("vibration")
vibration_logger.setLevel(logging.DEBUG)


# streamLogHandler = logging.StreamHandler()
# streamLogHandler.setLevel(logging.DEBUG)
# streamLogHandler.setFormatter(formatter)
# vibration_logger.addHandler(streamLogHandler)

filename = os.path.join("log", "vibration.log")
LogFileHandler = log_handler.TimedRotatingFileHandler(filename, when='midnight', interval=1, backupCount=30, encoding="utf-8")
LogFileHandler.setLevel(logging.DEBUG)
LogFileHandler.setFormatter(logging.Formatter("%(asctime)s-[%(funcName)s]-[line:%(lineno)d]-[%(levelname)s]-[%(threadName)s]: %(message)s"))
vibration_logger.addHandler(LogFileHandler)
#####################################################################################

A010_logger = logging.getLogger("A010")
A010_logger.setLevel(logging.DEBUG)

filename = os.path.join("log", "A010.log")
LogFileHandler = log_handler.TimedRotatingFileHandler(filename, when='midnight', interval=1, backupCount=30, encoding="utf-8")
LogFileHandler.setLevel(logging.DEBUG)
LogFileHandler.setFormatter(logging.Formatter("%(asctime)s-[%(funcName)s]-[line:%(lineno)d]-[%(levelname)s]-[%(threadName)s]: %(message)s"))
A010_logger.addHandler(LogFileHandler)