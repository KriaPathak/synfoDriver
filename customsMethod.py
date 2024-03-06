import struct

from pyModbusTCP.client import ModbusClient


def modbus_connection(NetworkAddress, Port, SlavID):
    client = ModbusClient(host=NetworkAddress, port=Port, unit_id=SlavID)
    return client


def read_from_input_register(client, register_address, register_no):
    value = client.read_input_registers(register_address, register_no)
    return value


def read_from_holding_registers(client, register_address, register_no):
    value = client.read_holding_registers(register_address, register_no)
    return value


def structpack(d1, d2):
    return struct.pack("HH", d1, d2)


def structunpack(packed_string):
    return struct.unpack("f", packed_string)[0]
