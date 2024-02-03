import request_handler
import response_handler
import helpers_request
import helpers_response
import data_handler
import uuid
class RequestManager:

    def __init__(self, connection, data_handler):
        self.conn = connection
        self.request_lst = []
        self.num_requests = 0
        self.dth = data_handler

    def __str__(self):
        s = f"num_of_request:{self.num_requests}\n"
        for req in self.request_lst:
            s += str(req) + "\n"

        return s

    def append(self,request):
        self.request_lst.append(request)
        self.num_requests += 1

    def start_request_sequence(self):

        # create RequestHandler instance
        rh = request_handler.RequestHandler(self.conn)
        # read minimum header into it
        rh.read_minimum_header()
        # append to request_manager
        self.append(rh)
        # validate the request
        response_code = self.validate_request()

        if response_code == helpers_response.Response['ERROR_F']:
            self.send_general_error_response()

        elif response_code == helpers_response.Response['REGISTER_F']:
            resh = response_handler.ResponseHandler(self.conn, helpers_response.Response['REGISTER_F'], "")
            resh.send_request()

        elif response_code == helpers_response.Response['REGISTER_S']:
            seq_ret_code = self.start_registration_success_sequence()
            if seq_ret_code == helpers_response.Response['ERROR_F']:
                self.send_general_error_response()

    def get_latest_req(self):
        return self.request_lst[self.num_requests - 1]

    def send_general_error_response(self):
        resh = response_handler.ResponseHandler(self.conn, helpers_response.Response['ERROR_F'], "")
        resh.send_request()

    def validate_request(self):
        print('Validating Request..')
        rh = self.get_latest_req()

        opcode = rh.opcode
        #if first request in the sequence
        if opcode == helpers_request.REQUEST['REGISTER']:
            if rh.payload_size == helpers_request.CLIENT_NAME_SIZE:
                rh.name = self.conn.recv(helpers_request.CLIENT_NAME_SIZE).decode('utf-8').rstrip('\0')

                # check if client name already exists, if it is send REGISTER_F
                name_exist = self.dth.is_name_exist(rh.name)

                if name_exist:
                    print(f"Validate request failed due to name already existing in db\n"
                          f" sending denial request: {helpers_response.Response['REGISTER_F']}")
                    return helpers_response.Response['REGISTER_F']

                else:
                    return helpers_response.Response['REGISTER_S']
            # invalid request, sending general error
            else:
                print(f"Validate request failed sending error due to invalid payload_size: {helpers_response.Response['ERROR_F']}")
                return helpers_response.Response['ERROR_F']

        elif opcode == helpers_request.REQUEST['LOGIN']:
            pass
        else:
            print(f"Validate request failed due to impossible starting sequence code:{opcode} \n"
                  f"sending Response: {helpers_response.Response['ERROR_F']}")
            return helpers_response.Response['ERROR_F']

    def start_registration_success_sequence(self):
        # add client to database and send register success Response
        print_uid = uuid.uuid4()
        new_uuid = print_uid.bytes
        print(new_uuid)
        print(print_uid)
        self.dth.add_new_client(id=new_uuid, name=self.get_latest_req().name)

        print(self.dth.ram_h)
        print(f"Validate request accepted sending approval request: {helpers_response.Response['REGISTER_S']}")
        resh = response_handler.ResponseHandler(self.conn, helpers_response.Response['REGISTER_S'], new_uuid)
        resh.send_request()

        # create RequestHandler instance
        rh = request_handler.RequestHandler(self.conn)
        # read minimum header into it
        rh.read_minimum_header()
        # append to request_manager
        self.append(rh)

        # read payload
        adder = 0
        payload = self.conn.recv(helpers_request.CLIENT_NAME_SIZE + helpers_request.CLIENT_PUBLIC_KEY_SIZE)
        rh.name = payload[:helpers_request.CLIENT_NAME_SIZE].decode('utf-8').rstrip('\0')
        adder += helpers_request.CLIENT_NAME_SIZE
        print('name=', rh.name)
        rsa_key = payload[adder: adder + helpers_request.CLIENT_PUBLIC_KEY_SIZE]
        print('key=', rsa_key)
        print(len(rsa_key))

        if len(rsa_key) != helpers_request.CLIENT_PUBLIC_KEY_SIZE:
            return helpers_response.Response['ERROR_F']

        self.dth.add_publickey(public_key=rsa_key, client_id=rh.client_id)
        # receive request with public key
        # generate AES key
        # create entry in table for client (SQLITE & RAM)
        # encrpyt AES key with public key
        # send to client



