from modbus import ModbusRTU
from modbusTCP import ModbusTCP
from modbuswithoutloop import ModbusMultiReg
from model import DriverDetail
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
                tcp = ModbusMultiReg(driverDetail[0], SlavID, client, FrequncyOfGetData, NetworkAddress, Port,
                                driverDetail[1], dt_string)
                tcp.start()


if __name__ == '__main__':
    try:
        modbusConnector()
    except Exception as ex:
        print(ex)

