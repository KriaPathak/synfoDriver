from customsMethod import currentDateTime
from modbus import ModbusRTU
from modbusTCP import ModbusTCP, logger
from modbuscoonection import ModbusConnection
from modbuswithoutloop import ModbusMultiReg
from model import DriverDetail, DeviceConnectionLog
from datetime import datetime
from pymodbus.client import ModbusSerialClient as ModbusClient


def modbusConnector():
    client = ""
    data = DriverDetail().find_all_driver_detail()
    BaurdRateI = 0
    DatabitsI = 0
    CommunicationPortI = ""
    ParityI = ""
    StopBitI = 0

    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
    for driverDetail in data:

        device_status = driverDetail[12]
        DevicedetailName = driverDetail[1]
        FrequncyOfGetData = driverDetail[2]
        Port = driverDetail[3]
        NetworkAddress = driverDetail[4]
        BaurdRate = driverDetail[5]
        Databits = driverDetail[6]
        CommunicationPort = driverDetail[7]
        Parity = driverDetail[8]
        StopBit = driverDetail[9]
        SlavID = driverDetail[10]
        DriverMasterID = driverDetail[11]
        Active = driverDetail[12]
        try:
            if DriverMasterID == 2:
                if Active:
                    if BaurdRateI != BaurdRate and DatabitsI != Databits and CommunicationPortI != CommunicationPort and ParityI != Parity and StopBitI != StopBit:
                        client = ModbusClient(
                            method='rtu',
                            port=CommunicationPort,
                            baudrate=BaurdRate,
                            timeout=StopBit,
                            parity=Parity[0:1],
                            stopbits=StopBit,
                            bytesize=Databits
                        )
                        BaurdRateI = BaurdRate
                        DatabitsI = Databits
                        CommunicationPortI = CommunicationPort
                        ParityI = Parity
                        StopBitI = StopBit

                        client.connect()

                        rtu = ModbusRTU(driverDetail[0], SlavID, client, FrequncyOfGetData, driverDetail[1], dt_string)
                        rtu.start()

            elif DriverMasterID == 1:
                if Active:
                    modbus_client = ModbusConnection(SlavID, NetworkAddress, Port).connection()
                    if modbus_client.open():
                        DeviceConnectionLog().insert(driverDetail[0], True, "Driver connection open", currentDateTime())
                        logger.info(
                                f'Port {str(Port)} Server at: {NetworkAddress}slavId {SlavID}')

                        tcp = ModbusTCP(driverDetail[0], SlavID, modbus_client, FrequncyOfGetData, NetworkAddress, Port,
                                        driverDetail[1], dt_string, "synfodriver" + str(driverDetail[0]))
                        tcp.start()

        except:
            DeviceConnectionLog().insert(driverDetail[0], False,
                                         'Client not connect', currentDateTime())


if __name__ == '__main__':
    try:
        modbusConnector()
    except Exception as ex:
        print(ex)
