import request_handler
import response_handler
import helpers_request
import helpers_response
import data_handler
import uuid
import aes
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

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

            if response_code == helpers_response.Response["REGISTER_AES_KEY"]:
                print("FINALE")
                pass

            elif seq_ret_code == helpers_response.Response['ERROR_F'] or\
                    seq_ret_code == helpers_response.Response['INTERNAL_F']:
                self.send_general_error_response()

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
        new_uuid = uuid.uuid4().bytes

        self.dth.add_new_client(id=new_uuid, name=self.get_latest_req().name)

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

        rsa_key = payload[adder: adder + helpers_request.CLIENT_PUBLIC_KEY_SIZE]

        if len(rsa_key) != helpers_request.CLIENT_PUBLIC_KEY_SIZE:
            return helpers_response.Response['ERROR_F']
        try:
            self.dth.add_publickey(public_key=rsa_key, client_id=rh.client_id)

            print(f"Generating aes_key for client:{rh.client_id} ")
            aes_key = aes.generate_aes_key()
            self.dth.add_aeskey(aes_key=aes_key, client_id=rh.client_id)

            print(f"encrypting aes_key for client:{rh.client_id} using his public_key")

            # Encrypt the AES key using RSA public key
            imported_public_key = RSA.import_key(self.dth.fetch_public_rsa(client_id=new_uuid))
            cipher_rsa = PKCS1_OAEP.new(imported_public_key)
            encrypted_aes_key = cipher_rsa.encrypt(aes_key)

            resh = response_handler.ResponseHandler(self.conn, helpers_response.Response['REGISTER_AES_KEY'],
                                                    new_uuid + encrypted_aes_key)

            print(f'Sending Response {helpers_response.Response["REGISTER_AES_KEY"]}')
            resh.send_request()

            return helpers_response.Response["REGISTER_AES_KEY"]

        except Exception as e:
            print(e)
            print(f'Responding with general error to client:{rh.client_id} ')
            return helpers_response.Response["INTERNAL_F"]



