from threading import Thread
import time
from customsMethod import structpack, structunpack, currentDateTime
from pyModbusTCP.client import ModbusClient
from model import TagMasterModel, TagModel, DeviceConnectionLog, DeviceException
# import logging
# logger = logging.getLogger('app_logger')
from logger import get_logger

logger = get_logger()
class ModbusTCP(Thread):
    retryAttemptsLeft = 3

    def __init__(self, DriverDetailID, slav_id, clientl, FrequncyOfGetData, NetworkAddress, Port, DriverName, datetime):
        super(ModbusTCP, self).__init__()
        self.DriverDetailID = DriverDetailID,
        self.slavid = slav_id,
        self.FrequncyOfGetData = FrequncyOfGetData
        self.NetworkAddress = NetworkAddress
        self.Port = Port
        self.SlavID = slav_id
        self.DriverName = DriverName
        self.auto_open = False
        self.auto_close = False
        self.modbus_client = None
        self.response = None

        # self.datetime = datetime

    def getDataFromTCP(self):

        if self.retryAttemptsLeft > 0:

            self.modbus_connection()
            DeviceConnectionLog().insert(self.DriverDetailID[0], True, "Driver connection open"+str(self.retryAttemptsLeft)+ "Network" + self.NetworkAddress + "slavId" + str(
                                             self.SlavID), currentDateTime())

        tag_list = TagMasterModel().find_by_DriverDetailID(self.DriverDetailID[0])

        while self.modbus_client:
            datetime = currentDateTime()
            tag_db_value_list = []
            tag_api_value_list = []
            random_string = ""

            try:
                for tag_data in tag_list:

                    data = ""
                    packed_string = ""

                    if tag_data[5] == 'INPUT REGISTER':
                        data = self.modbus_client.read_input_registers(int(tag_data[3]), int(tag_data[4]))

                    elif tag_data[5] == 'HOLDING REGISTER':
                        data = self.modbus_client.read_holding_registers(int(tag_data[3]), int(tag_data[4]))

                    if tag_data[7] == 'NO' and data != "" and data != 'None':
                        packed_string = structpack(data[0], data[1])

                    elif tag_data[7] == 'YES' and data != "" and data != 'None':
                        packed_string = structpack(data[1], data[0])

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
                    print("tag_db_value_list", str(tag_db_value_list) + self.NetworkAddress + str(self.SlavID))
                    TagModel().insert_multiple(tag_db_value_list)
                    logger.info(f'tag_db_value_list {str(tag_db_value_list)} Server at: {self.NetworkAddress}slavId {self.SlavID}')

                if len(tag_api_value_list) != 0:
                    len(tag_api_value_list)

                    # ApiServer().serverconnection(random_string)
                    # ApiServer().serverconnection(tag_api_value_list)

            except Exception as ex:
                print("exception", ex)

                self.modbus_client = None

                DeviceConnectionLog().insert(self.DriverDetailID[0], False,
                                             'Client Closed with Exception : Attempts Left' + str(
                                                 self.retryAttemptsLeft)+"Network"+self.NetworkAddress+"slavId"+str(self.SlavID),
                                             currentDateTime())

                self.retryAttemptsLeft = self.retryAttemptsLeft - 1

            self.modbus_client.close()

            time.sleep(1)

    def modbus_connection(self):
        if not self.modbus_client:

            self.modbus_client = ModbusClient(host=self.NetworkAddress, port=int(self.Port), unit_id=int(self.SlavID),
                                              auto_open=self.auto_open, auto_close=self.auto_close)
            if self.modbus_client.open():
                print("Connection modbus Server at:", self.NetworkAddress)
                logger.info(f'Connection modbus Server at:{self.NetworkAddress} slavId {self.SlavID}')
            else:
                logger.info(f'Connection fail modbus Server at:{self.NetworkAddress} slavId {self.SlavID}')
                print("fail to connect", self.NetworkAddress)
                self.modbus_client = None

    def run(self) -> None:
        try:
            self.getDataFromTCP()
        except Exception as ex:
            logger.error(f'An error modbus Server at {self.NetworkAddress}, restarting process.')
            logger.exception(ex)
            print("exception", ex)
            DeviceConnectionLog().insert(self.DriverDetailID[0], False,
                                         'Client Closed with Exception : Attempts Left' + str(
                                             self.retryAttemptsLeft) + "Network" + self.NetworkAddress + "slavId" + str(
                                             self.SlavID),
                                         currentDateTime())

            # DeviceConnectionLogID = DeviceConnectionLog().find_driver_detail_id(self.DriverDetailID[0])
            # if DeviceConnectionLogID[0] != 0:
            #     DeviceException().insert(str(ex), currentDateTime(), DeviceConnectionLogID[0])
