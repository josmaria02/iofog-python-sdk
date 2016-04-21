
from ws4py.client.threadedclient import WebSocketClient
import threading
import iomessage
import urllib2
import json

NEW_MESSAGE=13
RECEIPT=14
ACK=15
CONTROL=16

IOFABRIC_CONFIG_URL="http://iofabric:54321/v2/config/get"

class Client(WebSocketClient):
    def __init__(self, url, listener):
        super(Client, self).__init__(url)
        self.listener=listener

    def opened(self):
        self.listener.onConnected()

    def closed(self, code, reason=None):
        self.listener.onClosed()


    def received_message(self, m):
        msg_data=bytearray(m.data)
        if len(msg_data) == 0:
            return
        opt_code=msg_data[0]
        if opt_code == NEW_MESSAGE:
            msg=iomessage.bytes2message(msg_data[1:])
            self.send(bytearray([RECEIPT]))
            self.listener.onMessage(msg)
        if opt_code == RECEIPT:
            self.send(bytearray([ACK]))
        if opt_code == ACK:
            print "ACK recieved."
        if opt_code == CONTROL:
            self.listener.onUpdateConfig(json.load(urllib2.urlopen(IOFABRIC_CONFIG_URL)))

    def send_message(self, msg):
        raw_data=bytearray()
        raw_data+=bytearray([NEW_MESSAGE])
        raw_data+=iomessage.message2bytes(msg)
        self.send(raw_data, binary=True)

    def connect(self):
        super(Client, self).connect()
        self.worker = threading.Thread(target=worker, args=(self,))
        self.worker.start()


def worker(client):
    client.run_forever()
