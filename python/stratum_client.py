import json
import socket
import sys


class StratumClient(object):

    def __init__(self, settings):
        self._settings = settings
        self._socket = None

    def connect(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        address = (self._settings["host"], self._settings["port"])
        try:
            self._socket.connect(address)
        except ConnectionError:
            print("Failed to connect to the specified host {}:{}".format(*address))
            sys.exit(1)
        self._socket_readfile = self._socket.makefile('rb', 0)
        self._socket_writefile = self._socket.makefile('wb', 0)

        self._send_obj_to_server({
            "type": "connect",
            "payload": self._settings["name"]
        })

        response = self._receive_obj_from_server()
        if response["type"] != "name":
            print("Invalid response received from server")
            sys.exit(1)

        self._settings["name"] = response["payload"]
        self.name_received_from_server(response["payload"])

    def shutdown(self, sendClose=True):
        if sendClose:
            self._send_obj_to_server({
                "type": "close",
                "payload": None
            })

        self._socket_writefile.close()
        self._socket_readfile.close()
        self._socket.close()
        sys.exit(0)

    def run(self):
        while True:
            message = self.receive_message_from_server()
            self.messaged_received_from_server(message)

    def _send_obj_to_server(self, obj):
        s = json.dumps(obj) + "\n"
        self._socket_writefile.write(s.encode())

    def send_message_to_server(self, message):
        self._send_to_server({
            "type": "message",
            "payload": json.dumps(message)
        })

    def _receive_obj_from_server(self):
        b = self._socket_readfile.readline()
        obj = json.loads(b.decode().strip())
        if obj["type"] == "close":
            self.server_closed_connection()
            self.shutdown(False)
        return obj

    def receive_message_from_server(self):
        obj = self._receive_obj_from_server()
        if obj["type"] != "message":
            print("Invalid response received from server")
            sys.exit(1)
        return json.loads(obj["payload"])

    def name_received_from_server(self, name):
        print("Connected to server as {}".format(name))

    def server_closed_connection(self):
        print("Server closed the connection")

    def message_received_from_server(self, message):
        raise NotImplementedError


def main(client_constructor, **kwargs):
    settings = {
        "host": "localhost",
        "port": 8889,
        "name": None
    }

    # parse keyword arg parameters
    for key, value in kwargs:
        if key in settings:
            settings[key] = value

    # parse command line arg parameters
    args = sys.argv[1:]
    while args:
        try:
            arg = args.pop(0)
            if arg == "--host":
                settings["host"] = args.pop(0)
            elif arg == "--port":
                settings["port"] = int(args.pop(0))
            else:
                print("Invalid argument.")
                sys.exit(1)
        except:
            print("Invalid argument format.")
            sys.exit(1)

    client = client_constructor(settings)
    client.connect()
    client.run()
