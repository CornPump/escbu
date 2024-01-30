import struct
import helpers_request


class RequestHandler:

    # connection = socket connection
    def __init__(self, connection):

        self.conn = connection
        self.client_id = 0
        self.client_ver = 0
        self.opcode = 0
        self.payload_size = 0
        self.name = ""
        self.file_name = ""

    def __str__(self):
        return f'(client_id={self.client_id}, client_ver={self.client_ver}, opcode={self.opcode} ' \
               f',payload_size={self.payload_size}, name={self.name}, file_name={self.file_name})'

    @staticmethod
    def convert_to_little_endian(num: int, size: int):
        if size == 4:
            to_ret = struct.pack("<I", num)

        if size == 1:
                to_ret = struct.pack("<B", num)

        if size == 2:
            to_ret = struct.pack("<H", num)

        return to_ret[0]

    @staticmethod
    def convert_from_little_endian(num: int, size: int):

        if size == 4:
            to_ret = struct.unpack(">I", num)

        if size == 1:
                to_ret = struct.unpack(">B", num)

        if size == 2:
            to_ret = struct.unpack(">H", num)

        return to_ret[0]

    def read_minimum_header(self):

        # read minimum header data
        client_id = self.conn.recv(helpers_request.DEFAULT_CLIENT_ID_SIZE)
        client_version = self.convert_from_little_endian(self.conn.recv(helpers_request.DEFAULT_CLIENT_VERSION_SIZE),
                                                         helpers_request.DEFAULT_CLIENT_VERSION_SIZE)
        opcode = self.convert_from_little_endian(self.conn.recv(helpers_request.DEFAULT_CLIENT_CODE_SIZE),
                                                 helpers_request.DEFAULT_CLIENT_CODE_SIZE)
        payload_size = self.convert_from_little_endian(self.conn.recv(helpers_request.DEFAULT_CLIENT_PAYLOAD_SIZE_SIZE),
                                                       helpers_request.DEFAULT_CLIENT_PAYLOAD_SIZE_SIZE)

        self.client_id = client_id
        self.client_ver = client_version
        self.opcode = opcode
        self.payload_size = payload_size

    #def validate_minimum_header(self):

