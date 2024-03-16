# from rethinkdb import r
#
#
# class RethinkDatabase:
#
#     def __init__(self):
#         super(RethinkDatabase, self).__init__()
#
#
#
#     def InsertData(self,measurementvalue,datatime,tagname,value,devicename,count):
#         r.connect('127.0.0.1', 28015).repl()
#         self.connection = r.connect(db='synfodriver')
#         try:
#             r.table_create('modbusdata').run(self.connection)
#         except:
#             print("ookkk")
#         self.modbusdata = r.table('modbusdata')
#
#         jsonvalue={
#             'id': count,
#             'tagname': tagname,
#             'time': r.now().to_iso8601().run(self.connection),
#             'devicename': devicename
#         }
#         print(jsonvalue)
#         self.modbusdata.insert(jsonvalue).run(self.connection)
#
#         for modbus in self.modbusdata.run(self.connection):
#             print('modbus',modbus)

from pyModbusTCP.client import ModbusClient
from customsMethod import structpack, structunpack

client = ModbusClient('192.168.1.200', port=502, unit_id=1)
data = client.read_input_registers(00,50)
# print(data)
# packed_string = structpack(data[0], data[1])
# tagvalue = structunpack(packed_string)
# print(tagvalue)

tagvalue_list=[]
for j in range(0,16,2):
    packed_string = structpack(data[j], data[j+1])
    tagvalue = structunpack(packed_string)
    tagvalue_list.append(tagvalue)

print("data",tagvalue_list)

tagindex = [1,2,3,4,5,6,7,8,9,10,11,12,13,14]
print ("tagindex",tagindex)


mapp_val = []
for i,a in enumerate(tagvalue_list):
    b = tagindex[i] if i < len(tagindex) else None
    mapp_val.append(f"{b}:{a}" if a is not None else f"{b}")

print (mapp_val)


