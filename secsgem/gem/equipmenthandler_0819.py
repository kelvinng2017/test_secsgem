#####################################################################
# equipmenthandler.py
#
# (c) Copyright 2013-2015, Benjamin Parzella. All rights reserved.
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
"""Handler for GEM equipment."""

from ..common.fysom import Fysom
from ..gem.handler import GemHandler
from ..secs.variables import SecsVarString, SecsVarU4, SecsVarArray, SecsVarI2, \
    SecsVarI4, SecsVarBinary, SecsVarU1, SecsVarU2
from ..secs.dataitems import SV, ECV, ACKC5, ALED, ALCD, HCACK, CPACK, CEPACK

from datetime import datetime
from dateutil.tz import tzlocal

from time import sleep

simple_cmd_reply = True

''' ECID '''
ECID_ESTABLISH_COMMUNICATIONS_TIMEOUT = 1
GEM_MAX_SPOOL_TRANSMIT = 52
GEM_CONFIG_SPOOL = 66
GEM_OVER_WRITE_SPOOL = 67
GEM_TIME_FORMAT = 68

''' SVID '''
GEM_CLOCK = 3
GEM_CONTROL_STATE = 4
GEM_LINK_STATE = 5
GEM_PREVIOUS_CONTROL_STATE = 13
GEM_PREVIOUS_EC_STATE = 14
GEM_PROCESS_STATE = 15
GEM_ALARMS_ENABLED = 39
GEM_ALARMS_SET = 40
GEM_EVENTS_ENABLED = 41

GEM_SPOOL_COUNT_ACTUAL = 53
GEM_SPOOL_COUNT_TOTAL = 54
GEM_SPOOL_FULL_TIME = 55
GEM_SPOOL_START_TIME = 57
GEM_SPOOL_STATE = 58
GEM_SPOOL_UNLOAD_SUPSTATE = 59

''' CEID '''
GEM_CONTROL_STATE_LOCAL = 8
GEM_CONTROL_STATE_REMOTE = 9
GEM_MESSATE_RECOGNITION = 21
GEM_EQP_OFFLINE = 22
GEM_SPOOLING_ACTIVATED = 23
GEM_SPOOLING_DEACTIVATED = 24
GEM_SPOOL_TRANSMIT_FAILURE = 25

RCMD_START = "START"
RCMD_STOP = "STOP"

class DataValue(object):
    """Data value definition

    You can manually set the secs-type of the id with the 'id_type' keyword argument.

    Custom parameters can be set with the keyword arguments,
    they will be passed to the GemEquipmentHandlers callback
    :func:`secsgem.gem.equipmenthandler.GemEquipmentHandler.on_dv_value_request`.

    If use_callbacks is disabled, you can set the value with the value property.

    :param dvid: ID of the data value
    :type dvid: various
    :param name: long name of the data value
    :type name: string
    :param value_type: type of the data value
    :type value_type: type of class inherited from :class:`secsgem.secs.variables.SecsVar`
    :param use_callback: use the GemEquipmentHandler callbacks to get variable (True) or use internal value
    :type use_callback: boolean
    """

    def __init__(self, dvid, name, value_type, use_callback=True, **kwargs):
        self.dvid = dvid
        self.name = name
        self.value_type = value_type
        self.use_callback = use_callback
        self.value = 0

        if isinstance(self.dvid, int):
            self.id_type = SecsVarU4
        else:
            self.id_type = SecsVarString

        for key, value in kwargs.items():
            setattr(self, key, value)


class StatusVariable(object):
    """Status variable definition

    You can manually set the secs-type of the id with the 'id_type' keyword argument.

    Custom parameters can be set with the keyword arguments,
    they will be passed to the GemEquipmentHandlers callback
    :func:`secsgem.gem.equipmenthandler.GemEquipmentHandler.on_sv_value_request`.

    If use_callbacks is disabled, you can set the value with the value property.

    :param svid: ID of the status variable
    :type svid: various
    :param name: long name of the status variable
    :type name: string
    :param unit: unit (see SEMI E5, Units of Measure)
    :type unit: string
    :param value_type: type of the status variable
    :type value_type: type of class inherited from :class:`secsgem.secs.variables.SecsVar`
    :param use_callback: use the GemEquipmentHandler callbacks to get variable (True) or use internal value
    :type use_callback: boolean
    """

    def __init__(self, svid, name, unit, value_type, use_callback=True, **kwargs):
        self.svid = svid
        self.name = name
        self.unit = unit
        self.value_type = value_type
        self.use_callback = use_callback
        self.value = 0

        if isinstance(self.svid, int):
            self.id_type = SecsVarU4
        else:
            self.id_type = SecsVarString

        for key, value in kwargs.items():
            setattr(self, key, value)


class CollectionEvent(object):
    """Collection event definition

    You can manually set the secs-type of the id with the 'id_type' keyword argument.

    Custom parameters can be set with the keyword arguments,
    they will be passed to the GemEquipmentHandlers callback
    :func:`secsgem.gem.equipmenthandler.GemEquipmentHandler.on_dv_value_request`.

    If use_callbacks is disabled, you can set the value with the value property.

    :param ceid: ID of the collection event
    :type ceid: various
    :param name: long name of the collection event
    :type name: string
    :param data_values: data values available for this event
    :type data_values: list of DVIDs
    """

    def __init__(self, ceid, name, data_values, **kwargs):
        self.ceid = ceid
        self.name = name
        self.data_values = data_values

        if isinstance(self.ceid, int):
            self.id_type = SecsVarU4
        else:
            self.id_type = SecsVarString

        for key, value in kwargs.items():
            setattr(self, key, value)


class CollectionEventLink(object):
    """Representation for registered/linked collection event

    :param ce: ID of the collection event
    :type ce: :class:`secsgem.gem.equipmenthandler.CollectionEvent`
    :param reports: list of the linked reports
    :type reports: list of :class:`secsgem.gem.equipmenthandler.CollectionEventReport`
    """

    def __init__(self, ce, reports, **kwargs):
        self.ce = ce
        self._reports = reports
        self.enabled = False

        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def reports(self):
        """The list of the data values

        :returns: List of linked reports
        :rtype: list of :class:`secsgem.gem.equipmenthandler.CollectionEventReport`
        """
        return self._reports


class CollectionEventReport(object):
    """Report definition for registered collection events

    You can manually set the secs-type of the id with the 'id_type' keyword argument.

    :param rptid: ID of the report
    :type rptid: various
    :param vars: long name of the collection event
    :type vars: string
    """

    def __init__(self, rptid, variables, **kwargs):
        self.rptid = rptid
        self.vars = variables

        if isinstance(self.rptid, int):
            self.id_type = SecsVarU4
        else:
            self.id_type = SecsVarString

        for key, value in kwargs.items():
            setattr(self, key, value)


class EquipmentConstant(object):
    """Equipment constant definition

    You can manually set the secs-type of the id with the 'id_type' keyword argument.

    Custom parameters can be set with the keyword arguments,
    they will be passed to the GemEquipmentHandlers callbacks
    :func:`secsgem.gem.equipmenthandler.GemEquipmentHandler.on_ec_value_request`
    and :func:`secsgem.gem.equipmenthandler.GemEquipmentHandler.on_ec_value_update` .

    If use_callbacks is disabled, you can set the value with the value property.

    :param svid: ID of the equipment constant
    :type svid: various
    :param name: long name
    :type name: string
    :param min_value: minimum value
    :type min_value: various
    :param max_value: maximum value
    :type max_value: various
    :param default_value: default value
    :type default_value: various
    :param unit: unit (see SEMI E5, Units of Measure)
    :type unit: string
    :param value_type: type of the status variable
    :type value_type: type of class inherited from :class:`secsgem.secs.variables.SecsVar`
    :param use_callback: use the GemEquipmentHandler callbacks to get and set variable (True) or use internal value
    :type use_callback: boolean
    """

    def __init__(self, ecid, name, min_value, max_value, default_value, unit, value_type, use_callback=True, **kwargs):
        self.ecid = ecid
        self.name = name
        self.min_value = min_value
        self.max_value = max_value
        self.default_value = default_value
        self.unit = unit
        self.value_type = value_type
        self.use_callback = use_callback
        self.value = default_value

        if isinstance(self.ecid, int):
            self.id_type = SecsVarU4
        else:
            self.id_type = SecsVarString

        for key, value in kwargs.items():
            setattr(self, key, value)


class Alarm(object):
    """Alarm definition

    You can manually set the secs-type of the id with the 'id_type' keyword argument.

    Custom parameters can be set with the keyword arguments,
    they will be passed to the GemEquipmentHandlers callback
    :func:`secsgem.gem.equipmenthandler.GemEquipmentHandler.on_sv_value_request`.

    :param svid: ID of the status variable
    :type svid: various
    :param name: long name of the status variable
    :type name: string
    :param unit: unit (see SEMI E5, Units of Measure)
    :type unit: string
    :param value_type: type of the status variable
    :type value_type: type of class inherited from :class:`secsgem.secs.variables.SecsVar`
    :param use_callback: use the GemEquipmentHandler callbacks to get variable (True) or use internal value
    :type use_callback: boolean
    """

    def __init__(self, alid, name, text, code, ce_on, ce_off, **kwargs):
        self.alid = alid
        self.name = name
        self.text = text
        self.code = code
        self.ce_on = ce_on
        self.ce_off = ce_off
        self.enabled = False
        self.set = False

        if isinstance(self.alid, int):
            self.id_type = SecsVarU4
        else:
            self.id_type = SecsVarString

        for key, value in kwargs.items():
            setattr(self, key, value)


class RemoteCommand(object):
    """Remote command definition
    You can manually set the secs-type of the id with the 'id_type' keyword argument.
    Custom parameters can be set with the keyword arguments,
    they will be passed to the GemEquipmentHandlers callback
    :func:`secsgem.gem.equipmenthandler.GemEquipmentHandler._on_rcmd_<remote_command>`.
    :param rcmd: ID of the status variable
    :type rcmd: various
    :param name: long name of the status variable
    :type name: string
    :param params: array of available parameter names
    :type params: list
    :param ce_finished: collection event to trigger when remote command was finished
    :type ce_finished: types supported by data item CEID
    """

    def __init__(self, rcmd, name, params, ce_finished, **kwargs):
        self.rcmd = rcmd
        self.name = name
        self.params = params
        self.ce_finished = ce_finished

        if isinstance(self.rcmd, int):
            self.id_type = SecsVarU4
        else:
            self.id_type = SecsVarString

        for key, value in kwargs.items():
            setattr(self, key, value)


class GemEquipmentHandler(GemHandler):
    """Baseclass for creating equipment models. Inherit from this class and override required functions.

    :param address: IP address of remote host
    :type address: string
    :param port: TCP port of remote host
    :type port: integer
    :param active: Is the connection active (*True*) or passive (*False*)
    :type active: boolean
    :param session_id: session / device ID to use for connection
    :type session_id: integer
    :param name: Name of the underlying configuration
    :type name: string
    :param custom_connection_handler: object for connection handling (ie multi server)
    :type custom_connection_handler: :class:`secsgem.hsms.connections.HsmsMultiPassiveServer`
    :param initial_control_state: initial state for the control state model, one of ["EQUIPMENT_OFFLINE", "ATTEMPT_ONLINE", "HOST_OFFLINE", "ONLINE"]
    :type initial_control_state: string
    """

    def __init__(self, address, port, active, session_id, name, custom_connection_handler=None, initial_control_state="ATTEMPT_ONLINE", initial_online_control_state="REMOTE"):
        GemHandler.__init__(self, address, port, active, session_id, name, custom_connection_handler)

        self.isHost = False

        self.initialControlStates = ["EQUIPMENT_OFFLINE", "ATTEMPT_ONLINE", "HOST_OFFLINE", "ONLINE"]
        self.initialControlState = initial_control_state

        self.onlineControlStates = ["LOCAL", "REMOTE"]
        self.onlineControlState = initial_online_control_state

        self._time_format = 1
        
        self._spool_enable = 0
        
        self._DATAID = 0

        self._data_values = {
        }

        self._status_variables = {
            GEM_CLOCK: StatusVariable(GEM_CLOCK, "Clock", "", SecsVarString),
            GEM_CONTROL_STATE: StatusVariable(GEM_CONTROL_STATE, "ControlState", "", SecsVarBinary),
            GEM_EVENTS_ENABLED: StatusVariable(GEM_EVENTS_ENABLED, "EventsEnabled", "", SecsVarArray),
            GEM_ALARMS_ENABLED: StatusVariable(GEM_ALARMS_ENABLED, "AlarmsEnabled", "", SecsVarArray),
            GEM_ALARMS_SET: StatusVariable(GEM_ALARMS_SET, "AlarmsSet", "", SecsVarArray),
            GEM_LINK_STATE: StatusVariable(GEM_LINK_STATE, "LINK_STATE", "", SecsVarU1),
            #GEM_SPOOL_STATE: StatusVariable(GEM_SPOOL_STATE, "SPOOL_STATE", "", SecsVarU1),
            #GEM_SPOOL_UNLOAD_SUPSTATE: StatusVariable(GEM_SPOOL_UNLOAD_SUPSTATE, "SPOOL_UNLOAD_SUPSTATE", "", SecsVarU1),
        }

        self._collection_events = {
            GEM_EQP_OFFLINE: CollectionEvent(GEM_EQP_OFFLINE, "EquipmentOffline", []),
            GEM_CONTROL_STATE_LOCAL: CollectionEvent(GEM_CONTROL_STATE_LOCAL, "ControlStateLocal", []),
            GEM_CONTROL_STATE_REMOTE: CollectionEvent(GEM_CONTROL_STATE_REMOTE, "ControlStateRemote", []),
        }

        self._equipment_constants = {
            ECID_ESTABLISH_COMMUNICATIONS_TIMEOUT: EquipmentConstant(ECID_ESTABLISH_COMMUNICATIONS_TIMEOUT, "EstablishCommunicationsTimeout", 10, 120, 10, "sec", SecsVarI2),
            GEM_TIME_FORMAT: EquipmentConstant(GEM_TIME_FORMAT, "TimeFormat", 0, 3, 1, "", SecsVarU1),
            
            GEM_MAX_SPOOL_TRANSMIT: EquipmentConstant(GEM_MAX_SPOOL_TRANSMIT, "MaxSpoolTransmit", 0, 3, 1, "", SecsVarU2),
            GEM_CONFIG_SPOOL: EquipmentConstant(GEM_CONFIG_SPOOL, "ConfigSpool", 0, 1, 1, "", SecsVarU1),
            GEM_OVER_WRITE_SPOOL: EquipmentConstant(GEM_OVER_WRITE_SPOOL, "OverWriteSpool", 0, 1, 1, "", SecsVarBinary),
        }

        self._alarms = {
        }

        self._remote_commands = {
            RCMD_START: RemoteCommand(RCMD_START, "Start", [], []),
            RCMD_STOP: RemoteCommand(RCMD_STOP, "Stop", [], []),
        }

        self._enhance_remote_commands = {
        }

        self._registered_reports = {}
        self._registered_collection_events = {}

        ##############################################
        #   control state 
        ##############################################

        self.controlState = Fysom({
            'initial': "INIT",
            'events': [
                {'name': 'start', 'src': 'INIT', 'dst': 'CONTROL'},  # 1
                {'name': 'initial_offline', 'src': 'CONTROL', 'dst': 'OFFLINE'},  # 1
                {'name': 'initial_equipment_offline', 'src': 'OFFLINE', 'dst': 'EQUIPMENT_OFFLINE'},  # 2
                {'name': 'initial_attempt_online', 'src': 'OFFLINE', 'dst': 'ATTEMPT_ONLINE'},  # 2
                {'name': 'initial_host_offline', 'src': 'OFFLINE', 'dst': 'HOST_OFFLINE'},  # 2
                {'name': 'switch_online', 'src': 'EQUIPMENT_OFFLINE', 'dst': 'ATTEMPT_ONLINE'},  # 3
                {'name': 'attempt_online_fail_equipment_offline', 'src': 'ATTEMPT_ONLINE', 'dst': 'EQUIPMENT_OFFLINE'},  # 4
                {'name': 'attempt_online_fail_host_offline', 'src': 'ATTEMPT_ONLINE', 'dst': 'HOST_OFFLINE'},  # 4
                {'name': 'attempt_online_success', 'src': 'ATTEMPT_ONLINE', 'dst': 'ONLINE'},  # 5
                {'name': 'switch_offline', 'src': ["ONLINE", "ONLINE_LOCAL", "ONLINE_REMOTE"], 'dst': 'EQUIPMENT_OFFLINE'},  # 6, 12
                {'name': 'initial_online', 'src': 'CONTROL', 'dst': 'ONLINE'},  # 1
                {'name': 'initial_online_local', 'src': 'ONLINE', 'dst': 'ONLINE_LOCAL'},  # 7
                {'name': 'initial_online_remote', 'src': 'ONLINE', 'dst': 'ONLINE_REMOTE'},  # 7
                {'name': 'switch_online_local', 'src': 'ONLINE_REMOTE', 'dst': 'ONLINE_LOCAL'},  # 8
                {'name': 'switch_online_remote', 'src': 'ONLINE_LOCAL', 'dst': 'ONLINE_REMOTE'},  # 9
                {'name': 'remote_offline', 'src': ["ONLINE", "ONLINE_LOCAL", "ONLINE_REMOTE"], 'dst': 'HOST_OFFLINE'},  # 10
                {'name': 'remote_online', 'src': 'HOST_OFFLINE', 'dst': 'ONLINE'},  # 11
            ],
            'callbacks': {
                'onCONTROL': self._on_control_state_control,  # 1, forward online/offline depending on configuration
                'onOFFLINE': self._on_control_state_offline,  # 2, forward to configured offline state
                'onATTEMPT_ONLINE': self._on_control_state_attempt_online,  # 3, send S01E01
                'onONLINE': self._on_control_state_online,  # 7, forward to configured online state
                'oninitial_online_local': self._on_control_state_initial_online_local,  # 7, send collection event
                'onswitch_online_local': self._on_control_state_initial_online_local,  # 8, send collection event
                'oninitial_online_remote': self._on_control_state_initial_online_remote,  # 8, send collection event
                'onswitch_online_remote': self._on_control_state_initial_online_remote,  # 9, send collection event
            },
            'autoforward': [
                # {'src': 'OFFLINE', 'dst': 'EQUIPMENT_OFFLINE'},  # 2
                # {'src': 'EQUIPMENT_INITIATED_CONNECT', 'dst': 'WAIT_CRA'},  # 5
                # {'src': 'HOST_INITIATED_CONNECT', 'dst': 'WAIT_CR_FROM_HOST'},  # 10
            ]
        })

        self.controlState.start()

        ##############################################
        #   spool state Mike: 2019/12/12
        ##############################################
        
        self.spoolHistory = 'SPOOL_INACTIVE'
        
        self.spoolState = Fysom({
            'initial': 'POWER_ON',  # 8
            'events': [
                {'name': 'active_H', 'src': 'POWER_ON', 'dst': 'SPOOL_ACTIVATE'},  # 8
                {'name': 'inactive_H', 'src': 'POWER_ON', 'dst': 'SPOOL_INACTIVATE'},  # 8
                {'name': 'activate', 'src': 'SPOOL_INACTIVATE', 'dst': 'SPOOL_ACTIVATE'},  # 1
                {'name': 'transmit', 'src': 'NO_SPOOL_OUTPUT', 'dst': 'SPOOL_TRANSMIT'},  # 5
                {'name': 'stoptransmit', 'src': 'SPOOL_TRANSMIT', 'dst': 'NO_SPOOL_OUTPUT'},  # 6
                {'name': 'purge', 'src': 'NO_SPOOL_OUTPUT', 'dst': 'PURGE_SPOOL'},  # 4
            ],
            'callbacks': {
                #'onPOWER_ON': self._on_power_on,
            },
            'autoforward': [
                {'src': 'SPOOL_ACTIVATE', 'dst': 'NO_SPOOL_OUTPUT'},  # X
                {'src': 'PURGE_SPOOL', 'dst': 'SPOOL_INACTIVATE'},  # 3
            ]
        })

        ##############################################
        #   spool load state Mike: 2019/12/12
        ##############################################
        
        self.spoolLoadState = Fysom({
            'initial': 'SPOOL_NOT_FULL',  # 8
            'events': [
                {'name': 'full', 'src': 'SPOOL_NOT_FULL', 'dst': 'SPOOL_FULL'},  # 2
            ],
            'callbacks': {
                #'onPOWER_ON': self._on_power_on,
            },
            'autoforward': [
                {'src': 'SPOOL_ACTIVATE', 'dst': 'NO_SPOOL_OUTPUT'},  # X
                {'src': 'PURGE_SPOOL', 'dst': 'SPOOL_INACTIVATE'},  # 3
            ]
        })

    ##################################
    #   control state model
    ##################################

    def disable(self): # Mike: 2020/02/26
        """Disables the connection"""
        self.connection.disable()
        self.communicationState.disable()

        # update control state
        if self.controlState.current in ["ONLINE", "ONLINE_LOCAL", "ONLINE_REMOTE"]:
            self.controlState.switch_offline()

        self.logger.info("Connection disabled")

    def _on_control_state_control(self, _):
        if self.initialControlState == "ONLINE":
            self.controlState.initial_online()
        else:
            self.controlState.initial_offline()

    def _on_control_state_offline(self, _):
        if self.initialControlState == "EQUIPMENT_OFFLINE":
            self.controlState.initial_equipment_offline()
        elif self.initialControlState == "ATTEMPT_ONLINE":
            self.controlState.initial_attempt_online()
        elif self.initialControlState == "HOST_OFFLINE":
            self.controlState.initial_host_offline()

    def _on_control_state_attempt_online(self, _):
        if not self.communicationState.isstate("COMMUNICATING"):
            self.controlState.attempt_online_fail_host_offline() # Mike: 2020/03/25
            sleep(0.5)
            return

        response = self.are_you_there()

        if response is None:
            self.controlState.attempt_online_fail_host_offline() # Mike: 2020/03/25
            return

        if response.header.stream != 1 or response.header.function != 2:
            self.controlState.attempt_online_fail_host_offline() # Mike: 2020/03/25
            return

        self.controlState.attempt_online_success()

    def _on_control_state_online(self, _):
        if self.onlineControlState == "REMOTE":
            self.controlState.initial_online_remote()
        else:
            self.controlState.initial_online_local()

    def _on_control_state_initial_online_local(self, _):
        self.trigger_collection_events([GEM_CONTROL_STATE_LOCAL])

    def _on_control_state_initial_online_remote(self, _):
        self.trigger_collection_events([GEM_CONTROL_STATE_REMOTE])

    def control_switch_online(self):
        """Operator switches to online control state"""
        self.controlState.switch_online()

    def control_switch_offline(self):
        """Operator switches to offline control state"""
        self.controlState.switch_offline()
        self.trigger_collection_events([GEM_EQP_OFFLINE])

    def control_switch_online_local(self):
        """Operator switches to the local online control state"""
        self.controlState.switch_online_local()
        self.onlineControlState = "LOCAL"

    def control_switch_online_remote(self):
        """Operator switches to the local online control state"""
        self.controlState.switch_online_remote()
        self.onlineControlState = "REMOTE"

    def _on_s01f15(self, handler, packet):
        """Callback handler for Stream 1, Function 15, Request offline

        :param handler: handler the message was received on
        :type handler: :class:`secsgem.hsms.handler.HsmsHandler`
        :param packet: complete message received
        :type packet: :class:`secsgem.hsms.packets.HsmsPacket`
        """
        if self.controlState.current not in ["ONLINE", "ONLINE_LOCAL", "ONLINE_REMOTE"]: # Mike 2020/02/19
            return self.stream_function(1, 0)()

        del handler, packet  # unused parameters

        OFLACK = 0

        if self.controlState.current in ["ONLINE", "ONLINE_LOCAL", "ONLINE_REMOTE"]:
            self.controlState.remote_offline()
            self.trigger_collection_events([GEM_EQP_OFFLINE])

        return self.stream_function(1, 16)(OFLACK)

    def _on_s01f17(self, handler, packet):
        """Callback handler for Stream 1, Function 17, Request online

        :param handler: handler the message was received on
        :type handler: :class:`secsgem.hsms.handler.HsmsHandler`
        :param packet: complete message received
        :type packet: :class:`secsgem.hsms.packets.HsmsPacket`
        """
        del handler, packet  # unused parameters

        ONLACK = 1

        if self.controlState.isstate("HOST_OFFLINE"):
            self.controlState.remote_online()
            ONLACK = 0
        elif self.controlState.current in ["ONLINE", "ONLINE_LOCAL", "ONLINE_REMOTE"]:
            ONLACK = 2

        return self.stream_function(1, 18)(ONLACK)

    # data values

    @property
    def data_values(self):
        """The list of the data values

        :returns: Data value list
        :rtype: list of :class:`secsgem.gem.equipmenthandler.DataValue`
        """
        return self._data_values

    def on_dv_value_request(self, dvid, dv):
        """Get the data value depending on its configuation.

        Override in inherited class to provide custom data value request handling.

        :param dvid: Id of the data value encoded in the corresponding type
        :type dvid: :class:`secsgem.secs.variables.SecsVar`
        :param dv: The data value requested
        :type dv: :class:`secsgem.gem.equipmenthandler.DataValue`
        :returns: The value encoded in the corresponding type
        :rtype: :class:`secsgem.secs.variables.SecsVar`
        """
        del dvid  # unused variable

        return dv.value_type(dv.value)

    def _get_dv_value(self, dv):
        """Get the data value depending on its configuation

        :param dv: The data value requested
        :type dv: :class:`secsgem.gem.equipmenthandler.DataValue`
        :returns: The value encoded in the corresponding type
        :rtype: :class:`secsgem.secs.variables.SecsVar`
        """
        if dv.use_callback:
            return self.on_dv_value_request(dv.id_type(dv.dvid), dv)
        else:
            return dv.value_type(dv.value)

    ##################################
    #   status variables
    ##################################

    @property
    def status_variables(self):
        """The list of the status variables

        :returns: Status variable list
        :rtype: list of :class:`secsgem.gem.equipmenthandler.StatusVariables`
        """
        return self._status_variables

    def on_sv_value_request(self, svid, sv):
        """Get the status variable value depending on its configuation.

        Override in inherited class to provide custom status variable request handling.

        :param svid: Id of the status variable encoded in the corresponding type
        :type svid: :class:`secsgem.secs.variables.SecsVar`
        :param sv: The status variable requested
        :type sv: :class:`secsgem.gem.equipmenthandler.StatusVariable`
        :returns: The value encoded in the corresponding type
        :rtype: :class:`secsgem.secs.variables.SecsVar`
        """
        del svid  # unused variable

        return sv.value_type(sv.value)

    def _get_sv_value(self, sv):
        """Get the status variable value depending on its configuation

        :param sv: The status variable requested
        :type sv: :class:`secsgem.gem.equipmenthandler.StatusVariable`
        :returns: The value encoded in the corresponding type
        :rtype: :class:`secsgem.secs.variables.SecsVar`
        """
        if sv.svid == GEM_CLOCK:
            return sv.value_type(self._get_clock())
        if sv.svid == GEM_CONTROL_STATE:
            return sv.value_type(self._get_control_state_id())
        if sv.svid == GEM_EVENTS_ENABLED:
            events = self._get_events_enabled()
            return sv.value_type(SV, events)
        if sv.svid == GEM_ALARMS_ENABLED:
            alarms = self._get_alarms_enabled()
            return sv.value_type(SV, alarms)
        if sv.svid == GEM_ALARMS_SET:
            alarms = self._get_alarms_set()
            return sv.value_type(SV, alarms)
        if sv.svid == GEM_LINK_STATE:
            if self.communicationState.isstate("COMMUNICATING"):
                return sv.value_type(2)
            elif self.communicationState.isstate("DISABLE"):
                return sv.value_type(0)
            else:
                return sv.value_type(1)
        if sv.svid == GEM_SPOOL_STATE:
            if not self.communicationState.isstate("COMMUNICATING"):
                return sv.value_type(2)
            else:
                return sv.value_type(1)

        if sv.use_callback:
            return self.on_sv_value_request(sv.id_type(sv.svid), sv)
        else:
            return sv.value_type(sv.value)

    def _on_s01f01(self, handler, packet): # Mike: 2020/02/24
        """Callback handler for Stream 1, Function 1, Are You There

        :param handler: handler the message was received on
        :type handler: :class:`secsgem.hsms.handler.HsmsHandler`
        :param packet: complete message received
        :type packet: :class:`secsgem.hsms.packets.HsmsPacket`
        """
        if self.controlState.current not in ["ONLINE", "ONLINE_LOCAL", "ONLINE_REMOTE"]:
            return self.stream_function(1, 0)()
            
        del handler, packet  # unused parameters

        if self.isHost:
            return self.stream_function(1, 2)()
        else:
            return self.stream_function(1, 2)([self.MDLN, self.SOFTREV])

    def _on_s01f03(self, handler, packet):
        """Callback handler for Stream 1, Function 3, Equipment status request

        :param handler: handler the message was received on
        :type handler: :class:`secsgem.hsms.handler.HsmsHandler`
        :param packet: complete message received
        :type packet: :class:`secsgem.hsms.packets.HsmsPacket`
        """
        if self.controlState.current not in ["ONLINE", "ONLINE_LOCAL", "ONLINE_REMOTE"]: # Mike 2020/02/19
            return self.stream_function(1, 0)()

        del handler  # unused parameters

        message = self.secs_decode(packet)

        responses = []

        if len(message) == 0:
            for svid in sorted(self._status_variables): # Mike 2019/09/05
                sv = self._status_variables[svid]
                responses.append(self._get_sv_value(sv))
                #print("svid:{}, value:{}".format(svid, self._get_sv_value(sv)))
        else:
            for svid in message:
                if svid not in self._status_variables:
                    responses.append(SecsVarArray(SV, []))
                else:
                    sv = self._status_variables[svid]
                    responses.append(self._get_sv_value(sv))
        return self.stream_function(1, 4)(responses)

    def _on_s01f11(self, handler, packet):
        """Callback handler for Stream 1, Function 11, SV namelist request

        :param handler: handler the message was received on
        :type handler: :class:`secsgem.hsms.handler.HsmsHandler`
        :param packet: complete message received
        :type packet: :class:`secsgem.hsms.packets.HsmsPacket`
        """
        if self.controlState.current not in ["ONLINE", "ONLINE_LOCAL", "ONLINE_REMOTE"]: # Mike 2020/02/19
            return self.stream_function(1, 0)()

        del handler  # unused parameters

        message = self.secs_decode(packet)

        responses = []

        if len(message) == 0:
            for svid in sorted(self._status_variables): # Mike 2019/09/05
                sv = self._status_variables[svid]
                responses.append({"SVID": sv.svid, "SVNAME": sv.name, "UNITS": sv.unit})
        else:
            for svid in message:
                if svid not in self._status_variables:
                    responses.append({"SVID": svid, "SVNAME": "", "UNITS": ""})
                else:
                    sv = self._status_variables[svid]
                    responses.append({"SVID": sv.svid, "SVNAME": sv.name, "UNITS": sv.unit})

        return self.stream_function(1, 12)(responses)

    ##################################
    #   collection events
    ##################################

    @property
    def collection_events(self):
        """The list of the collection events

        :returns: Collection event list
        :rtype: list of :class:`secsgem.gem.equipmenthandler.CollectionEvent`
        """
        return self._collection_events

    @property
    def registered_reports(self):
        """The list of the subscribed reports

        :returns: Collection event report list
        :rtype: dictionary of subscribed reports
        """
        return self._registered_reports

    @property
    def registered_collection_events(self):
        """The list of the subscribed collection events

        :returns: Collection event list
        :rtype: dictionary of :class:`secsgem.gem.equipmenthandler.CollectionEventLink`

        """
        return self._registered_collection_events

    def trigger_collection_events(self, ceids):
        """Triggers the supplied collection events

        :param ceids: List of collection events
        :type ceids: list of various
        """
        if not isinstance(ceids, list):
            ceids = [ceids]

        for ceid in ceids:
            if ceid in self._registered_collection_events:
                if self._registered_collection_events[ceid].enabled:
                    reports = self._build_collection_event(ceid)

                    self._DATAID += 1
                    self._DATAID &= 255
                    try:
                        self.send_prime_message(self.stream_function(6, 11)({"DATAID": self._DATAID, "CEID": ceid, "RPT": reports}))
                    except Exception as err:
                        self.send_stream_function(self.stream_function(9, 9)())
                        raise Exception(err)
                else:
                    print("report disable")
            else: # Mike: 2020/03/25
                if ceid in self._collection_events:
                    reports = []

                    self._DATAID += 1
                    self._DATAID &= 255
                    try:
                        self.send_prime_message(self.stream_function(6, 11)({"DATAID": self._DATAID, "CEID": ceid, "RPT": reports}))
                    except Exception as err:
                        self.send_stream_function(self.stream_function(9, 9)())
                        raise Exception(err)

    def _on_s02f33(self, handler, packet):
        """Callback handler for Stream 2, Function 33, Define Report

        :param handler: handler the message was received on
        :type handler: :class:`secsgem.hsms.handler.HsmsHandler`
        :param packet: complete message received
        :type packet: :class:`secsgem.hsms.packets.HsmsPacket`
        """
        if self.controlState.current not in ["ONLINE", "ONLINE_LOCAL", "ONLINE_REMOTE"]: # Mike 2020/02/19
            return self.stream_function(2, 0)()

        del handler  # unused parameters

        message = self.secs_decode(packet)

        # 0  = Accept
        # 1  = Denied. Insufficient space.
        # 2  = Denied. Invalid format.
        # 3  = Denied. At least one RPTID already defined.
        # 4  = Denied. At least VID does not exist.
        # >4 = Other errors
        DRACK = 0

        # pre check message for errors
        for report in message.DATA:
            if report.RPTID in self._registered_reports and len(report.VID) > 0:
                DRACK = 3
            else:
                for vid in report.VID:
                    if (vid not in self._data_values) and (vid not in self._status_variables):
                        DRACK = 4

        # pre check okay
        if DRACK == 0:
            # no data -> remove all reports and links
            if not message.DATA:
                self._registered_collection_events.clear()
                self._registered_reports.clear()
            else:
                for report in message.DATA:
                    # no vids -> remove this reports and links
                    if not report.VID:
                        # remove report from linked collection events
                        for collection_event in list(self._registered_collection_events):
                            if report.RPTID in self._registered_collection_events[collection_event].reports:
                                self._registered_collection_events[collection_event].reports.remove(report.RPTID)
                                # remove collection event link if no collection events present
                                if not self._registered_collection_events[collection_event].reports:
                                    del self._registered_collection_events[collection_event]
                        # remove report
                        if report.RPTID in self._registered_reports:
                            del self._registered_reports[report.RPTID]
                    else:
                        # add report
                        self._registered_reports[report.RPTID] = CollectionEventReport(report.RPTID, report.VID)

        return self.stream_function(2, 34)(DRACK)

    def _on_s02f35(self, handler, packet):
        """Callback handler for Stream 2, Function 35, Link event report

        :param handler: handler the message was received on
        :type handler: :class:`secsgem.hsms.handler.HsmsHandler`
        :param packet: complete message received
        :type packet: :class:`secsgem.hsms.packets.HsmsPacket`
        """
        if self.controlState.current not in ["ONLINE", "ONLINE_LOCAL", "ONLINE_REMOTE"]: # Mike 2020/02/19
            return self.stream_function(2, 0)()

        del handler  # unused parameters

        message = self.secs_decode(packet)

        # 0  = Accepted
        # 1  = Denied. Insufficient space
        # 2  = Denied. Invalid format
        # 3  = Denied. At least one CEID link already defined
        # 4  = Denied. At least one CEID does not exist
        # 5  = Denied. At least one RPTID does not exist
        # >5 = Other errors
        LRACK = 0

        # pre check message for errors
        for event in message.DATA:
            if event.CEID.get() not in self._collection_events:
                LRACK = 4
            for rptid in event.RPTID:
                if event.CEID.get() in self._registered_collection_events:
                    ce = self._registered_collection_events[event.CEID.get()]
                    if rptid.get() in ce.reports:
                        LRACK = 3
                if rptid.get() not in self._registered_reports:
                    LRACK = 5

        # pre check okay
        if LRACK == 0:
            for event in message.DATA:
                # no report ids, remove all links for collection event
                if not event.RPTID:
                    if event.CEID.get() in self._registered_collection_events:
                        del self._registered_collection_events[event.CEID.get()]
                else:
                    if event.CEID.get() in self._registered_collection_events:
                        ce = self._registered_collection_events[event.CEID.get()]
                        for rptid in event.RPTID.get():
                            ce.reports.append(rptid)
                    else:
                        self._registered_collection_events[event.CEID.get()] = \
                            CollectionEventLink(self._collection_events[event.CEID.get()], event.RPTID.get())

        return self.stream_function(2, 36)(LRACK)

    def _on_s02f37(self, handler, packet):
        """Callback handler for Stream 2, Function 37, En-/Disable Event Report

        :param handler: handler the message was received on
        :type handler: :class:`secsgem.hsms.handler.HsmsHandler`
        :param packet: complete message received
        :type packet: :class:`secsgem.hsms.packets.HsmsPacket`
        """
        if self.controlState.current not in ["ONLINE", "ONLINE_LOCAL", "ONLINE_REMOTE"]: # Mike 2020/02/19
            return self.stream_function(2, 0)()

        del handler  # unused parameters

        message = self.secs_decode(packet)

        # 0  = Accepted
        # 1  = Denied. At least one CEID does not exist
        ERACK = 0

        if not self._set_ce_state(message.CEED.get(), message.CEID.get()):
            ERACK = 1

        return self.stream_function(2, 38)(ERACK)

    def _on_s06f15(self, handler, packet):
        """Callback handler for Stream 6, Function 15, event report request

        :param handler: handler the message was received on
        :type handler: :class:`secsgem.hsms.handler.HsmsHandler`
        :param packet: complete message received
        :type packet: :class:`secsgem.hsms.packets.HsmsPacket`
        """
        if self.controlState.current not in ["ONLINE", "ONLINE_LOCAL", "ONLINE_REMOTE"]: # Mike 2020/02/19
            return self.stream_function(6, 0)()

        del handler  # unused parameters

        message = self.secs_decode(packet)

        ceid = message.get()

        reports = []

        if ceid in self._registered_collection_events:
            if self._registered_collection_events[ceid].enabled:
                reports = self._build_collection_event(ceid)

        self._DATAID += 1
        self._DATAID &= 255
        return self.stream_function(6, 16)({"DATAID": self._DATAID, "CEID": ceid, "RPT": reports})

    def _on_s06f19(self, handler, packet): # Mike 2019/09/05
        """Callback handler for Stream 6, Function 19, individual report request

        :param handler: handler the message was received on
        :type handler: :class:`secsgem.hsms.handler.HsmsHandler`
        :param packet: complete message received
        :type packet: :class:`secsgem.hsms.packets.HsmsPacket`
        """
        if self.controlState.current not in ["ONLINE", "ONLINE_LOCAL", "ONLINE_REMOTE"]: # Mike 2020/02/19
            return self.stream_function(6, 0)()

        del handler  # unused parameters

        message = self.secs_decode(packet)

        rptid = message.get()

        report = self._registered_reports[rptid]
        variables = []
        for var in report.vars:
            if var in self._status_variables:
                v = self._get_sv_value(self._status_variables[var])
                variables.append(v)
            elif var in self._data_values:
                v = self._get_dv_value(self._data_values[var])
                variables.append(v)

        return self.stream_function(6, 20)(variables)

    def _set_ce_state(self, ceed, ceids):
        """En-/Disable event reports for the supplied ceids (or all, if ceid is an empty list)

        :param ceed: Enable (True) or disable (False) event reports
        :type ceed: bool
        :param ceids: List of collection events
        :type ceids: list of integer
        :returns: True if all ceids were ok, False if illegal ceid was supplied
        :rtype: bool
        """
        result = True
        if not ceids:
            for ceid in self._registered_collection_events:
                self._registered_collection_events[ceid].enabled = ceed
        else:
            for ceid in ceids:
                if ceid in self._registered_collection_events:
                    self._registered_collection_events[ceid].enabled = ceed
                else:
                    result = False

        return result

    def _build_collection_event(self, ceid):
        """Build reports for a collection event

        :param ceid: collection event to build
        :type ceid: integer
        :returns: collection event data
        :rtype: array
        """
        reports = []

        for rptid in self._registered_collection_events[ceid].reports:
            report = self._registered_reports[rptid]
            variables = []
            for var in report.vars:
                if var in self._status_variables:
                    v = self._get_sv_value(self._status_variables[var])
                    variables.append(v)
                elif var in self._data_values:
                    v = self._get_dv_value(self._data_values[var])
                    variables.append(v)

            reports.append({"RPTID": rptid, "V": variables})

        return reports

    ##################################
    #   equipment constants
    ##################################

    @property
    def equipment_constants(self):
        """The list of the equipments contstants

        :returns: Equipment constant list
        :rtype: list of :class:`secsgem.gem.equipmenthandler.EquipmentConstant`
        """
        return self._equipment_constants

    def on_ec_value_request(self, ecid, ec):
        """Get the equipment constant value depending on its configuation.

        Override in inherited class to provide custom equipment constant request handling.

        :param ecid: Id of the equipment constant encoded in the corresponding type
        :type ecid: :class:`secsgem.secs.variables.SecsVar`
        :param ec: The equipment constant requested
        :type ec: :class:`secsgem.gem.equipmenthandler.EquipmentConstant`
        :returns: The value encoded in the corresponding type
        :rtype: :class:`secsgem.secs.variables.SecsVar`
        """
        del ecid  # unused variable

        return ec.value_type(ec.value)

    def on_ec_value_update(self, ecid, ec, value):
        """Set the equipment constant value depending on its configuation.

        Override in inherited class to provide custom equipment constant update handling.

        :param ecid: Id of the equipment constant encoded in the corresponding type
        :type ecid: :class:`secsgem.secs.variables.SecsVar`
        :param ec: The equipment constant to be updated
        :type ec: :class:`secsgem.gem.equipmenthandler.EquipmentConstant`
        :param value: The value encoded in the corresponding type
        :type value: :class:`secsgem.secs.variables.SecsVar`
        """
        del ecid  # unused variable

        ec.value = value

    def _get_ec_value(self, ec):
        """Get the equipment constant value depending on its configuation

        :param ec: The equipment requested
        :type ec: :class:`secsgem.gem.equipmenthandler.EquipmentConstant`
        :returns: The value encoded in the corresponding type
        :rtype: :class:`secsgem.secs.variables.SecsVar`
        """
        if ec.ecid == ECID_ESTABLISH_COMMUNICATIONS_TIMEOUT:
            return ec.value_type(self.establishCommunicationTimeout)
        if ec.ecid == GEM_TIME_FORMAT:
            return ec.value_type(self._time_format)

        if ec.use_callback:
            return self.on_ec_value_request(ec.id_type(ec.ecid), ec)
        else:
            return ec.value_type(ec.value)

    def _set_ec_value(self, ec, value):
        """Get the equipment constant value depending on its configuation

        :param ec: The equipment requested
        :type ec: :class:`secsgem.gem.equipmenthandler.EquipmentConstant`
        :param value: The value encoded in the corresponding type
        :type value: :class:`secsgem.secs.variables.SecsVar`
        """
        if ec.ecid == ECID_ESTABLISH_COMMUNICATIONS_TIMEOUT:
            self.establishCommunicationTimeout = value
        if ec.ecid == GEM_TIME_FORMAT:
            self._time_format = value

        if ec.use_callback:
            self.on_ec_value_update(ec.id_type(ec.ecid), ec, value)
        else:
            ec.value = value

    def _on_s02f13(self, handler, packet):
        """Callback handler for Stream 2, Function 13, Equipment constant request

        :param handler: handler the message was received on
        :type handler: :class:`secsgem.hsms.handler.HsmsHandler`
        :param packet: complete message received
        :type packet: :class:`secsgem.hsms.packets.HsmsPacket`
        """
        if self.controlState.current not in ["ONLINE", "ONLINE_LOCAL", "ONLINE_REMOTE"]: # Mike 2020/02/19
            return self.stream_function(2, 0)()

        del handler  # unused parameters

        message = self.secs_decode(packet)

        responses = []

        if len(message) == 0:
            for ecid in self._equipment_constants:
                ec = self._equipment_constants[ecid]
                responses.append(self._get_ec_value(ec))
        else:
            for ecid in message:
                if ecid not in self._equipment_constants:
                    responses.append(SecsVarArray(ECV, []))
                else:
                    ec = self._equipment_constants[ecid]
                    responses.append(self._get_ec_value(ec))

        return self.stream_function(2, 14)(responses)

    def _on_s02f15(self, handler, packet):
        """Callback handler for Stream 2, Function 15, Equipment constant send

        :param handler: handler the message was received on
        :type handler: :class:`secsgem.hsms.handler.HsmsHandler`
        :param packet: complete message received
        :type packet: :class:`secsgem.hsms.packets.HsmsPacket`
        """
        if self.controlState.current not in ["ONLINE", "ONLINE_LOCAL", "ONLINE_REMOTE"]: # Mike 2020/02/19
            return self.stream_function(2, 0)()

        del handler  # unused parameters

        message = self.secs_decode(packet)

        eac = 0

        for ec in message:
            if ec.ECID not in self._equipment_constants:
                eac = 1
            else:
                constant = self.equipment_constants[ec.ECID.get()]
                
                if constant.min_value is not None:
                    if ec.ECV.get() < constant.min_value:
                        eac = 3 

                if constant.max_value is not None:
                    if ec.ECV.get() > constant.max_value:
                        eac = 3 

        if eac == 0:
            for ec in message:
                self._set_ec_value(self._equipment_constants[ec.ECID], ec.ECV)

        return self.stream_function(2, 16)(eac)

    def _on_s02f29(self, handler, packet):
        """Callback handler for Stream 2, Function 29, EC namelist request

        :param handler: handler the message was received on
        :type handler: :class:`secsgem.hsms.handler.HsmsHandler`
        :param packet: complete message received
        :type packet: :class:`secsgem.hsms.packets.HsmsPacket`
        """
        if self.controlState.current not in ["ONLINE", "ONLINE_LOCAL", "ONLINE_REMOTE"]: # Mike 2020/02/19
            return self.stream_function(2, 0)()

        del handler  # unused parameters

        message = self.secs_decode(packet)

        responses = []

        if len(message) == 0:
            for ecid in self._equipment_constants:
                ec = self._equipment_constants[ecid]
                responses.append({"ECID": ec.ecid, "ECNAME": ec.name, "ECMIN": ec.min_value if ec.min_value is not None else "", \
                    "ECMAX": ec.max_value if ec.max_value is not None else "", "ECDEF": ec.default_value, "UNITS": ec.unit})
        else:
            for ecid in message:
                if ecid not in self._equipment_constants:
                    responses.append({"ECID": ecid, "ECNAME": "", "ECMIN": "", "ECMAX": "", "ECDEF": "", "UNITS": ""})
                else:
                    ec = self._equipment_constants[ecid]
                    responses.append({"ECID": ec.ecid, "ECNAME": ec.name, "ECMIN": ec.min_value if ec.min_value is not None else "", \
                        "ECMAX": ec.max_value if ec.max_value is not None else "", "ECDEF": ec.default_value, "UNITS": ec.unit})

        return self.stream_function(2, 30)(responses)

    ##################################
    #   alarms
    ##################################

    @property
    def alarms(self):
        """The list of the alarms

        :returns: Alarms list
        :rtype: list of :class:`secsgem.gem.equipmenthandler.Alarm`
        """
        return self._alarms

    def set_alarm(self, alid):
        """The list of the alarms

        :param alid: Alarm id
        :type alid: str/int
        """
        if alid not in self.alarms:
            raise ValueError("Unknown alarm id {}".format(alid))
        
        if self.alarms[alid].set:
            return

        if self.alarms[alid].enabled:
            try:
                self.send_prime_message(self.stream_function(5, 1)({"ALCD": self.alarms[alid].code | ALCD.ALARM_SET , \
                    "ALID": alid, "ALTX": self.alarms[alid].text}))
            except Exception as err:
                self.send_stream_function(self.stream_function(9, 9)())
                raise Exception(err)
        
        self.alarms[alid].set = True

        self.trigger_collection_events([self.alarms[alid].ce_on])

    def clear_alarm(self, alid):
        """The list of the alarms

        :param alid: Alarm id
        :type alid: str/int
        """
        if alid not in self.alarms:
            raise ValueError("Unknown alarm id {}".format(alid))
        
        if not self.alarms[alid].set:
            return

        if self.alarms[alid].enabled:
            try:
                self.send_prime_message(self.stream_function(5, 1)({"ALCD": self.alarms[alid].code , "ALID": alid, "ALTX": self.alarms[alid].text}))
            except Exception as err:
                self.send_stream_function(self.stream_function(9, 9)())
                raise Exception(err)

        self.alarms[alid].set = False

        self.trigger_collection_events([self.alarms[alid].ce_off])
        
    def _on_s05f03(self, handler, packet): # Mike 2019/09/06
        """Callback handler for Stream 5, Function 3, Alarm en-/disabled

        :param handler: handler the message was received on
        :type handler: :class:`secsgem.hsms.handler.HsmsHandler`
        :param packet: complete message received
        :type packet: :class:`secsgem.hsms.packets.HsmsPacket`
        """
        if self.controlState.current not in ["ONLINE", "ONLINE_LOCAL", "ONLINE_REMOTE"]: # Mike 2020/02/19
            return self.stream_function(5, 0)()

        del handler  # unused parameters

        message = self.secs_decode(packet)

        # 0  = Accepted
        # 1  = Error
        result = ACKC5.ACCEPTED 

        alids = message.ALID.get()
        if not isinstance(alids, list):
            alids = [alids]

        if len(alids) == 0:
            alids = list(self.alarms.keys())
        
        for alid in alids:
            if alid not in self._alarms:
                result = ACKC5.ERROR
                return self.stream_function(5, 4)(result)
        
        for alid in alids:
            self.alarms[alid].enabled = (message.ALED.get() == ALED.ENABLE)

        return self.stream_function(5, 4)(result)

    def _on_s05f05(self, handler, packet): # Mike 2019/09/06
        """Callback handler for Stream 5, Function 5, Alarm list

        :param handler: handler the message was received on
        :type handler: :class:`secsgem.hsms.handler.HsmsHandler`
        :param packet: complete message received
        :type packet: :class:`secsgem.hsms.packets.HsmsPacket`
        """
        if self.controlState.current not in ["ONLINE", "ONLINE_LOCAL", "ONLINE_REMOTE"]: # Mike 2020/02/19
            return self.stream_function(5, 0)()

        del handler  # unused parameters

        message = self.secs_decode(packet)

        result = []

        alids = message.get()
        if not isinstance(alids, list):
            alids = [alids]

        if len(alids) == 0:
            alids = list(self.alarms.keys())

        for alid in alids:
            if alid not in self._alarms:
                result.append({"ALCD": None, "ALID": alid, "ALTX": ""})
            else:
                result.append({"ALCD": self.alarms[alid].code | (ALCD.ALARM_SET if self.alarms[alid].set else 0), "ALID": alid, "ALTX": self.alarms[alid].text})

        return self.stream_function(5, 6)(result)

    def _on_s05f07(self, handler, packet):
        """Callback handler for Stream 5, Function 7, Enabled alarm list

        :param handler: handler the message was received on
        :type handler: :class:`secsgem.hsms.handler.HsmsHandler`
        :param packet: complete message received
        :type packet: :class:`secsgem.hsms.packets.HsmsPacket`
        """
        if self.controlState.current not in ["ONLINE", "ONLINE_LOCAL", "ONLINE_REMOTE"]: # Mike 2020/02/19
            return self.stream_function(5, 0)()

        del handler, packet  # unused parameters

        result = []

        for alid in list(self.alarms.keys()):
            if self.alarms[alid].enabled:
                result.append({"ALCD": self.alarms[alid].code | (ALCD.ALARM_SET if self.alarms[alid].set else 0), \
                    "ALID": alid, "ALTX": self.alarms[alid].text})

        return self.stream_function(5, 8)(result)

    ##################################
    #   remote commands
    ##################################

    @property
    def remote_commands(self):
        """The list of the remote commands
        :returns: Remote command list
        :rtype: list of :class:`secsgem.gem.equipmenthandler.RemoteCommand`
        """
        return self._remote_commands

    def _on_s02f41(self, handler, packet): # Mike: 2020/03/16
        """Callback handler for Stream 2, Function 41, host command send
        The remote command handing differs from usual stream function handling, because we send the ack with later completion first.
        Then we run the actual remote command callback and signal success with the matching collection event.
        
        :param handler: handler the message was received on
        :type handler: :class:`secsgem.hsms.handler.HsmsHandler`
        :param packet: complete message received
        :type packet: :class:`secsgem.hsms.packets.HsmsPacket`
        """
        if self.controlState.current not in ["ONLINE", "ONLINE_LOCAL", "ONLINE_REMOTE"]: # Mike 2020/02/19
            return self.stream_function(2, 0)()
        del handler  # unused parameters
        err = False
        hcack = HCACK.ACK

        message = self.secs_decode(packet)

        rcmd_name = message.RCMD.get()
        rcmd_callback_name = "rcmd_" + rcmd_name
        
        ack_params = [] # Mike: 2020/03/09
        kwargs = {}
        for param in message.PARAMS.get():
            kwargs[param['CPNAME']]=param['CPVAL']

        if rcmd_name not in self._remote_commands:
            self.logger.info("remote command %s not registered", rcmd_name)
            hcack = HCACK.INVALID_COMMAND
            err = True
            #return self.stream_function(2, 42)([HCACK.INVALID_COMMAND, ack_params])

        if rcmd_callback_name not in self._callback_handler: # Mike: 2020/03/25
            self.logger.warning("callback for remote command %s not available", rcmd_name)
            hcack = HCACK.INVALID_COMMAND
            err = True
            #return self.stream_function(2, 42)([HCACK.INVALID_COMMAND, ack_params])
        else:
            cpname_list = []
            for param in message.PARAMS: # Mike: 2020/03/09
                cpname = param.CPNAME.get()
                cpname_list.append(param.CPNAME.get())
                if cpname not in self._remote_commands[rcmd_name].params: 
                    self.logger.warning("parameter %s for remote command %s not available", cpname, rcmd_name)
                    ack_params.append([cpname, CPACK.PARAMETER_UNKNOWN])
                    hcack = HCACK.PARAMETER_INVALID
                    err = True
                    #ack_params[param.CPNAME.get()] = CPACK.PARAMETER_UNKNOWN
                else:
                    ack_params.append([cpname, CPACK.ACK])
            for cpname in self._remote_commands[rcmd_name].params:
                if cpname not in cpname_list:
                    self.logger.warning("quantity of parameters for enhance remote command %s mismatch", rcmd_name)
                    hcack = HCACK.PARAMETER_INVALID
                    err = True
                    break

        if simple_cmd_reply:
            if err:
                hcack = HCACK.INVALID_COMMAND
                return self.stream_function(2, 42)([hcack])
            self.send_response(self.stream_function(2, 42)([hcack]), packet.header.system)
        else:
            if err:
                return self.stream_function(2, 42)([hcack, ack_params])
            self.send_response(self.stream_function(2, 42)([hcack, ack_params]), packet.header.system)

        callback = getattr(self._callback_handler, rcmd_callback_name)

        callback(**kwargs)

        self.trigger_collection_events(self._remote_commands[rcmd_name].ce_finished)

    @property
    def enhance_remote_commands(self):
        """The list of the remote commands
        :returns: Remote command list
        :rtype: list of :class:`secsgem.gem.equipmenthandler.RemoteCommand`
        """
        return self._enhance_remote_commands

    def _on_s02f49(self, handler, packet): # Mike: 2020/03/09
        """Callback handler for Stream 2, Function 41, host command send
        The remote command handing differs from usual stream function handling, because we send the ack with later completion first.
        Then we run the actual remote command callback and signal success with the matching collection event.
        
        :param handler: handler the message was received on
        :type handler: :class:`secsgem.hsms.handler.HsmsHandler`
        :param packet: complete message received
        :type packet: :class:`secsgem.hsms.packets.HsmsPacket`
        """
        if self.controlState.current not in ["ONLINE", "ONLINE_LOCAL", "ONLINE_REMOTE"]: # Mike 2020/02/19
            return self.stream_function(2, 0)()
        del handler  # unused parameters
        err = False
        hcack = HCACK.ACK

        message = self.secs_decode(packet)

        ercmd_name = message.RCMD.get()
        ercmd_callback_name = "ercmd_" + ercmd_name
        
        ack_params = [] # Mike: 2020/03/09
        kwargs = {}
        for param in message.PARAMS.get():
            if param['CPNAME'] not in kwargs:
                kwargs[param['CPNAME']] = []
            kwargs[param['CPNAME']].append(param['CEPVALS'])

        if ercmd_name not in self._enhance_remote_commands:
            self.logger.info("remote command %s not registered", ercmd_name)
            hcack = HCACK.INVALID_COMMAND
            err = True
            #return self.stream_function(2, 42)([HCACK.INVALID_COMMAND, ack_params])

        if ercmd_callback_name not in self._callback_handler: # Mike: 2020/03/25
            self.logger.warning("callback for remote command %s not available", ercmd_name)
            hcack = HCACK.INVALID_COMMAND
            err = True
            #return self.stream_function(2, 42)([HCACK.INVALID_COMMAND, ack_params])
        else:
            cpname_list = []
            for param in message.PARAMS: # Mike: 2020/03/09
                cpname = param.CPNAME.get()
                cpname_list.append(cpname)
                if cpname not in self._enhance_remote_commands[ercmd_name].params:  
                    self.logger.warning("parameter %s for enhance remote command %s not available", cpname, ercmd_name)
                    ack_params.append([cpname, CEPACK.CEPVAL_ILLEGAL_FORMAT])
                    hcack = HCACK.PARAMETER_INVALID
                    err = True
                    #ack_params[param.CPNAME.get()] = CPACK.PARAMETER_UNKNOWN
                else:
                    err0 = False
                    cepname_list = []
                    for cep in param.CEPVALS:
                        cepname = cep.CPNAME.get()
                        cepname_list.append(cepname)
                        if cepname not in self._enhance_remote_commands[ercmd_name].params[cpname]:
                            self.logger.warning("parameter %s in %s for remote command %s not available", cepname, cpname, ercmd_name)
                            hcack = HCACK.PARAMETER_INVALID
                            err = True
                            err0 = True
                    if err0:
                        ack_params.append([cpname, CEPACK.PARAMETER_UNKNOWN])
                    else:
                        err1 = False
                        for cepname in self._enhance_remote_commands[ercmd_name].params[cpname]:
                            if cepname not in cepname_list:
                                self.logger.warning("quantity of parameters in %s for enhance remote command %s mismatch", cpname, ercmd_name)
                                ack_params.append([cpname, CEPACK.CEPVAL_ILLEGAL_FORMAT])
                                hcack = HCACK.PARAMETER_INVALID
                                err = True
                                err1 = True
                                break
                        if not err1:
                            ack_params.append([cpname, CPACK.ACK])
            for cpname in self._enhance_remote_commands[ercmd_name].params:
                if cpname not in cpname_list:
                    self.logger.warning("quantity of parameters for enhance remote command %s mismatch", ercmd_name)
                    hcack = HCACK.PARAMETER_INVALID
                    err = True
                    break

        if simple_cmd_reply:
            if err:
                hcack = HCACK.INVALID_COMMAND
                return self.stream_function(2, 50)([hcack])
            self.send_response(self.stream_function(2, 50)([hcack]), packet.header.system)
        else:
            if err:
                return self.stream_function(2, 50)([hcack, ack_params])
            self.send_response(self.stream_function(2, 50)([hcack, ack_params]), packet.header.system)

        callback = getattr(self._callback_handler, ercmd_callback_name)

        callback(**kwargs)

        self.trigger_collection_events(self._remote_commands[ercmd_name].ce_finished)


    def _on_rcmd_START(self):
        print("start")
        pass

    def _on_rcmd_STOP(self):
        print("stop")
        pass

    ##################################
    #   helpers
    ##################################

    def _get_clock(self):
        """Returns the clock depending on configured time format

        :returns: time code
        :rtype: string
        """
        now = datetime.now(tzlocal())
        if self._time_format == 0:
            self.status_variables[GEM_CLOCK].value = now.strftime("%y%m%d%H%M%S")
            return now.strftime("%y%m%d%H%M%S")
        elif self._time_format == 2:
            self.status_variables[GEM_CLOCK].value = now.isoformat()
            return now.isoformat()
        else:
            self.status_variables[GEM_CLOCK].value = now.strftime("%Y%m%d%H%M%S") + now.strftime("%f")[0:2]
            return now.strftime("%Y%m%d%H%M%S") + now.strftime("%f")[0:2]

    def _on_s02f17(self, handler, packet): # Mike 2019/09/05
        """Callback handler for Stream 2, Function 17, Request online

        :param handler: handler the message was received on
        :type handler: :class:`secsgem.hsms.handler.HsmsHandler`
        :param packet: complete message received
        :type packet: :class:`secsgem.hsms.packets.HsmsPacket`
        """
        if self.controlState.current not in ["ONLINE", "ONLINE_LOCAL", "ONLINE_REMOTE"]: # Mike 2020/02/19
            return self.stream_function(2, 0)()

        del handler, packet  # unused parameters
        
        TIME = self._get_clock()
        
        return self.stream_function(2, 18)(TIME)

    def _on_s02f31(self, handler, packet): # Mike 2019/09/05
        """Callback handler for Stream 2, Function 31, Request online

        :param handler: handler the message was received on
        :type handler: :class:`secsgem.hsms.handler.HsmsHandler`
        :param packet: complete message received
        :type packet: :class:`secsgem.hsms.packets.HsmsPacket`
        """
        if self.controlState.current not in ["ONLINE", "ONLINE_LOCAL", "ONLINE_REMOTE"]: # Mike 2020/02/19
            return self.stream_function(2, 0)()

        del handler  # unused parameters

        message = self.secs_decode(packet)
        
        TIACK = 0
        
        return self.stream_function(2, 32)(TIACK)

    def _get_control_state_id(self):
        """The id of the control state for the current control state

        :returns: control state
        :rtype: integer
        """
        if self.controlState.isstate("EQUIPMENT_OFFLINE"):
            return 1
        if self.controlState.isstate("ATTEMPT_ONLINE"):
            return 2
        if self.controlState.isstate("HOST_OFFLINE"):
            return 3
        if self.controlState.isstate("ONLINE_LOCAL"):
            return 4
        if self.controlState.isstate("ONLINE_REMOTE"):
            return 5

    def _get_events_enabled(self):
        """List of the enabled collection events

        :returns: collection event
        :rtype: list of various
        """
        enabled_ceid = []

        for ceid in self._registered_collection_events:
            if self._registered_collection_events[ceid].enabled:
                enabled_ceid.append(ceid)

        return enabled_ceid

    def _get_alarms_enabled(self):
        """List of the enabled alarms

        :returns: alarms
        :rtype: list of various
        """
        enabled_alarms = []

        for alid in self._alarms:
            if self._alarms[alid].enabled:
                enabled_alarms.append(alid)

        return enabled_alarms

    def _get_alarms_set(self):
        """List of the set alarms

        :returns: alarms
        :rtype: list of various
        """
        set_alarms = []

        for alid in self._alarms:
            if self._alarms[alid].set:
                set_alarms.append(alid)

        return set_alarms

    def on_connection_closed(self, connection):
        """Connection was closed"""
        # call parent handlers
        GemHandler.on_connection_closed(self, connection)
        if self._get_ec_value(self._equipment_constants[GEM_CONFIG_SPOOL]):
            pass
            #self.spoolState.activate()

        # update control state
        if self.controlState.current in ["ONLINE", "ONLINE_LOCAL", "ONLINE_REMOTE"]:
            self.controlState.remote_offline()

        if self.controlState.current in ["EQUIPMENT_OFFLINE"]:
            self.controlState.switch_online()
