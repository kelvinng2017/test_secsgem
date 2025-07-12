# -*- coding: utf-8 -*-
#####################################################################
# gem_equipment.py
#
# (c) Copyright 2016, Benjamin Parzella. All rights reserved.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#####################################################################

import logging
import code

import secsgem

import collections

import traceback
from time import strftime
from time import localtime
from time import sleep
from datetime import datetime
#from communication_log_file_handler import CommunicationLogFileHandler

from . import E88_dataitems as DI

from global_variables import remotecmd_queue
from secsgem.common.fysom import Fysom

from datetime import datetime

import threading
from web_service_log import *
#from global_variables import eRacks

#from vehicle import VehicleMgr 
#chocp 2021/1/6


#chocp add
lock=threading.Lock()
def report_event(secsgem_h, ceid, dataset={}):
    lock.acquire()
    try:
        for key, value in dataset.items():
            #print(key, value)
            setattr(secsgem_h, key, value)
            
        secsgem_h.trigger_collection_events([ceid])
        #print('report_vehicle_event, ceid=%d'%ceid)
    except Exception as e:
        getattr(secsgem_h, "communicationLogger").warn('*** report event error ***')
        getattr(secsgem_h, "communicationLogger").warn('CEID:{}, DATASET:{}'.format(ceid, dataset))
        getattr(secsgem_h, "communicationLogger").warn(e)
        traceback.print_exc()
        pass
        
    lock.release()
    return

def alarm_set(secsgem_h, alid, alarm_set, dataset={}):
    lock.acquire()
    try:
        for key, value in dataset.items():
            #print(key, value)
            setattr(secsgem_h, key, value)
            
        if alarm_set:
            secsgem_h.set_alarm(alid,dataset.get("UnitID",""))
        else:
            secsgem_h.clear_alarm(alid)
        #print('alarm_set, alid=%d'%alid)
        sleep(0.05) #chocp 2021/11/24
    except Exception as e:
        getattr(secsgem_h, "communicationLogger").warn('*** report event error ***')
        getattr(secsgem_h, "communicationLogger").warn('ALID:{}, SET:{}, DATASET:{}'.format(alid, alarm_set, dataset))
        getattr(secsgem_h, "communicationLogger").warn(e)
        traceback.print_exc()
        pass
        
    lock.release()
    return

# Mike: 2020/07/29
def get_variables(secsgem_h, key):
    lock.acquire()
    try:

        value=''
        value=getattr(secsgem_h, key)
            
    except Exception as e:
        getattr(secsgem_h, "communicationLogger").warn('*** get variables error ***')
        getattr(secsgem_h, "communicationLogger").warn(e)
        traceback.print_exc()
        pass
        
    lock.release()
    return value

# Mike: 2020/07/29
def update_variables(secsgem_h, dataset={}):
    lock.acquire()
    try:

        for key, value in dataset.items():
            #print(key, value)
            setattr(secsgem_h, key, value)
            
    except Exception as e:
        getattr(secsgem_h, "logger").warn('*** update variables error ***')
        getattr(secsgem_h, "logger").warn(e)
        traceback.print_exc()
        pass
        
    lock.release()
    return



CarrierNum=5
CommandNum=5
PortNum=5
VehicleNum=5
TransNum=5

########################
#       SVID
########################
''' basic '''
#GEM_ALARMID=1
#GEM_ESTABLISH_COMMUNICATIONS_TIMEOUT=2
GEM_ALARMS_ENABLED=3
GEM_ALARMS_SET=4
GEM_CLOCK=5
GEM_CONTROL_STATE=6
GEM_EVENTS_ENABLED=7
GEM_LINK_STATE=8
GEM_MDLN=9
GEM_SOFTREV=10

GEM_SPOOL_COUNT_ACTUAL=23
GEM_SPOOL_COUNT_TOTAL=24
GEM_SPOOL_FULL_TIME=25
GEM_SPOOL_START_TIME=27
GEM_SPOOL_STATE=28
GEM_SPOOL_UNLOAD_SUPSTATE=29


''' SV '''
SV_SCState=73 # U2: init=1, paused=2, auto=3, pausing=4
SV_EqpName=61 # A
SV_ActiveCarriers=301 # CarrierInfo*n
SV_ActiveTransfers=52 # TransferCommand*n
SV_ActiveZones=53 # ZoneData*n
SV_EnhancedCarriers=51 # EnhancedCarrierInfo*n
SV_EnhancedTransfers=302 # EnhancedTranferCommand*n
SV_EnhancedActiveZones=107 # EnhancedZoneData*n


SV_UnitAlarmList=360 # UnitAlarmInfo*n
SV_UnitAlarmInfo=361 # ALCD, ALID, ALTX, ALED


''' tmp sv, for events, not available '''
SV_CarrierID=54 # A
SV_CarrierInfo=55 # CarrierID, CarrierLoc
SV_CarrierLoc=56 # A
SV_CarrierState=203 # U2: wait_in=1, transfer=2, wait_out=3, completed=4, alternate=5
SV_CarrierZoneName=605 # A
#SV_CurrentPortStates=81 # PortID, PortTransferState 2=Normal, 1=Abnormal
SV_CommandID=58 # A
SV_CommandInfo=59 # CommandID, Priority
#SV_CommandName=57 # A
SV_CommandType=608 # A
SV_Dest=60 # A
SV_EmptyCarrier=62 # U2: empty=0, not empty=1
SV_EnhancedCarrierInfo=611 # CarrierID, CarrierLoc, CarrierZoneName, InstallTime, CarrierState
SV_EnhancedTransferCommand=612 # TransferState, CommandInfo, TransferInfo
SV_EnhancedZoneData=613 # ZoneName, ZoneCapacity, ZoneSize, ZoneType
SV_ErrorID=63 # A
SV_HandoffType=64 # U2: man=1, auto=2
SV_IDReadStatus=67 # U2: succ=0, fail=1, duplicate=2, mismatch=3
SV_InstallTime=12 # A: TIME
#SV_PortID=80 # A
SV_PortType=64 # A: OP=output, BP=buffer, LP=loading
SV_Priority=65 # U2
SV_RecoveryOptions=68 # A: blank, RETRY, ABORT
SV_ResultCode=69 # U2: succ=0, cancel=1, abort=2
SV_Source=70 # A
SV_StockerCraneID=623 # A
SV_StockerUnitID=71 # A
SV_StockerUnitInfo=72 # StockerUnitID, StockerUnitState
SV_ShelfUnitInfo=77 # ShelfUnitID, ShelfUnitState
SV_ShelfUnitState=82 # U2: AVAIL=1, PROHIBIT=2, PICKUP(Manual)=3, RESERVED(Manual)=4, RESERVED(AUTO)=5
SV_ShelfUnitID=78 # ShelfUnitID, ShelfUnitState, CarrierID
SV_StockerUnitState=79 # U2: unknown=0, empty=1, occupied=2, error=3, manual=4
SV_TransferCommand=74 # CommandInfo, TransferInfo
SV_TransferInfo=75 # CarrierID, CarrierLoc, Dest
SV_TransferState=629 # U2: queued=1, transfering=2, paused=3, canceling=4, aborting=5
SV_ZoneCapacity=76 # U2
SV_ZoneData=172 # ZoneName, ZoneCapacity
SV_ZoneName=370 # A
SV_ZoneSize=175 # U2
SV_ZoneType=176 # U2: shelf=1, port=2, other=3
SV_ZoneState=635 # U2: UP=1, DOWN=2, other=0
SV_DeviceID=640


SV_ALTX=651
SV_ALSV=652
SV_AlarmsSetDescription=40
SV_UnitType=653
SV_UnitID=83
SV_Level=655
SV_SubCode=657

########################
#       CEID
########################
''' Control State '''
GEM_EQP_OFFLINE=1
GEM_CONTROL_STATE_LOCAL=2
GEM_CONTROL_STATE_REMOTE=3

''' SC state transition events '''
SCAutoCompleted=53
SCAutoInitiated=54
SCPauseCompleted=55
SCPaused=56
SCPauseInitiated=57

''' transfer command state transition events '''
TransferAbortCompleted=101
TransferAbortFailed=102
TransferAbortInitiated=103
TransferCancelCompleted=104
TransferCancelFailed=105
TransferCancelInitiated=106
TransferCompleted=107
TransferInitiated=108
TransferPaused=109
TransferResumed=110

''' stocker carrier state transition events '''
CarrierInstallCompleted=151
CarrierRemoveCompleted=152
CarrierRemoved=153
CarrierResumed=154
CarrierStored=155
CarrierStoredAlt=156
CarrierTransferring=157
CarrierWaitIn=158
CarrierWaitOut=159
ZoneCapacityChange=160

''' stocker crane state transition events '''
CraneActive=201
CraneIdle=202

''' port transfer state transition events'''
#PortInService=301
#PortOutOfService=302

''' non-transition events '''
CarrierIDRead=251
CarrierLocateCompleted=252
IDReadError=253
OperatorInitiatedAction=254

DeviceOnline=301
DeviceOffline=302

secsgem.gem.equipmenthandler.GEM_MDLN=GEM_MDLN
secsgem.gem.equipmenthandler.GEM_SOFTREV=GEM_SOFTREV
secsgem.gem.equipmenthandler.GEM_CLOCK=GEM_CLOCK
secsgem.gem.equipmenthandler.GEM_ALARMS_ENABLED=GEM_ALARMS_ENABLED
secsgem.gem.equipmenthandler.GEM_ALARMS_SET=GEM_ALARMS_SET
secsgem.gem.equipmenthandler.GEM_CONTROL_STATE=GEM_CONTROL_STATE
secsgem.gem.equipmenthandler.GEM_LINK_STATE=GEM_LINK_STATE
secsgem.gem.equipmenthandler.GEM_EVENTS_ENABLED=GEM_EVENTS_ENABLED
secsgem.gem.equipmenthandler.GEM_EQP_OFFLINE=GEM_EQP_OFFLINE
secsgem.gem.equipmenthandler.GEM_CONTROL_STATE_LOCAL=GEM_CONTROL_STATE_LOCAL
secsgem.gem.equipmenthandler.GEM_CONTROL_STATE_REMOTE=GEM_CONTROL_STATE_REMOTE
secsgem.gem.equipmenthandler.GEM_SPOOL_COUNT_ACTUAL=GEM_SPOOL_COUNT_ACTUAL
secsgem.gem.equipmenthandler.GEM_SPOOL_COUNT_TOTAL=GEM_SPOOL_COUNT_TOTAL
secsgem.gem.equipmenthandler.GEM_SPOOL_FULL_TIME=GEM_SPOOL_FULL_TIME
secsgem.gem.equipmenthandler.GEM_SPOOL_START_TIME=GEM_SPOOL_START_TIME
secsgem.gem.equipmenthandler.GEM_SPOOL_STATE=GEM_SPOOL_STATE
secsgem.gem.equipmenthandler.GEM_SPOOL_UNLOAD_SUPSTATE=GEM_SPOOL_UNLOAD_SUPSTATE


class Carrier():
    def __init__(self, secsgem_h, CARRIERID):
        self.h=secsgem_h
        self.CarrierID=CARRIERID
        self.CarrierIDRead=''
        self.CarrierLoc=''
        self.CarrierState=0 # U2: wait_in=1, transfer=2, wait_out=3, completed=4, alternate=5
        self.CarrierZoneName=''
        self.CarrierDeviceName=''
        self.CommandID=''
        self.Dest=''
        self.HandoffType=1 # U2: man=1, auto=2
        self.IDReadStatus=0 # U2: succ=0, fail=1, duplicate=2, mismatch=3
        self.InstallTime=''
        self.PortType='' # A: OP=output, BP=buffer, LP=loading

        #####################################
        #   control state 
        #####################################
        ''' CarrierState '''
        self.State=Fysom({
            'initial': "none",
            'events': [
                {'name': 'wait_in', 'src': ['none', 'WAIT_OUT', 'WAIT_OUT_2'], 'dst': 'WAIT_IN'},  # 1, 13
                {'name': 'transfer', 'src': ['WAIT_IN', 'COMPLETED'], 'dst': 'TRANSFERING'},  # 2, 4
                {'name': 'store', 'src': 'TRANSFERING', 'dst': 'COMPLETED'},  # 3
                {'name': 'wait_out', 'src': ['none', 'TRANSFERING', 'WAIT_OUT_2'], 'dst': 'WAIT_OUT'},  # 5, 6, 14
                {'name': 'wait_out', 'src': 'WAIT_OUT', 'dst': 'WAIT_OUT_2'},  # 6
                {'name': 'remove', 'src': ['WAIT_OUT', 'WAIT_OUT_2'], 'dst': 'none'},  # 7
                {'name': 'alternated', 'src': 'TRANSFERING', 'dst': 'ALTERNATE'},  # 8
                {'name': 'resume', 'src': 'ALTERNATE', 'dst': 'TRANSFERING'},  # 9
                {'name': 'add_carrier', 'src': 'none', 'dst': 'COMPLETED'},  # 10
                {'name': 'mod_carrier', 'src': 'COMPLETED', 'dst': 'COMPLETED'},  #
                {'name': 'kill_carrier', 'src': ['WAIT_IN', 'TRANSFERING', 'WAIT_OUT', 'WAIT_OUT_2', 'COMPLETED', 'ALTERNATE'], 'dst': 'none'},  # 11
            ],
            'callbacks': {
                'onWAIT_IN': self._on_carrier_state_WAIT_IN,  # 
                'onTRANSFERING': self._on_carrier_state_TRANSFERING,  # 
                'onWAIT_OUT': self._on_carrier_state_WAIT_OUT,  # 
                'onWAIT_OUT_2': self._on_carrier_state_WAIT_OUT,  # 
                'onCOMPLETED': self._on_carrier_state_COMPLETED,  # 
                'onALTERNATE': self._on_carrier_state_ALTERNATE,  # 
                'onbeforewait_in': self._on_carrier_state_wait_in,  # 1, send collection event (CarrierWaitIn)
                'onbeforetransfer': self._on_carrier_state_transfer,  # 2, 4, send collection event (CarrierTransferring)
                'onbeforestore': self._on_carrier_state_store,  # 3, send collection event (CarrierStored)
                'onbeforewait_out': self._on_carrier_state_wait_out,  # 5, 6, send collection event (CarrierWaitOut)
                'onbeforeremove': self._on_carrier_state_remove,  # 7, send collection event (CarrierRemoved)
                'onbeforealternated': self._on_carrier_state_alternated,  # 8, send collection event (CarrierStoredAlt)
                'onbeforeresume': self._on_carrier_state_resume,  # 9, send collection event (CarrierResumed)
                'onbeforeadd_carrier': self._on_carrier_state_add_carrier,  # 10, send collection event (CarrierInstallCompleted)
                'onbeforemod_carrier': self._on_carrier_state_mod_carrier,  # send collection event (CarrierInstallCompleted)
                'onbeforekill_carrier': self._on_carrier_state_kill_carrier,  # 11, send collection event (CarrierRemoveCompleted)
            },
            'autoforward': [
                # {'src': '', 'dst': ''},  # 
            ]
        })

    #####################################
    #       State Machine Callback
    #####################################
    def _on_carrier_state_WAIT_IN(self, _):  # 
        self.CarrierState=1

    def _on_carrier_state_TRANSFERING(self, _):  # 
        self.CarrierState=2

    def _on_carrier_state_WAIT_OUT(self, _):  # 
        self.CarrierState=3

    def _on_carrier_state_COMPLETED(self, _):  # 
        self.CarrierState=6

    def _on_carrier_state_ALTERNATE(self, _):  # 
        self.CarrierState=5

    

    def _on_carrier_state_wait_in(self, _):  # 1, send collection event (CarrierWaitIn)
        
        dataset={}
        dataset['CarrierID']=self.CarrierIDRead
        dataset['CarrierLoc']=self.CarrierLoc
        dataset['CarrierZoneName']=self.CarrierZoneName
        e88equipmen_logger.warning("CarrierWaitIn1: {}".format(dataset))
        report_event(self.h, CarrierWaitIn, dataset)

    def _on_carrier_state_transfer(self, _):  # 2, 4, send collection event (CarrierTransferring)
        # e88equipmen_logger.warning("CarrierTransferring")
        dataset={}
        dataset['CarrierID']=self.CarrierID
        dataset['CarrierLoc']=self.CarrierLoc
        dataset['CarrierZoneName']=self.CarrierZoneName
        e88equipmen_logger.warning("CarrierTransferring1: {}".format(dataset))
        report_event(self.h, CarrierTransferring, dataset)

    def _on_carrier_state_store(self, _):  # 3, send collection event (CarrierStored)
        # e88equipmen_logger.warning("CarrierInstallComplete1")
        dataset={}
        dataset['CarrierID']=self.CarrierID
        dataset['CarrierLoc']=self.CarrierLoc
        dataset['CarrierZoneName']=self.CarrierZoneName
        # dataset['HandoffType']=self.HandoffType
        # dataset['PortType']=self.PortType
        e88equipmen_logger.warning("CarrierInstallComplete1: {}".format(dataset))
        report_event(self.h, CarrierInstallCompleted, dataset)

    

    def _on_carrier_state_wait_out(self, _):  # 5, 6, send collection event (CarrierWaitOut)
        dataset={}
        dataset['CarrierID']=self.CarrierID
        dataset['CarrierLoc']=self.CarrierLoc
        dataset['CarrierZoneName']=self.CarrierZoneName
        dataset['PortType']=self.PortType
        report_event(self.h, CarrierWaitOut, dataset)
        if self.IDReadStatus != 0:
            dataset={}
            dataset['CarrierID']=self.CarrierID
            dataset['CarrierLoc']=self.CarrierLoc
            dataset['IDReadStatus']=IDREADSTATUS
            report_event(self.h, IDReadError, dataset)

    def _on_carrier_state_remove(self, _):  # 7, send collection event (CarrierRemoved)
        dataset={}
        dataset['CarrierID']=self.CarrierID
        dataset['CarrierLoc']=self.CarrierLoc
        dataset['CarrierZoneName']=self.CarrierZoneName
        dataset['HandoffType']=self.HandoffType
        dataset['PortType']=self.PortType
        e88equipmen_logger.warning("CarrierRemoved: {}".format(dataset))
        report_event(self.h, CarrierRemoved, dataset)

    def _on_carrier_state_alternated(self, _):  # 8, send collection event (CarrierStoredAlt)
        dataset={}
        dataset['CommandID']=self.CommandID
        dataset['CarrierID']=self.CarrierID
        dataset['CarrierLoc']=self.CarrierLoc
        dataset['CarrierZoneName']=self.CarrierZoneName
        dataset['Dest']=self.Dest
        report_event(self.h, CarrierStoredAlt, dataset)

    def _on_carrier_state_resume(self, _):  # 9, send collection event (CarrierResumed)
        dataset={}
        dataset['CommandID']=self.CommandID
        dataset['CarrierID']=self.CarrierID
        dataset['CarrierLoc']=self.CarrierLoc
        dataset['CarrierZoneName']=self.CarrierZoneName
        dataset['Dest']=self.Dest
        report_event(self.h, CarrierResumed, dataset)

    def _on_carrier_state_add_carrier(self, _):  # 10, send collection event (CarrierInstallCompleted)
        # e88equipmen_logger.warning("CarrierInstallComplete2")
        dataset={}
        dataset['CarrierID']=self.CarrierID
        dataset['CarrierLoc']=self.CarrierLoc
        dataset['CarrierZoneName']=self.CarrierZoneName
        dataset['HandoffType']=self.HandoffType
        dataset['PortType']=self.PortType
        e88equipmen_logger.warning("CarrierInstallComplete2: {}".format(dataset))
        report_event(self.h, CarrierInstallCompleted, dataset)

    def _on_carrier_state_mod_carrier(self, _):  # send collection event (CarrierInstallCompleted)
        # e88equipmen_logger.warning("CarrierInstallComplete3")
        dataset={}
        dataset['CarrierID']=self.CarrierID
        dataset['CarrierLoc']=self.CarrierLoc
        dataset['CarrierZoneName']=self.CarrierZoneName
        dataset['HandoffType']=self.HandoffType
        dataset['PortType']=self.PortType
        e88equipmen_logger.warning("CarrierInstallComplete3: {}".format(dataset))
        report_event(self.h, CarrierInstallCompleted, dataset)

    def _on_carrier_state_kill_carrier(self, _):  # 11, send collection event (CarrierRemoveCompleted)
        dataset={}
        dataset['CarrierID']=self.CarrierID
        dataset['CarrierLoc']=self.CarrierLoc
        dataset['CarrierZoneName']=self.CarrierZoneName
        dataset['HandoffType']=self.HandoffType
        dataset['PortType']=self.PortType
        e88equipmen_logger.warning("CarrierRemoveCompleted: {}".format(dataset))
        report_event(self.h, CarrierRemoveCompleted, dataset)

    #####################################
    #       Normal Function Define
    #####################################

    def locate(self):
        dataset={}
        dataset['CarrierID']=self.CarrierID
        dataset['CarrierLoc']=self.CarrierLoc
        dataset['CarrierZoneName']=self.CarrierZoneName
        report_event(self.h, CarrierLocateCompleted, dataset)
    
    def id_read(self, CARRIERID, IDREADSTATUS=0):
        self.CarrierID=CARRIERID
        dataset={}
        dataset['CarrierID']=self.CarrierID
        dataset['CarrierLoc']=self.CarrierLoc
        dataset['IDReadStatus']=IDREADSTATUS
        report_event(self.h, CarrierIDRead, dataset)

class TransferCommand():
    def __init__(self, secsgem_h, COMMANDID):
        self.h=secsgem_h
        self.CommandID=COMMANDID
        self.CarrierID=''
        self.CarrierLoc=''
        self.CarrierZoneName=''
        self.Priority=''
        self.ResultCode=0 # U2: succ=0, cancel=1, abort=2
        self.Dest=''
        self.TransferState=0 # U2: queued=1, transfering=2, paused=3, canceling=4, aborting=5

        #####################################
        #   control state 
        #####################################
        ''' TransferState '''
        self.State=Fysom({
            'initial': "none",
            'events': [
                {'name': 'queue', 'src': 'none', 'dst': 'QUEUED'},  # 0
                {'name': 'transfer', 'src': ['QUEUED', 'CANCELLING'], 'dst': 'TRANSFERING'},  # 1, 10
                {'name': 'cancel', 'src': 'QUEUED', 'dst': 'CANCELLING'},  # 2
                {'name': 'cancel_completed', 'src': 'CANCELLING', 'dst': 'COMPLETED'},  # 3
                {'name': 'pause', 'src': 'TRANSFERING', 'dst': 'PAUSED'},  # 4
                {'name': 'resume', 'src': 'PAUSED', 'dst': 'TRANSFERING'},  # 5
                {'name': 'complete', 'src': ['COMPLETED', 'TRANSFERING', 'PAUSED'], 'dst': 'none'},  # 6
                {'name': 'abort', 'src': ['TRANSFERING', 'PAUSED'], 'dst': 'ABORTING'},  # 7
                {'name': 'abort_completed', 'src': 'ABORTING', 'dst': 'COMPLETED'},  # 8
                {'name': 'abort_failed', 'src': 'ABORTING', 'dst': 'ACTIVE'},  # 9
                {'name': 'cancel_failed', 'src': 'CANCELLING', 'dst': 'QUEUED'},  # 11
                {'name': 'history_tranfering', 'src': 'ACTIVE', 'dst': 'TRANSFERING'},  # 9-1
                {'name': 'history_paused', 'src': 'ACTIVE', 'dst': 'PAUSED'},  # 9-2
            ],
            'callbacks': {
                'onQUEUED': self._on_transfer_state_QUEUED,  # 
                'onTRANSFERING': self._on_transfer_state_TRANSFERING,  # 
                'onPAUSED': self._on_transfer_state_PAUSED,  # 
                'onCANCELLING': self._on_transfer_state_CANCELLING,  # 
                'onABORTING': self._on_transfer_state_ABORTING,  # 
                'onACTIVE': self._on_transfer_state_ACTIVE,  # 
                'onCOMPLETED': self._on_transfer_state_COMPLETED,  # 
                'onbeforetransfer': self._on_transfer_state_transfer,  # 1, 10, send collection event (TransferInitiated)
                'onbeforecancel': self._on_transfer_state_cancel,  # 2, send collection event (TransferCancelInitiated)
                'onbeforecancel_completed': self._on_transfer_state_cancel_completed,  # 3, send collection event (TransferCancelCompleted)
                'onbeforepause': self._on_transfer_state_pause,  # 4, send collection event (TransferPaused)
                'onbeforeresume': self._on_transfer_state_resume,  # 5, send collection event (TransferResumed)
                'onbeforecomplete': self._on_transfer_state_complete,  # 6, send collection event (TransferCompleted)
                'onbeforeabort': self._on_transfer_state_abort,  # 7, send collection event (TransferAbortInitiated)
                'onbeforeabort_completed': self._on_transfer_state_abort_completed,  # 8, send collection event (TransferAbortCompleted)
                'onbeforeabort_failed': self._on_transfer_state_abort_failed,  # 9, send collection event (TransferAbortFailed)
                'onbeforecancel_failed': self._on_transfer_state_cancel_failed,  # 11, send collection event (TransferCancelFailed)
            },
            'autoforward': [
            ]
        })

    #####################################
    #       State Machine Callback
    #####################################
    def _on_transfer_state_QUEUED(self, _):  # 
        self.TransferState=1

    def _on_transfer_state_TRANSFERING(self, _):  # 
        self.TransferState=2

    def _on_transfer_state_PAUSED(self, _):  # 
        self.TransferState=3

    def _on_transfer_state_CANCELLING(self, _):  # 
        self.TransferState=4

    def _on_transfer_state_ABORTING(self, _):  # 
        self.TransferState=5

    def _on_transfer_state_ACTIVE(self, _):  # 
        if self.history == 'TRANSFER':
            self.State.history_tranfering()
        else:
            self.State.history_paused()

    def _on_transfer_state_COMPLETED(self, _):  # 
        self.State.complete()

    def _on_transfer_state_transfer(self, _):  # 1, 10, send collection event (TransferInitiated)
        self.history='TRANSFER'
        dataset={}
        dataset['CommandID']=self.CommandID
        dataset['CarrierID']=self.CarrierID
        dataset['CarrierLoc']=self.CarrierLoc
        dataset['CarrierZoneName']=self.CarrierZoneName
        dataset['Dest']=self.Dest
        report_event(self.h, TransferInitiated, dataset)

    def _on_transfer_state_cancel(self, _):  # 2, send collection event (TransferCancelInitiated)
        dataset={}
        dataset['CommandID']=self.CommandID
        dataset['CarrierID']=self.CarrierID
        dataset['CarrierLoc']=self.CarrierLoc
        dataset['CarrierZoneName']=self.CarrierZoneName
        report_event(self.h, TransferCancelInitiated, dataset)

    def _on_transfer_state_cancel_completed(self, _):  # 3, send collection event (TransferCancelCompleted)
        self.ResultCode=1
        dataset={}
        dataset['CommandID']=self.CommandID
        dataset['CarrierID']=self.CarrierID
        dataset['CarrierLoc']=self.CarrierLoc
        dataset['CarrierZoneName']=self.CarrierZoneName
        report_event(self.h, TransferCancelCompleted, dataset)

    def _on_transfer_state_pause(self, _):  # 4, send collection event (TransferPaused)
        self.history='PAUSED'
        dataset={}
        dataset['CommandID']=self.CommandID
        dataset['CarrierID']=self.CarrierID
        dataset['CarrierLoc']=self.CarrierLoc
        dataset['CarrierZoneName']=self.CarrierZoneName
        report_event(self.h, TransferPaused, dataset)

    def _on_transfer_state_resume(self, _):  # 5, send collection event (TransferResumed)
        self.history='TRANSFER'
        dataset={}
        dataset['CommandID']=self.CommandID
        dataset['CarrierID']=self.CarrierID
        dataset['CarrierLoc']=self.CarrierLoc
        dataset['CarrierZoneName']=self.CarrierZoneName
        report_event(self.h, TransferResumed, dataset)

    def _on_transfer_state_complete(self, _):  # 6, send collection event (TransferCompleted)
        dataset={}
        dataset['CommandID']=self.CommandID
        dataset['CarrierID']=self.CarrierID
        dataset['CarrierLoc']=self.CarrierLoc
        dataset['ResultCode']=self.ResultCode
        dataset['CarrierZoneName']=self.CarrierZoneName
        report_event(self.h, TransferCompleted, dataset)

    def _on_transfer_state_abort(self, _):   # 7, send collection event (TransferAbortInitiated)
        dataset={}
        dataset['CommandID']=self.CommandID
        dataset['CarrierID']=self.CarrierID
        dataset['CarrierLoc']=self.CarrierLoc
        dataset['CarrierZoneName']=self.CarrierZoneName
        report_event(self.h, TransferAbortInitiated, dataset)

    def _on_transfer_state_abort_completed(self, _):  # 8, send collection event (TransferAbortCompleted)
        self.ResultCode=2
        dataset={}
        dataset['CommandID']=self.CommandID
        dataset['CarrierID']=self.CarrierID
        dataset['CarrierLoc']=self.CarrierLoc
        dataset['CarrierZoneName']=self.CarrierZoneName
        report_event(self.h, TransferAbortCompleted, dataset)

    def _on_transfer_state_abort_failed(self, _):  # 9, send collection event (TransferAbortFailed)
        dataset={}
        dataset['CommandID']=self.CommandID
        dataset['CarrierID']=self.CarrierID
        dataset['CarrierLoc']=self.CarrierLoc
        dataset['CarrierZoneName']=self.CarrierZoneName
        report_event(self.h, TransferAbortFailed, dataset)

    def _on_transfer_state_cancel_failed(self, _):  # 11, send collection event (TransferCancelFailed)
        dataset={}
        dataset['CommandID']=self.CommandID
        dataset['CarrierID']=self.CarrierID
        dataset['CarrierLoc']=self.CarrierLoc
        dataset['CarrierZoneName']=self.CarrierZoneName
        report_event(self.h, TransferCancelFailed, dataset)

class Zone():
    def __init__(self, secsgem_h, ZONENAME):
        self.h=secsgem_h
        self.ZoneName=ZONENAME
        self.ZoneSize=0
        self.ZoneCapacity=0
        self.ZoneType=0 # U2: shelf=1, port=2, other=3
        self.ZoneState=0 # U2: UP=1, DOWN=2, OTHER=0
        self.WaterLevel='unknown'
        self.ZoneUnitState={}
        self.ShelfState={} # U2: AVAIL=1, PROHIBIT=2, PICKUP(Manual)=3, RESERVED(Manual)=4, RESERVED(AUTO)=5
        self.StockerUnit={}
        self.lock=threading.Lock()

    def capacity_decrease(self):
        self.lock.acquire()
        self.ZoneCapacity -= 1
        dataset={}
        dataset['ZoneData']={'ZoneName':self.ZoneName, 'ZoneCapacity':self.ZoneCapacity}
        report_event(self.h, ZoneCapacityChange, dataset)
        self.lock.release()

    def capacity_increase(self):
        self.lock.acquire()
        self.ZoneCapacity += 1
        dataset={}
        dataset['ZoneData']={'ZoneName':self.ZoneName, 'ZoneCapacity':self.ZoneCapacity}
        report_event(self.h, ZoneCapacityChange, dataset)
        self.lock.release()

    def zone_capacity_change(self, CAPACITY):
        self.lock.acquire()
        self.ZoneCapacity=CAPACITY
        dataset={}
        dataset['ZoneData']={'ZoneName':self.ZoneName, 'ZoneCapacity':self.ZoneCapacity}
        report_event(self.h, ZoneCapacityChange, dataset)
        self.lock.release()

    def set_shelf_state(self, shelf_id, state):
        """Set shelf state for a specific shelf
        
        :param shelf_id: Shelf identifier
        :type shelf_id: str
        :param state: Shelf state value (1: AVAIL, 2: PROHIBIT, 3: PICKUP(Manual), 4: RESERVED(Manual), 5: RESERVED(AUTO))
        :type state: int
        """
        if state in [1, 2, 3, 4, 5]:
            self.ShelfState[shelf_id] = state
        else:
            raise ValueError("Invalid shelf state. Must be 1-5 (AVAIL, PROHIBIT, PICKUP(Manual), RESERVED(Manual), RESERVED(AUTO))")

    def get_shelf_state(self, shelf_id):
        """Get shelf state for a specific shelf
        
        :param shelf_id: Shelf identifier
        :type shelf_id: str
        :return: Shelf state value, default 1 (AVAIL) if not set
        :rtype: int
        """
        return self.ShelfState.get(shelf_id, 1)

    def zone_alarm_set(self, alid, is_set, dataset={}): # Mike: 2021/07/12
        dataset['ZoneName']=self.ZoneName
        ALSV=[]
        for key, value in dataset.items():
            ALSV.append(str(key)+':'+str(value))
        dataset['ALSV']=', '.join(ALSV)
        dataset['ALTX']=AlarmTable[alid]['text']
        alarm_set(self.h, alid, is_set, dataset)


class Carriers():
    def __init__(self, secsgem_h):
        self.Data={}
        self.h=secsgem_h

    def add(self, CARRIERID):
        if CARRIERID not in self.Data:
            self.Data[CARRIERID]=Carrier(self.h, CARRIERID)
            self.Data[CARRIERID].InstallTime=datetime.now().strftime('%Y%m%d%H%M%S%f')[:16]
            return True
        return False

    def set(self, CARRIERID, datasets):
        if CARRIERID not in self.Data:
            self.add(CARRIERID)
        for key, value in datasets.items():
            setattr(self.Data[CARRIERID], key, value)

    def mod(self, CARRIERID, NEWCARRIERID):
        if CARRIERID in self.Data and NEWCARRIERID not in self.Data:
            self.Data[NEWCARRIERID]=self.Data[CARRIERID]
            del self.Data[CARRIERID]
            return True
        return False

    def delete(self, CARRIERID):
        if CARRIERID in self.Data:
            del self.Data[CARRIERID]
            return True
        return False

class Transfers():
    def __init__(self,secsgem_h):
        self.Data={}
        self.h=secsgem_h

    def add(self, COMMANDID):
        if COMMANDID not in self.Data:
            self.Data[COMMANDID]=TransferCommand(self.h, COMMANDID)
            return True
        return False

    def set(self, COMMANDID, datasets):
        if COMMANDID not in self.Data:
            self.add(COMMANDID)
        for key, value in datasets.items():
            setattr(self.Data[COMMANDID], key, value)
            
    def mod(self, COMMANDID, NEWCOMMANDID):
        if COMMANDID in self.Data and NEWCOMMANDID not in self.Data:
            self.Data[NEWCOMMANDID]=self.Data[COMMANDID]
            del self.Data[COMMANDID]
            return True
        return False

    def delete(self, COMMANDID):
        if COMMANDID in self.Data:
            del self.Data[COMMANDID]
            return True
        return False

class Zones():
    def __init__(self, secsgem_h):
        self.Data={}
        self.ZoneMap={}
        self.h=secsgem_h

    def add(self, ZONENAME):
        if ZONENAME not in self.Data:
            self.Data[ZONENAME]=Zone(self.h, ZONENAME)
            return True
        return False

    def set(self, ZONENAME, datasets):
        if ZONENAME not in self.Data:
            self.add(ZONENAME)
        for key, value in datasets.items():
            setattr(self.Data[ZONENAME], key, value)

    def mod(self, ZONENAME, NEWZONENAME):
        if ZONENAME in self.Data and NEWZONENAME not in self.Data:
            self.Data[NEWZONENAME]=self.Data[ZONENAME]
            del self.Data[ZONENAME]
            return True
        return False

    def delete(self, ZONENAME):
        if ZONENAME in self.Data:
            del self.Data[ZONENAME]
            return True
        return False


GenIndex=0
GenLock=threading.Lock()
def FailureIDGEN(fail_loc, dup_carrier=None): # zhangpeng 2025-02-25 Adjust the format for failure ID
    global GenIndex, GenLock
    GenLock.acquire()
    if fail_loc and dup_carrier: # Duplicate
        ret='UNKNOWNDUP-{}-{}-{:04d}'.format(dup_carrier, fail_loc, GenIndex) # e.g. UNKNOWNDUP-CARRIER456-E1P1-0000
    elif fail_loc: # ReadFail
        ret='UNKNOWN-{}-{:04d}'.format(fail_loc, GenIndex) # e.g. UNKNOWN-E1P1-0000
    else:
        ret='FAILURE{:04d}'.format(GenIndex)
    GenIndex=(GenIndex+1) % 10000
    GenLock.release()
    return ret


AlarmTable={
    20001: {'report':[SV_ALTX, SV_ALSV, SV_UnitType, SV_UnitID, SV_Level, SV_SubCode],'text':'SC internal error, code exception'},
    20002: {'report':[SV_ALTX, SV_ALSV, SV_UnitType, SV_UnitID, SV_Level, SV_SubCode, SV_ZoneName, SV_CarrierLoc],'text':'Base read rfid error'},
    20003: {'report':[SV_ALTX, SV_ALSV, SV_UnitType, SV_UnitID, SV_Level, SV_SubCode, SV_ZoneName, SV_CarrierLoc],'text':'E84 error'},
    20004: {'report':[SV_ALTX, SV_ALSV, SV_UnitType, SV_UnitID, SV_Level, SV_SubCode, SV_ZoneName],'text':'Off line, retry communication with rack timeout'},
    20005: {'report':[SV_ALTX, SV_ALSV, SV_UnitType, SV_UnitID, SV_Level, SV_SubCode, SV_ZoneName, SV_CarrierLoc],'text':'Port in manual mode'},

    20051: {'report':[SV_ALTX, SV_ALSV, SV_UnitType, SV_UnitID, SV_Level, SV_SubCode, SV_ZoneName], 'text':'Erack off line'},
    20052: {'report':[SV_ALTX, SV_ALSV, SV_UnitType, SV_UnitID, SV_Level, SV_SubCode, SV_ZoneName], 'text':'Erack water level high'},
    20053: {'report':[SV_ALTX, SV_ALSV, SV_UnitType, SV_UnitID, SV_Level, SV_SubCode, SV_ZoneName], 'text':'Erack water level full'},
    20054: {'report':[SV_ALTX, SV_ALSV, SV_UnitType, SV_UnitID, SV_Level, SV_SubCode, SV_ZoneName], 'text':'Erack water level low'},
    20055: {'report':[SV_ALTX, SV_ALSV, SV_UnitType, SV_UnitID, SV_Level, SV_SubCode, SV_ZoneName], 'text':'Erack water level empty'},

    30001: {'report':[SV_ALTX, SV_ALSV, SV_UnitType, SV_UnitID, SV_Level, SV_SubCode, SV_ZoneName], 'text':'Erack Rack connect fail'},
    30002: {'report':[SV_ALTX, SV_ALSV, SV_UnitType, SV_UnitID, SV_Level, SV_SubCode, SV_ZoneName], 'text':'receive null string from socket'},
    30003: {'report':[SV_ALTX, SV_ALSV, SV_UnitType, SV_UnitID, SV_Level, SV_SubCode, SV_ZoneName], 'text':'linking timeout'},
    30004: {'report':[SV_ALTX, SV_ALSV, SV_UnitType, SV_UnitID, SV_Level, SV_SubCode, SV_ZoneName], 'text':'receive format error from socket'},
    30005: {'report':[SV_ALTX, SV_ALSV, SV_UnitType, SV_UnitID, SV_Level, SV_SubCode, SV_ZoneName], 'text':'Erack syntax error'},
}


class E88MirleEquipment(secsgem.GemEquipmentHandler):
    def __init__(self, address, port, active, session_id, name='Gyro Agvc', log_name="E88_hsms_communication", mdln='STKC_v1.1', T3=45, T5=10, T6=5, T7=10, T8=5, custom_connection_handler=None, initial_control_state="ONLINE", initial_online_control_state="REMOTE"):

        SOFTREV='' # Mike: 2021/11/12
        try:
            f=open('version.txt','r')
            SOFTREV=f.readline()
            f.close()
        except:
            pass

        secsgem.GemEquipmentHandler.__init__(self, address, port, active, session_id, name, custom_connection_handler, initial_control_state, initial_online_control_state)
        buddha = u'''
                            _oo0oo_
                            o8888888o
                            88" . "88
                            (| -_- |)
                            0\\  =  /0
                            ___/`---'\\___
                        .' \\\\|     |// '.
                        / \\\\|||  :  |||// \\
                        / _||||| -:- |||||_ \\
                    |   | \\\\\\  -  /// |   |
                    | \\_|  ''\\---/''  |_/ |
                    \\  .-\\__  '-'  ___/-. /
                    ___'. .'  /--.--\\  `. .'___
                ."" '<  `.___\\_<|>_/___.' >' "".
                | | :  `- \\`.;`\\ _ /`;.`/ - ` : | |
                \\  \\ `_.   \\_ __\\ /__ _/   .-` /  /
            =====`-.____`.___ \\_____/___.-`___.-'=====
                            `=---='

                     not BUG
        '''
        print(buddha)
        self.connection.T3=T3
        self.connection.T5=T5
        self.connection.T6=T6
        self.connection.T7=T7
        self.connection.T8=T8

        self.MDLN=mdln
        self.SOFTREV=SOFTREV
        self.EqpName=name
        self.communicationLogger=logging.getLogger(log_name)
        self.communicationLogger.setLevel(logging.DEBUG)
        self.logger=self.communicationLogger
        self.connection.logger=self.communicationLogger

        self._spool_enable=0

        self.rcmd_auto_reply=False

        self.ERROR_MSG=''

        self.active_alarms=[] # Mike: 2021/05/17

        self.ERROR_MSG=''

        self.active_alarms=[] # Mike: 2021/05/17
        self.UnitAlarmInfo={}
        self.UnitAlarmList={}


        self.failure_map={}

        self.remote_commands_callback=None

        ### example: ActiveCarriers={
        ###              "123456": {"CarrierID": "123456", "CarrierLoc": "aaaa"},
        ###              "654321": {"CarrierID": "654321", "CarrierLoc": "bbbb"}
        ###          }
        self.ActiveCarriers={} # CarrierInfo*n

        ### example: self.ActiveTransfers={
        ###              "cmd1": {
        ###                  "CommandInfo": {"CommandID":"cmd1", "Priority":1},
        ###                  "TransferInfo": {"CarrierID": "123456", "CarrierLoc": "aaaa", "Dest": "LP1"},
        ###              "cmd2": {
        ###                  "CommandInfo": {"CommandID":"cmd2", "Priority":2},
        ###                  "TransferInfo": {"CarrierID": "111111", "CarrierLoc": "cccc", "Dest": "STORAGE"}}
        ###          }
        self.ActiveTransfers={} # TransferCommand*n

        ### example: ActiveZones={
        ###              "STORAGE": {"ZoneName": "STORAGE", "ZoneCapacity": 30},
        ###              "STORAGE2": {"ZoneName": "STORAGE2", "ZoneCapacity": 50}
        ###          }
        self.ActiveZones={} # ZoneData*n

        ### example: EnhancedCarriers={
        ###              "123456": {"CarrierID": "123456", "CarrierLoc": "aaaa", "CarrierZoneName": "STORAGE", "InstallTime": "2021042210132233", "CarrierState": 1},
        ###              "654321": {"CarrierID": "654321", "CarrierLoc": "bbbb", "CarrierZoneName": "STORAGE", "InstallTime": "2021042210151842", "CarrierState": 2}
        ###          }
        self.EnhancedCarriers={} # EnhancedCarrierInfo*n

        ### example: EnhancedTransfers={
        ###              "cmd1": {
        ###                  "TransferState": ,
        ###                  "CommandInfo": {"CommandID":"cmd1", "Priority":1},
        ###                  "TransferInfo": {"CarrierID": "123456", "CarrierLoc": "aaaa", "Dest": "LP1"}},
        ###              "cmd2": {
        ###                  "TransferState": ,
        ###                  "CommandInfo": {"CommandID":"cmd2", "Priority":2},
        ###                  "TransferInfo": {"CarrierID": "111111", "CarrierLoc": "cccc", "Dest": "STORAGE"}}
        ###          }
        self.EnhancedTransfers={} # EnhancedTranferCommand*n

        ### example: EnhancedActiveZones={
        ###              "STORAGE": {"ZoneName": "STORAGE", "ZoneCapacity": 30, "ZoneSize": 80, "ZoneType": 1},
        ###              "STORAGE2": {"ZoneName": "STORAGE2", "ZoneCapacity": 50, "ZoneSize": 80, "ZoneType": 2}
        ###          }
        self.EnhancedActiveZones={} # EnhancedZoneData*n

        self.Carriers=Carriers(self)
        self.Transfers=Transfers(self)
        self.Zones=Zones(self)

        ''' tmp sv, for events, not available '''
        self.CarrierID='' # A
        self.CarrierLoc='' # A
        self.CarrierState=0 # U2: wait_in=1, transfer=2, wait_out=3, completed=4, alternate=5
        self.CarrierZoneName='' # A
        self.CommandName='' # A
        self.CommandID='' # A
        self.CommandType='' # A
        self.Dest='' # A
        self.EmptyCarrier=0 # U2: empty=0, not empty=1
        self.ErrorID='' # A
        self.HandoffType=0 # U2: man=1, auto=2
        self.IDReadStatus=0 # U2: succ=0, fail=1, duplicate=2, mismatch=3
        self.InstallTime='' # A: TIME
        self.PortType='' # A: OP=output, BP=buffer, LP=loading
        self.Priority=0 # U2
        self.RecoveryOptions='' # A: blank, RETRY, ABORT
        self.ResultCode=0 # U2: succ=0, cancel=1, abort=2
        self.Source='' # A
        self.SCState=1 # U2: SC_init=1, paused=2, auto=3, pausing=4
        self.StockerCraneID='' # A
        self.StockerUnitID='' # A
        self.ShelfUnitID='' # A
        self.ShelfUnitState=0 # U2: AVAIL=1, PROHIBIT=2, PICKUP(Manual)=3, RESERVED(Manual)=4, RESERVED(AUTO)=5
        self.StockerUnitState=0 # U2
        self.TransferState=0 # U2: queued=1, transfering=2, paused=3, canceling=4, aborting=5
        self.ZoneCapacity=0 # U2
        self.ZoneName='' # A
        self.ZoneSize=0 # U2
        self.ZoneType=0 # U2: shelf=1, port=2, other=3
        self.DeviceID=''
        self.ShelfState=1 # U2: AVAIL=1, PROHIBIT=2, PICKUP(Manual)=3, RESERVED(Manual)=4, RESERVED(AUTO)=5

        self.ALTX=''
        self.ALSV=''
        self.UnitType=''
        self.UnitID=''
        self.Level=''
        self.SubCode=''

        # 儲位狀態映射
        self.shelf_state_mapping = {
            'Available': 1,
            'AVAIL': 1,
            'Prohibit': 2,
            'PROHIBIT': 2,
            'PickupManual': 3,
            'PICKUP': 3,
            'ReservedManual': 4,
            'RESERVED_MANUAL': 4,
            'ReservedAuto': 5,
            'RESERVED': 5,
            'RESERVED_AUTO': 5,
            # 數值映射（以防傳入數值字串）
            '1': 1,
            '2': 2,
            '3': 3,
            '4': 4,
            '5': 5
        }

        self.CarrierInfo={'CarrierID':'', 'CarrierLoc':''} # CarrierID, CarrierLoc
        self.CommandInfo={'CommandID':'', 'Priority':0} # CommandID, Priority
        self.ShelfUnitInfo={'ShelfUnitID':self.ShelfUnitID, 'ShelfUnitState':self.ShelfUnitState} # ShelfUnitID, ShelfUnitState, CarrierID
        self.StockerUnitInfo={'StockerUnitID':self.StockerUnitID, 'StockerUnitState':self.StockerUnitState} # StockerUnitID, StockerUnitState
        self.TransferInfo={'CarrierID':self.CarrierID, 'CarrierLoc':self.CarrierLoc, 'Dest':self.Dest} # CarrierID, CarrierLoc, Dest
        self.ZoneData={'ZoneName':self.ZoneName, 'ZoneCapacity':self.ZoneCapacity} # ZoneName, ZoneCapacity
        self.TransferCommand={'CommandInfo':self.CommandInfo, 'TransferInfo':self.TransferInfo} # CommandInfo, TransferInfo
        self.EnhancedCarrierInfo={'CarrierID':self.CarrierID, 'CarrierLoc':self.CarrierLoc, 'CarrierZoneName':self.CarrierZoneName, 'InstallTime':self.InstallTime, 'CarrierState':self.CarrierState} # CarrierID, CarrierLoc, CarrierZoneName, InstallTime, CarrierState
        self.EnhancedTransferCommand={'TransferState':self.TransferState, 'CommandInfo':self.CommandInfo, 'TransferInfo':self.TransferInfo} # TransferState, CommandInfo, TransferInfo
        self.EnhancedZoneData={'ZoneName':self.ZoneName, 'ZoneCapacity':self.ZoneCapacity, 'ZoneSize':self.ZoneSize, 'ZoneType':self.ZoneType} # ZoneName, ZoneCapacity, ZoneSize, ZoneType


        #####################################
        #     Status Variable Declaration
        #####################################
        ''' SV initial '''
        self.status_variables.update({
            GEM_MDLN: secsgem.StatusVariable(GEM_MDLN, "GEM_MDLN", "", secsgem.SecsVarString, False),
            GEM_SOFTREV: secsgem.StatusVariable(GEM_SOFTREV, "GEM_SOFTREV", "", secsgem.SecsVarString, False),
            SV_EqpName: secsgem.StatusVariable(SV_EqpName, "SV_EqpName", "", secsgem.SecsVarString, True),
            SV_SCState: secsgem.StatusVariable(SV_SCState, "SV_SCState", "", secsgem.SecsVarU2, True),
            SV_ActiveCarriers: secsgem.StatusVariable(SV_ActiveCarriers, "SV_ActiveCarriers", "", secsgem.SecsVarArray, True),
            SV_ActiveTransfers: secsgem.StatusVariable(SV_ActiveTransfers, "SV_ActiveTransfers", "", secsgem.SecsVarArray, True),
            SV_ActiveZones: secsgem.StatusVariable(SV_ActiveZones, "SV_ActiveZones", "", secsgem.SecsVarArray, True),
            SV_EnhancedCarriers: secsgem.StatusVariable(SV_EnhancedCarriers, "SV_EnhancedCarriers", "", secsgem.SecsVarArray, True),
            SV_EnhancedTransfers: secsgem.StatusVariable(SV_EnhancedTransfers, "SV_EnhancedTransfers", "", secsgem.SecsVarArray, True),
            SV_EnhancedActiveZones: secsgem.StatusVariable(SV_EnhancedActiveZones, "SV_EnhancedActiveZones", "", secsgem.SecsVarArray, True),
            SV_CarrierID: secsgem.StatusVariable(SV_CarrierID, "SV_CarrierID", "", secsgem.SecsVarString, True),
            SV_CarrierInfo: secsgem.StatusVariable(SV_CarrierInfo, "SV_CarrierInfo", "", secsgem.SecsVarList, True),
            SV_CarrierLoc: secsgem.StatusVariable(SV_CarrierLoc, "SV_CarrierLoc", "", secsgem.SecsVarString, True),
            SV_CarrierZoneName: secsgem.StatusVariable(SV_CarrierZoneName, "SV_CarrierZoneName", "", secsgem.SecsVarString, True),
            # SV_CommandName: secsgem.StatusVariable(SV_CommandName, "SV_CommandName", "", secsgem.SecsVarString, True),
            SV_CommandID: secsgem.StatusVariable(SV_CommandID, "SV_CommandID", "", secsgem.SecsVarString, True),
            SV_CommandInfo: secsgem.StatusVariable(SV_CommandInfo, "SV_CommandInfo", "", secsgem.SecsVarList, True),
            SV_CommandType: secsgem.StatusVariable(SV_CommandType, "SV_CommandType", "", secsgem.SecsVarString, True),
            SV_Dest: secsgem.StatusVariable(SV_Dest, "SV_Dest", "", secsgem.SecsVarString, True),
            SV_EmptyCarrier: secsgem.StatusVariable(SV_EmptyCarrier, "SV_EmptyCarrier", "", secsgem.SecsVarU2, True),
            SV_EnhancedCarrierInfo: secsgem.StatusVariable(SV_EnhancedCarrierInfo, "SV_EnhancedCarrierInfo", "", secsgem.SecsVarList, True),
            SV_EnhancedTransferCommand: secsgem.StatusVariable(SV_EnhancedTransferCommand, "SV_EnhancedTransferCommand", "", secsgem.SecsVarList, True),
            SV_EnhancedZoneData: secsgem.StatusVariable(SV_EnhancedZoneData, "SV_EnhancedZoneData", "", secsgem.SecsVarList, True),
            SV_ErrorID: secsgem.StatusVariable(SV_ErrorID, "SV_ErrorID", "", secsgem.SecsVarString, True),
            SV_HandoffType: secsgem.StatusVariable(SV_HandoffType, "SV_HandoffType", "", secsgem.SecsVarU2, True),
            SV_IDReadStatus: secsgem.StatusVariable(SV_IDReadStatus, "SV_IDReadStatus", "", secsgem.SecsVarU2, True),
            SV_InstallTime: secsgem.StatusVariable(SV_InstallTime, "SV_InstallTime", "", secsgem.SecsVarString, True),
            SV_PortType: secsgem.StatusVariable(SV_PortType, "SV_PortType", "", secsgem.SecsVarString, True),
            SV_Priority: secsgem.StatusVariable(SV_Priority, "SV_Priority", "", secsgem.SecsVarU2, True),
            SV_RecoveryOptions: secsgem.StatusVariable(SV_RecoveryOptions, "SV_RecoveryOptions", "", secsgem.SecsVarString, True),
            SV_ResultCode: secsgem.StatusVariable(SV_ResultCode, "SV_ResultCode", "", secsgem.SecsVarU2, True),
            SV_Source: secsgem.StatusVariable(SV_Source, "SV_Source", "", secsgem.SecsVarString, True),
            SV_StockerCraneID: secsgem.StatusVariable(SV_StockerCraneID, "SV_StockerCraneID", "", secsgem.SecsVarString, True),
            SV_StockerUnitID: secsgem.StatusVariable(SV_StockerUnitID, "SV_StockerUnitID", "", secsgem.SecsVarString, True),
            SV_ShelfUnitID: secsgem.StatusVariable(SV_ShelfUnitID, "SV_ShelfUnitID", "", secsgem.SecsVarString, True),
                
            SV_StockerUnitInfo: secsgem.StatusVariable(SV_StockerUnitInfo, "SV_StockerUnitInfo", "", secsgem.SecsVarList, True),
            SV_ShelfUnitInfo: secsgem.StatusVariable(SV_ShelfUnitInfo, "SV_ShelfUnitInfo", "", secsgem.SecsVarList, True),
            SV_StockerUnitState: secsgem.StatusVariable(SV_StockerUnitState, "SV_StockerUnitState", "", secsgem.SecsVarU2, True),
            SV_TransferCommand: secsgem.StatusVariable(SV_TransferCommand, "SV_TransferCommand", "", secsgem.SecsVarList, True),
            SV_TransferInfo: secsgem.StatusVariable(SV_TransferInfo, "SV_TransferInfo", "", secsgem.SecsVarList, True),
            SV_TransferState: secsgem.StatusVariable(SV_TransferState, "SV_TransferState", "", secsgem.SecsVarU2, True),
            SV_ZoneCapacity: secsgem.StatusVariable(SV_ZoneCapacity, "SV_ZoneCapacity", "", secsgem.SecsVarU2, True),
            SV_ZoneData: secsgem.StatusVariable(SV_ZoneData, "SV_ZoneData", "", secsgem.SecsVarList, True),
            SV_ZoneName: secsgem.StatusVariable(SV_ZoneName, "SV_ZoneName", "", secsgem.SecsVarString, True),
            SV_ZoneSize: secsgem.StatusVariable(SV_ZoneSize, "SV_ZoneSize", "", secsgem.SecsVarU2, True),
            SV_ZoneType: secsgem.StatusVariable(SV_ZoneType, "SV_ZoneType", "", secsgem.SecsVarU2, True),
            SV_DeviceID: secsgem.StatusVariable(SV_DeviceID, "SV_DeviceID", "", secsgem.SecsVarString, True),
            SV_ALTX: secsgem.StatusVariable(SV_ALTX, "SV_ALTX", "", secsgem.SecsVarString, True), # Mike: 2021/11/08
            SV_ALSV: secsgem.StatusVariable(SV_ALSV, "SV_ALSV", "", secsgem.SecsVarString, True), # Mike: 2021/11/08
            SV_AlarmsSetDescription: secsgem.StatusVariable(SV_AlarmsSetDescription, "SV_AlarmsSetDescription", "", secsgem.SecsVarList, True),
            SV_UnitType: secsgem.StatusVariable(SV_UnitType, "SV_UnitType", "", secsgem.SecsVarString, True), # Mike: 2021/11/29
            SV_UnitID: secsgem.StatusVariable(SV_UnitID, "SV_UnitID", "", secsgem.SecsVarString, True), # Mike: 2021/11/29
            SV_Level: secsgem.StatusVariable(SV_Level, "SV_Level", "", secsgem.SecsVarString, True), # Mike: 2021/12/01
            SV_SubCode: secsgem.StatusVariable(SV_SubCode, "SV_SubCode", "", secsgem.SecsVarString, True), #Chi 2022/06/17
            SV_UnitAlarmList: secsgem.StatusVariable(SV_UnitAlarmList, "SV_UnitAlarmList", "", secsgem.SecsVarArray, True),
            SV_UnitAlarmInfo: secsgem.StatusVariable(SV_UnitAlarmInfo, "SV_UnitAlarmInfo", "", secsgem.SecsVarList, True),
            
        })
        self.status_variables[GEM_MDLN].value=self.MDLN
        self.status_variables[GEM_SOFTREV].value=self.SOFTREV

        #####################################
        #  Equipment Constants Declaration
        #####################################
        ''' EC initial '''
        '''self.equipment_constants.update({
            ECID: secsgem.EquipmentConstant(ECID, "EC", EC_max, EC_min, EC_default, "EC_unit", secsgem.SecsVarU4, False),
        })'''

        #####################################
        #       Report Declaration
        #####################################
        ''' Report initial '''
        for ALID, DATA in AlarmTable.items():
            if DATA['report']:
                self.registered_reports.update({
                    ALID+500000: secsgem.CollectionEventReport(ALID+500000, DATA['report']),
                })

        self.registered_reports.update({
            GEM_EQP_OFFLINE: secsgem.CollectionEventReport(GEM_EQP_OFFLINE, [GEM_MDLN]),#OffLineModeChange Report
            GEM_CONTROL_STATE_LOCAL: secsgem.CollectionEventReport(GEM_CONTROL_STATE_LOCAL,[GEM_CONTROL_STATE]),#OnLineLocal ModeChange Report
            GEM_CONTROL_STATE_REMOTE: secsgem.CollectionEventReport(GEM_CONTROL_STATE_REMOTE, [GEM_MDLN]), # OnLineRemoteModeChange Report
            # Common Report ID 2 for SC events according to specification
            2: secsgem.CollectionEventReport(2, [SV_EqpName]),  # Common Report for SC events - 修正為 SV_EqpName
                # OnLineRemoteModeChange
            # SC STATE TRANSITION EVENTS - 修正為使用 SV_EqpName
            53: secsgem.CollectionEventReport(53, [SV_EqpName]),#SCAutoCompleted Report
            54: secsgem.CollectionEventReport(54, [SV_EqpName]),#SCAutoInitiated Report
            55: secsgem.CollectionEventReport(55, [SV_EqpName]),#SCPauseCompleted Report
            56: secsgem.CollectionEventReport(56, [SV_EqpName]),#SCPaused Report 
            57: secsgem.CollectionEventReport(57, [SV_EqpName]),#SCPauseInitiated Report
            #SCPaused+5000: secsgem.CollectionEventReport(SCPaused+5000, []),
            #SCPauseInitiated+5000: secsgem.CollectionEventReport(SCPauseInitiated+5000, []),
            # TRANSFER COMMAND STATE TRANSITION EVENTS
            TransferAbortCompleted+5000: secsgem.CollectionEventReport(TransferAbortCompleted+5000, [SV_CommandID, SV_CarrierID, SV_CarrierLoc, SV_CarrierZoneName]),
            TransferAbortFailed+5000: secsgem.CollectionEventReport(TransferAbortFailed+5000, [SV_CommandID, SV_CarrierID, SV_CarrierLoc, SV_CarrierZoneName]),
            TransferAbortInitiated+5000: secsgem.CollectionEventReport(TransferAbortInitiated+5000, [SV_CommandID, SV_CarrierID, SV_CarrierLoc, SV_CarrierZoneName]),
            TransferCancelCompleted+5000: secsgem.CollectionEventReport(TransferCancelCompleted+5000, [SV_CommandID, SV_CarrierID, SV_CarrierLoc, SV_CarrierZoneName]),
            TransferCancelFailed+5000: secsgem.CollectionEventReport(TransferCancelFailed+5000, [SV_CommandID, SV_CarrierID, SV_CarrierLoc, SV_CarrierZoneName]),
            TransferCancelInitiated+5000: secsgem.CollectionEventReport(TransferCancelInitiated+5000, [SV_CommandID, SV_CarrierID, SV_CarrierLoc, SV_CarrierZoneName]),
            TransferCompleted+5000: secsgem.CollectionEventReport(TransferCompleted+5000, [SV_CommandID, SV_CarrierID, SV_CarrierLoc, SV_ResultCode, SV_CarrierZoneName]),
            TransferInitiated+5000: secsgem.CollectionEventReport(TransferInitiated+5000, [SV_CommandID, SV_CarrierID, SV_CarrierLoc, SV_CarrierZoneName, SV_Dest]),
            TransferPaused+5000: secsgem.CollectionEventReport(TransferPaused+5000, [SV_CommandID, SV_CarrierID, SV_CarrierLoc, SV_CarrierZoneName]),
            TransferResumed+5000: secsgem.CollectionEventReport(TransferResumed+5000, [SV_CommandID, SV_CarrierID, SV_CarrierLoc, SV_CarrierZoneName]),
            # STOCKER CARRIER STATE TRANSITION EVENTS
            106: secsgem.CollectionEventReport(106, [SV_CarrierID, SV_CarrierLoc, SV_CarrierZoneName]),
            CarrierRemoveCompleted+5000: secsgem.CollectionEventReport(CarrierRemoveCompleted+5000, [SV_CarrierID, SV_CarrierLoc, SV_CarrierZoneName, SV_HandoffType, SV_PortType]),
            CarrierRemoved+5000: secsgem.CollectionEventReport(CarrierRemoved+5000, [SV_CarrierID, SV_CarrierLoc, SV_CarrierZoneName, SV_HandoffType, SV_PortType]),
            CarrierResumed+5000: secsgem.CollectionEventReport(CarrierResumed+5000, [SV_CommandID, SV_CarrierID, SV_CarrierLoc, SV_CarrierZoneName, SV_Dest]),
            CarrierStored+5000: secsgem.CollectionEventReport(CarrierStored+5000, [SV_CarrierID, SV_CarrierLoc, SV_CarrierZoneName, SV_HandoffType, SV_PortType]),
            CarrierStoredAlt+5000: secsgem.CollectionEventReport(CarrierStoredAlt+5000, [SV_CommandID, SV_CarrierID, SV_CarrierLoc, SV_CarrierZoneName, SV_Dest]),
            CarrierTransferring+5000: secsgem.CollectionEventReport(CarrierTransferring+5000, [SV_CarrierID, SV_CarrierLoc, SV_CarrierZoneName]),
            CarrierWaitIn+5000: secsgem.CollectionEventReport(CarrierWaitIn+5000, [SV_CarrierID, SV_CarrierLoc, SV_CarrierZoneName]),
            CarrierWaitOut+5000: secsgem.CollectionEventReport(CarrierWaitOut+5000, [SV_CarrierID, SV_CarrierLoc, SV_CarrierZoneName, SV_PortType]),
            ZoneCapacityChange+5000: secsgem.CollectionEventReport(ZoneCapacityChange+5000, [SV_ZoneData]),
            # STOCKER CRANE STATE TRANSITION EVENTS
            CraneActive+5000: secsgem.CollectionEventReport(CraneActive+5000, [SV_CommandID, SV_StockerCraneID]),
            CraneIdle+5000: secsgem.CollectionEventReport(CraneIdle+5000, [SV_CommandID, SV_StockerCraneID]),
            # NON-TRANSITION EVENTS
            CarrierIDRead+5000: secsgem.CollectionEventReport(CarrierIDRead+5000, [SV_CarrierID, SV_CarrierLoc, SV_IDReadStatus]),
            CarrierLocateCompleted+5000: secsgem.CollectionEventReport(CarrierLocateCompleted+5000, [SV_CarrierID, SV_CarrierLoc, SV_CarrierZoneName]),
            IDReadError+5000: secsgem.CollectionEventReport(IDReadError+5000, [SV_CarrierID, SV_CarrierLoc, SV_IDReadStatus]),
            OperatorInitiatedAction+5000: secsgem.CollectionEventReport(OperatorInitiatedAction+5000, [SV_CommandID, SV_CommandType, SV_CarrierID, SV_Source, SV_Dest, SV_Priority]),
            DeviceOnline+5000: secsgem.CollectionEventReport(DeviceOnline+5000, [SV_DeviceID]),
            DeviceOffline+5000: secsgem.CollectionEventReport(DeviceOffline+5000, [SV_DeviceID]),
        })


        #####################################
        #       Event Declaration/Link
        #####################################
        ''' Report link initial'''
        for ALID, DATA in AlarmTable.items():
            if DATA['report']:
                self.registered_collection_events.update({
                    ALID+100000: secsgem.CollectionEventLink(ALID+100000, [ALID+500000]),
                    ALID+200000: secsgem.CollectionEventLink(ALID+200000, [ALID+500000]),
                })
                self.registered_collection_events[ALID+100000].enabled=True
                self.registered_collection_events[ALID+200000].enabled=True
            else:
                self.registered_collection_events.update({
                    ALID+100000: secsgem.CollectionEventLink(ALID+100000, [ALID+500000]),
                    ALID+200000: secsgem.CollectionEventLink(ALID+200000, [ALID+500000]),
                })
                self.registered_collection_events[ALID+100000].enabled=True
                self.registered_collection_events[ALID+200000].enabled=True

        self.registered_collection_events.update({
            GEM_EQP_OFFLINE: secsgem.CollectionEventLink(GEM_EQP_OFFLINE, [2]),
            GEM_CONTROL_STATE_REMOTE: secsgem.CollectionEventLink(GEM_CONTROL_STATE_REMOTE, [2]),
            GEM_CONTROL_STATE_LOCAL:secsgem.CollectionEventLink(GEM_CONTROL_STATE_LOCAL, [1]),
            # SC STATE TRANSITION EVENTS - Use RPTID 2 according to specification
            SCAutoCompleted: secsgem.CollectionEventLink(SCAutoCompleted, [2]),
            SCAutoInitiated: secsgem.CollectionEventLink(SCAutoInitiated, [2]),
            SCPauseCompleted: secsgem.CollectionEventLink(SCPauseCompleted, [2]),
            SCPaused: secsgem.CollectionEventLink(SCPaused, [2]),
            SCPauseInitiated: secsgem.CollectionEventLink(SCPauseInitiated, [2]),

            # TRANSFER COMMAND STATE TRANSITION EVENTS
            TransferAbortCompleted: secsgem.CollectionEventLink(TransferAbortCompleted, [TransferAbortCompleted+5000]),
            TransferAbortFailed: secsgem.CollectionEventLink(TransferAbortFailed, [TransferAbortFailed+5000]),
            TransferAbortInitiated: secsgem.CollectionEventLink(TransferAbortInitiated, [TransferAbortInitiated+5000]),
            TransferCancelCompleted: secsgem.CollectionEventLink(TransferCancelCompleted, [TransferCancelCompleted+5000]),
            TransferCancelFailed: secsgem.CollectionEventLink(TransferCancelFailed, [TransferCancelFailed+5000]),
            TransferCancelInitiated: secsgem.CollectionEventLink(TransferCancelInitiated, [TransferCancelInitiated+5000]),
            TransferCompleted: secsgem.CollectionEventLink(TransferCompleted, [TransferCompleted+5000]),
            TransferInitiated: secsgem.CollectionEventLink(TransferInitiated, [TransferInitiated+5000]),
            TransferPaused: secsgem.CollectionEventLink(TransferPaused, [TransferPaused+5000]),
            TransferResumed: secsgem.CollectionEventLink(TransferResumed, [TransferResumed+5000]),

            # STOCKER CARRIER STATE TRANSITION EVENTS
            CarrierInstallCompleted: secsgem.CollectionEventLink(CarrierInstallCompleted, [106]),
            CarrierRemoveCompleted: secsgem.CollectionEventLink(CarrierRemoveCompleted, [CarrierRemoveCompleted+5000]),
            CarrierRemoved: secsgem.CollectionEventLink(CarrierRemoved, [CarrierRemoved+5000]),
            CarrierResumed: secsgem.CollectionEventLink(CarrierResumed, [CarrierResumed+5000]),
            CarrierStored: secsgem.CollectionEventLink(CarrierStored, [CarrierStored+5000]),
            CarrierStoredAlt: secsgem.CollectionEventLink(CarrierStoredAlt, [CarrierStoredAlt+5000]),
            CarrierTransferring: secsgem.CollectionEventLink(CarrierTransferring, [CarrierTransferring+5000]),
            CarrierWaitIn: secsgem.CollectionEventLink(CarrierWaitIn, [CarrierWaitIn+5000]),
            CarrierWaitOut: secsgem.CollectionEventLink(CarrierWaitOut, [CarrierWaitOut+5000]),
            ZoneCapacityChange: secsgem.CollectionEventLink(ZoneCapacityChange, [ZoneCapacityChange+5000]),

            # STOCKER CRANE STATE TRANSITION EVENTS
            CraneActive: secsgem.CollectionEventLink(CraneActive, [CraneActive+5000]),
            CraneIdle: secsgem.CollectionEventLink(CraneIdle, [CraneIdle+5000]),

            # NON-TRANSITION EVENTS
            CarrierIDRead: secsgem.CollectionEventLink(CarrierIDRead, [CarrierIDRead+5000]),
            CarrierLocateCompleted: secsgem.CollectionEventLink(CarrierLocateCompleted, [CarrierLocateCompleted+5000]),
            IDReadError: secsgem.CollectionEventLink(IDReadError, [IDReadError+5000]),
            OperatorInitiatedAction: secsgem.CollectionEventLink(OperatorInitiatedAction, [OperatorInitiatedAction+5000]),
            DeviceOnline: secsgem.CollectionEventLink(DeviceOnline, [DeviceOnline+5000]),
            DeviceOffline: secsgem.CollectionEventLink(DeviceOffline, [DeviceOffline+5000]),
        })

        self.registered_collection_events[GEM_EQP_OFFLINE].enabled = True
        self.registered_collection_events[GEM_CONTROL_STATE_REMOTE].enabled = True
        self.registered_collection_events[GEM_CONTROL_STATE_LOCAL].enabled = True
        self.registered_collection_events[SCAutoCompleted].enabled=True
        self.registered_collection_events[SCAutoInitiated].enabled=True
        self.registered_collection_events[SCPauseCompleted].enabled=True
        self.registered_collection_events[SCPaused].enabled=True
        self.registered_collection_events[SCPauseInitiated].enabled=True
        
        self.registered_collection_events[TransferAbortCompleted].enabled=True
        self.registered_collection_events[TransferAbortFailed].enabled=True
        self.registered_collection_events[TransferAbortInitiated].enabled=True
        self.registered_collection_events[TransferCancelCompleted].enabled=True
        self.registered_collection_events[TransferCancelFailed].enabled=True
        self.registered_collection_events[TransferCancelInitiated].enabled=True
        self.registered_collection_events[TransferCompleted].enabled=True
        self.registered_collection_events[TransferInitiated].enabled=True
        self.registered_collection_events[TransferPaused].enabled=True
        self.registered_collection_events[TransferResumed].enabled=True

        self.registered_collection_events[CarrierInstallCompleted].enabled=True
        self.registered_collection_events[CarrierRemoveCompleted].enabled=True
        self.registered_collection_events[CarrierRemoved].enabled=True
        self.registered_collection_events[CarrierResumed].enabled=True
        self.registered_collection_events[CarrierStored].enabled=True
        self.registered_collection_events[CarrierStoredAlt].enabled=True
        self.registered_collection_events[CarrierTransferring].enabled=True
        self.registered_collection_events[CarrierWaitIn].enabled=True
        self.registered_collection_events[CarrierWaitOut].enabled=True
        self.registered_collection_events[ZoneCapacityChange].enabled=True

        self.registered_collection_events[CraneActive].enabled=True
        self.registered_collection_events[CraneIdle].enabled=True

        self.registered_collection_events[CarrierIDRead].enabled=True
        self.registered_collection_events[CarrierLocateCompleted].enabled=True
        self.registered_collection_events[IDReadError].enabled=True
        self.registered_collection_events[OperatorInitiatedAction].enabled=True
        self.registered_collection_events[DeviceOnline].enabled=True
        self.registered_collection_events[DeviceOffline].enabled=True


        #####################################
        #    Stream Function Registration
        #####################################
        # Register  Terminal Display function
        self.register_stream_function(10, 3, self._on_s10f3)


        #####################################
        #         Alarm Declaration
        #####################################
        ''' Alarm initial '''
        for ALID, DATA in AlarmTable.items():
            self.alarms.update({
                #alid: secsgem.Alarm((alid), "name", "text", secsgem.ALCD.PERSONAL_SAFETY | secsgem.ALCD.EQUIPMENT_SAFETY, set_ce, clear_ce),
                ALID: secsgem.Alarm((ALID), DATA['text'], DATA['text'], secsgem.ALCD.PERSONAL_SAFETY | secsgem.ALCD.EQUIPMENT_SAFETY, ALID+100000, ALID+200000,UnitID=""),
            })
            self.alarms[ALID].enabled=True


        #####################################
        #     Remote Command Declaration
        #####################################
        ''' Remote command '''
        self.remote_commands.clear()

        self.remote_commands.update({
            "ABORT": secsgem.RemoteCommand("ABORT", "abort command", ["COMMANDID"], None),
            "ASSOCIATE": secsgem.RemoteCommand("ASSOCIATE", "associate command", ["CARRIERID", "CARRIERLOC", "ASSOCIATEDATA"], None), # Mike: 2020/05/27
            "BINDING": secsgem.RemoteCommand("BINDING", "binding command", ["CARRIERID", "LOTID", "NEXTSTEP", "EQLIST", "PRIORITY"], None), # Mike: 2020/05/27
            "CANCEL": secsgem.RemoteCommand("CANCEL", "cancel command", ["COMMANDID"], None),
            "INSTALL": secsgem.RemoteCommand("INSTALL", "install command", ["CARRIERID", "CARRIERLOC"], None),
            "SCAN": secsgem.RemoteCommand("SCAN", "scan command", ["CARRIERID","CARRIERLOC"],None),
            "INFOUPDATE": secsgem.RemoteCommand("INFOUPDATE", "in foup date command", ["CARRIERID"], None, ["*"]), # Mike: 2021/08/11
            "INFOUPDATEBYRACK": secsgem.RemoteCommand("INFOUPDATEBYRACK", "in foup date command", ["ERACKID"], None, ["*"]), # 2024/04/18 For sj by erack update info
            "LOCATE": secsgem.RemoteCommand("LOCATE", "locate command", ["CARRIERID"], None),
            "LOCSTATECHG": secsgem.RemoteCommand("LOCSTATECHG", "shelf state change command", ["SHELFID", "SHELFSTATE"], None),
            "PAUSE": secsgem.RemoteCommand("PAUSE", "pause command", [], None),
            "REMOVE": secsgem.RemoteCommand("REMOVE", "remove command", ["CARRIERID"], None),
            "RESUME": secsgem.RemoteCommand("RESUME", "resume command", [], None),
            "RETRY": secsgem.RemoteCommand("RETRY", "retry command", ["ERRORID"], None),
            "PICKUPAUTH": secsgem.RemoteCommand("PICKUPAUTH", "pickup auth command", ["SHELFID"], None),
        })


        #####################################
        # Enhanced Remote Command Declaration
        #####################################
        ''' Enhance Remote command '''
        self.enhance_remote_commands.clear()

        self.enhance_remote_commands.update({
            "TRANSFER": secsgem.RemoteCommand("TRANSFER", "transfer command", {"COMMANDINFO":["COMMANDID", "PRIORITY"], "TRANSFERINFO":["CARRIERID", "SOURCE", "DEST"]}, None),
        })

        #####################################
        # Force Override RPTID 2 Definition
        #####################################
        # Ensure RPTID 2 contains GEM_MDLN for SCPauseCompleted according to specification
        self.registered_reports[2] = secsgem.CollectionEventReport(2, [GEM_MDLN])
        
        #####################################
        #          Control State 
        #####################################
        ''' SCState '''
        self.State=Fysom({
            'initial': "none",
            'events': [
                {'name': 'initial_done', 'src': 'SC_INIT', 'dst': 'PAUSED'},  # 2
                {'name': 'resume', 'src': ['PAUSED', 'PAUSING'], 'dst': 'AUTO'},  # 3, 6
                {'name': 'pause', 'src': 'AUTO', 'dst': 'PAUSING'},  # 4
                {'name': 'pause_completed', 'src': 'PAUSING', 'dst': 'PAUSED'},  # 5
            ],
            'callbacks': {
                'onSC_INIT': self._on_SC_state_SC_INIT,  # 
                'onPAUSED': self._on_SC_state_PAUSED,  # 
                'onAUTO': self._on_SC_state_AUTO,  # 
                'onPAUSING': self._on_SC_state_PAUSING,  # 
                'onbeforeinitial_done': self._on_SC_state_initial_done,  # 2, send collection event (SCPaused)
                'onbeforeresume': self._on_SC_state_resume,  # 3, 6, send collection event (SCAutoCompleted)
                'onbeforepause': self._on_SC_state_pause,  # 4, send collection event (SCPauseInitiated)
                'onbeforepause_completed': self._on_SC_state_pause_completed,  # 5, send collection event (SCPauseCompleted)
            },
            'autoforward': [
                {'src': 'none', 'dst': 'SC_INIT'},  # 1
            ]
        })


    #####################################
    #       Variable Callback
    #####################################
    def on_sv_value_request(self, svid, sv):
        if sv.svid == SV_SCState:
            value=self.SCState
            return sv.value_type(value)
        elif sv.svid == SV_EqpName:
            value=self.EqpName
            return sv.value_type(value)
        elif sv.svid == SV_EnhancedCarriers:
            L_EnhancedCarriers=[]
            for key, EnhancedCarrier in self.Carriers.Data.items():
                EnhancedCarrierInfo_n=secsgem.SecsVarList([DI.CARRIERID, DI.CARRIERLOC, DI.CARRIERZONENAME, DI.INSTALLTIME, DI.CARRIERSTATE], [EnhancedCarrier.CarrierID, EnhancedCarrier.CarrierLoc, EnhancedCarrier.CarrierZoneName, EnhancedCarrier.InstallTime, EnhancedCarrier.CarrierState])
                L_EnhancedCarriers.append(EnhancedCarrierInfo_n)
            ret=secsgem.SecsVarArray(DI.ENHANCEDCARRIERSUNIT, L_EnhancedCarriers)
            return ret
        elif sv.svid == SV_EnhancedTransfers:
            L_EnhancedTransfers=[]
            for key, EnhancedTransfer in self.Transfers.Data.items():
                CommandInfo=secsgem.SecsVarList([DI.COMMANDID, DI.PRIORITY], [EnhancedTransfer.CommandID, EnhancedTransfer.Priority])
                TransferInfo=secsgem.SecsVarList([DI.CARRIERID, DI.CARRIERLOC, DI.DEST], [EnhancedTransfer.CarrierID, EnhancedTransfer.CarrierLoc, EnhancedTransfer.Dest])
                EnhancedTransferCommand_n=secsgem.SecsVarList([DI.TRANSFERSTATE, DI.COMMANDINFO, DI.TRANSFERINFO], [EnhancedTransfer.TransferState, CommandInfo, TransferInfo])
                L_EnhancedTransfers.append(EnhancedTransferCommand_n)
            ret=secsgem.SecsVarArray(DI.ENHANCEDTRANSFERSUNIT, L_EnhancedTransfers)
            return ret
        elif sv.svid == SV_EnhancedActiveZones:
            L_EnhancedActiveZones=[]
            for key, EnhancedActiveZone in self.Zones.Data.items():
                L_StockerUnitInfo=[]
                for key, ShelfUnitInfo in EnhancedActiveZone.ShelfUnit.items():
                    action_logger.debug("key:{}, ShelfUnitInfo:{}".format(key, ShelfUnitInfo))
                    
                    
                for key, StockerUnitInfo in EnhancedActiveZone.StockerUnit.items():
                    StokerUnitInfo_n=secsgem.SecsVarList([DI.STOCKERUNITID, DI.STOCKERUNITSTATE, DI.CARRIERID], [StockerUnitInfo['StockerUnitID'], StockerUnitInfo['StockerUnitState'], StockerUnitInfo['CarrierID']])
                    L_StockerUnitInfo.append(StokerUnitInfo_n)
                A_StockerUnitInfo=secsgem.SecsVarArray(DI.STOCKERUNITINFO, L_StockerUnitInfo)
                EnhancedZoneData_n=secsgem.SecsVarList([DI.ZONENAME, DI.ZONECAPACITY, DI.ZONESIZE, DI.ZONETYPE, DI.STOCKERUNIT], [EnhancedActiveZone.ZoneName, EnhancedActiveZone.ZoneCapacity, EnhancedActiveZone.ZoneSize, EnhancedActiveZone.ZoneType, A_StockerUnitInfo])
                L_EnhancedActiveZones.append(EnhancedZoneData_n)
            ret=secsgem.SecsVarArray(DI.ENHANCEDACTIVEZONESUNIT, L_EnhancedActiveZones)
            return ret
        elif sv.svid == SV_ActiveCarriers:
            L_ActiveCarriers=[]
            for key, ActiveCarrier in self.Carriers.Data.items():
                CarrierInfo_n=secsgem.SecsVarList([DI.CARRIERID, DI.CARRIERLOC], [ActiveCarrier.CarrierID, ActiveCarrier.CarrierLoc])
                L_ActiveCarriers.append(CarrierInfo_n)
            ret=secsgem.SecsVarArray(DI.ACTIVECARRIERSUNIT, L_ActiveCarriers)
            return ret
        elif sv.svid == SV_ActiveTransfers:
            L_ActiveTransfers=[]
            for key, ActiveTransfer in self.Transfers.Data.items():
                CommandInfo=secsgem.SecsVarList([DI.COMMANDID, DI.PRIORITY], [ActiveTransfer.CommandID, ActiveTransfer.Priority])
                TransferInfo=secsgem.SecsVarList([DI.CARRIERID, DI.CARRIERLOC, DI.DEST], [ActiveTransfer.CarrierID, ActiveTransfer.CarrierLoc, ActiveTransfer.Dest])
                TransferCommand_n=secsgem.SecsVarList([DI.COMMANDINFO, DI.TRANSFERINFO], [CommandInfo, TransferInfo])
                L_ActiveTransfers.append(TransferCommand_n)
            ret=secsgem.SecsVarArray(DI.ACTIVETRANSFERSUNIT, L_ActiveTransfers)
            return ret
        elif sv.svid == SV_ActiveZones:
            L_ActiveZones=[]
            for key, ActiveZone in self.Zones.Data.items():
                ZoneData_n=secsgem.SecsVarList([DI.ZONENAME, DI.ZONECAPACITY], [ActiveZone.ZoneName, ActiveZone.ZoneCapacity])
                L_ActiveZones.append(ZoneData_n)
            ret=secsgem.SecsVarArray(DI.ACTIVEZONESUNIT, L_ActiveZones)
            return ret
        elif sv.svid == SV_AlarmsSetDescription:####kelvinng 20250626
            L_AlarmsSetDescription=[]
            e88equipmen_logger.debug(self.alarms.items())
            for alid, alarm in self.alarms.items():
                e88equipmen_logger.debug(alarm.UnitID)
                if alarm.set:
                    UnitInfo=secsgem.SecsVarList([DI.UNITID,DI.UNITSTATE], [alarm.UnitID,3])
                    EnhancedALID_n=secsgem.SecsVarList([DI.ALID,DI.UNITINFO, DI.ALTX], [alid,UnitInfo,alarm.text])
                    L_AlarmsSetDescription.append(EnhancedALID_n)
            ret=secsgem.SecsVarArray(DI.ACTIVECARRIERSUNIT, L_AlarmsSetDescription)
            return ret
        # For inner use
        elif sv.svid == SV_EnhancedCarrierInfo:
            ret=secsgem.SecsVarList([DI.CARRIERID, DI.CARRIERLOC, DI.CARRIERZONENAME, DI.INSTALLTIME, DI.CARRIERSTATE], [self.EnhancedCarrierInfo['CarrierID'], self.EnhancedCarrierInfo['CarrierLoc'], self.EnhancedCarrierInfo['CarrierZoneName'], self.EnhancedCarrierInfo['InstallTime'], self.EnhancedCarrierInfo['CarrierState']])
            return ret
        elif sv.svid == SV_EnhancedTransferCommand:
            CommandInfo=secsgem.SecsVarList([DI.COMMANDID, DI.PRIORITY], [self.EnhancedTransferCommand['CommandInfo']['CommandID'], self.EnhancedTransferCommand['CommandInfo']['Priority']])
            TransferInfo=secsgem.SecsVarList([DI.CARRIERID, DI.CARRIERLOC, DI.DEST], [self.EnhancedTransferCommand['TransferInfo']['CarrierID'], self.EnhancedTransferCommand['TransferInfo']['CarrierLoc'], self.EnhancedTransferCommand['TransferInfo']['Dest']])
            ret=secsgem.SecsVarList([DI.TRANSFERSTATE, DI.COMMANDINFO, DI.TRANSFERINFO], [self.EnhancedTransferCommand['TransferState'], CommandInfo, TransferInfo])
            return ret
        elif sv.svid == SV_EnhancedZoneData:
            ret=secsgem.SecsVarList([DI.ZONENAME, DI.ZONECAPACITY, DI.ZONESIZE, DI.ZONETYPE], [self.EnhancedZoneData['ZoneName'], self.EnhancedZoneData['ZoneCapacity'], self.EnhancedZoneData['ZoneSize'], self.EnhancedZoneData['ZoneType']])
            return ret
        elif sv.svid == SV_TransferCommand:
            CommandInfo=secsgem.SecsVarList([DI.COMMANDID, DI.PRIORITY], [self.TransferCommand['CommandInfo']['CommandID'], self.TransferCommand['CommandInfo']['Priority']])
            TransferInfo=secsgem.SecsVarList([DI.CARRIERID, DI.CARRIERLOC, DI.DEST], [self.TransferCommand['TransferInfo']['CarrierID'], self.TransferCommand['TransferInfo']['CarrierLoc'], self.TransferCommand['TransferInfo']['Dest']])
            ret=secsgem.SecsVarList([DI.COMMANDINFO, DI.TRANSFERINFO], [CommandInfo, TransferInfo])
            return ret
        elif sv.svid == SV_CarrierInfo:
            ret=secsgem.SecsVarList([DI.CARRIERID, DI.CARRIERLOC], [self.CarrierInfo['CarrierID'], self.CarrierInfo['CarrierLoc']])
            return ret
        elif sv.svid == SV_CommandInfo:
            ret=secsgem.SecsVarList([DI.COMMANDID, DI.PRIORITY], [self.CommandInfo['CommandID'], self.CommandInfo['Priority']])
            return ret
        elif sv.svid == SV_ShelfUnitInfo:
            ret=secsgem.SecsVarList([DI.STOCKERUNITID, DI.STOCKERUNITSTATE], [self.ShelfUnitInfo['StockerUnitID'], self.ShelfUnitInfo['StockerUnitState']])
            return ret
        elif sv.svid == SV_StockerUnitInfo:
            ret=secsgem.SecsVarList([DI.STOCKERUNITID, DI.STOCKERUNITSTATE], [self.StockerUnitInfo['StockerUnitID'], self.StockerUnitInfo['StockerUnitState']])
            return ret
        elif sv.svid == SV_TransferInfo:
            ret=secsgem.SecsVarList([DI.CARRIERID, DI.CARRIERLOC, DI.DEST], [self.TransferInfo['CarrierID'], self.TransferInfo['CarrierLoc'], self.TransferInfo['Dest']])
            return ret
        elif sv.svid == SV_ZoneData:
            ret=secsgem.SecsVarList([DI.ZONENAME, DI.ZONECAPACITY], [self.ZoneData['ZoneName'], self.ZoneData['ZoneCapacity']])
            return ret
        elif sv.svid == SV_CarrierID:
            value=self.CarrierID
            return sv.value_type(value)
        elif sv.svid == SV_CarrierLoc:
            value=self.CarrierLoc
            return sv.value_type(value)
        elif sv.svid == SV_CarrierState:
            value=self.CarrierState
            return sv.value_type(value)
        elif sv.svid == SV_CarrierZoneName:
            value=self.CarrierZoneName
            return sv.value_type(value)
        elif sv.svid == SV_CommandID:
            value=self.CommandID
            return sv.value_type(value)
        elif sv.svid == SV_CommandType:
            value=self.CommandType
            return sv.value_type(value)
        elif sv.svid == SV_Dest:
            value=self.Dest
            return sv.value_type(value)
        elif sv.svid == SV_EmptyCarrier:
            value=self.EmptyCarrier
            return sv.value_type(value)
        elif sv.svid == SV_DeviceID:
            value=self.DeviceID
            return sv.value_type(value)
        elif sv.svid == SV_ErrorID:
            value=self.ErrorID
            return sv.value_type(value)
        elif sv.svid == SV_HandoffType:
            value=self.HandoffType
            return sv.value_type(value)
        elif sv.svid == SV_IDReadStatus:
            value=self.IDReadStatus
            return sv.value_type(value)
        elif sv.svid == SV_InstallTime:
            value=self.InstallTime
            return sv.value_type(value)
        elif sv.svid == SV_PortType:
            value=self.PortType
            return sv.value_type(value)
        elif sv.svid == SV_Priority:
            value=self.Priority
            return sv.value_type(value)
        elif sv.svid == SV_RecoveryOptions:
            value=self.RecoveryOptions
            return sv.value_type(value)
        elif sv.svid == SV_ResultCode: # U2
            value=self.ResultCode
            return sv.value_type(value)
        elif sv.svid == SV_Source:
            value=self.Source
            return sv.value_type(value)
        elif sv.svid == SV_StockerCraneID:
            value=self.StockerCraneID
            return sv.value_type(value)
        elif sv.svid == SV_StockerUnitID:
            value=self.StockerUnitID
            return sv.value_type(value)
        elif sv.svid == SV_StockerUnitState:
            value=self.StockerUnitState
            return sv.value_type(value)
        elif sv.svid == SV_TransferState:
            value=self.TransferState
            return sv.value_type(value)
        elif sv.svid == SV_ZoneCapacity:
            value=self.ZoneCapacity
            return sv.value_type(value)
        elif sv.svid == SV_ZoneName:
            value=self.ZoneName
            return sv.value_type(value)
        elif sv.svid == SV_ZoneSize:
            value=self.ZoneSize
            return sv.value_type(value)
        elif sv.svid == SV_ZoneType:
            value=self.ZoneType
            return sv.value_type(value)
        elif sv.svid == SV_ALTX: # Mike: 2021/11/08
            value=self.ALTX
            return sv.value_type(value)
        elif sv.svid == SV_ALSV: # Mike: 2021/11/08
            value=self.ALSV
            return sv.value_type(value)
        elif sv.svid == SV_UnitType: # Mike: 2021/11/29
            value=self.UnitType
            return sv.value_type(value)
        elif sv.svid == SV_UnitID: # Mike: 2021/11/29
            value=self.UnitID
            return sv.value_type(value)
        elif sv.svid == SV_Level: # Mike: 2021/12/01
            value=self.Level
            return sv.value_type(value)
        elif sv.svid == SV_SubCode: # Chi: 2022/06/17
            value=self.SubCode
            return sv.value_type(value)
        elif sv.svid == SV_UnitAlarmList:
            L_UnitAlarms=[]
            for info in self.UnitAlarmList.values():
                alarm=secsgem.SecsVarList([
                    secsgem.UNITID, secsgem.ALID, secsgem.ALTX, secsgem.MAINSTATE
                ], [
                    info.get('UNITID', ''),
                    info.get('ALID', 0),
                    info.get('ALTX', ''),
                    info.get('MIANSTATE', 2)
                ])
                L_UnitAlarms.append(alarm)
            ret=secsgem.SecsVarArray(DI.UNITALARMLIST, L_UnitAlarms)
            return ret
        elif sv.svid == SV_UnitAlarmInfo:
            info=self.UnitAlarmInfo if self.UnitAlarmInfo else {}
            ret=secsgem.SecsVarList([
                secsgem.UNITID, secsgem.ALID, secsgem.ALTX, secsgem.MAINSTATE
            ], [
                info.get('UNITID', ''),
                info.get('ALID', 0),
                info.get('ALTX', ''),
                info.get('MIANSTATE', 0)
            ])
            return ret
        elif sv.svid == SV_ShelfState:
            value=self.ShelfState
            return sv.value_type(value)

        '''
        def on_dv_value_request(self, dvid, dv):
        if dv.dvid=1:
            dv_list=secsgem.SecsVarList([
                secsgem.AAA,
            ])
            dv_list.AAA=AAA
            return dv_list
        '''

    #####################################
    #      Stream Function Callback
    #####################################
    def _on_s02f15(self, handler, packet):
        return self.stream_function(9, 5)() # Function Disable (New EC)

    def _on_s06f23(self, handler, packet):
        return self.stream_function(6, 0)() # Function Disable (spool)

    def _on_s02f17(self, handler, packet):
        """Callback handler for Stream 2, Function 17, Request online

        :param handler: handler the message was received on
        :type handler: :class:`self.secsgem_e82_hsms.handler.HsmsHandler`
        :param packet: complete message received
        :type packet: :class:`self.secsgem_e82_hsms.packets.HsmsPacket`
        """
        if self.controlState.current not in ["ONLINE", "ONLINE_LOCAL", "ONLINE_REMOTE"]:
            return self.stream_function(2, 0)()

        del handler, packet  # unused parameters

        TIME=datetime.now().strftime('%Y%m%d%H%M%S%f')[:16]

        return self.stream_function(2, 18)(TIME)

    def _on_s02f31(self, handler, packet):
        """Callback handler for Stream 2, Function 31, Request online

        :param handler: handler the message was received on
        :type handler: :class:`self.secsgem_e82_hsms.handler.HsmsHandler`
        :param packet: complete message received
        :type packet: :class:`self.secsgem_e82_hsms.packets.HsmsPacket`
        """
        if self.controlState.current not in ["ONLINE", "ONLINE_LOCAL", "ONLINE_REMOTE"]:
            return self.stream_function(2, 0)()

        del handler  # unused parameters

        message=self.secs_decode(packet)
        TIME=message.get() # TIME='YYYYmmddHHMMSSXX'

        # set system date
        if len(TIME) not in [14, 16]:
            return self.stream_function(2, 32)(secsgem.TIACK.ERROR)

        YY=TIME[0:4]
        mm=TIME[4:6]
        dd=TIME[6:8]
        HH=TIME[8:10]
        MM=TIME[10:12]
        SS=TIME[12:14]
        XX=TIME[14:16] if len(TIME) == 16 else '00'

        TIME="{}{}{} {}:{}:{}.{}".format(YY,mm,dd,HH,MM,SS,XX)

        print ("set time: {}".format(TIME))
        return self.stream_function(2, 32)(secsgem.TIACK.OK)

        commands.getoutput("sudo timedatectl set-ntp off")
        msg=commands.getoutput('sudo date -s "'+TIME+'"')

        if "cst" not in msg:
            commands.getoutput("sudo timedatectl set-ntp on")
            return self.stream_function(2, 32)(secsgem.TIACK.ERROR)

        return self.stream_function(2, 32)(secsgem.TIACK.OK)

    def _on_s10f3(self, handler, packet):
        """Callback handler for Stream 10, Function 3, Terminal Display Single

        :param handler: handler the message was received on
        :type handler: :class:`self.secsgem_e82_hsms.handler.HsmsHandler`
        :param packet: complete message received
        :type packet: :class:`self.secsgem_e82_hsms.packets.HsmsPacket`
        """
        if self.controlState.current not in ["ONLINE", "ONLINE_LOCAL", "ONLINE_REMOTE"]:
            return self.stream_function(10, 4)(secsgem.ACKC10.NOT_DISPLAYED)

        del handler  # unused parameters

        try:
            action_logger.info("S10F3 message received")
            # Decode S10F3 message
            s10f3_message = self.secs_decode(packet)
            
            action_logger.debug("s10f3_message: {}".format(s10f3_message))
            action_logger.debug("type s10f3_message: {}".format(type(s10f3_message)))
            
            # Parse S10F3 message
            # S10F3 format: <L [2] <B TID> <A TEXT>>
            TID = 0
            TEXT = ""
            
            if hasattr(s10f3_message, '__len__') and len(s10f3_message) >= 2:
                # Extract Terminal ID (first element - Binary)
                if hasattr(s10f3_message[0], 'get'):
                    TID = s10f3_message[0].get()
                else:
                    TID = s10f3_message[0]
                
                # Extract Text (second element - ASCII)
                if hasattr(s10f3_message[1], 'get'):
                    TEXT = s10f3_message[1].get()
                else:
                    TEXT = s10f3_message[1]
            elif hasattr(s10f3_message, 'get'):
                # If it's a single object, try to get the value
                parsed_data = s10f3_message.get()
                if isinstance(parsed_data, (list, tuple)) and len(parsed_data) >= 2:
                    TID = parsed_data[0] if parsed_data[0] is not None else 0
                    TEXT = parsed_data[1] if parsed_data[1] is not None else ""
            
            # Convert TID to integer if it's not already
            if isinstance(TID, bytes):
                TID = int.from_bytes(TID, byteorder='big') if TID else 0
            elif not isinstance(TID, int):
                TID = int(TID) if str(TID).isdigit() else 0
            
            # Ensure TEXT is a string
            if isinstance(TEXT, bytes):
                TEXT = TEXT.decode('utf-8', errors='ignore')
            elif TEXT is None:
                TEXT = ""
            else:
                TEXT = str(TEXT)
            
            # Log the parsed terminal display message
            action_logger.info("Terminal Display - TID: {}, TEXT: '{}'".format(TID, TEXT))
            
            # Display the message on terminal/console
            terminal_msg = "[Terminal Display] TID: {} - {}".format(TID, TEXT)
            print(terminal_msg)
            
            # Send to remote command callback if available for application layer processing
            # if self.remote_commands_callback:
            #     obj = {
            #         'remote_cmd': 'terminal_display',
            #         'TID': TID,
            #         'TEXT': TEXT,
            #         'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            #     }
            #     th = threading.Thread(target=self.remote_commands_callback, args=(obj,))
            #     th.setDaemon(True)
            #     th.start()
            
            # Return S10F4 acknowledgment with OK status
            return self.stream_function(10, 4)(secsgem.ACKC10.ACCEPTED)
            
        except Exception as e:
            self.communicationLogger.error("Error processing S10F3 message: {}".format(e))
            traceback.print_exc()
            return self.stream_function(10, 4)(secsgem.ACKC10.NOT_DISPLAYED)

    def set_alarm(self, alid, UnitID =''): # Mike: 2021/11/26
        e88equipmen_logger.debug("set alarm,UnitID:{}".format(UnitID))
        """The list of the alarms

        :param alid: Alarm id
        :type alid: str/int
        """
        if alid not in self.alarms:
            raise ValueError("Unknown alarm id {}".format(alid))

        '''if not self.alarms[alid].set:
            return'''

        if self.alarms[alid].enabled:
            if not self._spool_enable and (self.controlState.current not in ["ONLINE", "ONLINE_LOCAL", "ONLINE_REMOTE"] or not self.communicationState.isstate("COMMUNICATING")):
                pass
            else:
                try:

                    self.send_prime_message(self.stream_function(5, 1)({"ALCD": self.alarms[alid].code | secsgem.ALCD.ALARM_SET , \
                        "ALID": alid, "ALTX": self.alarms[alid].text}))
                except Exception as err:
                    self.send_stream_function(self.stream_function(9, 9)())
                    raise Exception(err)
        self.alarms[alid].UnitID=UnitID
        
        self.alarms[alid].set=True
        alarm_info={
            'UNITID': UnitID,
            'ALID': alid,
            'ALTX': self.alarms[alid].text,
            'MIANSTATE': 2
        }
        self.UnitAlarmInfo=alarm_info
        self.UnitAlarmList[alid]=alarm_info

        self.trigger_collection_events([self.alarms[alid].ce_on])

    def clear_alarm(self, alid, alarmlevel =''): # Mike: 2021/11/26
        """The list of the alarms

        :param alid: Alarm id
        :type alid: str/int
        """
        if alid not in self.alarms:
            raise ValueError("Unknown alarm id {}".format(alid))

        '''if not self.alarms[alid].set:
            return'''

        if self.alarms[alid].enabled:
            if not self._spool_enable and (self.controlState.current not in ["ONLINE", "ONLINE_LOCAL", "ONLINE_REMOTE"] or not self.communicationState.isstate("COMMUNICATING")):
                pass
            else:
                try:
                    self.send_prime_message(self.stream_function(5, 1)({"ALCD": self.alarms[alid].code , "ALID": alid, "ALTX": self.alarms[alid].text}))
                except Exception as err:
                    self.send_stream_function(self.stream_function(9, 9)())
                    raise Exception(err)

        self.alarms[alid].set=False

        if alid in self.UnitAlarmList:
            del self.UnitAlarmList[alid]
        if self.UnitAlarmInfo.get('ALID')==alid:
            self.UnitAlarmInfo={}

        self.trigger_collection_events([self.alarms[alid].ce_off])

    #####################################
    #      Remote Command Callback
    #####################################
    def _on_rcmd_ABORT(self, COMMANDID, system, ack_params):
        print("\nget abort cmd, param:{}".format([COMMANDID]))
        print("get abort cmd, system:{}, ack_parmas:{}\n".format(system, ack_params))

        if COMMANDID not in self.Transfers.Data:
            ack_params.append(['COMMANDID', 2])
            print("\nCommandID not found.\n")
            self.send_response(self.stream_function(2,42)([3, ack_params]), system)
        elif False and self.SCState in [3, 2, 4] and self.Transfers.Data[COMMANDID].TransferState in [3, 2] and self.Carriers.Data[self.Transfers.Data[COMMANDID].CarrierID].CarrierState in [5, 2, 1, 3]:
            obj={}
            obj['remote_cmd']='abort'
            obj['CommandID']=COMMANDID
            obj['system']=system
            obj['ack_params']=ack_params
            self.COMMANDID=COMMANDID
            if self.remote_commands_callback:
                th=threading.Thread(target=self.remote_commands_callback, args=(obj,))
                th.setDaemon(True)
                th.start()
            else:
                remotecmd_queue.append(obj)

            if self.rcmd_auto_reply:
                self.ResultCode=2
                self.send_response(self.stream_function(2,42)([0, ack_params]), system)

            self.transfer_abort(COMMANDID)
        else:
            print("\nabort cmd can not perform now.\n")
            self.send_response(self.stream_function(2,42)([2, ack_params]), system)
    
    def _on_rcmd_ASSOCIATE(self, CARRIERID, CARRIERLOC, ASSOCIATEDATA, system, ack_params): # Mike: 2021/05/27
        print("\nget associate cmd, param:{}, {}, {}".format(CARRIERID, CARRIERLOC, ASSOCIATEDATA))
        print("get associate cmd, system:{}, ack_parmas:{}\n".format(system, ack_params))

        if CARRIERID not in self.Carriers.Data:
            ack_params.append(['CARRIERID', 2])
            print("\nCarrierID not found.\n")
            self.send_response(self.stream_function(2,42)([3, ack_params]), system)
        elif self.SCState in [3, 2, 4]:
            obj={}
            obj['remote_cmd']='associate'
            obj['CarrierID']=CARRIERID
            obj['CarrierLoc']=CARRIERLOC
            obj['AssociateData']=ASSOCIATEDATA
            obj['system']=system
            obj['ack_params']=ack_params
            self.send_response(self.stream_function(2,42)([0]), system)
            
            if self.remote_commands_callback:
                th=threading.Thread(target=self.remote_commands_callback, args=(obj,))
                th.setDaemon(True)
                th.start()
            else:
                remotecmd_queue.append(obj)

            if self.rcmd_auto_reply:
                self.send_response(self.stream_function(2,42)([0, ack_params]), system)

            if self.Carriers.Data[CARRIERID].CarrierLoc == CARRIERLOC:
                datasets={}
                datasets['AssociateData']=ASSOCIATEDATA
                self.Carriers.set(CARRIERID, datasets)
        else:
            print("\ninstall cmd can not perform now.\n")
            self.send_response(self.stream_function(2,42)([2, ack_params]), system)

    def _on_rcmd_AUTO(self, ZONENAME, system, ack_params):
        print("\nget auto cmd, param:{}".format([]))
        print("get auto cmd, system:{}, ack_parmas:{}\n".format(system, ack_params))

        if self.SCState in [3, 2, 4]:
            obj={}
            obj['remote_cmd']='auto'
            obj['ZoneName']=ZONENAME
            obj['system']=system
            obj['ack_params']=ack_params

            if self.remote_commands_callback:
                th=threading.Thread(target=self.remote_commands_callback, args=(obj,))
                th.setDaemon(True)
                th.start()
            else:
                remotecmd_queue.append(obj)

            if self.rcmd_auto_reply:
                self.send_response(self.stream_function(2,42)([0, ack_params]), system)

        else:
            print("\nauto cmd can not perform now.\n")
            self.send_response(self.stream_function(2,42)([2, ack_params]), system)

    def _on_rcmd_BINDING(self, CARRIERID, LOTID, NEXTSTEP, EQLIST, PRIORITY, system, ack_params): # Mike: 2021/05/27
        print("\nget binding cmd, param:{}, {}, {}, {}, {}".format(CARRIERID, LOTID, NEXTSTEP, EQLIST, PRIORITY))
        print("get binding cmd, system:{}, ack_parmas:{}\n".format(system, ack_params))

        if CARRIERID not in self.Carriers.Data:
            ack_params.append(['CARRIERID', 2])
            print("\nCarrierID not found.\n")
            self.send_response(self.stream_function(2,42)([3, ack_params]), system)
        elif self.SCState in [3, 2, 4]:
            obj={}
            obj['remote_cmd']='binding'
            obj['CarrierID']=CARRIERID
            obj['LotID']=LOTID
            obj['NextStep']=NEXTSTEP
            obj['EQList']=EQLIST
            obj['Priority']=PRIORITY
            obj['system']=system
            obj['ack_params']=ack_params
            self.send_response(self.stream_function(2,42)([0]), system)

            if self.remote_commands_callback:
                th=threading.Thread(target=self.remote_commands_callback, args=(obj,))
                th.setDaemon(True)
                th.start()
            else:
                remotecmd_queue.append(obj)

            if self.rcmd_auto_reply:
                self.send_response(self.stream_function(2,42)([0, ack_params]), system)

            if self.Carriers.Data[CARRIERID].CarrierLoc == CARRIERLOC:
                datasets={}
                datasets['LotID']=LOTID
                datasets['NextStep']=NEXTSTEP
                datasets['EQList']=EQLIST
                datasets['Priority']=PRIORITY
                self.Carriers.set(CARRIERID, datasets)
        else:
            print("\ninstall cmd can not perform now.\n")
            self.send_response(self.stream_function(2,42)([2, ack_params]), system)

    def _on_rcmd_BOOK(self, ZONENAME, system, ack_params):
        print("\nget book cmd, param:{}".format([]))
        print("get book cmd, system:{}, ack_parmas:{}\n".format(system, ack_params))

        if ZONENAME not in self.Zones.Data:
            ack_params.append(['ZONENAME', 2])
            print("\nZonename not found.\n")
            self.send_response(self.stream_function(2,42)([3, ack_params]), system)
        elif self.SCState in [3, 2, 4]:
            obj={}
            obj['remote_cmd']='book'
            obj['ZoneName']=ZONENAME
            obj['system']=system
            obj['ack_params']=ack_params

            if self.remote_commands_callback:
                th=threading.Thread(target=self.remote_commands_callback, args=(obj,))
                th.setDaemon(True)
                th.start()
            else:
                remotecmd_queue.append(obj)

            if self.rcmd_auto_reply:
                self.send_response(self.stream_function(2,42)([0, ack_params]), system)

        else:
            print("\nbook cmd can not perform now.\n")
            self.send_response(self.stream_function(2,42)([2, ack_params]), system)

    def _on_rcmd_CANCEL(self, COMMANDID, system, ack_params):
        print("\nget cancel cmd, param:{}".format([COMMANDID]))
        print("get cancel cmd, system:{}, ack_parmas:{}\n".format(system, ack_params))

        if COMMANDID not in self.Transfers.Data:
            ack_params.append(['COMMANDID', 2])
            print("\nCommandID not found.\n")
            self.send_response(self.stream_function(2,42)([3, ack_params]), system)
        elif False and self.SCState in [3, 2, 4] and self.Transfers.Data[COMMANDID].TransferState in [1]:
            obj={}
            obj['remote_cmd']='cancel'
            obj['CommandID']=COMMANDID
            obj['system']=system
            obj['ack_params']=ack_params

            if self.remote_commands_callback:
                th=threading.Thread(target=self.remote_commands_callback, args=(obj,))
                th.setDaemon(True)
                th.start()
            else:
                remotecmd_queue.append(obj)

            if self.rcmd_auto_reply:
                self.send_response(self.stream_function(2,42)([0, ack_params]), system)

            self.transfer_cancel(COMMANDID)
        else:
            print("\ncancel cmd can not perform now.\n")
            self.send_response(self.stream_function(2,42)([2, ack_params]), system)

    def _on_rcmd_INSTALL(self, CARRIERID, CARRIERLOC, system, ack_params):
        print("\nget install cmd, param:{}".format([CARRIERID, CARRIERLOC]))
        print("get install cmd, system:{}, ack_parmas:{}\n".format(system, ack_params))

        if CARRIERID not in self.Carriers.Data:
            ack_params.append(['CARRIERID', 2])
            print("\nCarrierID not found.\n")
            self.send_response(self.stream_function(2,42)([3, ack_params]), system)
        elif self.SCState in [3, 2, 4]:
            obj={}
            obj['remote_cmd']='install'
            obj['CarrierID']=CARRIERID
            obj['CarrierLoc']=CARRIERLOC
            obj['system']=system
            obj['ack_params']=ack_params

            if self.remote_commands_callback:
                th=threading.Thread(target=self.remote_commands_callback, args=(obj,))
                th.setDaemon(True)
                th.start()
            else:
                remotecmd_queue.append(obj)

            if self.rcmd_auto_reply:
                self.send_response(self.stream_function(2,42)([0, ack_params]), system)

            self.carrier_add(CARRIERID, CARRIERLOC, self.Zones.ZoneMap.get(CARRIERLOC, ''))
        else:
            print("\ninstall cmd can not perform now.\n")
            self.send_response(self.stream_function(2,42)([2, ack_params]), system)

    def _on_rcmd_INFOUPDATE(self, CARRIERID, system, ack_params, **kwargs): # Mike: 2021/08/11
        print("\nget infoupedate cmd, param:{}".format([CARRIERID, kwargs]))
        print("get infoupedate cmd, system:{}, ack_parmas:{}\n".format(system, ack_params))
        if CARRIERID not in self.Carriers.Data:
            ack_params.append(['CARRIERID', 2])
            print("\nCarrierID not found.\n")
            self.send_response(self.stream_function(2,42)([3, ack_params]), system)
        elif self.SCState in [3, 2, 4]:
            obj={}
            obj['remote_cmd']='infoupdate'
            obj['CarrierID']=CARRIERID
            obj['Data']={}
            for key, value in kwargs.items():
                obj['Data'][key]=value
            obj['system']=system
            obj['ack_params']=ack_params

            if self.remote_commands_callback:
                th=threading.Thread(target=self.remote_commands_callback, args=(obj,))
                th.setDaemon(True)
                th.start()
            else:
                remotecmd_queue.append(obj)

            if self.rcmd_auto_reply:
                self.send_response(self.stream_function(2,42)([0]), system)
        else:
            print("\nlocate cmd can not perform now.\n")
            self.send_response(self.stream_function(2,42)([2, ack_params]), system)
            
    def _on_rcmd_INFOUPDATEBYRACK(self, ERACKID, system, ack_params, **kwargs): # 2024/04/18
        print("\nget infoupdatebyrack cmd, param:{}".format([ERACKID, kwargs]))
        print("get infoupdatebyrack cmd, system:{}, ack_parmas:{}\n".format(system, ack_params))
        if ERACKID not in self.Zones.Data:
            ack_params.append(['ERACKID', 2])
            print("\ERACKID not found.\n")
            self.send_response(self.stream_function(2,42)([3, ack_params]), system)
        elif self.SCState in [3, 2, 4]:
            obj={}
            obj['remote_cmd']='infoupdatebyrack'
            obj['ErackID']=ERACKID
            obj['Data']={}
            for key, value in kwargs.items():
                obj['Data'][key]=value
            obj['system']=system
            obj['ack_params']=ack_params
            if self.remote_commands_callback:
                th=threading.Thread(target=self.remote_commands_callback, args=(obj,))
                th.setDaemon(True)
                th.start()
            else:
                remotecmd_queue.append(obj)

            if self.rcmd_auto_reply:
                self.send_response(self.stream_function(2,42)([0]), system)
        else:
            print("\nlocate cmd can not perform now.\n")
            self.send_response(self.stream_function(2,42)([2, ack_params]), system)

    def _on_rcmd_LOCATE(self, CARRIERID, system, ack_params): # Mike: 2020/08/18
        print("\nget locate cmd, param:{}".format([CARRIERID]))
        print("get locate cmd, system:{}, ack_parmas:{}\n".format(system, ack_params))

        if CARRIERID and CARRIERID not in self.Carriers.Data:
            ack_params.append(['CARRIER', 2])
            print("\nCarrierID not found.\n")
            self.send_response(self.stream_function(2,42)([3, ack_params]), system)
        elif self.SCState in [3, 2, 4]:
            obj={}
            obj['remote_cmd']='locate'
            obj['CarrierID']=CARRIERID
            obj['system']=system
            obj['ack_params']=ack_params

            if self.remote_commands_callback:
                th=threading.Thread(target=self.remote_commands_callback, args=(obj,))
                th.setDaemon(True)
                th.start()
            else:
                remotecmd_queue.append(obj)

            if self.rcmd_auto_reply:
                self.send_response(self.stream_function(2,42)([0, ack_params]), system)

            if CARRIERID:
                self.carrier_locate(CARRIERID)
                for key, value in self.failure_map:
                    if value == CARRIERID:
                        self.carrier_locate(key)
            else:
                for carrier in self.Carriers.Data:
                    self.carrier_locate(carrier)
        else:
            print("\nlocate cmd can not perform now.\n")
            self.send_response(self.stream_function(2,42)([2, ack_params]), system)

    def check_carrier_location(self, CARRIERID, CARRIERLOC):
        """Check if the specified CARRIERID is at the specified CARRIERLOC location"""
        if CARRIERID in self.Carriers.Data:
            return self.Carriers.Data[CARRIERID].CarrierLoc == CARRIERLOC
        return False

    def _on_rcmd_SCAN(self, CARRIERID, CARRIERLOC, system, ack_params):
        action_logger.warning("get scan cmd, param:{}".format([CARRIERID, CARRIERLOC, system, ack_params]))
        
        if self.SCState not in [3, 2, 4]:
            print("\nscan cmd can not perform now.\n")
            self.send_response(self.stream_function(2,42)([2, ack_params]), system)
            return

        # Check if the CARRIERID at CARRIERLOC location is correct
        if CARRIERID:
            if self.check_carrier_location(CARRIERID, CARRIERLOC):
                # Inventory matches - No action needed
                print("\n[SCAN] Inventory matches: CarrierID {} at location {} is correct.\n".format(CARRIERID, CARRIERLOC))
                self.send_response(self.stream_function(2,42)([0, ack_params]), system)
                return
            else:
                # Inventory is not matches - need manual scan processing
                print("\n[SCAN] Inventory mismatch: CarrierID {} not at location {}, need manual scan.\n".format(CARRIERID, CARRIERLOC))

        # Send ACK first to indicate command received
        self.send_response(self.stream_function(2,42)([0, ack_params]), system)

        # Create manual scan command object
        obj={}
        obj['remote_cmd']='scan'
        obj['CarrierLoc']=CARRIERLOC
        obj['system']=system
        obj['ack_params']=ack_params
        obj['expected_carrier_id']=CARRIERID  # Save expected CarrierID
        if CARRIERID:
            obj['CarrierID']=CARRIERID

        # Send to remote_commands_callback for processing
        if self.remote_commands_callback:
            th=threading.Thread(target=self.remote_commands_callback, args=(obj,))
            th.setDaemon(True)
            th.start()
        else:
            remotecmd_queue.append(obj)

    def process_scan_result(self, CARRIERLOC, expected_carrier_id, actual_carrier_id, IDREADSTATUS=0):
        """Process scan result and send corresponding events"""
        action_logger.info("process_scan_result:carrierloc={}, expected_carrier_id={}, actual_carrier_id={}, IDREADSTATUS={}".format(CARRIERLOC, expected_carrier_id, actual_carrier_id, IDREADSTATUS))
        # print("\n[SCAN] Processing scan result: location={}, expected={}, actual={}, status={}".format(
            # CARRIERLOC, expected_carrier_id, actual_carrier_id, IDREADSTATUS))
        
        # 1. Send CarrierIDRead event
        if actual_carrier_id:
            self.carrier_id_read(actual_carrier_id, CARRIERLOC, IDREADSTATUS)
        else:
            # If no CarrierID is read, use failure status
            self.carrier_id_read('', CARRIERLOC, 1)
        
        # 2. If there is expected CarrierID and it doesn't match actual, need to perform remove and install operations
        if expected_carrier_id and expected_carrier_id != actual_carrier_id:
            # Send CarrierRemoveCompleted event (remove original CarrierID)
            if expected_carrier_id in self.Carriers.Data:
                print("\n[SCAN] Remove original CarrierID: {}".format(expected_carrier_id))
                self.carrier_kill(expected_carrier_id)
            
            # Send CarrierInstallCompleted event (install read CarrierID)
            if actual_carrier_id:
                print("\n[SCAN] Install read CarrierID: {}".format(actual_carrier_id))
                carrier_zone = self.Zones.ZoneMap.get(CARRIERLOC, '')
                self.carrier_add(actual_carrier_id, CARRIERLOC, carrier_zone)

    def _on_rcmd_MANUAL(self, ZONENAME, system, ack_params):
        print("\nget manual cmd, param:{}".format([]))
        print("get manual cmd, system:{}, ack_parmas:{}\n".format(system, ack_params))

        if self.SCState in [3, 2, 4]:
            obj={}
            obj['remote_cmd']='manual'
            obj['ZoneName']=ZONENAME
            obj['system']=system
            obj['ack_params']=ack_params

            if self.remote_commands_callback:
                th=threading.Thread(target=self.remote_commands_callback, args=(obj,))
                th.setDaemon(True)
                th.start()
            else:
                remotecmd_queue.append(obj)

            if self.rcmd_auto_reply:
                self.send_response(self.stream_function(2,42)([0, ack_params]), system)

        else:
            print("\nmanual cmd can not perform now.\n")
            self.send_response(self.stream_function(2,42)([2, ack_params]), system)

    def _on_rcmd_PAUSE(self, system, ack_params):
        print("\nget pause cmd, param:{}".format([]))
        print("get pause cmd, system:{}, ack_parmas:{}\n".format(system, ack_params))

        if self.SCState in [3]:
            obj={}
            obj['remote_cmd']='sc_pause' #2022/08/09 Chi 
            obj['system']=system
            obj['ack_params']=ack_params
            
            action_logger.warning("self.remote_commands_callback:{}".format(self.remote_commands_callback))
            if self.remote_commands_callback:
                action_logger.error("78778")
                th=threading.Thread(target=self.remote_commands_callback, args=(obj,))
                th.setDaemon(True)
                th.start()
            else:
                action_logger.error("99999")
                remotecmd_queue.append(obj)

            action_logger.warning("self.rcmd_auto_reply:{}".format(self.rcmd_auto_reply))
            if self.rcmd_auto_reply:
                self.send_response(self.stream_function(2,42)([0, ack_params]), system)

            self.pause()
        else:
            print("\npause cmd can not perform now.\n")
            self.send_response(self.stream_function(2,42)([2, ack_params]), system)

    def _on_rcmd_REMOVE(self, CARRIERID, system, ack_params):
        print("\nget remove cmd, param:{}".format([]))
        print("get remove cmd, system:{}, ack_parmas:{}\n".format(system, ack_params))

        if CARRIERID not in self.Carriers.Data:
            ack_params.append(['CARRIERID', 2])
            print("\nCarrierID not found.\n")
            self.send_response(self.stream_function(2,42)([3, ack_params]), system)
        elif self.SCState in [3, 2, 4] and self.Carriers.Data[CARRIERID].CarrierState in [5, 4, 1, 3]:
            obj={}
            obj['remote_cmd']='remove'
            obj['CarrierID']=CARRIERID
            obj['system']=system
            obj['ack_params']=ack_params

            if self.remote_commands_callback:
                th=threading.Thread(target=self.remote_commands_callback, args=(obj,))
                th.setDaemon(True)
                th.start()
            else:
                remotecmd_queue.append(obj)

            if self.rcmd_auto_reply:
                self.send_response(self.stream_function(2,42)([0, ack_params]), system)

            self.carrier_kill(CARRIERID)
        else:
            print("\nremove cmd can not perform now.\n")
            self.send_response(self.stream_function(2,42)([2, ack_params]), system)

    def _on_rcmd_RESUME(self, system, ack_params):
        print("\nget resume cmd, param:{}".format([]))
        print("get resume cmd, system:{}, ack_parmas:{}\n".format(system, ack_params))

        if self.SCState in [2, 4]:
            obj={}
            obj['remote_cmd']='sc_resume'  #2022/08/09 Chi 
            obj['system']=system
            obj['ack_params']=ack_params

            if self.remote_commands_callback:
                th=threading.Thread(target=self.remote_commands_callback, args=(obj,))
                th.setDaemon(True)
                th.start()
            else:
                remotecmd_queue.append(obj)

            if self.rcmd_auto_reply:
                self.send_response(self.stream_function(2,42)([0, ack_params]), system)

            self.resume()
        else:
            print("\nresume cmd can not perform now.\n")
            self.send_response(self.stream_function(2,42)([2, ack_params]), system)

    def _on_rcmd_RETRY(self, ERRORID, system, ack_params):
        print("\nget retry cmd, param:{}".format([ERRORID]))
        print("get retry cmd, system:{}, ack_parmas:{}\n".format(system, ack_params))

        if False and self.active_alarms and self.SCState in [3, 2, 4] and self.Transfers.Data[self.active_alarms[ERRORID]['CommandID']].TransferState in [3]:
            obj={}
            obj['remote_cmd']='retry'
            obj['ErrorID']=ERRORID
            obj['system']=system
            obj['ack_params']=ack_params

            if self.remote_commands_callback:
                th=threading.Thread(target=self.remote_commands_callback, args=(obj,))
                th.setDaemon(True)
                th.start()
            else:
                remotecmd_queue.append(obj)

            if self.rcmd_auto_reply:
                self.send_response(self.stream_function(2,42)([0, ack_params]), system)
        else:
            print("\nretry cmd can not perform now.\n")
            self.send_response(self.stream_function(2,42)([2, ack_params]), system)

    def _on_rcmd_PICKUPAUTH(self, SHELFID, system, ack_params):
        print("\nget pickupauth cmd, param:{}".format([SHELFID]))
        print("get pickupauth cmd, system:{}, ack_parmas:{}\n".format(system, ack_params))

        if self.SCState in [3, 2, 4]:
            obj={}
            obj['remote_cmd']='pickupauth'
            obj['ShelfID']=SHELFID
            obj['system']=system
            obj['ack_params']=ack_params

            if self.remote_commands_callback:
                th=threading.Thread(target=self.remote_commands_callback, args=(obj,))
                th.setDaemon(True)
                th.start()
            else:
                remotecmd_queue.append(obj)

            if self.rcmd_auto_reply:
                self.send_response(self.stream_function(2,42)([0, ack_params]), system)
        else:
            print("\npickupauth cmd can not perform now.\n")
            self.send_response(self.stream_function(2,42)([2, ack_params]), system)

    def _on_ercmd_TRANSFER(self, COMMANDINFO, TRANSFERINFO, system, ack_params):
        print("\nget transfer cmd, param:{}".format([COMMANDINFO, TRANSFERINFO]))
        print("get transfer cmd, system:{}, ack_parmas:{}\n".format(system, ack_params))

        CommandID=COMMANDINFO[0][0][1]
        Priority=COMMANDINFO[0][1][1]
        CarrierID=TRANSFERINFO[0][0][1]
        Source=TRANSFERINFO[0][1][1]
        Dest=TRANSFERINFO[0][2][1]

        if CommandID in self.Transfers.Data:
            ack_params.append(['COMMANDID', 2])
            print("\nCommandID already exists.\n")
            self.send_response(self.stream_function(2,50)([3, ack_params]), system)
        elif CarrierID not in self.Carriers.Data:
            ack_params.append(['CARRIERID', 2])
            print("\CARRIERID not found.\n")
            self.send_response(self.stream_function(2,50)([3, ack_params]), system)
        elif Priority > 99:
            ack_params.append(['PRIORITY', 2])
            print("\PRIORITY error.\n")
            self.send_response(self.stream_function(2,50)([3, ack_params]), system)
            return
        elif self.SCState in [3, 2, 4] and CommandID not in self.Transfers.Data and self.Carriers.Data[CarrierID].CarrierState in [1, 4]:

            obj={}
            obj['remote_cmd']='transfer'
            obj['commandinfo']={'CommandID':CommandID, 'Priority':Priority}
            obj['transferinfo']={'CarrierID':CarrierID, 'Source':Source, 'Dest':Dest}
            obj['system']=system
            obj['ack_params']=ack_params

            if self.remote_commands_callback:
                th=threading.Thread(target=self.remote_commands_callback, args=(obj,))
                th.setDaemon(True)
                th.start()
            else:
                remotecmd_queue.append(obj)

            if self.rcmd_auto_reply:
                self.send_response(self.stream_function(2, 50)([0, ack_params]), system)

            self.transfer_cmd(CommandID, Priority, CarrierID, Source, Dest)
        else:
            print("\ntransfer cmd can not perform now.\n")
            self.send_response(self.stream_function(2,42)([2, ack_params]), system)

    #####################################
    #       State Machine Callback
    #####################################
    ''' SCState '''

    def _on_SC_state_SC_INIT(self, _):  # 
        self.SCState=1

    def _on_SC_state_PAUSED(self, _):  # 
        self.SCState=2

    def _on_SC_state_AUTO(self, _):  # 
        self.SCState=3

    def _on_SC_state_PAUSING(self, _):  # 
        self.SCState=4

    def _on_SC_state_initial(self, _):  # 1, send collection event (SCAutoInitiated)
        self.trigger_collection_events([SCAutoInitiated])

    def _on_SC_state_initial_done(self, _):  # 2, send collection event (SCPaused)
        self.trigger_collection_events([SCPaused])

    def _on_SC_state_resume(self, _):  # 3, 6, send collection event (SCAutoCompleted)
        self.trigger_collection_events([SCAutoCompleted])

    def _on_SC_state_pause(self, _):  # 4, send collection event (SCPauseInitiated)
        self.trigger_collection_events([SCPauseInitiated])

    def _on_SC_state_pause_completed(self, _):  # 5, send collection event (SCPauseCompleted)
        self.trigger_collection_events([SCPauseCompleted])
        

    #####################################
    #       Normal Function Define
    #####################################
    def initial(self):
        self.State.initial_done()

    def pause(self):
        # Check if we can pause before attempting state transition
        if self.State.current == 'AUTO':
            self.State.pause()
            th=threading.Thread(target=self.pausing,)
            th.setDaemon(True)
            th.start()
        else:
            # Log the invalid state transition attempt
            action_logger.warning("Cannot pause: current state is {}, expected AUTO".format(self.State.current))
            # Optionally sync the SCState with actual state
            if self.State.current == 'SC_INIT':
                self.SCState = 1
            elif self.State.current == 'PAUSED':
                self.SCState = 2
            elif self.State.current == 'AUTO':
                self.SCState = 3
            elif self.State.current == 'PAUSING':
                self.SCState = 4
    
    def pausing(self):
        check=True
        while check:
            if self.SCState != 4:
                break
            check=False
            for key, TransferCommand in self.Transfers.Data.items():
                if TransferCommand.TransferState not in [0, 1]:
                    check=True
            sleep(0.5)
        else:
            self.State.pause_completed()
            # sleep(1)
            # self.State.initial_done()

    def resume(self):
        # Check if we can resume before attempting state transition
        if self.State.current in ['PAUSED', 'PAUSING']:
            self.State.resume()
        else:
            # Log the invalid state transition attempt
            action_logger.warning("Cannot resume: current state is {}, expected PAUSED or PAUSING".format(self.State.current))
            # Optionally sync the SCState with actual state
            if self.State.current == 'SC_INIT':
                self.SCState = 1
            elif self.State.current == 'PAUSED':
                self.SCState = 2
            elif self.State.current == 'AUTO':
                self.SCState = 3
            elif self.State.current == 'PAUSING':
                self.SCState = 4

    def carrier_wait_in(self, CARRIERID, CARRIERLOC, CARRIERZONENAME, NoIDRead=False):
        if CARRIERID not in self.Carriers.Data:
            self.Carriers.Data[CARRIERID]=Carrier(self, CARRIERID)
            self.Carriers.Data[CARRIERID].InstallTime=datetime.now().strftime('%Y%m%d%H%M%S%f')[:16]
        if not NoIDRead:
            self.Carriers.Data[CARRIERID].CarrierIDRead=CARRIERID
        last_zone=self.Carriers.Data[CARRIERID].CarrierZoneName
        self.Carriers.Data[CARRIERID].CarrierLoc=CARRIERLOC
        self.Carriers.Data[CARRIERID].CarrierZoneName=CARRIERZONENAME
        self.Carriers.Data[CARRIERID].State.wait_in()
        if last_zone != CARRIERZONENAME:
            if last_zone:
                self.Zones.Data[last_zone].capacity_increase()
            self.Zones.Data[CARRIERZONENAME].capacity_decrease()

    def carrier_transfer(self, CARRIERID, DEST):
        if CARRIERID in self.Carriers.Data:
            self.Carriers.Data[CARRIERID].Dest=DEST
            if self.Carriers.Data[CARRIERID].State.current == 'ALTERNATE':
                self.Carriers.Data[CARRIERID].State.alternated_transfer()
            else:
                self.Carriers.Data[CARRIERID].State.transfer()
            self.Zones.Data[self.Carriers.Data[CARRIERID].CarrierZoneName].capacity_increase()
            return True
        return False

    def carrier_store(self, CARRIERID, CARRIERLOC, CARRIERZONENAME):
        if CARRIERID in self.Carriers.Data:
            self.Carriers.Data[CARRIERID].Dest=''
            self.Carriers.Data[CARRIERID].CarrierLoc=CARRIERLOC
            self.Carriers.Data[CARRIERID].CarrierZoneName=CARRIERZONENAME
            self.Carriers.Data[CARRIERID].State.store()
            self.Zones.Data[CARRIERZONENAME].capacity_decrease()
            return True
        return False

    def carrier_wait_out(self, CARRIERID, CARRIERLOC, CARRIERZONENAME, PORTTYPE):
        if CARRIERID not in self.Carriers.Data:
            self.Carriers.Data[CARRIERID]=Carrier(self, CARRIERID)
            self.Carriers.Data[CARRIERID].InstallTime=datetime.now().strftime('%Y%m%d%H%M%S%f')[:16]
        if self.Carriers.Data[CARRIERID].State.current not in ['none', 'WAIT_OUT', 'WAIT_OUT_2']:
            return False
        last_state=self.Carriers.Data[CARRIERID].State.current
        last_zone=self.Carriers.Data[CARRIERID].CarrierZoneName
        self.Carriers.Data[CARRIERID].Dest=''
        self.Carriers.Data[CARRIERID].CarrierLoc=CARRIERLOC
        self.Carriers.Data[CARRIERID].CarrierZoneName=CARRIERZONENAME
        self.Carriers.Data[CARRIERID].PortType=PORTTYPE
        self.Carriers.Data[CARRIERID].State.wait_out()
        if last_zone != CARRIERZONENAME:
            if last_zone:
                self.Zones.Data[last_zone].capacity_increase()
            self.Zones.Data[CARRIERZONENAME].capacity_decrease()
        return True

    def carrier_remove(self, CARRIERID, HANDOFFTYPE):
        if CARRIERID in self.Carriers.Data:
            self.Carriers.Data[CARRIERID].HandoffType=HANDOFFTYPE
            self.Carriers.Data[CARRIERID].State.remove()
            self.Zones.Data[self.Carriers.Data[CARRIERID].CarrierZoneName].capacity_increase()
            while self.Carriers.Data[CARRIERID].State.current != 'none':
                sleep(0.5)
            del self.Carriers.Data[CARRIERID]
            return True
        return False

    def carrier_alternated(self, CARRIERID, COMMANDID, CARRIERLOC, CARRIERZONENAME, DEST):
        if CARRIERID in self.Carriers.Data:
            self.Carriers.Data[CARRIERID].CommandID=COMMANDID
            self.Carriers.Data[CARRIERID].CarrierLoc=CARRIERLOC
            self.Carriers.Data[CARRIERID].CarrierZoneName=CARRIERZONENAME
            self.Carriers.Data[CARRIERID].Dest=DEST
            self.Carriers.Data[CARRIERID].State.alternated()
            self.Zones.Data[CARRIERZONENAME].capacity_decrease()
            return True
        return False

    def carrier_resume(self, CARRIERID):
        if CARRIERID in self.Carriers.Data:
            self.Carriers.Data[CARRIERID].State.resume()
            self.Zones.Data[self.Carriers.Data[CARRIERID].CarrierZoneName].capacity_increase()
            return True
        return False

    def carrier_add(self, CARRIERID, CARRIERLOC, CARRIERZONENAME):
        Zone=CARRIERZONENAME
        if not Zone:
            Zone=self.Zones.ZoneMap.get(CARRIERLOC, '')
        if CARRIERID not in self.Carriers.Data:
            self.Carriers.Data[CARRIERID]=Carrier(self, CARRIERID)
            self.Carriers.Data[CARRIERID].InstallTime=datetime.now().strftime('%Y%m%d%H%M%S%f')[:16]
            self.Carriers.Data[CARRIERID].CarrierID=CARRIERID
            self.Carriers.Data[CARRIERID].CarrierLoc=CARRIERLOC
            self.Carriers.Data[CARRIERID].CarrierZoneName=Zone
            self.Carriers.Data[CARRIERID].State.add_carrier()
            if Zone:
                self.Zones.Data[Zone].capacity_decrease()
            return True
        else:
            last_zone=self.Carriers.Data[CARRIERID].CarrierZoneName
            self.Carriers.Data[CARRIERID].CarrierLoc=CARRIERLOC
            if Zone:
                self.Carriers.Data[CARRIERID].CarrierZoneName=Zone
            self.Carriers.Data[CARRIERID].State.mod_carrier()
            if Zone:
                if last_zone != Zone:
                    self.Zones.Data[last_zone].capacity_increase()
                    self.Zones.Data[Zone].capacity_decrease()

    def carrier_kill(self, CARRIERID):
        e88equipmen_logger.debug("carrier_kill:{}".format(CARRIERID))
        if CARRIERID in self.Carriers.Data:
            self.Zones.Data[self.Carriers.Data[CARRIERID].CarrierZoneName].capacity_increase()
            self.Carriers.Data[CARRIERID].State.kill_carrier()
            while self.Carriers.Data[CARRIERID].State.current != 'none':
                sleep(0.5)
            del self.Carriers.Data[CARRIERID]
            return True
        return False
    
    def carrier_locate(self, CARRIERID):
        if CARRIERID:
            if CARRIERID in self.Carriers.Data:
                self.Carriers.Data[CARRIERID].locate()
                return True
            return False
        else:
            for CarrierID in self.Carriers.Data:
                self.Carriers.Data[CARRIERID].locate()
            return True
    
    def carrier_id_read(self, CARRIERID, CARRIERLOC, IDREADSTATUS):
        if CARRIERID and CARRIERID not in self.Carriers.Data:
            self.Carriers.Data[CARRIERID]=Carrier(self, CARRIERID)
            self.Carriers.Data[CARRIERID].CarrierID=CARRIERID
            self.Carriers.Data[CARRIERID].CarrierLoc=CARRIERLOC
            self.Carriers.Data[CARRIERID].InstallTime=datetime.now().strftime('%Y%m%d%H%M%S%f')[:16]
            self.Carriers.Data[CARRIERID].id_read(CARRIERID, IDREADSTATUS)
            return ''
        else:
            ID=FailureIDGEN(CARRIERLOC, CARRIERID)
            self.Carriers.Data[ID]=Carrier(self, ID)
            self.Carriers.Data[ID].CarrierID=ID
            self.Carriers.Data[ID].InstallTime=datetime.now().strftime('%Y%m%d%H%M%S%f')[:16]
            self.Carriers.Data[ID].id_read(ID, 2)
            return ID
    
    def carrier_rename(self, CARRIERID, NEWCARRIERID):
        return self.Carriers.mod(CARRIERID, NEWCARRIERID)
    
    def zone_capacity_change(self, ZONENAME, CAPACITY):
        self.Zones.Data[ZONENAME].capacity_change(CAPACITY)

    def transfer_cmd(self, COMMANDID, PRIORITY, CARRIERID, CARRIERLOC, DEST):
        if COMMANDID not in self.Transfers.Data:
            self.Transfers.Data[COMMANDID]=TransferCommand(self, COMMANDID)
            self.Transfers.Data[COMMANDID].CarrierID=CARRIERID
            self.Transfers.Data[COMMANDID].CarrierLoc=CARRIERLOC
            if CARRIERID in self.Carriers.Data:
                self.Transfers.Data[COMMANDID].CarrierLoc=self.Carriers.Data[CARRIERID].CarrierLoc
                self.Transfers.Data[COMMANDID].CarrierZoneName=self.Carriers.Data[CARRIERID].CarrierZoneName
            self.Transfers.Data[COMMANDID].Dest=DEST
            self.Transfers.Data[COMMANDID].Priority=PRIORITY
            self.Transfers.Data[COMMANDID].State.queue()

    def transfer_start(self, COMMANDID):
        self.Transfers.Data[COMMANDID].State.transfer()
        self.carrier_transfer(self.Transfers.Data[COMMANDID].CarrierID, self.Transfers.Data[COMMANDID].Dest)

    def transfer_pause(self, COMMANDID):
        self.Transfers.Data[COMMANDID].State.pause()

    def transfer_resume(self, COMMANDID):
        self.Transfers.Data[COMMANDID].State.resume()

    def transfer_complete(self, COMMANDID, DEST=''):
        if DEST:
            self.Transfers.Data[COMMANDID].Dest=DEST
        self.Transfers.Data[COMMANDID].State.complete()
        while self.Transfers.Data[COMMANDID].State.current != 'none':
            sleep(0.5)
        del self.Transfers.Data[COMMANDID]

    def transfer_cancel(self, COMMANDID):
        self.Transfers.Data[COMMANDID].State.cancel()

    def transfer_cancel_succ(self, COMMANDID):
        self.Transfers.Data[COMMANDID].State.cancel_completed()
        while self.Transfers.Data[COMMANDID].State.current != 'none':
            sleep(0.5)
        del self.Transfers.Data[COMMANDID]

    def transfer_cancel_failed(self, COMMANDID):
        self.Transfers.Data[COMMANDID].State.cancel_failed()

    def transfer_abort(self, COMMANDID):
        self.Transfers.Data[COMMANDID].State.abort()

    def transfer_abort_succ(self, COMMANDID):
        self.Transfers.Data[COMMANDID].State.abort_completed()
        while self.Transfers.Data[COMMANDID].State.current != 'none':
            sleep(0.5)
        del self.Transfers.Data[COMMANDID]

    def transfer_abort_failed(self, COMMANDID):
        self.Transfers.Data[COMMANDID].State.abort_failed()

    def enable_event(self, CEID_list):
        for CEID in CEID_list:
            if CEID in self.registered_collection_events:
                self.registered_collection_events[CEID].enabled=True

    def disable_event(self, CEID_list):
        for CEID in CEID_list:
            if CEID in self.registered_collection_events:
                self.registered_collection_events[CEID].enabled=False

    def set_shelf_state(self, state):
        """Set the shelf state
        
        :param state: Shelf state value
        :type state: int
        
        States:
        1: AVAIL
        2: PROHIBIT  
        3: PICKUP (Manual)
        4: RESERVED (Manual)
        5: RESERVED (AUTO)
        """
        if state in [1, 2, 3, 4, 5]:
            self.ShelfState = state
        else:
            raise ValueError("Invalid shelf state. Must be 1-5 (AVAIL, PROHIBIT, PICKUP(Manual), RESERVED(Manual), RESERVED(AUTO))")

    def process_locstatechg(self, SHELFID, SHELFSTATE_VALUE):
        """Process LOCSTATECHG command for specific shelf
        
        :param SHELFID: Shelf identifier (e.g. 'TBD01P01')
        :type SHELFID: str
        :param SHELFSTATE_VALUE: New shelf state value (1-5)
        :type SHELFSTATE_VALUE: int
        :return: Success status
        :rtype: bool
        """
        try:
            # Find the zone containing this shelf
            target_zone = None
            for zonename, zone in self.Zones.Data.items():
                if hasattr(zone, 'ShelfUnit') and SHELFID in zone.ShelfUnit:
                    target_zone = zone
                    break
                elif hasattr(zone, 'StockerUnit') and SHELFID in zone.StockerUnit:
                    target_zone = zone
                    break
            
            if target_zone:
                # Update ShelfState in the zone
                target_zone.set_shelf_state(SHELFID, SHELFSTATE_VALUE)
                
                # Update ShelfUnit state if it exists
                if hasattr(target_zone, 'ShelfUnit') and SHELFID in target_zone.ShelfUnit:
                    old_state = target_zone.ShelfUnit[SHELFID].get('ShelfUnitState', 1)
                    target_zone.ShelfUnit[SHELFID]['ShelfUnitState'] = SHELFSTATE_VALUE
                    
                    e88equipmen_logger.info("LOCSTATECHG: Updated {} from state {} to {}".format(
                        SHELFID, old_state, SHELFSTATE_VALUE))
                    
                return True
            else:
                e88equipmen_logger.warning("LOCSTATECHG: ShelfID {} not found in any zone".format(SHELFID))
                return False
                
        except Exception as e:
            e88equipmen_logger.error("LOCSTATECHG processing error: {}".format(e))
            return False

    def _on_rcmd_LOCSTATECHG(self, SHELFID, SHELFSTATE, system, ack_params):
        print("\nget locstatechg cmd, param:{}".format([SHELFID, SHELFSTATE]))
        print("get locstatechg cmd, system:{}, ack_parmas:{}\n".format(system, ack_params))

        # 檢查 SC 狀態
        if self.SCState not in [3, 2, 4]:
            print("\nlocstatechg cmd can not perform now.\n")
            self.send_response(self.stream_function(2,42)([2, ack_params]), system)
            return

        # 驗證 SHELFSTATE 參數
        if SHELFSTATE not in self.shelf_state_mapping:
            ack_params.append(['SHELFSTATE', 2])
            print("\nInvalid SHELFSTATE: {}.\n".format(SHELFSTATE))
            self.send_response(self.stream_function(2,42)([3, ack_params]), system)
            return

        # 回應 HCACK = 0x04 (非同步已接受指令)
        self.send_response(self.stream_function(2,42)([4, ack_params]), system)

        # 處理指令
        shelf_state_value = self.shelf_state_mapping[SHELFSTATE]
        success = self.process_locstatechg(SHELFID, shelf_state_value)

        # 建立遠端指令物件發送到應用層處理
        obj={}
        obj['remote_cmd']='locstatechg'
        obj['ShelfID']=SHELFID
        obj['ShelfState']=SHELFSTATE
        obj['ShelfStateValue']=shelf_state_value
        obj['system']=system
        obj['ack_params']=ack_params
        obj['success']=success

        # 發送到遠端指令處理
        if self.remote_commands_callback:
            th=threading.Thread(target=self.remote_commands_callback, args=(obj,))
            th.setDaemon(True)
            th.start()
        else:
            remotecmd_queue.append(obj)

        if success:
            print("\nLOCSTATECHG completed successfully for ShelfID: {}\n".format(SHELFID))
        else:
            print("\nLOCSTATECHG failed for ShelfID: {}\n".format(SHELFID))

