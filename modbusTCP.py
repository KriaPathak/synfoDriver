import struct
from threading import Thread
from datetime import datetime
import time

from customsMethod import structpack, structunpack
from logger import get_logger
from pyModbusTCP.client import ModbusClient
# from NoSqlDB import RethinkDatabase
from model import TagMasterModel, TagModel, DeviceConnectionLog
from servercilentConnection import ApiServer

logger = get_logger()


class ModbusTCP(Thread):

    def __init__(self, DriverDetailID, slav_id, client, FrequncyOfGetData, NetworkAddress, Port, DriverName, datetime):
        super(ModbusTCP, self).__init__()
        self.DriverDetailID = DriverDetailID,
        self.slavid = slav_id,
        self.client = client
        self.FrequncyOfGetData = FrequncyOfGetData
        self.NetworkAddress = NetworkAddress
        self.Port = Port
        self.SlavID = slav_id
        self.DriverName = DriverName
        self.datetime = datetime

    def kelvinToCelsius(self, kelvin):
        return kelvin - 273.15

    def getDataFromRTU(self):

        Isconnect = 0
        count = 0

        client = ModbusClient(host=self.NetworkAddress, port=int(self.Port), unit_id=int(self.SlavID))

        if client.open() and Isconnect == 0:
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
            DeviceConnectionLog().insert(self.DriverDetailID[0], client.open(), 'connect device',
                                         dt_string)
            Isconnect = 1
        else:
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
            DeviceConnectionLog().insert(self.DriverDetailID[0], client.open(), 'Device is not connected',
                                         dt_string)
            Isconnect = 0

        while True:

            tag_DBvalue_list = []
            tag_APIvalue_list = []
            taglist = TagMasterModel().find_by_DriverDetailID(self.DriverDetailID[0])
            random_string = ""

            try:

                if client.open():
                    print(taglist)
                    for tag_data in taglist:

                        count = count + 1
                        data = ""
                        packed_string = ""

                        if tag_data[5] == 'INPUT REGISTER':
                            data = client.read_input_registers(int(tag_data[3]), int(tag_data[4]))


                        elif tag_data[5] == 'HOLDING REGISTER':
                            data = client.read_holding_registers(int(tag_data[3]), int(tag_data[4]))

                        if tag_data[7] == 'NO' and data != "":
                            packed_string = structpack(data[0], data[1])

                        elif tag_data[7] == 'YES' and data != "":
                            packed_string = structpack(data[1], data[0])

                        if len(packed_string) != 0:
                            tagvalue = structunpack(packed_string)

                            if tag_data[9] == 'YES':
                                tag_value_ = (tag_data[0], tagvalue, self.datetime)
                                tag_DBvalue_list.append(tag_value_)

                                # else:
                                #     Isconnect = 2
                                #     if (self.client.connected==False and Isconnect == 2):
                                #         now = datetime.now()
                                #         dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
                                #         DeviceConnectionLog().insert(self.DriverDetailID[0], self.client.connected,
                                #                                      'disconnect device', dt_string)
                                #         Isconnect = 3
                                #     print(res)
                                #     print("3")

                            elif (tag_data[9] == 'NO'):
                                tagName = TagMasterModel().find_by_TagID(tag_data[0])
                                tag_apivalue_ = (tag_data[0], tagvalue, self.datetime)
                                tag_APIvalue_list.append(tag_apivalue_)
                                data = "tagindex" + ' ' + str(tag_data[0]) + ' ' + "tagvalue" + str(tagvalue)
                                random_string = random_string + ' '.join(data)
                                # RethinkDatabase().InsertData(self.DriverName, now, tagName[2], tagvalue, count)

                if len(tag_DBvalue_list) != 0:
                    print("network address", self.NetworkAddress)
                    print("tag_DBvalue_list",tag_DBvalue_list)
                    TagModel().insert_multiple(tag_DBvalue_list)
                if len(tag_APIvalue_list) != 0:
                    print("network address", self.NetworkAddress)
                    print("random_string", random_string)
                    # ApiServer().serverconnection(random_string)
                    # ApiServer().serverconnection(tag_APIvalue_list)



            except Exception as ex:
                print("nooooo")
                logger.exception(ex)
                Isconnect = 3
                if (self.client.open() == False and Isconnect != 3):
                    now = datetime.now()
                    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
                    DeviceConnectionLog().insert(self.DriverDetailID[0], self.client.open(),
                                                 'disconnect device', dt_string)
                    Isconnect = 5
                self.getDataFromRTU()
            client.close()
            time.sleep(self.FrequncyOfGetData)

    def run(self) -> None:
        try:
            self.getDataFromRTU()
        except Exception as ex:
            logger.exception(ex)
