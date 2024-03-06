import logging
import sys
from signalrcore.hub_connection_builder import HubConnectionBuilder
import threading
import random
import string
from datetime import datetime

class ApiServer:

    def serverconnection(self,messageData):
        server_url = "https://localhost:7268/commhub"
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        hub_connection = HubConnectionBuilder() \
            .with_url(server_url, options={"verify_ssl": False}) \
            .configure_logging(logging.DEBUG, socket_trace=True, handler=handler) \
            .with_automatic_reconnect({
            "type": "interval",
            "keep_alive_interval": 10,
            "intervals": [1, 3, 5, 6, 7, 87, 3]
        }).build()

        hub_connection.on_open(lambda: print("connection opened and handshake received ready to send messages"))
        hub_connection.on_error(lambda: print("error has occurred"))
        hub_connection.on_close(lambda: print("connection closed"))

        hub_connection.on("ReceiveMessage", print)
        hub_connection.start()
        message = None
        while message != "exit()":
            hub_connection.send("SendData", [[messageData]])


        hub_connection.stop()