from colorlog import StreamHandler, ColoredFormatter
from logging.handlers import TimedRotatingFileHandler
from os.path import dirname, join
from pathlib import Path

import logging
import os

class SystemLogFormatter(logging.Formatter):
    def format(self, record):
        record.event = 'SYSTEM'
        record.user = 'SYSTEM'
        record.url = None
        record.remote_addr = None

        if 'event' in record.args:
            record.event = record.args.get('event')

        if 'user' in record.args:
            record.user = record.args.get('user')
        
        return super().format(record)

class Logger:
    def __init__(self, name, file = None) -> None:
        colored_formatter = ColoredFormatter('%(log_color)s%(asctime)s-[%(funcName)s]-[line:%(lineno)d]-[%(levelname)s]-[%(threadName)s]:%(message)s')
        formatter = SystemLogFormatter('%(asctime)s-[%(funcName)s]-[line:%(lineno)d]-[%(levelname)s]-[%(threadName)s]:%(message)s')

        log_file = join(os.getcwd(), 'log', file)

        if not Path(log_file).is_file():
            os.makedirs(dirname(log_file), exist_ok=True)
            log_file_handler = logging.FileHandler(log_file, mode='w', encoding=None, delay=False)
        
        timed_file_handler = TimedRotatingFileHandler(log_file, when='midnight', backupCount=30)
        timed_file_handler.setFormatter(formatter)

        self.log = logging.getLogger(name)

        stream_handler = StreamHandler()
        stream_handler.setFormatter(colored_formatter)

        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(timed_file_handler)
        self.log.addHandler(stream_handler)

    def debug(self, message, args = None):
        if args is not None:
            self.log.debug(message, args)
        else:
            self.log.debug(message)
        
    def info(self, message, args = None):
        if args is not None:
            self.log.info(message, args)
        else:
            self.log.info(message)
        
    def warning(self, message, args = None):
        if args is not None:
            self.log.warning(message, args)
        else:
            self.log.warning(message)
        
    def error(self, message, args = None):
        if args is not None:
            self.log.error(message, args)
        else:
            self.log.error(message)

class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find('/api/tsc_queue') == -1
