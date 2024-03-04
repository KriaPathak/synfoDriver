import struct
from threading import Thread
from datetime import datetime
import time

from pyModbusTCP.client import ModbusClient

from NoSqlDB import RethinkDatabase
from model import TagMasterModel, TagModel, DeviceConnectionLog


class ModbusTCP(Thread):

    def __init__(self,DriverDetailID, slavid,client,FrequncyOfGetData,NetworkAddress,Port,DriverName):
        super(ModbusTCP, self).__init__()
        self.DriverDetailID=DriverDetailID,
        self.slavid = slavid,
        self.client=client
        self.FrequncyOfGetData=FrequncyOfGetData
        self.NetworkAddress=NetworkAddress
        self.Port=Port
        self.SlavID=slavid
        self.DriverName=DriverName

    def kelvinToCelsius(self,kelvin):
        return kelvin - 273.15
    def getDataFromRTU(self):


        Isconnect = 0
        count=0
        client = ModbusClient(host=self.NetworkAddress, port=int(self.Port), unit_id=int(self.SlavID),
                              auto_open=True,
                              auto_close=True)
        while True:
            tag_DB_value_list = []
            tag_API_value_list = []
            taglist = TagMasterModel().find_by_DriverDetailID(self.DriverDetailID[0])


            try:


                for tagdata in taglist:
                    count=count+1
                    print(tagdata)
                    # if(tagdata[8]=='YES'):

                    # data=""
                    data = client.read_input_registers(int(tagdata[3]), int(tagdata[4]))
                    if(tagdata[5]=='INPUT REGISTER'):

                        data = client.read_input_registers(int(tagdata[3]), int(tagdata[4]))
                    elif(tagdata[5] == 'HOLDING REGISTER'):

                        data = client.read_holding_registers(int(tagdata[3]), int(tagdata[4]))
                        packed_string=""
                        # print("data",data)
                    if(tagdata[7]=='NO'):
                        packed_string = struct.pack("HH", data[0], data[1])
                    else:
                        packed_string = struct.pack("HH", data[1], data[0])


                    unpacked_float = struct.unpack("f", packed_string)[0]
                    # print(unpacked_float)
                    now = datetime.now()
                    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
                    tagvalue=unpacked_float

                    tag_value_ = (tagdata[0], tagvalue, dt_string)

                    if(tagdata[9]=='YES'):
                        tag_DB_value_list.append(tag_value_)
                        TagModel().insert(tagdata[0], tagvalue, dt_string)
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
                                # print(self.client.connected)
                    elif(tagdata[9]=='NO'):
                        tag_API_value_list.append(tag_value_)
                        tagName = TagMasterModel().find_by_TagID(tagdata[0])
                        RethinkDatabase().InsertData(self.DriverName, now, tagName[2], tagvalue, count)
            except:
            #
            #     if (self.client.connected == False and Isconnect != 3):
            #         now = datetime.now()
            #         dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
            #         DeviceConnectionLog().insert(self.DriverDetailID[0], self.client.connected,
            #                                      'disconnect device', dt_string)
            #         Isconnect = 5
               self.getDataFromRTU()


            time.sleep(self.FrequncyOfGetData)

    def run(self) -> None:

        self.getDataFromRTU()

        # time.sleep(1)








