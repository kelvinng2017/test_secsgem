#####################################################################
# packets.py
#
# (c) Copyright 2015, Benjamin Parzella. All rights reserved.
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
"""Contains objects that encapsulate secs I messages"""

import struct


class SecsIHeader:
    """Generic SECS-I header

    Base for different specific headers

    :param system: message ID
    :type system: integer
    :param device_id: device / device ID
    :type device_id: integer

    **Example**::

        >>> import secsgem
        >>>
        >>> secsgem.secsi.packets.SecsIHeader(3, 100)
        SecsIHeader({deviceID:0x0064, stream:00, function:00, block_num:0x0001, system:0x00000003, requireResponse:False, })

    """

    def __init__(self, system, device_id, to_host, block_num):
        self.deviceID = device_id
        self.toHost = to_host
        self.endBlock = True
        self.requireResponse = False
        self.stream = 0x00
        self.function = 0x00
        self.endBlock = False
        self.blockNum = block_num
        self.system = system

    def __str__(self):
        """Generate string representation for an object of this class"""
        return '{deviceID:0x%04x, stream:%02d, function:%02d, blockNum:0x%04x, system:0x%08x, toHost:%r, requireResponse:%r, endBlock:%r}' % \
            (self.deviceID, self.stream, self.function, self.blockNum, self.system, self.toHost, self.requireResponse, self.endBlock)

    def __repr__(self):
        """Generate textual representation for an object of this class"""
        return "%s(%s)" % (self.__class__.__name__, self.__str__())

    def encode(self):
        """Encode header to secs_i packet

        :returns: encoded header
        :rtype: string

        **Example**::

            >>> import secsgem
            >>>
            >>> header = secsgem.secs_i.packets.SecsILinktestReqHeader(2)
            >>> secsgem.common.format_hex(header.encode())
            'ff:ff:00:00:00:05:00:00:00:02'

        """
        header_deviceID = self.deviceID
        if self.toHost:
            header_deviceID |= 0b10000000
        header_stream = self.stream
        if self.requireResponse:
            header_stream |= 0b10000000
        header_block_num = self.block_num
        if self.endBlock:
            header_block_num |= 0b10000000

        return struct.pack(">HBBHL", header_deviceID, header_stream, self.function, header_block_num, self.system)


'''class SecsISelectReqHeader(SecsIHeader):
    """Header for Select Request

    Header for message with SType 1.

    :param system: message ID
    :type system: integer

    **Example**::

        >>> import secsgem
        >>>
        >>> secsgem.secs_i.packets.SecsISelectReqHeader(14)
        SecsISelectReqHeader({deviceID:0xffff, stream:00, function:00, pType:0x00, sType:0x01, system:0x0000000e, requireResponse:False})

    """

    def __init__(self, system, toHost, device_id):
        SecsIHeader.__init__(self, system, device_id, 0x0001)
        self.toHost = toHost
        self.requireResponse = False
        self.endBlock = True
        self.stream = 0x00
        self.function = 0x00
        self.pType = 0x00
        self.sType = 0x01'''


'''class SecsISelectRspHeader(SecsIHeader):
    """Header for Select Response

    Header for message with SType 2.

    :param system: message ID
    :type system: integer

    **Example**::

        >>> import secsgem
        >>>
        >>> secsgem.secs_i.packets.SecsISelectRspHeader(24)
        SecsISelectRspHeader({deviceID:0xffff, stream:00, function:00, pType:0x00, sType:0x02, system:0x00000018, requireResponse:False})

    """

    def __init__(self, system, toHost):
        SecsIHeader.__init__(self, system, 0xFFFF)
        self.toHost = toHost
        self.requireResponse = False
        self.stream = 0x00
        self.function = 0x00
        self.pType = 0x00
        self.sType = 0x02'''


'''class SecsIDeselectReqHeader(SecsIHeader):
    """Header for Deselect Request

    Header for message with SType 3.

    :param system: message ID
    :type system: integer

    **Example**::

        >>> import secsgem
        >>>
        >>> secsgem.secs_i.packets.SecsIDeselectReqHeader(1)
        SecsIDeselectReqHeader({deviceID:0xffff, stream:00, function:00, pType:0x00, sType:0x03, system:0x00000001, requireResponse:False})

    """

    def __init__(self, system, toHost):
        SecsIHeader.__init__(self, system, 0xFFFF)
        self.toHost = toHost
        self.requireResponse = False
        self.stream = 0x00
        self.function = 0x00
        self.pType = 0x00
        self.sType = 0x03'''


'''class SecsIDeselectRspHeader(SecsIHeader):
    """Header for Deselect Response

    Header for message with SType 4.

    :param system: message ID
    :type system: integer

    **Example**::

        >>> import secsgem
        >>>
        >>> secsgem.secs_i.packets.SecsIDeselectRspHeader(1)
        SecsIDeselectRspHeader({deviceID:0xffff, stream:00, function:00, pType:0x00, sType:0x04, system:0x00000001, requireResponse:False})

    """

    def __init__(self, system, toHost):
        SecsIHeader.__init__(self, system, 0xFFFF)
        self.toHost = toHost
        self.requireResponse = False
        self.stream = 0x00
        self.function = 0x00
        self.pType = 0x00
        self.sType = 0x04'''


'''class SecsILinktestReqHeader(SecsIHeader):
    """Header for Linktest Request

    Header for message with SType 5.

    :param system: message ID
    :type system: integer

    **Example**::

        >>> import secsgem
        >>>
        >>> secsgem.secs_i.packets.SecsILinktestReqHeader(2)
        SecsILinktestReqHeader({deviceID:0xffff, stream:00, function:00, pType:0x00, sType:0x05, system:0x00000002, requireResponse:False})

    """

    def __init__(self, system, toHost):
        SecsIHeader.__init__(self, system, 0xFFFF)
        self.toHost = toHost
        self.requireResponse = False
        self.stream = 0x00
        self.function = 0x00
        self.pType = 0x00
        self.sType = 0x05'''


'''class SecsILinktestRspHeader(SecsIHeader):
    """Header for Linktest Response

    Header for message with SType 6.

    :param system: message ID
    :type system: integer

    **Example**::

        >>> import secsgem
        >>>
        >>> secsgem.secs_i.packets.SecsILinktestRspHeader(10)
        SecsILinktestRspHeader({deviceID:0xffff, stream:00, function:00, pType:0x00, sType:0x06, system:0x0000000a, requireResponse:False})

    """

    def __init__(self, system, toHost):
        SecsIHeader.__init__(self, system, 0xFFFF)
        self.toHost = toHost
        self.requireResponse = False
        self.stream = 0x00
        self.function = 0x00
        self.pType = 0x00
        self.sType = 0x06'''


'''class SecsIRejectReqHeader(SecsIHeader):
    """Header for Reject Request

    Header for message with SType 7.

    :param system: message ID
    :type system: integer
    :param s_type: sType of rejected message
    :type s_type: integer
    :param reason: reason for rejection
    :type reason: integer

    **Example**::

        >>> import secsgem
        >>>
        >>> secsgem.secs_i.packets.SecsIRejectReqHeader(17, 3, 4)
        SecsIRejectReqHeader({deviceID:0xffff, stream:03, function:04, pType:0x00, sType:0x07, system:0x00000011, requireResponse:False})

    """

    def __init__(self, system, s_type, reason, toHost):
        SecsIHeader.__init__(self, system, 0xFFFF)
        self.toHost = toHost
        self.requireResponse = False
        self.stream = s_type
        self.function = reason
        self.pType = 0x00
        self.sType = 0x07'''


'''class SecsISeparateReqHeader(SecsIHeader):
    """Header for Separate Request

    Header for message with SType 9.

    :param system: message ID
    :type system: integer

    **Example**::

        >>> import secsgem
        >>>
        >>> secsgem.secs_i.packets.SecsISeparateReqHeader(17)
        SecsISeparateReqHeader({deviceID:0xffff, stream:00, function:00, pType:0x00, sType:0x09, system:0x00000011, requireResponse:False})

    """

    def __init__(self, system, toHost):
        SecsIHeader.__init__(self, system, 0xFFFF)
        self.toHost = toHost
        self.requireResponse = False
        self.stream = 0x00
        self.function = 0x00
        self.pType = 0x00
        self.sType = 0x09'''


class SecsIStreamFunctionHeader(SecsIHeader):
    """Header for SECS message

    Header for message with SType 0.

    :param system: message ID
    :type system: integer
    :param stream: messages stream
    :type stream: integer
    :param function: messages function
    :type function: integer
    :param require_response: is response expected from remote
    :type require_response: boolean
    :param device_id: device / device ID
    :type device_id: integer

    **Example**::

        >>> import secsgem
        >>>
        >>> secsgem.secs_i.packets.SecsIStreamFunctionHeader(22, 1, 1, True, 100, True, True, 100)
        SecsIStreamFunctionHeader({deviceID:0x0064, stream:01, function:01, blockNum:0x0001, system:0x00000016, requireResponse:True, toHost:True, endBlock:True})

    """

    def __init__(self, system, stream, function, require_response, device_id, to_host, block_num):
        SecsIHeader.__init__(self, system, device_id, to_Host, block_num)
        self.requireResponse = require_response
        self.stream = stream
        self.function = function


class SecsIPacket:
    """Class for secs_i packet.

    Contains all required data and functions.

    :param header: header used for this packet
    :type header: :class:`secsgem.secs_i.packets.SecsIHeader` and derived
    :param data: data part used for streams and functions (SType 0)
    :type data: string

    **Example**::

        >>> import secsgem
        >>>
        >>> secsgem.secs_i.packets.SecsIPacket(secsgem.secs_i.packets.SecsILinktestReqHeader(2))
        SecsIPacket({'header': SecsILinktestReqHeader({deviceID:0xffff, stream:00, function:00, pType:0x00, sType:0x05, system:0x00000002, requireResponse:False, toHost:Fasle}), 'data': ''})

    """

    def __init__(self, header=None, data=b""):
        if header is None:
            self.header = SecsIHeader(0, 0, 0, 1)
        else:
            self.header = header

        self.data = data

    def __str__(self):
        """Generate string representation for an object of this class"""
        data = "'header': " + self.header.__str__()
        return data

    def __repr__(self):
        """Generate textual representation for an object of this class"""
        return "%s({'header': %s, 'data': '%s'})" % (self.__class__.__name__, self.header.__repr__(), self.data.decode("utf-8"))

    def encode(self):
        """Encode packet data to secs_i packet

        :returns: encoded packet
        :rtype: string

        **Example**::

            >>> import secsgem
            >>>
            >>> packet = secsgem.secs_i.packets.SecsIPacket(secsgem.secs_i.packets.SecsILinktestReqHeader(2))
            >>> secsgem.common.format_hex(packet.encode())
            '00:00:00:0a:ff:ff:00:00:00:05:00:00:00:02'

        """
        headerdata = self.header.encode()

        length = len(headerdata) + len(self.data)

        checksum = 0

        msg = headerdata + self.data
        for i in range(length):
            checksum += msg[i]

        return struct.pack(">B", length) + headerdata + self.data + struct.pack(">H", checksum)

    @staticmethod
    def decode(text):
        """Decode byte array secs_i packet to SecsIPacket object

        :returns: received packet object
        :rtype: :class:`secsgem.secs_i.packets.SecsIPacket`

        **Example**::

            >>> import secsgem
            >>>
            >>> packetData = b"\\x00\\x00\\x00\\x0b\\xff\\xff\\x00\\x00\\x00\\x05\\x00\\x00\\x00\\x02"
            >>>
            >>> secsgem.format_hex(packetData)
            '0c:00:01:01:01:80:05:00:00:00:02'
            >>>
            >>> secsgem.secs_i.packets.SecsIPacket.decode(packetData)
            SecsIPacket({'header': SecsIHeader({deviceID:0x0001, stream:00, function:00, block_num:0x0001, system:0x00000002, requireResponse:False, toHost:False, endBlock:True}), 'data': ''})


        """
        data_length = len(text) - 10 - 2
        data_length_text = str(data_length) + "s"

        res = struct.unpack(">BHBBHL" + data_length_text, text)

        toHost = (((res[1] & 0b10000000) >> 7) == 1)
        deviceID = res[1] & 0b01111111
        blockNum = res[4] & 0b01111111
        result = SecsIPacket(SecsIHeader(res[5], deviceID, toHost, blockNum))
        result.header.requireResponse = (((res[2] & 0b10000000) >> 7) == 1)
        result.header.stream = res[2] & 0b01111111
        result.header.function = res[3]
        result.header.endBlock = (((res[4] & 0b10000000) >> 7) == 1)
        result.header.system = res[5]
        result.data = res[6][:-2]

        return result
