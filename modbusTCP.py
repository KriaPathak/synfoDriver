from threading import Thread
import time
from customsMethod import structpack, structunpack, currentDateTime
from logging.handlers import RotatingFileHandler
from modbuscoonection import ModbusConnection
from model import TagMasterModel, TagModel, DeviceConnectionLog, DeviceException
import logging,os
from dotenv import load_dotenv


load_dotenv()




logLevel = os.getenv('LOG_LEVEL')
logLevel = 40 if logLevel is None else int(logLevel)

logger = logging.getLogger('app_logger')
handler = RotatingFileHandler(filename= 'logs/synfodriver_error_log.log',
                              maxBytes=1024 * 1024 * 20,
                              backupCount=10)
handler.setFormatter(logging.Formatter(
    fmt='%(asctime)s %(levelname)s %(threadName)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))

logger.addHandler(handler)
logger.setLevel(logLevel)


class ModbusTCP(Thread):
    retryAttemptsLeft = 3

    def __init__(self, DriverDetailID, slav_id, modbus_client, FrequncyOfGetData, NetworkAddress, Port, DriverName, datetime,
                 name):
        super().__init__(name=name)
        self.DriverDetailID = DriverDetailID,
        self.FrequncyOfGetData = FrequncyOfGetData
        self.NetworkAddress = NetworkAddress
        self.Port = Port
        self.SlavID = slav_id
        self.DriverName = DriverName
        self.modbus_client = modbus_client

    def getDataFromTCP(self):

        if self.retryAttemptsLeft < 3:
            self.modbus_client.close()
            self.modbus_client = ModbusConnection(self.SlavID, self.NetworkAddress, self.Port).connection()

        tag_list = TagMasterModel().find_by_DriverDetailID(self.DriverDetailID[0])

        while True:
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
                    # logger.info(
                    #     f'tag_db_value_list {str(tag_db_value_list)} Server at: {self.NetworkAddress}slavId {self.SlavID}')

                if len(tag_api_value_list) != 0:
                    len(tag_api_value_list)

                    # ApiServer().serverconnection(random_string)
                    # ApiServer().serverconnection(tag_api_value_list)

            except Exception as ex:
                self.modbus_client.close()

                DeviceConnectionLog().insert(self.DriverDetailID[0], False,
                                             'Client Closed with Exception : Attempts Left' + str(
                                                 self.retryAttemptsLeft) + "Network" + self.NetworkAddress + "slavId" + str(
                                                 self.SlavID),
                                             currentDateTime())

                self.retryAttemptsLeft = self.retryAttemptsLeft - 1


            time.sleep(60)

    def run(self) -> None:
        try:
            self.getDataFromTCP()
        except Exception as ex:
            logger.error(f'An error modbus Server at {self.NetworkAddress}, restarting process.')
            logger.exception(ex)

            DeviceConnectionLog().insert(self.DriverDetailID[0], False,
                                         'Client Closed with Exception : Attempts Left' + str(
                                             self.retryAttemptsLeft) + "Network" + self.NetworkAddress + "slavId" + str(
                                             self.SlavID),
                                         currentDateTime())
