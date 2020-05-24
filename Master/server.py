from base_type.packet import *
from Master.controller import Controller


class Server:

    PARSE_BYTES = 3

    def __init__(self, controller: Controller, config):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.config = config
        self.config["host"] = socket.gethostbyname(socket.gethostname())
        self.controller = controller
        self.conn.bind((self.config["host"], self.config["port"]))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def __del__(self):
        self.conn.close()

    def listen(self, backlog=5):
        print(f"Listening at {self.config['host']}:{self.config['port']}")
        self.conn.listen(backlog)
        client_socket = None
        while True:
            print("Entering listen loop")
            try:
                client_socket, address = self.conn.accept()
                print(f"Connection from {address} has been established!")
                try:
                    req = self.await_request(client_socket, address)
                    print(f"Packet received {Request(req['request'])}")
                    resp = self.process_request(req)
                    self.send_response(client_socket, resp)
                except EndOfPacketError or EmptyPacket as err:
                    print(err)
            except KeyboardInterrupt:
                print("Shutting down server")
                break
            except BasePacketException as ex:
                print(f"ERROR: {ex}")
                client_socket.close()

    def await_request(self, client, address) -> dict:
        # TODO fix this error which causes this loop to stuff up
        payload = b""
        data = b" "
        new = True
        buffer = self.config["packet_buffer_size"]
        header_size = self.config["packet_header_size"]
        msg = {}
        length = 0
        while data:
            data = client.recv(buffer)
            if len(data) > 0:
                if new:
                    length = int(data[:header_size])
                    print(f"New Request packet from {address}  -  Length: {length}")
                    new = False
                    payload = data
                    continue
                payload += data
                if len(payload) - header_size == length:
                    try:
                        msg = json.loads(payload[header_size:], encoding="utf-8")
                    except json.decoder.JSONDecodeError as e:
                        print(f"ERROR: {e}")
                        raise InvalidPacket(payload)
                    finally:
                        new = not bool(payload) and bool(msg)
            if msg:
                return msg
            elif new:
                print("EMPTY")
                raise EmptyPacket(address)

    def process_request(self, packet) -> Response:
        request = Request(packet["request"])
        response = None
        if request is Request.USER_LOGIN:
            if self.controller.login(packet["user"], packet["password"]):
                response = Response(1.1)
            else:
                response = Response(0.1)
        elif request is Request.USER_VERIFY or request is Request.CAR_RETURN:
            pass
        if not response:
            response = Response(0)
        return response

    def send_response(self, client, response: Response):
        payload = response.get_payload(self.config["packet_header_size"], **self.config)
        client.send(payload)

