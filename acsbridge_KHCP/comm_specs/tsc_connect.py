from threading import Thread
from time import sleep

import collections
import traceback
import threading

from SEMI.e82_proxy import E82Proxy
# from SEMI.e88_proxy import E88Proxy
from SEMI.vid_v3 import AlarmTable

import time
from time import time as time2

import json
import os

states = []
port_states = {}





class TSCConnect(Thread):
    def __init__(self, logger, sio = None) -> None:
        self.stop = False
        self.e82 = NotImplemented
        self.e82h=None
        
        # self.e88 = None
        self.tsc_logger = logger
        
        self.sio = sio
        self.receive_queue = collections.deque()
        self.alarms = {}
        self.check_list=[]

    

    def _e82_callback(self, name, **kwargs):#TSC_AGV回報Event用的
        self.tsc_logger.debug('{}: {}'.format(name, kwargs))
        # if name=="TransferAbortCompleted":
        #     if kwargs["CommandID"] in self.check_list:
        #         self.tsc_logger.error("{} TransferAbortCompleted duplication".format(kwargs["CommandID"]))
        #         self.check_list.remove(kwargs["CommandID"])
        #     else:
        #         self.check_list.append(kwargs["CommandID"])
        #         self.tsc_logger.info("{} TransferAbortCompleted not duplication".format(kwargs["CommandID"]))
        #         send_to_e82_event_quent_dict={
        #             "event_name":name,
        #             "event_data":kwargs
        #         }
        #         e82_event_quent.put(send_to_e82_event_quent_dict)
        # else:
        #     send_to_e82_event_quent_dict={
        #         "event_name":name,
        #         "event_data":kwargs
        #     }
        #     e82_event_quent.put(send_to_e82_event_quent_dict)
        

            
            
        
        

    # def _e88_callback(self, name, **kwargs):#TSC_Erack回報Event用的
    #     self.tsc_logger.debug('{}: {}'.format(name, kwargs))

        
    
    def run(self):
        
        count_restart = 0 
       
        while not self.stop:
            try:
                self.e82 = E82Proxy("127.0.0.1", 5000, True, 0, 'e82', 'e82_communication', self._e82_callback)
                #self.e88 = E88Proxy(config.e88_ip, config.e88_port, True, 0, 'e88', 'e88_communication', self._e88_callback)
            
                self.tsc_logger.warning('ACS SEMI E88+E82 Starting')
                self.e82.enable()#啟動e82
                #self.e88.enable()#啟動e88
                self.tsc_logger.warning('ACS SEMI E88+E82 Started')
                tic = time2()
                timeout_counter = 0
                while not self.stop:
                    try:
                        toc = time2()
                        self.e82h=self.e82.h.communicationState.current
                        if self.e82.h.communicationState.current == 'COMMUNICATING':  #如果E82有連線
                            tic = time2()
                            self.stop=False
                        if toc-tic > 60:
                            self.e82.disable()
                            #self.e88.disable()
                            self.tsc_logger.warning('E82+E88 Disconnected')
                            break
                        time.sleep(1)
                    except KeyboardInterrupt:
                        self.tsc_logger.warning('ACS killed by user')
                        self.stop = True
                    except:
                        self.tsc_logger.error(traceback.format_exc())
                        pass
                else:
                    self.tsc_logger.warning('ACS SEMI E88+E82 Stopping')
                    self.e82.disable()
                    #self.e88.disable()
                    self.tsc_logger.warning('ACS SEMI E88+E82 Stopped')
            except:
                self.tsc_logger.error(traceback.format_exc())
                self.stop = True
                self.e82.disable()
                #self.e88.disable()
