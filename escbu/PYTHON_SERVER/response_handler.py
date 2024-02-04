import helpers_request
import request_handler
import helpers_response
class ResponseHandler():

    def __init__(self, connection, opcode, payload):

        self.conn = connection
        self.opcode = opcode
        self.payload_size = len(payload)
        self.payload = payload
        self.server_version = helpers_request.SERVER_VERSION

    def __str__(self):
        return f'( opcode={self.opcode} payload_size={self.payload_size}' \
               f',payloade={self.payload}, server_version={self.server_version})'

    def send_request(self):


        rh = request_handler.RequestHandler(self.conn)

        header = rh.convert_to_little_endian(self.server_version,helpers_response.DEFAULT_SERVER_VERSION_SIZE)\
                 + rh.convert_to_little_endian(self.opcode,helpers_response.DEFAULT_SERVER_CODE_SIZE) + \
                 rh.convert_to_little_endian(self.payload_size,helpers_response.DEFAULT_CLIENT_PAYLOAD_SIZE_SIZE)

        if self.payload:
            header += self.payload


        print('Resh:Header= ',header)

        try:
            self.conn.sendall(header)
        except Exception as e:
            print(e)
            print("couldn't send message")
            exit()
