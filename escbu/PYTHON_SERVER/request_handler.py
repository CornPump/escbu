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
            to_ret = struct.pack(">I", num)

        if size == 1:
                to_ret = struct.pack(">B", num)

        if size == 2:
            to_ret = struct.pack(">H", num)
        return to_ret

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
        min_header = self.conn.recv(helpers_request.DEFAULT_CLIENT_ID_SIZE +
                                    helpers_request.DEFAULT_CLIENT_VERSION_SIZE +
                                    helpers_request.DEFAULT_CLIENT_CODE_SIZE +
                                    helpers_request.DEFAULT_CLIENT_PAYLOAD_SIZE_SIZE)

        adder = helpers_request.DEFAULT_CLIENT_ID_SIZE

        client_id = min_header[:adder]

        client_version = self.convert_from_little_endian(
            min_header[adder:adder + helpers_request.DEFAULT_CLIENT_VERSION_SIZE],
        helpers_request.DEFAULT_CLIENT_VERSION_SIZE)
        adder += helpers_request.DEFAULT_CLIENT_VERSION_SIZE


        opcode = self.convert_from_little_endian(
            min_header[adder:adder + helpers_request.DEFAULT_CLIENT_CODE_SIZE],
            helpers_request.DEFAULT_CLIENT_CODE_SIZE)
        adder += helpers_request.DEFAULT_CLIENT_CODE_SIZE

        payload_size = self.convert_from_little_endian(
            min_header[adder:adder + helpers_request.DEFAULT_CLIENT_PAYLOAD_SIZE_SIZE],
            helpers_request.DEFAULT_CLIENT_PAYLOAD_SIZE_SIZE)

        self.client_id = client_id
        self.client_ver = client_version
        self.opcode = opcode
        self.payload_size = payload_size

        result = [key for key, item in helpers_request.REQUEST.items() if item == opcode]

        print(f'Received Request:{result}: (client_id:{client_id},opcode:{opcode},client_version:{client_version},payload_size:{payload_size})')


