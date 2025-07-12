# -*- coding: utf-8 -*-
import collections
import traceback
import threading
import time
import socket
import re
import os
import logging.handlers as log_handler
import logging
import argparse
import semi.e88_equipment as E88 #can use singleton
import global_variables
from global_variables import Vehicle
from global_variables import output
from global_variables import remotecmd_queue
import tools
from web_service_log import erack_logger
import json
import copy
from pprint import pformat

import queue
import alarms
from web_service_log import *
#from workstation.order_mgr import OrderMgr
from workstation.eq_mgr import EqMgr

class GetSocketNullString():
    pass

class GyroErackAdapter(threading.Thread):
    #def __init__(self, idx, name, mac, zoneID, func, loc, Transfers, Carriers, Zones, ip, port=5000, ZoneSize=12, ZoneType=1):
    def update_params(self, setting):
        self.idx=setting['idx']
        self.device_id=setting['eRackID']
        self.mac=setting['mac']
        self.groupID=setting['groupID'] if setting['groupID'] else setting['eRackID'] #9/26
        self.zone=setting['zone']
        self.link_zone=setting.get('link', '') #v8.24F for SJ
        if not self.link_zone: self.link_zone=self.zone #v8.24F for SJ
        
        self.ip=setting['ip']
        self.port=int(setting.get('port', 5000))
        #self.func=setting.get('func', '')
        try:
            self.func=json.loads(setting.get('func', {})) #chocp 2023/9/11
        except:
            self.func={}
        self.loc=setting.get('location', '')
        self.type=setting.get('type', '3x4')
        self.zonesize=int(setting.get('zonesize', 12))
        
        res=re.match(r'(\d+)x(\d+)', self.type)  #fix2
        self.rows=int(res.group(1))
        self.columns=int(res.group(2))
        self.slot_num=self.rows*self.columns

        def format_parse(validSlotType, slot_num): #2023/12/26 chocp
            config={}
            if validSlotType:
                slot_type_list=validSlotType.split(',')
                for desc in slot_type_list:
                    key=desc.split(':')[0].strip()
                    config[key]=[]
                    try:
                        value=desc.split(':')[1]
                        for port in value.split('|'):
                            config[key].append(int(port.strip()))
                    except:
                        for port_no in range(1, slot_num+1): #
                            config[key].append(port_no) 
                        pass
            return config #{'8S':[1,2,3], '12S':[7,8,15], '12C':[1,2,3,4,5,6,7,8,9,10,11,12]}

        self.validSlotType=format_parse(setting.get('validCarrierType', ''), self.slot_num) 
        
        #for auto dispatch
        self.autodispatch=setting.get('AutoDispatch', False) #3/17 chi
        self.waterlevelhigh=int(setting.get('WaterLevelHigh', 80)) #3/17 chi
        self.waterlevellow=int(setting.get('WaterLevelLow', 20)) #3/17 chi
        self.returnto=setting.get('ReturnTo', 'None' ) #3/17 chi
        self.batchsize=int(setting.get('BatchSize', 4)) #3/17 chi
        self.water_level_table={} # Mike: 2022/06/14
        if setting.get('alarmEmptyEnable', False):
            self.water_level_table['empty']=alarms.ErackLevelEmptyWarning
        if setting.get('alarmLowEnable', False):
            self.water_level_table['low']=alarms.ErackLevelLowWarning
        if setting.get('alarmHighEnable', False):
            self.water_level_table['high']=alarms.ErackLevelHighWarning
        if setting.get('alarmFullEnable', False):
            self.water_level_table['full']=alarms.ErackLevelFullWarning
 
    def __init__(self, secsgem_e88_h, setting, Transfers, Carriers, Zones):
        self.model='Shelf'
        self.zonetype=1
        self.secsgem_e88_h=secsgem_e88_h
        
        self.E88_Transfers=Transfers
        self.E88_Carriers=Carriers
        self.E88_Zones=Zones
        self.zonestate='auto'

        self.available=0 #9/26 chocp
        self.water_level=''
        self.last_water_level=''

        self.update_params(setting)
        print(self.device_id, self.rows, self.columns, self.slot_num)

        self.thread_stop=False
        self.sock=0
        self.alarm_table={20002:[], 20003:[], 20051:0, 20005:[]}
        self.associate_queue=collections.deque()
        self.last_erack_status='None'
        self.connected=False
        self.sync=False
        self.syncing_time=0
        self.erack_status='DOWN'
        self.sendby=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        #chocp fix 2021/119
        self.read_carriers=[]
        self.last_carriers=[]
        self.carriers=[]
        self.lots=[]

        for i in range(self.rows):
            for j in range(self.columns):
                self.read_carriers.append({'carrierID':''})
                self.lots.append({'lotID':'', 'stage':'', 'product':'', 'machine':'', 'desc':'',"lpt":"", "qty":"", 'booked':0, 'booked_for':'','recipe':''})
                self.last_carriers.append({'box_color':'', 'area_id':'', 'checked':1, 'carrierID':'', 'status':'down', 'idx':self.columns*i+j, 'rack_row':i+1, 'rack_col':j+1, 'errorCode':'', 'create_time':0,'direction':'', 'direction_target':'','transfering':False})
                self.carriers.append({'box_color':'', 'area_id':'', 'checked':1, 'carrierID':'', 'status':'down', 'idx':self.columns*i+j, 'rack_row':i+1, 'rack_col':j+1, 'errorCode':'', 'create_time':0,'direction':'', 'direction_target':'','transfering':False})

        try:
            sector=json.loads(setting.get('sector', '{}'))
            for area_id, slots_string in sector.items():
                #print(area_id, slots_string)
                for slot_no_str in slots_string.split(','):
                    slot_no=int(slot_no_str)
                    self.carriers[slot_no-1]['area_id']=area_id
                    self.carriers[slot_no-1]['box_color']=global_variables.color_sectors.get(area_id)
                    self.last_carriers[slot_no-1]['area_id']=area_id
                    self.last_carriers[slot_no-1]['box_color']=global_variables.color_sectors.get(area_id)
        except:
            traceback.print_exc()
            pass

        self.zone_list={}
        self.turn=0 #every 3 echo, update 1 relative lot info
        self.begin=0
        self.end=0

        self.raw_logger=logging.getLogger(self.device_id+'_raw') # Mike: 2021/05/17
        for h in self.raw_logger.handlers[:]: # Mike: 2021/09/22
            self.raw_logger.removeHandler(h)
            h.close()
        self.raw_logger.setLevel(logging.DEBUG)

        fileHandler=log_handler.TimedRotatingFileHandler(os.path.join("log", "Gyro_{}_raw.log".format(self.device_id)), when='midnight', interval=1, backupCount=7)
        fileHandler.setLevel(logging.INFO)
        fileHandler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s"))
        self.raw_logger.addHandler(fileHandler)

        self.heart_beat=0
        threading.Thread.__init__(self)
        self.lock=threading.Lock()

    def zone_capacity_change(self, zonename, change): # Mike: 2022/06/14
        if change == 'Inc':
            self.E88_Zones.Data[zonename].capacity_increase()
        elif change == 'Dec':
            self.E88_Zones.Data[zonename].capacity_decrease()
        elif isinstance(change, int):
            self.E88_Zones.Data[zonename].zone_capacity_change(change)
        else:
            pass

        try:
            if zonename in global_variables.SectorSettings:
                size=self.E88_Zones.Data[zonename].ZoneSize
                high=size * global_variables.SectorSettings[zonename]['waterLevelHigh'] / 100
                low=size * global_variables.SectorSettings[zonename]['waterLevelLow'] / 100
                valid=size - self.E88_Zones.Data[zonename].ZoneCapacity
                level=None
                if valid == 0:
                    level='empty'
                elif valid < low:
                    level='low'
                elif valid < high:
                    level='normal'
                elif valid < size:
                    level='high'
                else:
                    level='full'
                # print(zonename, size, high, low, valid, level, self.E88_Zones.Data[zonename].WaterLevel)
                if self.E88_Zones.Data[zonename].WaterLevel != level:
                    if level in global_variables.SectorSettings[zonename]['water_level_table']:
                        global_variables.SectorSettings[zonename]['water_level_table'][level](zonename, handler=self.secsgem_e88_h)
                    self.E88_Zones.set(zonename, {'WaterLevel': level})
        except:
            traceback.print_exc()

    def notify_panel(self, force=False):
        try:
            n=0
            m=0
            mCarriers=[]
            check=True
            for idx, carrier in enumerate(self.carriers):
                #mCarriers.append(carrier) #big bug: 2021/2/21 chocp
                
                # carrier['state'] = self.lots[idx]['state']
                mCarriers.append(copy.deepcopy(carrier))
                
                mCarriers[idx]['lot']=self.lots[idx]
                #print(carrier['status'], carrier['carrierID'], self.lots[idx]['booked'])
                if carrier['status'] == 'up' and carrier['carrierID'] == '': #9/26 chocp
                    m+=1   #chi 2022/09/19 for water level warning without booking 
                    if not self.lots[idx]['booked']:
                        n+=1

            if self.erack_status == 'DOWN':
                self.available=0
            else:
                self.available=n

            if global_variables.filter =='erack':
                check=False if not force else True

            if check:
                
                
                output('eRackStatusUpdate', {
                        'idx':self.idx,
                        'DeviceID':self.device_id,
                        'MAC':self.mac,
                        'IP':self.ip,
                        'Status':self.erack_status,
                        'carriers':mCarriers,
                        'SlotNum':self.slot_num,
                        'StockNum':self.slot_num-self.available
                        })

            if m == 0:
                self.water_level='full'

            elif m < self.slot_num-self.slot_num*self.waterlevelhigh/100:
                self.water_level='high'

            elif m < self.slot_num-self.slot_num*self.waterlevellow/100:
                self.water_level='medium'

            elif m<self.slot_num:
                self.water_level='low'

            elif m == self.slot_num:
                self.water_level='empty'
            else:
                pass

            if self.last_water_level != self.water_level:
                if self.water_level in self.water_level_table:
                    self.water_level_table[self.water_level](self.device_id, handler=self.secsgem_e88_h)
                self.last_water_level=self.water_level
            pass

        except Exception:
            print('notify_panel_fail')

    def set_machine_info(self, port_no, dest, vehicle_id=''): #chocp add 9/24
        print('set_machine_info', port_no, dest)

        
        if global_variables.RackNaming == 7:
            if self.lots[port_no-1]['state'] in ["Identified","Associated","PreDispatch"]:
                self.carriers[port_no-1]['state']='Dispatch'
                self.lots[port_no-1]['state']='Dispatch'
                if vehicle_id:
                    self.lots[port_no-1]['machine']=dest + ' by {}'.format(vehicle_id) 
                else:
                    self.lots[port_no-1]['machine']=dest
            elif self.lots[port_no-1]['state'] in ['Dispatch']:
                if self.device_id in ["TBD01","TBD02"]:
                    self.carriers[port_no-1]['state']='Associated'
                    self.lots[port_no-1]['state']='Associated'
                else:
                    self.carriers[port_no-1]['state']='Identified'
                    self.lots[port_no-1]['state']='Identified'
                if "by" in self.lots[port_no-1]['machine']:
                    orginal_dest=str(self.lots[port_no-1]['machine']).split("by")[0]
                    self.lots[port_no-1]['machine']=orginal_dest
        else:
            if vehicle_id:
                    self.lots[port_no-1]['machine']=dest + ' by {}'.format(vehicle_id) 
            else:
                self.lots[port_no-1]['machine']=dest
        
        self.notify_panel()

    def set_booked_flag(self, port_no, flag=False, vehicle_id='', source=''): #2022/3/18 #Booked
        print('set_booked_flag', port_no, flag)
        
        if flag:
            self.lots[port_no-1]['booked']=1
            self.lots[port_no-1]['booked_for']=vehicle_id
            self.lots[port_no-1]['desc']=vehicle_id + ' from {}'.format(source) if source else ''
            self.carriers[port_no-1]['state']='Booked'
            
        else:
            self.lots[port_no-1]['booked']=0
            self.lots[port_no-1]['booked_for']=''
            self.lots[port_no-1]['desc']=''
            self.carriers[port_no-1]['state']='Empty'
           

        

        self.notify_panel()

    def locstatechg_update(self, shelf_id, shelf_state_value):
        """Update shelf state for LOCSTATECHG command
        
        :param shelf_id: Shelf identifier (e.g. 'TBD01P01')
        :type shelf_id: str
        :param shelf_state_value: New shelf state value (1-5)
        :type shelf_state_value: int
        :return: Success status
        :rtype: bool
        """
        try:
            erack_logger.info("LOCSTATECHG: Processing ShelfID={}, ShelfState={}".format(
                shelf_id, shelf_state_value))
            
            # 檢查是否為此設備的儲位
            if not shelf_id.startswith(self.device_id):
                erack_logger.debug("LOCSTATECHG: ShelfID {} does not belong to device {}".format(
                    shelf_id, self.device_id))
                return False
            
            # 查找對應的 zone 和更新 ShelfUnit
            for zonename in self.zone_list:
                if shelf_id in self.zone_list[zonename]:
                    if zonename in self.E88_Zones.Data:
                        # 更新 ShelfUnit 的 ShelfUnitState
                        if shelf_id in self.E88_Zones.Data[zonename].ShelfUnit:
                            old_state = self.E88_Zones.Data[zonename].ShelfUnit[shelf_id].get('ShelfUnitState', 1)
                            self.E88_Zones.Data[zonename].ShelfUnit[shelf_id]['ShelfUnitState'] = shelf_state_value
                            
                            erack_logger.info("LOCSTATECHG: Updated ShelfUnit {}: state {} -> {}".format(
                                shelf_id, old_state, shelf_state_value))
                            
                            # 同步更新 Zone 的 ShelfState
                            if hasattr(self.E88_Zones.Data[zonename], 'set_shelf_state'):
                                self.E88_Zones.Data[zonename].set_shelf_state(shelf_id, shelf_state_value)
                            
                            erack_logger.info("LOCSTATECHG: Successfully updated ShelfID {} to state {}".format(
                                shelf_id, shelf_state_value))
                            return True
                        else:
                            erack_logger.warning("LOCSTATECHG: ShelfUnit {} not found in zone {}".format(
                                shelf_id, zonename))
                            return False
                    break
            else:
                erack_logger.warning("LOCSTATECHG: ShelfID {} not found in device {} zone list".format(
                    shelf_id, self.device_id))
                return False
                
        except Exception as e:
            erack_logger.error("LOCSTATECHG processing error: {}".format(e))
            traceback.print_exc()
            return False

    def eRackStatusUpdate(self):
        carrier_change=False
        states=[]
        for idx, carrier in enumerate(self.carriers):
            #only update to host if carrier status change
            sendby=0
            # 9/19, 9/21
            rack_id=self.device_id
            port_no=idx+1
            erack_logger.info("port_no: {}".format(port_no))
            zonename=carrier['area_id'] if carrier['area_id'] else self.groupID if (self.groupID and global_variables.RackNaming == 2) else self.device_id

            res, CarrierLoc=tools.print_rackport_format(rack_id, port_no, self.rows, self.columns)
            if not res:
                raise alarms.SCSyntaxWarning(rack_id, handler=self.secsgem_e88_h)

            h_vehicle=None
            if Vehicle.h != 0:
                for vehicle_id, h_vehicle in Vehicle.h.vehicles.items():
                    if h_vehicle.AgvState in ['Acquiring', 'Depositing'] and h_vehicle.action_in_run['target'] == CarrierLoc: #have bug
                        sendby=1
                        break
                else:
                    h_vehicle=None
                    
            if self.erack_status == 'DOWN':
                carrier['status']='down'
                carrier['carrierID']=''
                carrier['checked']=0

            if carrier['status'] == 'down':
                erack_logger.debug("carrier 1: {}".format(carrier))
                self.E88_Zones.Data[zonename].StockerUnit[CarrierLoc]['StockerUnitState']=3
                self.E88_Zones.Data[zonename].StockerUnit[CarrierLoc]['CarrierID']=carrier['carrierID']
                # Synchronize CarrierID of ShelfUnit.
                self.E88_Zones.Data[zonename].ShelfUnit[CarrierLoc]['CarrierID']=carrier['carrierID']
                
                #for rack update
                state={'SlotID': idx+1, 'Status':'Fail'}
                states.append(state)
                #for port update
                if self.last_carriers[idx]!=carrier:
                    carrier_change=True
                    # E82.report_event(self.secsgem_e82_h, E82.PortStatusUpdate, {'RackID':self.device_id , 'SlotID':state['SlotID'], 'SlotStatus':state['Status'], 'SendBy': sendby})
                    if carrier['checked'] and CarrierLoc not in self.E88_Carriers.Mapping: #if carrier check by operator,then launch movin event
                        FAILUREID=E88.FailureIDGEN(CarrierLoc, carrier['carrierID'])
                        self.read_carriers[idx]['carrierID']=FAILUREID
                        self.E88_Carriers.Mapping[CarrierLoc]=self.read_carriers[idx]['carrierID']
                        self.E88_Carriers.add(FAILUREID)
                        datasets={}
                        datasets['CarrierID']=FAILUREID
                        datasets['CarrierLoc']=CarrierLoc
                        datasets['CarrierIDRead']=carrier['carrierID']
                        datasets['CarrierZoneName']=zonename
                        datasets['CarrierDeviceName']=self.device_id
                        datasets['HandoffType']=sendby+1
                        datasets['PortType']=self.type # Mike: 2022/04/15
                        self.E88_Carriers.set(FAILUREID, datasets)
                        self.E88_Carriers.Data[FAILUREID].id_read(FAILUREID, 1)
                        self.E88_Carriers.Data[FAILUREID].State.wait_in()
                        self.zone_capacity_change(zonename, 'Dec')
                        self.E88_Carriers.Data[FAILUREID].State.transfer()
                        self.E88_Carriers.Data[FAILUREID].State.wait_out()
                        if h_vehicle and global_variables.TSCSettings.get('Safety', {}).get('TrBackReqCheck', 'yes').lower() == 'yes':
                            h_vehicle.adapter.robot_check_control(False)

                    if CarrierLoc not in self.alarm_table[20002]: #if carrier check by operator,then launch movin event
                        datasets={}
                        datasets['UnitType']='Rack'
                        datasets['UnitID']=self.device_id
                        datasets['Level']='Error'
                        datasets['SubCode']=20002
                        datasets['CarrierLoc']=CarrierLoc
                        self.E88_Zones.Data[zonename].zone_alarm_set(20002, True, datasets)
                        self.alarm_table[20002].append(CarrierLoc)

            elif carrier['carrierID'] == '':
                erack_logger.debug("carrier 2: {}".format(carrier))
                self.E88_Zones.Data[zonename].StockerUnit[CarrierLoc]['StockerUnitState']=1
                self.E88_Zones.Data[zonename].StockerUnit[CarrierLoc]['CarrierID']=carrier['carrierID']
                # Synchronize CarrierID of ShelfUnit.
                self.E88_Zones.Data[zonename].ShelfUnit[CarrierLoc]['CarrierID']=carrier['carrierID']
                self.E88_Zones.Data[zonename].ShelfUnit[CarrierLoc]['ShelfUnitState']=1
                #for rack update
                state={'SlotID': idx+1, 'Status':'None'}
                states.append(state)
                #for port update
                if self.last_carriers[idx]!=carrier:
                    carrier_change=True
                    # E82.report_event(self.secsgem_e82_h, E82.PortStatusUpdate, {'RackID':self.device_id , 'SlotID':state['SlotID'], 'SlotStatus':state['Status'], 'SendBy': sendby})
                    if CarrierLoc in self.E88_Carriers.Mapping:
                        print(CarrierLoc, self.E88_Carriers.Mapping[CarrierLoc])
                        if self.E88_Carriers.Mapping[CarrierLoc] in self.E88_Carriers.Data:
                            datasets={}
                            datasets['HandoffType']=sendby+1
                            self.E88_Carriers.set(self.E88_Carriers.Mapping[CarrierLoc], datasets)
                            # Check carrier state machine current state to avoid calling kill_carrier in none state
                            current_state = self.E88_Carriers.Data[self.E88_Carriers.Mapping[CarrierLoc]].State.current
                            if self.E88_Carriers.Data[self.E88_Carriers.Mapping[CarrierLoc]].CarrierState == 3:
                                self.E88_Carriers.Data[self.E88_Carriers.Mapping[CarrierLoc]].State.remove()
                            elif current_state != 'none':
                                # Only call kill_carrier when not in none state
                                self.E88_Carriers.Data[self.E88_Carriers.Mapping[CarrierLoc]].State.kill_carrier()
                            else:
                                erack_logger.debug("warning: carrier {} in location {} is already in none state, skip kill_carrier".format(self.E88_Carriers.Mapping[CarrierLoc], CarrierLoc))
                                
                            self.E88_Carriers.delete(self.E88_Carriers.Mapping[CarrierLoc])
                            self.zone_capacity_change(zonename, 'Inc')
                            if CarrierLoc in self.E88_Carriers.Mapping:
                                del self.E88_Carriers.Mapping[CarrierLoc]
                            self.read_carriers[idx]['carrierID']=''

                    #add cacel order when carrier remove 2023/1/17
                    if global_variables.RackNaming in [13,35] and sendby==0:
                        carrierID=self.last_carriers[idx]['carrierID']
                        if carrierID:
                            WorkID=EqMgr.getInstance().orderMgr.query_work_list_by_carrierID(carrierID)
                            if WorkID:
                                obj={'remote_cmd':'work_cancel', 'WorkID':WorkID}
                                remotecmd_queue.append(obj)
                            if global_variables.field_id == 'USG3':
                                erack_WorkID=EqMgr.getInstance().orderMgr.query_erack_work_list_by_carrierID(carrierID)
                                if erack_WorkID:
                                    obj={'CommandID':erack_WorkID}
                                    EqMgr.getInstance().orderMgr.cancel_transfer(obj)
                                    # print('>>carrier_removed:{}'.format(obj))
                                    # carrier['cmd_send']=False

                if CarrierLoc in self.alarm_table[20002]: #if carrier check by operator,then launch movin event
                    datasets={}
                    datasets['UnitType']='Rack'
                    datasets['UnitID']=self.device_id
                    datasets['Level']='Error'
                    datasets['SubCode']=20002
                    datasets['CarrierLoc']=CarrierLoc
                    self.E88_Zones.Data[zonename].zone_alarm_set(20002, False, datasets)
                    self.alarm_table[20002].remove(CarrierLoc)

            else:
                erack_logger.debug("carrier 3: {}".format(carrier))
                self.E88_Zones.Data[zonename].StockerUnit[CarrierLoc]['StockerUnitState']=2
                self.E88_Zones.Data[zonename].StockerUnit[CarrierLoc]['CarrierID']=carrier['carrierID']
                # Synchronize CarrierID of ShelfUnit.
                self.E88_Zones.Data[zonename].ShelfUnit[CarrierLoc]['CarrierID']=carrier['carrierID']
                #for rack update
                state={'SlotID': idx+1, 'Status':carrier['carrierID']}
                states.append(state)

                if self.last_carriers[idx]!=carrier:
                    #print('diff', self.last_carriers[idx], carrier)
                    carrier_change=True
                    if carrier['checked']: #if carrier check by operator,then launch movin event
                        
                        if global_variables.TSCSettings.get('Other', {}).get('RTDCarrierLocateCheck','yes') != 'yes': #Sean for UMC 23/12/27
                            for work in EqMgr.getInstance().orderMgr.work_list:
                                if work['CarrierID'] == carrier['carrierID']:
                                    EqMgr.getInstance().orderMgr.update_work_location(work['WorkID'], CarrierLoc)
                                #print(work)
                        if h_vehicle and global_variables.TSCSettings.get('Safety', {}).get('TrBackReqCheck', 'yes').lower() == 'yes':
                            h_vehicle.adapter.robot_check_control(True)

                        if carrier['carrierID'] not in self.E88_Carriers.Data:
                            erack_logger.debug("carrier 3.1: {}".format(self.E88_Carriers.Data))
                            if CarrierLoc not in self.E88_Carriers.Mapping:
                                erack_logger.debug("carrier 3.1.1: {}".format(self.E88_Carriers.Mapping))
                                self.E88_Carriers.Mapping[CarrierLoc]=carrier['carrierID']
                                self.read_carriers[idx]['carrierID']=carrier['carrierID']
                                self.E88_Carriers.add(self.E88_Carriers.Mapping[CarrierLoc])
                                datasets={}
                                datasets['CarrierID']=self.E88_Carriers.Mapping[CarrierLoc]
                                datasets['CarrierLoc']=CarrierLoc
                                datasets['CarrierIDRead']=self.E88_Carriers.Mapping[CarrierLoc]
                                datasets['CarrierZoneName']=zonename
                                datasets['CarrierDeviceName']=self.device_id
                                datasets['HandoffType']=sendby+1
                                datasets['PortType']=self.type # Mike: 2022/04/15
                                self.E88_Carriers.set(self.E88_Carriers.Mapping[CarrierLoc], datasets)
                                self.E88_Carriers.Data[self.E88_Carriers.Mapping[CarrierLoc]].id_read(self.E88_Carriers.Mapping[CarrierLoc], 0)
                                self.E88_Carriers.Data[self.E88_Carriers.Mapping[CarrierLoc]].State.wait_in()
                                self.zone_capacity_change(zonename, 'Dec')
                                self.E88_Carriers.Data[self.E88_Carriers.Mapping[CarrierLoc]].State.transfer()
                                self.E88_Carriers.Data[self.E88_Carriers.Mapping[CarrierLoc]].State.store()

                                if global_variables.field_id == 'USG3':  #for USG3 2023/12/15
                                    global_variables.bridge_h.report({'event':'CarrierStored', 'data':{
                                        'CarrierID':datasets['CarrierID'],
                                        'CarrierLoc':datasets['CarrierLoc'],
                                        'HandoffType':datasets['HandoffType']}})
                            else:
                                erack_logger.debug("carrier 3.1.2: {}".format(self.E88_Carriers.Mapping))
                                current_state = self.E88_Carriers.Data[self.E88_Carriers.Mapping[CarrierLoc]].State.current
                                if current_state != 'none':
                                    self.E88_Carriers.Data[self.E88_Carriers.Mapping[CarrierLoc]].State.kill_carrier()
                                else:
                                    erack_logger.debug("warning: carrier {} in location {} is already in none state, skip kill_carrier".format(self.E88_Carriers.Mapping[CarrierLoc], CarrierLoc))
                                old_carrier_id=self.E88_Carriers.Mapping[CarrierLoc]
                                self.E88_Carriers.Mapping[CarrierLoc]=carrier['carrierID']
                                self.read_carriers[idx]['carrierID']=carrier['carrierID']
                                datasets={}
                                datasets['CarrierID']=self.E88_Carriers.Mapping[CarrierLoc]
                                datasets['CarrierLoc']=CarrierLoc
                                datasets['CarrierIDRead']=self.E88_Carriers.Mapping[CarrierLoc]
                                datasets['CarrierZoneName']=zonename
                                datasets['CarrierDeviceName']=self.device_id
                                datasets['HandoffType']=sendby+1
                                datasets['PortType']=self.type # Mike: 2022/04/15
                                
                                
                                self.E88_Carriers.mod(old_carrier_id, self.E88_Carriers.Mapping[CarrierLoc])
                                
                                self.E88_Carriers.set(self.E88_Carriers.Mapping[CarrierLoc], datasets)
                            if CarrierLoc in self.alarm_table[20002]: #if carrier check by operator,then launch movin event
                                datasets={}
                                datasets['UnitType']='Rack'
                                datasets['UnitID']=self.device_id
                                datasets['Level']='Error'
                                datasets['SubCode']=20002
                                datasets['CarrierLoc']=CarrierLoc
                                self.E88_Zones.Data[zonename].zone_alarm_set(20002, False, datasets)
                                self.alarm_table[20002].remove(CarrierLoc)
                        else:
                            if CarrierLoc not in self.E88_Carriers.Mapping:
                                tmp=self.E88_Carriers.Data[carrier['carrierID']]
                                if self.E88_Zones.Data[tmp.CarrierZoneName].ZoneUnitState[tmp.CarrierDeviceName] == 1: # Duplicate
                                    FAILUREID=E88.FailureIDGEN(CarrierLoc, carrier['carrierID'])
                                    self.read_carriers[idx]['carrierID']=FAILUREID
                                    self.E88_Carriers.Mapping[CarrierLoc]=FAILUREID
                                    self.E88_Carriers.add(self.E88_Carriers.Mapping[CarrierLoc])
                                    datasets={}
                                    datasets['CarrierID']=carrier['carrierID']
                                    datasets['CarrierLoc']=CarrierLoc
                                    datasets['CarrierIDRead']=self.E88_Carriers.Mapping[CarrierLoc]
                                    datasets['CarrierZoneName']=zonename
                                    datasets['CarrierDeviceName']=self.device_id
                                    datasets['HandoffType']=sendby+1
                                    datasets['PortType']=self.type # Mike: 2022/04/15
                                    self.E88_Carriers.set(self.E88_Carriers.Mapping[CarrierLoc], datasets)
                                    self.E88_Carriers.Data[self.E88_Carriers.Mapping[CarrierLoc]].id_read(self.E88_Carriers.Mapping[CarrierLoc], 2)
                                    self.E88_Carriers.Data[self.E88_Carriers.Mapping[CarrierLoc]].State.wait_in()
                                    self.zone_capacity_change(zonename, 'Dec')
                                    self.E88_Carriers.Data[self.E88_Carriers.Mapping[CarrierLoc]].State.transfer()
                                    self.E88_Carriers.Data[self.E88_Carriers.Mapping[CarrierLoc]].State.wait_out()
                                    if CarrierLoc not in self.alarm_table[20002]: #if carrier check by operator,then launch movin event
                                        datasets={}
                                        datasets['UnitType']='Rack'
                                        datasets['UnitID']=self.device_id
                                        datasets['Level']='Error'
                                        datasets['SubCode']=20002
                                        datasets['CarrierLoc']=CarrierLoc
                                        self.E88_Zones.Data[zonename].zone_alarm_set(20002, True, datasets)
                                        self.alarm_table[20002].append(CarrierLoc)
                                else:
                                    FAILUREID=E88.FailureIDGEN(CarrierLoc, carrier['carrierID'])
                                    old_carrier_loc=self.E88_Carriers.Data[carrier['carrierID']].CarrierLoc
                                    self.E88_Carriers.Mapping[old_carrier_loc]=FAILUREID
                                    self.E88_Carriers.mod(carrier['carrierID'], FAILUREID)
                                    datasets={}
                                    datasets['CarrierID']=FAILUREID
                                    self.E88_Carriers.set(FAILUREID, datasets)
                                    self.E88_Carriers.Data[FAILUREID].State.transfer()
                                    self.E88_Carriers.Data[FAILUREID].State.wait_out()

                                    self.E88_Carriers.Mapping[CarrierLoc]=carrier['carrierID']
                                    self.read_carriers[idx]['carrierID']=carrier['carrierID']
                                    self.E88_Carriers.add(self.E88_Carriers.Mapping[CarrierLoc])
                                    datasets={}
                                    datasets['CarrierID']=self.E88_Carriers.Mapping[CarrierLoc]
                                    datasets['CarrierLoc']=CarrierLoc
                                    datasets['CarrierIDRead']=self.E88_Carriers.Mapping[CarrierLoc]
                                    datasets['CarrierZoneName']=zonename
                                    datasets['CarrierDeviceName']=self.device_id
                                    datasets['HandoffType']=sendby+1
                                    datasets['PortType']=self.type # Mike: 2022/04/15
                                    self.E88_Carriers.set(self.E88_Carriers.Mapping[CarrierLoc], datasets)
                                    self.E88_Carriers.Data[self.E88_Carriers.Mapping[CarrierLoc]].id_read(self.E88_Carriers.Mapping[CarrierLoc], 0)
                                    self.E88_Carriers.Data[self.E88_Carriers.Mapping[CarrierLoc]].State.wait_in()
                                    self.zone_capacity_change(zonename, 'Dec')
                                    self.E88_Carriers.Data[self.E88_Carriers.Mapping[CarrierLoc]].State.transfer()
                                    self.E88_Carriers.Data[self.E88_Carriers.Mapping[CarrierLoc]].State.store()
                                pass
                            else: # Duplicate
                                old_carrier_id=self.E88_Carriers.Mapping[CarrierLoc]
                                FAILUREID=E88.FailureIDGEN(CarrierLoc, carrier['carrierID'])
                                self.read_carriers[idx]['carrierID']=FAILUREID
                                self.E88_Carriers.Mapping[CarrierLoc]=FAILUREID
                                datasets={}
                                datasets['CarrierID']=carrier['carrierID']
                                datasets['CarrierLoc']=CarrierLoc
                                datasets['CarrierIDRead']=self.E88_Carriers.Mapping[CarrierLoc]
                                datasets['CarrierZoneName']=zonename
                                datasets['CarrierDeviceName']=self.device_id
                                datasets['HandoffType']=sendby+1
                                datasets['PortType']=self.type # Mike: 2022/04/15
                                self.E88_Carriers.mod(old_carrier_id, self.E88_Carriers.Mapping[CarrierLoc])
                                self.E88_Carriers.set(self.E88_Carriers.Mapping[CarrierLoc], datasets)
                                if CarrierLoc not in self.alarm_table[20002]: #if carrier check by operator,then launch movin event
                                    datasets={}
                                    datasets['UnitType']='Rack'
                                    datasets['UnitID']=self.device_id
                                    datasets['Level']='Error'
                                    datasets['SubCode']=20002
                                    datasets['CarrierLoc']=CarrierLoc
                                    self.E88_Zones.Data[zonename].zone_alarm_set(20002, True, datasets)
                                    self.alarm_table[20002].append(CarrierLoc)

                if self.last_carriers[idx]['checked']!=carrier['checked']: #only for update panel chocp: 2021/6/22
                    carrier_change=True

        if carrier_change:
            
            self.notify_panel(force=True)   
            #print('eRack Secs and panel Update...')
            self.last_carriers=copy.deepcopy(self.carriers)

        if self.last_erack_status!=self.erack_status:
            
            self.notify_panel(force=True)
            #print('eRack Panel Update...')
            self.last_erack_status=self.erack_status

    def on_notify(self, event, data):
        #print('eRack {} get {}, data {}'.format(self.device_id, event, data))
        if event == 'acquire_start_evt' or event == 'deposit_start_evt':
            #self.sendby[0]=1
            pass
        elif event == 'acquire_complete_evt' or event == 'deposit_complete_evt':
            #self.sendby[0]=1
            pass

    def eRackInfoUpdate(self, info):
        erack_logger.debug("info:{}".format(info))

        if info['cmd'] == 'scan':
            # Handle manual scan command
            port_idx = info.get('port_idx', 0)
            carrier_loc = info.get('carrier_loc', '')
            expected_carrier_id = info.get('expected_carrier_id', '')
            
            try:
                # Call device scan method
                scan_result = self.scan(port_idx + 1, carrier_loc, expected_carrier_id)  # port_no is 1-based
                action_logger.debug("do scan: port_idx: {}, carrier_loc: {}, expected_carrier_id: {}, scan_result: {}".format(port_idx + 1, carrier_loc, expected_carrier_id, scan_result))
                
                
                # Get scan results
                actual_carrier_id = scan_result.get('carrier_id', '') if scan_result else ''
                idread_status = scan_result.get('idread_status', 0) if scan_result else 1
                
                # Notify TSC scan results
                if hasattr(self, 'tsc_handler') and self.tsc_handler:
                    action_logger.debug("hihi")
                    self.tsc_handler.process_scan_result(
                        carrier_loc, expected_carrier_id, actual_carrier_id, idread_status)
                    
                action_logger.debug("scan result: actual_scarrier_id: {}, idread_status: {}".format(actual_carrier_id, idread_status))
                
                
                    
            except Exception as e:
                action_logger.error("sacn error: {}".format(e))
                
                traceback.print_exc()
                
                # Notify TSC scan failure
                if hasattr(self, 'tsc_handler') and self.tsc_handler:
                    self.tsc_handler.process_scan_result(
                        carrier_loc, expected_carrier_id, '', 1)

        elif info['cmd'] == 'associate':
            data=info['data']
            print(data)
            try:
                lot_info=data.split(',') #ASECL use ','
                print(lot_info)
                if len(lot_info) == 1: #chi 2022/09/26
                    self.lots[info['port_idx']]['lotID']='{}'.format(lot_info[0])
                else:
                    self.lots[info['port_idx']]['lotID']='{}({})'.format(lot_info[0], len(lot_info)) if lot_info[0] else ''
                self.lots[info['port_idx']]['desc']=info.get('addition', [''])[0] #chocp 9/2
                print(self.lots[info['port_idx']]['lotID'], self.lots[info['port_idx']]['desc'])
            except:
                traceback.print_exc()
                pass

        elif info['cmd'] == 'infoupdate':
            
            self.lots[info['port_idx']]['lotID']=''
            self.lots[info['port_idx']]['stage']=''
            self.lots[info['port_idx']]['desc']=''
            self.lots[info['port_idx']]['cust']=''  #chi 2022/10/18 use LowerLevelErack for spil CY
            self.lots[info['port_idx']]['product']=''
            self.lots[info['port_idx']]['lottype']=''
            self.lots[info['port_idx']]['partID']=''
            self.lots[info['port_idx']]['automotive']=''
            self.lots[info['port_idx']]['state']=''
            self.lots[info['port_idx']]['holdcode']=''
            self.lots[info['port_idx']]['turnratio']=0
            self.lots[info['port_idx']]['eotd']=''
            self.lots[info['port_idx']]['holdreas']=''
            self.lots[info['port_idx']]['potd']=''
            self.lots[info['port_idx']]['waferlot']=''
            self.lots[info['port_idx']]['recipe']=''
            self.lots[info['port_idx']]['alarm']=''
            self.lots[info['port_idx']]['device'] = ''
            self.lots[info['port_idx']]['lpt']=''
            self.lots[info['port_idx']]['qty']=''
            self.lots[info['port_idx']]['background_color']=''
            self.lots[info['port_idx']]['buzzer']=''

            erack_logger.debug("info['data']:{}".format(info['data']))


            if 'assyLotList' in info['data']:#chipmos use
                
                
                
                lotID=info['data'].get("assyLotList",'')
                self.lots[info['port_idx']]['lotID']=lotID
                
            
            if 'entity' in info['data']:#chipmos use
                
                machine=info['data'].get("entity",'')
                self.lots[info['port_idx']]['machine']=machine

            if 'errorCode' in info['data']:
                
                errcode=info['data'].get("errorCode",'')
                self.lots[info['port_idx']]['errorCode']=errcode

            if 'message' in info['data']:
                
                lotsmessage=info['data'].get("message",'')
                self.lots[info['port_idx']]['desc']=lotsmessage

            if 'result' in info['data']:
                if info['data'].get("result","") == "confirm":
                    self.carriers[info['port_idx']]['state']='PreDispatch'
                    self.lots[info['port_idx']]['state']='PreDispatch'



            if 'send_associated_status' in info['data']:
                result_send_associated_status=info['data'].get("send_associated_status",True)
                if result_send_associated_status:
                    self.carriers[info['port_idx']]['state']='Associated'
                    self.lots[info['port_idx']]['state']='Associated'
                else:
                    self.carriers[info['port_idx']]['state']='Identified'
                    self.lots[info['port_idx']]['state']='Identified'
                if info['data'].get("errorCode",'') != '':
                    if info['data'].get("message",'') != '70005':
                        self.carriers[info['port_idx']]['state']='Error'
                        self.lots[info['port_idx']]['state']='Error'
                    else:
                        self.lots[info['port_idx']]['errorCode']=''
            
        
            if 'lotID' in info['data']:
                #self.lots[info['port_idx']]['lotID']=info['data']['lotID']
                lot_info=info['data']['lotID'].split(',') #ASECL use ','
                #print(lot_info)
                #lotID='{}({})'.format(lot_info[0], len(lot_info)) #chocp 2021/12/15
                if len(lot_info) == 1: #chi 2022/09/26
                    lotID='{}'.format(lot_info[0])
                else:
                    lotID='{}({})'.format(lot_info[0], len(lot_info))  if lot_info[0] else '' #chocp 2021/12/15 ......

                self.lots[info['port_idx']]['lotID']=lotID
            if 'stage' in info['data']: # Mike: 2022/05/04
                # self.lots[info['port_idx']]['stage']=info['data']['stage']
                stage_info=info['data']['stage'].split(',') #ASECL use ','
                #print(stage_info)
                #lotID='{}({})'.format(lot_info[0], len(lot_info)) #chocp 2021/12/15
                if len(stage_info) == 1: #chi 2022/09/26
                    stage='{}'.format(stage_info[0])
                else:
                    stage='{}({})'.format(stage_info[0], len(stage_info))  if stage_info[0] else '' #chocp 2021/12/15 ......

                self.lots[info['port_idx']]['stage']=stage
            if 'CustID' in info['data']: # Mike: 2022/05/04
                if global_variables.RackNaming not in [13, 35]:
                    # self.lots[info['port_idx']]['stage']=info['data']['stage']
                    cust_info=info['data']['CustID'].split(',') #ASECL use ','
                    #print(cust_info)
                    #lotID='{}({})'.format(lot_info[0], len(lot_info)) #chocp 2021/12/15
                    if len(cust_info) == 1: #chi 2022/09/26
                        cust_info='{}'.format(cust_info[0])
                    else:
                        cust_info='{}({})'.format(cust_info[0], len(cust_info))  if cust_info[0] else '' #chocp 2021/12/15 ......

                    self.lots[info['port_idx']]['cust']=cust_info
                else:
                    # print('add_cust_1', info['data']['CustID'])
                    self.lots[info['port_idx']]['cust']=info['data']['CustID']
                    # print('add_cust_2', info['data']['CustID'])

            if 'DeviceID' in info['data']: # Jwo 2024/03/29
                # print('add_device_1', info['data']['DeviceID'])
                self.lots[info['port_idx']]['device']=info['data']['DeviceID']
                # print('add_device_2', info['data']['DeviceID'])
            if 'Product' in info['data']: # Mike: 2022/05/04
                # self.lots[info['port_idx']]['stage']=info['data']['stage']
                product_info=info['data']['Product'].split(',') #ASECL use ','
                #print(product_info)
                #lotID='{}({})'.format(lot_info[0], len(lot_info)) #chocp 2021/12/15
                if len(product_info) == 1: #chi 2022/09/26
                    product_info='{}'.format(product_info[0])
                else:
                    product_info='{}({})'.format(product_info[0], len(product_info))  if product_info[0] else '' #chocp 2021/12/15 ......

                self.lots[info['port_idx']]['product']=product_info
            if 'LotType' in info['data']: # Mike: 2022/05/04
                # self.lots[info['port_idx']]['stage']=info['data']['stage']
                lottype_info=info['data']['LotType'].split(',') #ASECL use ','
                #print(lottype_info)
                #lotID='{}({})'.format(lot_info[0], len(lot_info)) #chocp 2021/12/15
                if len(lottype_info) == 1: #chi 2022/09/26
                    lottype_info='{}'.format(lottype_info[0])
                else:
                    lottype_info='{}({})'.format(lottype_info[0], len(lottype_info))  if lottype_info[0] else '' #chocp 2021/12/15 ......

                self.lots[info['port_idx']]['lottype']=lottype_info
            if 'PartID' in info['data']: # Mike: 2022/05/04
                # self.lots[info['port_idx']]['stage']=info['data']['stage']
                part_info=info['data']['PartID'].split(',') #ASECL use ','
                #print(part_info)
                #lotID='{}({})'.format(lot_info[0], len(lot_info)) #chocp 2021/12/15
                if len(part_info) == 1: #chi 2022/09/26
                    part_info='{}'.format(part_info[0])
                else:
                    part_info='{}({})'.format(part_info[0], len(part_info))  if part_info[0] else '' #chocp 2021/12/15 ......

                self.lots[info['port_idx']]['partID']=part_info
            if 'Automotive' in info['data']: # Mike: 2022/05/04
                self.lots[info['port_idx']]['automotive']=info['data']['Automotive']
            if 'State' in info['data']: # Mike: 2022/05/04
                self.lots[info['port_idx']]['state']=info['data']['State']
            if 'HoldCode' in info['data']: # Mike: 2022/05/04
                self.lots[info['port_idx']]['holdcode']=info['data']['HoldCode']
            if 'TurnRatio' in info['data']: # Mike: 2022/05/04
                self.lots[info['port_idx']]['turnratio']=info['data']['TurnRatio']
            if 'EOTD' in info['data']: # Mike: 2022/05/04
                self.lots[info['port_idx']]['eotd']=info['data']['EOTD']
            if 'desc' in info['data']:
                self.lots[info['port_idx']]['desc']=info['data']['desc']
                pattern=r"LPT:(\d+) QTY:(\d+)" #2024/04/18 for TI AT
                lqdata=re.search(pattern, info['data']['desc'])
                matches= lqdata.groups() if lqdata else ["",""]
                self.lots[info['port_idx']]['lpt']=matches[0]
                self.lots[info['port_idx']]['qty']=matches[1]
            if 'HoldReas' in info['data']: # Mike: 2023/05/25
                self.lots[info['port_idx']]['holdreas']=info['data']['HoldReas']
            if 'POTD' in info['data']: # Mike: 2023/05/25
                self.lots[info['port_idx']]['potd']=info['data']['POTD']
            if 'WaferLot' in info['data']: # Mike: 2023/05/25
                self.lots[info['port_idx']]['waferlot']=info['data']['WaferLot']
            if 'queueTime' in info['data']: # Mike: 2023/05/25
                self.lots[info['port_idx']]['queue_time']=info['data']['queueTime']
            if 'recipe' in info['data']: # 8.23A
                self.lots[info['port_idx']]['recipe']=info['data']['recipe']
            if 'alarm' in info['data']: #
                self.lots[info['port_idx']]['alarm']=info['data']['alarm']
            if 'color' in info['data']: #
                self.lots[info['port_idx']]['background_color']=info['data']['color']
            if 'buzzer' in info['data']: #
                self.lots[info['port_idx']]['buzzer']=info['data']['buzzer']

            #chocp add
            if 'carrierType' in info['data']:
                self.lots[info['port_idx']]['carrierType']=info['data']['carrierType']
                print('get infoupdate carrierType:', self.lots[info['port_idx']]['carrierType'])

            if 'priority' in info['data']:
                self.lots[info['port_idx']]['priority']=info['data']['priority']
                print('get infoupdate priority:', self.lots[info['port_idx']]['priority'])
        
        elif info['cmd'] == 'scan': # Manual scan function handling
            try:
                port_idx = info.get('port_idx', 0)
                carrier_loc = info.get('carrier_loc', '')
                expected_carrier_id = info.get('expected_carrier_id', '')
                
                # Set expected carrier ID for use in scan result callback
                self.expected_scan_carrier_id = expected_carrier_id
                
                # Calculate actual port number (port_idx starts from 0, port_no starts from 1)
                port_no = port_idx + 1
                
                # Send scan command to device
                self.scan(port_no, carrier_loc)
                
                # Log scan operation
                erack_logger.info("Execute manual scan operation: Device {}, Port {}, Location {}, Expected carrier ID {}".format(
                    self.device_id, port_no, carrier_loc, expected_carrier_id))
                
            except Exception as e:
                erack_logger.error("Manual scan operation error: {}".format(e))
                traceback.print_exc()
        
        elif info['cmd'] == 'locstatechg': # Shelf state change handling
            try:
                # 從遠端指令參數中取得正確的參數名稱
                shelf_id = info.get('ShelfID', info.get('shelf_id', ''))
                shelf_state_value = info.get('ShelfStateValue', info.get('shelf_state_value', 1))
                
                erack_logger.info("Processing LOCSTATECHG command: ShelfID={}, ShelfState={}".format(
                    shelf_id, shelf_state_value))
                
                # 使用專門的 locstatechg_update 方法處理
                success = self.locstatechg_update(shelf_id, shelf_state_value)
                
                if success:
                    erack_logger.info("LOCSTATECHG completed successfully for ShelfID: {}".format(shelf_id))
                else:
                    erack_logger.warning("LOCSTATECHG failed for ShelfID: {}".format(shelf_id))
                    
            except Exception as e:
                erack_logger.error("LOCSTATECHG processing error: {}".format(e))
                traceback.print_exc()
        
        erack_logger.info(self.lots)
            
        self.notify_panel()

    def manual(self): # Mike: 2021/07/09
        doc={'head':{'device name':'E88_interface', 'date':time.strftime("%Y%m%d-%H:%M:%S", time.localtime()), 'service':'request', 'typeName':'command'}, 'data':{'command':'manual'}}
        self.sock.send(bytearray(json.dumps(doc) + '\n', encoding='utf-8'))

    def auto(self): # Mike: 2021/07/09
        doc={'head':{'device name':'E88_interface', 'date':time.strftime("%Y%m%d-%H:%M:%S", time.localtime()), 'service':'request', 'typeName':'command'}, 'data':{'command':'auto'}}
        self.sock.send(bytearray(json.dumps(doc) + '\n', encoding='utf-8'))

    def book(self, table): # Mike: 2021/07/09
        doc={'head':{'device name':'E88_interface', 'date':time.strftime("%Y%m%d-%H:%M:%S", time.localtime()), 'service':'request', 'typeName':'booked'}, 'data':{table}}
        self.sock.send(bytearray(json.dumps(doc) + '\n', encoding='utf-8'))
    
    def scan(self, port_no, carrier_loc, expected_carrier_id=""):
        """Send manual scan command to device"""
        try:
            scan_doc = {
                'head': {
                    'device name': 'E88_interface', 
                    'date': time.strftime("%Y%m%d-%H:%M:%S", time.localtime()), 
                    'service': 'request', 
                    'typeName': 'scan'
                }, 
                'data': {
                    'command': 'scan', 
                    'port': port_no,
                    'loc': carrier_loc,
                    'expected_carrier_id': expected_carrier_id
                }
            }
            
            if self.connected and self.sock:
                self.sock.send(bytearray(json.dumps(scan_doc ) + '\n', encoding='utf-8'))
                # self.raw_logger.debug('TSC => scan: {}'.format(doc))
                action_logger.debug("send scan: port_no: {}, carrier_loc: {}, expected_carrier_id: {}".format(port_no, carrier_loc, expected_carrier_id))
                
                
                # # Temporarily return a simulated scan result
                # # Actual scan results will be handled in device response
                # if port_no <= len(self.carriers) and self.carriers[port_no-1].get('CarrierID'):
                #     # If the port has a carrier, return the carrier's ID
                #     return {
                #         'carrier_id': self.carriers[port_no-1]['CarrierID'],
                #         'idread_status': 0
                #     }
                # else:
                #     # If the port has no carrier, return empty
                #     return {
                #         'carrier_id': '',
                #         'idread_status': 1
                #     }
            else:
                action_logger.error("device {} is not connected, can't send scan command".format(self.device_id))
               
                # return {
                #     'carrier_id': '',
                #     'idread_status': 1
                # }
                
        except Exception as e:
            action_logger.error("send scan error: {}".format(e))
            
            traceback.print_exc()
            # return {
            #     'carrier_id': '',
            #     'idread_status': 1
            # }

    def handle_scan_result(self, scan_data):
        """Handle scan results from device"""
        try:
            data = scan_data.get('data', {})
            port_no = data.get('port', 0)
            carrier_loc = data.get('loc', '')
            actual_carrier_id = data.get('carrier_id', '')
            scan_status = data.get('status', 'failed')
            scan_result = data.get('result', 'not_found')
            
            erack_logger.info("Received scan result: Port {}, Location {}, Carrier ID {}, Status {}, Result {}".format(
                port_no, carrier_loc, actual_carrier_id, scan_status, scan_result))
            
            if scan_status == 'success':
                # Get expected carrier ID (from tsc_handler)
                expected_carrier_id = getattr(self, 'expected_scan_carrier_id', '')
                
                if hasattr(self, 'tsc_handler') and self.tsc_handler:
                    # Call TSC scan result processing method
                    if scan_result == 'found' and actual_carrier_id:
                        IDREADSTATUS = 0  # Success
                    else:
                        IDREADSTATUS = 1  # Failed
                        
                    self.tsc_handler.process_scan_result(
                        carrier_loc, expected_carrier_id, actual_carrier_id, IDREADSTATUS)
                else:
                    print("TSC handler not found, cannot process scan result")
            else:
                print("Scan failed: {}".format(scan_data))
                
        except Exception as e:
            print("Error processing scan result: {}".format(e))
            traceback.print_exc()

    def connect(self): # Mike: 2021/07/09
        doc={'head':{'device name':'E88_interface', 'date':time.strftime("%Y%m%d-%H:%M:%S", time.localtime()), 'service':'request', 'typeName':'connection'}, 'data':{'connection':True}}
        self.sock.send(bytearray(json.dumps(doc) + '\n', encoding='utf-8'))

    def disconnect(self): # Mike: 2021/07/09
        doc={'head':{'device name':'E88_interface', 'date':time.strftime("%Y%m%d-%H:%M:%S", time.localtime()), 'service':'request', 'typeName':'connection'}, 'data':{'connection':False}}
        self.sock.send(bytearray(json.dumps(doc) + '\n', encoding='utf-8'))

    def pickupauth(self, shelf_no, timeout=30):
        def _check():
            start=time.time()
            while time.time()-start < timeout:
                try:
                    if self.carriers[shelf_no-1]['carrierID'] == '':
                        break
                except Exception:
                    traceback.print_exc()
                    break
                time.sleep(1)
            else:
                erack_logger.warning('pickupauth timeout on {}-{}'.format(self.device_id, shelf_no))
                return

            try:
                rack_id=self.device_id
                port_no=shelf_no
                res, CarrierLoc=tools.print_rackport_format(rack_id, port_no, self.rows, self.columns)
                if res and CarrierLoc in self.E88_Carriers.Mapping:
                    self.E88_Carriers.Data[self.E88_Carriers.Mapping[CarrierLoc]].State.store()
            except Exception:
                traceback.print_exc()

        th=threading.Thread(target=_check)
        th.setDaemon(True)
        th.start()

    def set_shelf_unit(self, carrier_loc, shelf_unit_id, shelf_unit_state, carrier_id=''):
        """Set ShelfUnit for specific location
        
        :param carrier_loc: Carrier location (e.g.: 'TBD01P01')
        :type carrier_loc: str
        :param shelf_unit_id: Shelf unit ID
        :type shelf_unit_id: str
        :param shelf_unit_state: Shelf unit state (0: unknown, 1: empty, 2: occupied, 3: error, 4: manual)
        :type shelf_unit_state: int
        :param carrier_id: Carrier ID
        :type carrier_id: str
        """
        try:
            if shelf_unit_state not in [0, 1, 2, 3, 4]:
                raise ValueError("Invalid shelf unit state. Must be 0-4 (unknown, empty, occupied, error, manual)")
            
            for zonename in self.zone_list:
                if carrier_loc in self.zone_list[zonename] and zonename in self.E88_Zones.Data:
                    self.E88_Zones.Data[zonename].ShelfUnit[carrier_loc] = {
                        'ShelfUnitID': shelf_unit_id,
                        'ShelfUnitState': shelf_unit_state,
                        'CarrierID': carrier_id
                    }
                    erack_logger.info("Location {} ShelfUnit updated to: ShelfUnitID={}, ShelfUnitState={}, CarrierID={}".format(
                        carrier_loc, shelf_unit_id, shelf_unit_state, carrier_id))
                    return True
                    
            erack_logger.warning("Location {} does not exist in device {}".format(carrier_loc, self.device_id))
            return False
        except Exception as e:
            erack_logger.error("Failed to set ShelfUnit: {}".format(e))
            return False

    def set_all_shelf_unit(self, shelf_unit_state, carrier_id=''):
        """Set ShelfUnit for all locations on this device
        
        :param shelf_unit_state: Shelf unit state (0: unknown, 1: empty, 2: occupied, 3: error, 4: manual)
        :type shelf_unit_state: int
        :param carrier_id: Carrier ID
        :type carrier_id: str
        """
        try:
            if shelf_unit_state not in [0, 1, 2, 3, 4]:
                raise ValueError("Invalid shelf unit state. Must be 0-4 (unknown, empty, occupied, error, manual)")
            
            for zonename in self.zone_list:
                if zonename in self.E88_Zones.Data:
                    for carrier_loc in self.zone_list[zonename]:
                        self.E88_Zones.Data[zonename].ShelfUnit[carrier_loc] = {
                            'ShelfUnitID': carrier_loc,
                            'ShelfUnitState': shelf_unit_state,
                            'CarrierID': carrier_id
                        }
                    
            erack_logger.info("Device {} all locations ShelfUnit updated to: ShelfUnitState={}, CarrierID={}".format(
                self.device_id, shelf_unit_state, carrier_id))
        except Exception as e:
            erack_logger.error("Failed to set all ShelfUnit: {}".format(e))

    def get_shelf_unit(self, carrier_loc=None):
        """Get ShelfUnit
        
        :param carrier_loc: Carrier location, if None returns all locations' units
        :type carrier_loc: str or None
        :return: Shelf unit info
        :rtype: dict or dict of dict
        """
        try:
            if carrier_loc:
                # Get specific location's unit
                for zonename in self.zone_list:
                    if carrier_loc in self.zone_list[zonename] and zonename in self.E88_Zones.Data:
                        return self.E88_Zones.Data[zonename].ShelfUnit.get(carrier_loc, {
                            'ShelfUnitID': carrier_loc,
                            'ShelfUnitState': 0,
                            'CarrierID': ''
                        })
                return {'ShelfUnitID': carrier_loc, 'ShelfUnitState': 0, 'CarrierID': ''}  # Default
            else:
                # Get all locations' units
                all_units = {}
                for zonename in self.zone_list:
                    if zonename in self.E88_Zones.Data:
                        for loc in self.zone_list[zonename]:
                            all_units[loc] = self.E88_Zones.Data[zonename].ShelfUnit.get(loc, {
                                'ShelfUnitID': loc,
                                'ShelfUnitState': 0,
                                'CarrierID': ''
                            })
                return all_units
        except Exception as e:
            erack_logger.error("Failed to get ShelfUnit: {}".format(e))
            return {'ShelfUnitID': carrier_loc, 'ShelfUnitState': 0, 'CarrierID': ''} if carrier_loc else {}

    def run(self):
        for i in range(self.rows*self.columns): # Mike: 2021/09/22
            rack_id=self.device_id
            port_no=i+1
            area_id=self.carriers[i]['area_id']
            zonename=area_id if area_id else self.groupID if (self.groupID and global_variables.RackNaming == 2) else self.device_id

            res, CarrierLoc=tools.print_rackport_format(rack_id, port_no, self.rows, self.columns)
            if not res:
                raise alarms.SCSyntaxWarning(self.device_id, handler=self.secsgem_e88_h)

            self.E88_Zones.ZoneMap[CarrierLoc]=self.E88_Zones
            if zonename not in self.zone_list:
                self.zone_list[zonename]={}
            self.zone_list[zonename][CarrierLoc]={'StockerUnitID':CarrierLoc, 'StockerUnitState':0, 'CarrierID':''}

        for zonename in self.zone_list:
            if zonename in self.E88_Zones.Data:
                datasets={}
                datasets['ZoneSize']=self.E88_Zones.Data[zonename].ZoneSize + len(self.zone_list[zonename])
                datasets['ZoneCapacity']=self.E88_Zones.Data[zonename].ZoneCapacity + len(self.zone_list[zonename])
                self.E88_Zones.Data[zonename].StockerUnit.update(self.zone_list[zonename])
                self.E88_Zones.Data[zonename].ZoneUnitState[self.device_id]=1
                # Initialize ShelfUnit for each CarrierLoc
                for CarrierLoc in self.zone_list[zonename]:
                    self.E88_Zones.Data[zonename].ShelfUnit[CarrierLoc]={'ShelfUnitID': CarrierLoc, 'ShelfUnitState': 1, 'CarrierID': ''}  # Initialize to empty state
            else:
                self.E88_Zones.add(zonename)
                datasets={}
                datasets['ZoneSize']=len(self.zone_list[zonename])
                datasets['ZoneCapacity']=len(self.zone_list[zonename])
                datasets['ZoneType']=self.zonetype # 1: eRack 2: dummy loadport
                datasets['StockerUnit']=dict(self.zone_list[zonename])
                datasets['ZoneUnitState']={self.device_id:1}
                # Initialize ShelfUnit for each CarrierLoc
                shelf_unit_dict = {}
                for CarrierLoc in self.zone_list[zonename]:
                    shelf_unit_dict[CarrierLoc] = {'ShelfUnitID': CarrierLoc, 'ShelfUnitState': 1, 'CarrierID': ''}  # Initialize to empty state
                datasets['ShelfUnit']=shelf_unit_dict
            self.E88_Zones.set(zonename, datasets)
            print("debug setting:", self.device_id, zonename, self.E88_Zones.Data[zonename].ZoneSize, self.E88_Zones.Data[zonename].ZoneCapacity, self.zone_list[zonename])

        print('\n<start eRack thread:{}>\n'.format(self.device_id))
        self.eRackStatusUpdate()
        E88_com_state=''
        last_E88_com_state=''
        start_up=True
        buf=''
        while not self.thread_stop:
            self.heart_beat=time.time()
            try:
                if not self.connected:
                    if not self.alarm_table[20051] and not start_up: #if carrier check by operator,then launch movin event
                        # self.E88_Zones.Data[self.device_id].zone_alarm_set(20051, True)
                        alarms.ErackOffLineWarning(self.device_id, handler=self.secsgem_e88_h)
                        self.alarm_table[20051]=1
                        dataset={'DeviceID':self.device_id}
                        E88.report_event(self.secsgem_e88_h, E88.DeviceOffline, dataset)
                        for zonename in self.zone_list:
                            self.E88_Zones.Data[zonename].ZoneUnitState[self.device_id]=2
                            # Set all CarrierLoc ShelfUnit to error state when device is offline
                            for CarrierLoc in self.zone_list[zonename]:
                                # 設備離線時，將 ShelfUnit 設置為錯誤狀態並清除 CarrierID
                                if CarrierLoc in self.E88_Zones.Data[zonename].ShelfUnit:
                                    self.E88_Zones.Data[zonename].ShelfUnit[CarrierLoc]['CarrierID'] = ''
                                else:
                                    self.E88_Zones.Data[zonename].ShelfUnit[CarrierLoc]={'ShelfUnitID': CarrierLoc, 'ShelfUnitState': 3, 'CarrierID': ''}
                            state=0
                            for key, val in self.E88_Zones.Data[zonename].ZoneUnitState.items():
                                state=1 if val == 1 else 2 if val == 2 and state != 1 else 0
                            self.E88_Zones.Data[zonename].ZoneState=state
                    start_up=False
                    retry=0
                    while(retry<5 and not self.thread_stop): #fix 5
                        try:
                            print('Rack adapter {} connecting {}, {}'.format(self.device_id, self.ip, self.port))
                            self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            self.sock.settimeout(5)
                            self.sock.connect((self.ip, self.port))
                            self.connected=True
                            self.syncing_time=time.time()
                            break
                        except Exception as e:
                            retry+=1
                            time.sleep(2)
                            pass
                    else:
                        print('Out loop for ')
                        raise alarms.ConnectWarning(self.device_id, self.ip, self.port, handler=self.secsgem_e88_h)
                    if self.alarm_table[20051]: #if carrier check by operator,then launch movin event
                        # self.E88_Zones.Data[self.device_id].zone_alarm_set(20051, False)
                        alarms.ErackOffLineWarning(self.device_id, handler=self.secsgem_e88_h)
                        self.secsgem_e88_h.clear_alarm(20051)
                        self.alarm_table[20051]=0
                    dataset={'DeviceID':self.device_id}
                    E88.report_event(self.secsgem_e88_h, E88.DeviceOnline, dataset)
                    buf=''
                else:
                    for zonename in self.zone_list:
                        self.E88_Zones.Data[zonename].ZoneUnitState[self.device_id]=1
                        # Set all CarrierLoc ShelfUnit to empty state when device is online
                        for CarrierLoc in self.zone_list[zonename]:
                            # 只在設備剛上線時初始化 ShelfUnit 狀態，不要無條件重置 CarrierID
                            if CarrierLoc not in self.E88_Zones.Data[zonename].ShelfUnit:
                                self.E88_Zones.Data[zonename].ShelfUnit[CarrierLoc]={'ShelfUnitID': CarrierLoc, 'ShelfUnitState': 1, 'CarrierID': ''}
                        self.E88_Zones.Data[zonename].ZoneState=1
                    #==================================================================
                    try:
                        self.sock.settimeout(3) #chocp 2022/11/10 #from 10sec
                        tmp = self.sock.recv(2048).decode('utf-8')
                        self.raw_logger.debug('TSC <= {}'.format(tmp))
                        buf=buf+tmp
                        if buf == '':
                            # print('SocketNullStringWarning')
                            raise GetSocketNullString()

                        begin=buf.find('[')
                        end=buf.find(']')

                        if  begin<0 or end<0:
                            continue
                        second_begin=buf.rfind('[')
                        if second_begin != begin and second_begin < end:
                            print('SocketFormatWarning', begin, end)
                            print(buf)
                            buf=''
                            raise alarms.SocketFormatWarning(self.device_id, handler=self.secsgem_e88_h)

                        raw_rx=buf[begin:end+1]
                        buf=buf[end+1:]

                        try:
                            received_data=json.loads(raw_rx) #avoid two echo in buffer
                            #query_payload=json.loads(raw_rx) #???? chocp 2021/12/15
                            # print(received_data)
                            
                            # Check if it's a scan result response
                            if isinstance(received_data, dict) and received_data.get('head', {}).get('typeName') == 'scan_result':
                                # Handle scan result
                                self.handle_scan_result(received_data)
                                continue  # Continue to next loop after handling scan result
                            else:
                                # Normal query_payload handling
                                query_payload = received_data
                        except:
                            print('SocketFormatWarning', 'parse json error')
                            print(raw_rx)
                            raise alarms.SocketFormatWarning(self.device_id, handler=self.secsgem_e88_h)
                    #except socket.timeout:
                    except GetSocketNullString:
                        raise alarms.SocketNullStringWarning(self.device_id, handler=self.secsgem_e88_h)

                    except:
                        traceback.print_exc()
                        if self.syncing_time and (time.time()-self.syncing_time > 10): #chocp 2021/10/4
                            raise alarms.LinkLostWarning(self.device_id, handler=self.secsgem_e88_h)
                        else:
                            self.sync=False
                            time.sleep(1)
                            continue

                    self.erack_status='UP'
                    self.sync=True
                    self.syncing_time=time.time()

                    datasets=[]
                    doc={'res':'no found', 'datasets':datasets, 'time':time.time()}

                    connection=((self.secsgem_e88_h.communicationState.current, self.secsgem_e88_h.controlState.current) == ('COMMUNICATING', 'ONLINE_REMOTE'))

                    for idx, port in enumerate(query_payload): #have 12 pcs
                        if idx > self.slot_num-1: #choc add 2021/11/9
                            break

                        ststus=port['status']
                        ststus_parse=ststus.split('_')
                        if len(ststus_parse) == 2: #8.22H-1
                            port['status']=ststus_parse[1]
                            self.carriers[idx]['direction']=ststus_parse[0]
                            if self.carriers[idx]['direction'] == self.carriers[idx]['direction_target']:
                                self.carriers[idx]['direction_target']= ''

                        if port['status'] == 'ERROR' or port['status'] == 'DISABLE': #chocp:2021/5/31
                            self.carriers[idx]['status']='down'
                            self.lots[idx]['booked']=0 #2022/7/13 for residual book when slot error
                            self.lots[idx]['booked_for']='' #2022/7/13 for residual book when slot error
                            self.carriers[idx]['errorCode']=port.get('errorCode', '')                                
                        elif port['status'] == 'TURNBACK':
                            self.carriers[idx]['status']='turnback'
                            self.lots[idx]['booked']=0 #2022/7/13 for residual book when slot error
                            self.lots[idx]['booked_for']=''
                        elif port['status'] == 'TURNFRONT':
                            self.carriers[idx]['status']='turnfront'
                            self.lots[idx]['booked']=0 #2022/7/13 for residual book when slot error
                            self.lots[idx]['booked_for']=''
                        else:
                            self.carriers[idx]['status']='up'
                            self.carriers[idx]['carrierID']=port['carrierID'].strip() #9/26 chocp
                            self.carriers[idx]['checked']=port.get('checked', 1) #chocp:2021/5/31
                            self.carriers[idx]['alarm']=port.get('alarm', '') # Mike: 2021/6/22
                            self.carriers[idx]['errorCode']=port.get('errorCode', '') # Mike: 2021/6/22
                            #port.get('check', True) ...........
                            if self.carriers[idx]['carrierID'] == '': #clear lot info
                                self.carriers[idx]['create_time']=0 #for auto dispatch
                                self.lots[idx]['lotID']=''
                                self.lots[idx]['stage']=''
                                self.lots[idx]['machine']=''
                                self.lots[idx]['desc']=''
                                self.lots[idx]['cust']=''
                                self.lots[idx]['partID']=''
                                self.lots[idx]['lottype']=''
                                self.lots[idx]['automotive']=''
                                self.lots[idx]['state']=''
                                self.lots[idx]['holdcode']=''
                                self.lots[idx]['turnratio']=0
                                self.lots[idx]['eotd']=''
                                self.lots[idx]['holdreas']=''
                                self.lots[idx]['potd']=''
                                self.lots[idx]['waferlot']=''
                                self.lots[idx]['recipe']=''
                                self.lots[idx]['lpt']=''
                                self.lots[idx]['qty']=''
                                self.lots[idx]['queue_time']=''
                                self.lots[idx]['alarm']=''
                                self.lots[idx]['background_color']=''
                                self.lots[idx]['buzzer']=''
                                self.lots[idx]['device']=''
                                #self.lots[idx]['booked']=0 #chocp add 0917
                            else:
                                self.lots[idx]['booked']=0 #chocp 9/17
                                self.lots[idx]['booked_for']='' #chocp 10/3

                                if not self.carriers[idx].get('create_time', 0): 
                                    self.carriers[idx]['create_time']=time.time() #for auto dispatch
                                
                        if idx in range(self.begin, self.end): #chocp 2021/12/14
                            datasets_index={\
                                        'index':idx,\
                                        'lotID': self.lots[idx].get('lotID',''),\
                                        'stage':self.lots[idx].get('stage',''),\
                                        'product':self.lots[idx].get('product',''),\
                                        'machine':self.lots[idx].get('machine',''),\
                                        'cust':self.lots[idx].get('cust',''),\
                                        'partID':self.lots[idx].get('partID',''),\
                                        'lottype':self.lots[idx].get('lottype',''),\
                                        'automotive':self.lots[idx].get('automotive',''),\
                                        'state':self.lots[idx].get('state',''),\
                                        'holdcode':self.lots[idx].get('holdcode',''),\
                                        'turnratio':self.lots[idx].get('turnratio',0),\
                                        'eotd':self.lots[idx].get('eotd',''),\
                                        'holdreas':self.lots[idx].get('holdreas',''),\
                                        'potd':self.lots[idx].get('potd',''),\
                                        'waferlot':self.lots[idx].get('waferlot',''),\
                                        'desc':self.lots[idx].get('desc',''),\
                                        'device':self.lots[idx].get('device',''),\
                                        'booked':self.lots[idx].get('booked', 0),\
                                        'area_id':self.carriers[idx].get('area_id', ''),\
                                        'box_color':self.carriers[idx].get('box_color', 0), #chocp 2021/12/14
                                        'direction_target':self.carriers[idx].get('direction_target', ''),
                                        'recipe':self.lots[idx].get('recipe',''),
                                        'alarm':self.lots[idx].get('alarm',''),
                                        "lpt":self.lots[idx].get("lpt",""),
                                        "qty":self.lots[idx].get("qty",""),
                                        "lptdesc":self.lots[idx].get("stage",""),
                                        "queue_time":self.lots[idx].get("queue_time",""),
                                        "background_color":self.lots[idx].get('background_color', ''),
                                        "buzzer":self.lots[idx].get('buzzer', ''),
                                        'errorCode':self.lots[idx].get('errorCode', ''),
                                        }
                            datasets_use={}
                            erack_data_item=[] #8.25.11-1
                            if global_variables.RackNaming == 9: #Qualcomm
                                erack_data_item=global_variables.global_erack_item['QUALCOMM'].erack_data

                            elif global_variables.RackNaming in [23,16,34, 54]: #SJ
                                erack_data_item=global_variables.global_erack_item['SJ'].erack_data

                            elif global_variables.RackNaming in [17,11]: #Jcet
                                erack_data_item=global_variables.global_erack_item['JCET'].erack_data

                            elif global_variables.RackNaming == 26: #TI CBUMP
                                erack_data_item=global_variables.global_erack_item['TI'].erack_data

                            elif global_variables.RackNaming == 24: #SkyworksSG
                                erack_data_item=global_variables.global_erack_item['SKYWORKSSG'].erack_data

                            elif global_variables.RackNaming == 7: #Chipmos
                                erack_data_item=global_variables.global_erack_item['CHIPMOS'].erack_data

                            else:
                                erack_data_item=global_variables.global_erack_item['NORMAL'].erack_data

                            for i in erack_data_item:
                                if i in datasets_index.keys():
                                    datasets_use[i]=datasets_index[i]
                            datasets.append(datasets_use)

                            doc={'res':'found', 'datasets':datasets, 'time':time.time(), 'connection':connection}

                    self.turn=(self.turn+1)%self.rows
                    self.begin=self.columns*self.turn
                    self.end=self.begin+self.columns
                    msg = bytearray(json.dumps(doc) + '\n', encoding='utf-8')
                    self.sock.send(msg) #response remote query #chocp:2021/5/31
                    self.raw_logger.debug('TSC => {}'.format(msg))
                    self.eRackStatusUpdate()

                    try:
                        E88_com_state=self.secsgem_e88_h.communicationState.current
                        if E88_com_state != last_E88_com_state:
                            last_E88_com_state=E88_com_state

                    except Exception as e:
                        print(e)

            except alarms.MyException as e: #ErackOffLineWarning
                #traceback.print_exc()
                self.sock.close()
                self.connected=False
                self.sync=False
                self.erack_status='DOWN'

                # output('AlarmSet', {'type':e.alarm_set, 'code':e.code, 'extend_code':e.sub_code, 'txt':e.txt})
                self.eRackStatusUpdate()
                time.sleep(1)

            except: #ErackOffLineWarning
                traceback.print_exc()
                self.sock.close()
                self.connected=False
                self.sync=False
                self.erack_status='DOWN'

                # output('AlarmSet', {'type':'Error', 'code':30000, 'extend_code':self.device_id, 'txt':traceback.format_exc()})
                self.eRackStatusUpdate()
                time.sleep(1)
                #self.secsgem_e82_h.set_alarm(self.error_code)
        else:
            for idx, carrier in enumerate(self.carriers): # Mike: 2021/12/01
                rack_id=self.device_id
                port_no=idx+1
                CarrierLoc=''
                zonename=carrier['area_id'] if carrier['area_id'] else self.groupID if (self.groupID and global_variables.RackNaming == 2) else self.device_id
                res, CarrierLoc=tools.print_rackport_format(rack_id, port_no, self.rows, self.columns)
                if not res:
                    alarms.SCSyntaxWarning(rack_id, handler=self.secsgem_e88_h)

                self.E88_Zones.Data[zonename].StockerUnit[CarrierLoc]['StockerUnitState']=1
                self.E88_Zones.Data[zonename].StockerUnit[CarrierLoc]['CarrierID']=''

                if CarrierLoc in self.E88_Carriers.Mapping:
                    if self.E88_Carriers.Mapping[CarrierLoc] in self.E88_Carriers.Data:
                        # Check carrier state machine current state to avoid calling kill_carrier in none state
                        current_state = self.E88_Carriers.Data[self.E88_Carriers.Mapping[CarrierLoc]].State.current
                        if self.E88_Carriers.Data[self.E88_Carriers.Mapping[CarrierLoc]].CarrierState == 3:
                            self.E88_Carriers.Data[self.E88_Carriers.Mapping[CarrierLoc]].State.remove()
                        elif current_state != 'none':
                            # Only call kill_carrier when not in none state
                            self.E88_Carriers.Data[self.E88_Carriers.Mapping[CarrierLoc]].State.kill_carrier()
                        else:
                            print("Warning: Carrier {} at location {} is already in none state, skip kill_carrier".format(self.E88_Carriers.Mapping[CarrierLoc], CarrierLoc))
                        self.E88_Carriers.delete(self.E88_Carriers.Mapping[CarrierLoc])
                        self.zone_capacity_change(zonename, 'Inc')
                        if CarrierLoc in self.E88_Carriers.Mapping:
                            del self.E88_Carriers.Mapping[CarrierLoc]
                        self.read_carriers[idx]['carrierID']=''

            for zonename in self.zone_list:
                datasets={}
                datasets['ZoneSize']=self.E88_Zones.Data[zonename].ZoneSize - len(self.zone_list[zonename])
                datasets['ZoneCapacity']=self.E88_Zones.Data[zonename].ZoneCapacity - len(self.zone_list[zonename])
                self.zone_capacity_change(zonename, datasets['ZoneCapacity'])
                if datasets['ZoneSize'] > 0:
                    self.E88_Zones.set(zonename, datasets)
                    for CarrierLoc in self.zone_list[zonename]:
                        del self.E88_Zones.Data[zonename].StockerUnit[CarrierLoc]
                else:
                    self.E88_Zones.delete(zonename)
                print(zonename, datasets['ZoneSize'], datasets['ZoneCapacity'], self.zone_list[zonename])

            dataset={'DeviceID':self.device_id}
            E88.report_event(self.secsgem_e88_h, E88.DeviceOffline, dataset)
            self.sock.close()
            print('\n<end eRack thread:{}>\n'.format(self.device_id))