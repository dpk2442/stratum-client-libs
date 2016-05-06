import json
import socket
import sys


class StratumGSClient(object):

    def __init__(self, settings, client_instance_constructor):
        self._settings = settings
        self._socket = None
        self._socket_readfile = None
        self._socket_writefile = None
        self._client_instance_constructor = client_instance_constructor
        self._client_instances = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._socket_writefile: self._socket_writefile.close()
        if self._socket_readfile: self._socket_readfile.close()
        if self._socket: self._socket.close()

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

        self.send_obj_to_server({
            "type": "connect",
            "name": self._settings["name"],
            "max_games": self._settings["max_games"]
        })

        response = self._receive_obj_from_server()
        if response["type"] != "name":
            print("Invalid response received from server")
            sys.exit(1)

        self._settings["name"] = response["name"]
        print("Connected to server as {}".format(response["name"]))


    def run(self):
        while True:
            obj = self._receive_obj_from_server()
            if obj["type"] == "close":
                game_id = obj["game_id"]
                if game_id in self._client_instances:
                    self._client_instances[game_id].server_closed_connection()
                    del self._client_instances[game_id]
            elif obj["type"] == "message":
                game_id = obj["game_id"]
                message = json.loads(obj["payload"])
                if game_id in self._client_instances:
                    self._client_instances[game_id].message_received_from_server(message)
            elif obj["type"] == "start":
                game_id = obj["game_id"]
                client_instance = self._client_instance_constructor(self, game_id)
                self._client_instances[game_id] = client_instance
            else:
                print("Invalid response received from server")
                sys.exit(1)

    def send_obj_to_server(self, obj):
        s = json.dumps(obj) + "\n"
        self._socket_writefile.write(s.encode())

    def _receive_obj_from_server(self):
        b = self._socket_readfile.readline()
        return json.loads(b.decode().strip())


class StratumGSClientInstance:

    def __init__(self, client, game_id):
        self._client = client
        self._game_id = game_id

    def send_message_to_server(self, message):
        self._client.send_obj_to_server({
            "type": "message",
            "game_id": self._game_id,
            "payload": json.dumps(message)
        })

    def server_closed_connection(self):
        print("Server closed the connection")

    def message_received_from_server(self, message):
        raise NotImplementedError


def main(client_instance_constructor, **kwargs):
    settings = {
        "host": "localhost",
        "port": 8889,
        "name": None,
        "max_games": 5
    }

    # parse keyword arg parameters
    for key, value in kwargs.items():
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
            elif arg == "--max-games":
                settings["max_games"] = int(args.pop(0))
            else:
                print("Invalid argument.")
                sys.exit(1)
        except:
            print("Invalid argument format.")
            sys.exit(1)

    with StratumGSClient(settings, client_instance_constructor) as client:
        client.connect()
        client.run()
