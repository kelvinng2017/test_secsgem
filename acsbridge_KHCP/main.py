import logging
from handlers import Logger
from comm_specs.tsc_connect import TSCConnect
from logging.handlers import TimedRotatingFileHandler
import threading


if __name__ == "__main__":
    tsc = TSCConnect(Logger('tsc', 'tsc.log'))

    tsc_thread = threading.Thread(target=tsc.run)
    tsc_thread.setDaemon(False)  # 不設置為 daemon thread
    tsc_thread.start()
    
    try:
        tsc_thread.join()  # 無限等待，直到 thread 結束
    except KeyboardInterrupt:
        print("Received keyboard interrupt, shutting down...")
        tsc.stop = True
        tsc_thread.join()
        print("Application stopped.")