from threading import Thread
from datetime import datetime
import time
from customsMethod import structpack, structunpack, currentDateTime
from logger import get_logger
from pyModbusTCP.client import ModbusClient
from model import TagMasterModel, TagModel, DeviceConnectionLog, DeviceException

logger = get_logger()


class modbuswitoutloop(Thread):

    def __init__(self, DriverDetailID, slav_id, clientl, FrequncyOfGetData, NetworkAddress, Port, DriverName, datetime):
        super(modbuswitoutloop, self).__init__()
        self.DriverDetailID = DriverDetailID,
        self.slavid = slav_id,

        self.FrequncyOfGetData = FrequncyOfGetData
        self.NetworkAddress = NetworkAddress
        self.Port = Port
        self.SlavID = slav_id
        self.DriverName = DriverName
        # self.datetime = datetime

    def getDataFromRTU(self):

        connectionTag = 0

        client = ModbusClient(host=self.NetworkAddress, port=int(self.Port), unit_id=int(self.SlavID))

        if client.open() and connectionTag == 0:
            DeviceConnectionLog().insert(self.DriverDetailID[0], client.open(),
                                         'Device client open', currentDateTime())
            connectionTag = 1

        tag_list = TagMasterModel().find_by_DriverDetailID(self.DriverDetailID[0])

        while True:
            datetime = currentDateTime()
            tag_db_value_list = []
            tag_api_value_list = []
            random_string = ""

            try:
                if client.open():
                    print("net", self.NetworkAddress)

                    if client.open() and connectionTag == 2:
                        DeviceConnectionLog().insert(self.DriverDetailID[0], client.open(),
                                                     'Device client open', currentDateTime())
                        connectionTag = 1

                    data = ""
                    packed_string = ""


                    data = client.read_input_registers(int(tag_list[0][3]), 2*len(tag_list))
                    print("test",data)

                    for j in range(0, 16, 2):
                        packed_string = structpack(data[j], data[j + 1])
                        tagvalue = structunpack(packed_string)
                        tagvalue_list.append(tagvalue)

                    for tag_data in tag_list:


                        if len(packed_string) != 0:
                            tag_value = structunpack(packed_string)

                            if tag_data[9] == 'YES':
                                tag_value_ = (tag_data[0], tag_value, datetime)
                                tag_db_value_list.append(tag_value_)

                            elif tag_data[9] == 'NO':
                                tagName = TagMasterModel().find_by_TagID(tag_data[0])
                                tag_api_value_ = (tag_data[0], tag_value, datetime)
                                tag_api_value_list.append(tag_api_value_)
                                data = "tagindex" + ' ' + str(tag_data[0]) + ' ' + "tagvalue" + str(tag_value)
                                random_string = random_string + ' '.join(data)

                    if len(tag_db_value_list) != 0:
                        TagModel().insert_multiple(tag_db_value_list)

                    if len(tag_api_value_list) != 0:
                        len(tag_api_value_list)

                        # ApiServer().serverconnection(random_string)
                        # ApiServer().serverconnection(tag_api_value_list)

                else:
                    if client.is_open == False and connectionTag != 2:
                        DeviceConnectionLog().insert(self.DriverDetailID[0], client.open(),
                                                     'Device client close', currentDateTime())
                        connectionTag = 2
                client.close()

            except Exception as ex:
                print(ex)
                print("exception", type(ex))
                if client.is_open == False and connectionTag != 3:
                    DeviceConnectionLog().insert(self.DriverDetailID[0], client.open(),
                                                 'Device client close', currentDateTime())
                    connectionTag = 3

                driverID = DeviceConnectionLog().find_driver_detail_id(self.DriverDetailID[0])
                print(driverID)
                if driverID[0] != 0:
                    DeviceException().insert(str(ex), currentDateTime(), driverID[0])
            time.sleep(self.FrequncyOfGetData)

    def run(self) -> None:
        try:
            self.getDataFromRTU()
        except Exception as ex:
            print(ex)
            print("exception", type(ex))

            driverID = DeviceConnectionLog().find_driver_detail_id(self.DriverDetailID[0])
            if driverID[0] != 0:
                DeviceException().insert(str(ex), currentDateTime(), driverID[0])
