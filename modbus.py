import struct
from threading import Thread
from datetime import datetime
import time
from model import TagMasterModel, TagModel, DeviceConnectionLog


class ModbusRTU(Thread):

    def __init__(self,DriverDetailID, slavid,client,FrequncyOfGetData,DriverName,datetime):
        super(ModbusRTU, self).__init__()
        self.DriverDetailID=DriverDetailID,
        self.slavid = slavid,
        self.client=client
        self.FrequncyOfGetData=FrequncyOfGetData
        self.DriverName=DriverName
        self.datetime=datetime

    def getDataFromRTU(self):


        Isconnect = 0

        while True:

            taglist = TagMasterModel().find_by_DriverDetailID(self.DriverDetailID[0])
            try:

                if (self.client.connected and Isconnect == 0):
                    now = datetime.now()
                    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
                    DeviceConnectionLog().insert(self.DriverDetailID[0], self.client.connected, 'connect device',
                                                 dt_string)
                    Isconnect = 1
                if(self.client.connected):
                    for tagdata in taglist:
                        print(tagdata)
                        # if(tagdata[8]=='YES'):
                        #     print("tttttt")
                        res=""
                        if(tagdata[5]=='INPUT REGISTER'):
                            # print("kkkkk")
                            print("address"+tagdata[3])
                            print("count"+tagdata[4])
                            print("salve"+self.slavid[0])
                            res = self.client.read_input_registers(address=int(tagdata[3]), count=int(tagdata[4]), slave=self.slavid[0])

                        if not res.isError():

                            data = res.registers
                            packed_string=""
                            print(data)
                            if(tagdata[7]=='No'):
                                packed_string = struct.pack("HH", data[0], data[1])
                            else:
                                packed_string = struct.pack("HH", data[1], data[0])

                            data = struct.unpack("f", packed_string)
                            unpacked_float = struct.unpack("f", packed_string)[0]



                            # if(tagdata[9]=='YES'):
                            #     print("yyyyyyy")
                            TagModel().insert(tagdata[0], unpacked_float, self.datetime)
                        else:
                            Isconnect = 2
                            if (self.client.connected==False and Isconnect == 2):
                                now = datetime.now()
                                dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
                                DeviceConnectionLog().insert(self.DriverDetailID[0], self.client.connected,
                                                             'disconnect device', dt_string)
                                Isconnect = 3
                            print(res)
                            print("3")
                            # print(self.client.connected)
            except:

                if (self.client.connected == False and Isconnect != 3):
                    now = datetime.now()
                    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
                    DeviceConnectionLog().insert(self.DriverDetailID[0], self.client.connected,
                                                 'disconnect device', dt_string)
                    Isconnect = 5
                self.getDataFromRTU()


            time.sleep(self.FrequncyOfGetData)

    def run(self) -> None:

        self.getDataFromRTU()

        # time.sleep(1)








