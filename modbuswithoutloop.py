from threading import Thread
import time
from customsMethod import structpack, structunpack, currentDateTime
from pyModbusTCP.client import ModbusClient
from model import TagMasterModel, TagModel, DeviceConnectionLog, DeviceException
from servercilentConnection import ApiServer


class ModbusMultiReg(Thread):
    retryAttemptsLeft = 3

    def __init__(self, DriverDetailID, slav_id, clientl, FrequncyOfGetData, NetworkAddress, Port, DriverName, datetime):
        super(ModbusMultiReg, self).__init__()
        self.DriverDetailID = DriverDetailID,
        self.slavid = slav_id,
        self.FrequncyOfGetData = FrequncyOfGetData
        self.NetworkAddress = NetworkAddress
        self.Port = Port
        self.SlavID = slav_id
        self.DriverName = DriverName
        # self.datetime = datetime

    def getDataFromMultiReg(self):

        # client = ModbusClient(host=self.NetworkAddress, port=int(self.Port), unit_id=int(self.SlavID))
        # if self.retryAttemptsLeft > 0:
        #     client.open()
        # else:
        #     return
        # print("open", client.is_open)
        # if client.is_open:
        #     DeviceConnectionLog().insert(self.DriverDetailID[0], True, "Driver open", currentDateTime())

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

                    # if tag_data[5] == 'INPUT REGISTER':
                    #     data = client.read_input_registers(int(tag_data[3]), int(tag_data[4]))
                    #
                    # elif tag_data[5] == 'HOLDING REGISTER':
                    #     data = client.read_holding_registers(int(tag_data[3]), int(tag_data[4]))
                    #
                    # if tag_data[7] == 'NO' and data != "" and data != 'None':
                    #     packed_string = structpack(data[0], data[1])
                    #
                    # elif tag_data[7] == 'YES' and data != "" and data != 'None':
                    #     packed_string = structpack(data[1], data[0])
                    #
                    # if len(packed_string) != 0:
                    tag_value = 5642

                    if tag_data[9] == 'YES':
                        tag_value_ = (tag_data[0], tag_value, datetime)
                        tag_db_value_list.append(tag_value_)

                    elif tag_data[9] == 'NO':
                        tagName = TagMasterModel().find_by_TagID(tag_data[0])
                        # tag_api_value_ = (tag_data[0], tag_value, datetime)
                        tag_api_value_ = {
                            'TagId': tag_data[0],
                            'TagValue': tag_value,
                            'DateandTime': datetime
                        }
                        tag_api_value_list.append(tag_api_value_)
                        data = "tagindex" + ' ' + str(tag_data[0]) + ' ' + "tagvalue" + str(tag_value)
                        random_string = random_string + ' '.join(data)

                if len(tag_db_value_list) != 0:
                    print("tag_db_value_list", str(tag_db_value_list) + self.NetworkAddress + str(self.SlavID))
                    TagModel().insert_multiple(tag_db_value_list)

                if len(tag_api_value_list) != 0:
                    len(tag_api_value_list)
                    print("SignalR",tag_api_value_list)

                    # ApiServer().serverconnection(random_string)
                    ApiServer().serverconnection(tag_api_value_list)

            except Exception as ex:

                print("exception", ex)
                # client.close()
                DeviceConnectionLog().insert(self.DriverDetailID[0], False,
                                             'Client Closed with Exception : Attempts Left' + str(
                                                 self.retryAttemptsLeft),
                                             currentDateTime())
                self.retryAttemptsLeft = self.retryAttemptsLeft - 1
                DeviceConnectionLogID = DeviceConnectionLog().find_driver_detail_id(self.DriverDetailID[0])

                if DeviceConnectionLogID[0] != 0:
                    DeviceException().insert(str(ex), currentDateTime(), DeviceConnectionLogID[0])
            time.sleep(10)

        # client.close()
        # DeviceConnectionLog().insert(self.DriverDetailID[0], False, 'Client Closed with Successful tags import',
        #                              currentDateTime())

    def run(self) -> None:
        try:
            self.getDataFromMultiReg()
        except Exception as ex:

            print("exception", ex)

            DeviceConnectionLogID = DeviceConnectionLog().find_driver_detail_id(self.DriverDetailID[0])
            if DeviceConnectionLogID[0] != 0:
                DeviceException().insert(str(ex), currentDateTime(), DeviceConnectionLogID[0])
