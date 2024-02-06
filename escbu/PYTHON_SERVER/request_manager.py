import request_handler
import response_handler
import helpers_request
import helpers_response
import operation
import uuid
import aes
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import os

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

            if seq_ret_code == helpers_response.Response["REGISTER_AES_KEY"]:
                self.start_receive_file_sequence()

            elif seq_ret_code == helpers_response.Response['ERROR_F'] or \
                    seq_ret_code == helpers_response.Response['INTERNAL_F']:
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
            print(f'Responding with general error to client:{rh.client_id} '
                  f'but got helpers_response.Response["INTERNAL_F"]:Internal_error')
            return helpers_response.Response["INTERNAL_F"]


    def start_receive_file_sequence(self):
        # create RequestHandler instance
        rh = request_handler.RequestHandler(self.conn)
        # read minimum header into it
        rh.read_minimum_header()
        # append to request_manager
        self.append(rh)
        none_file_payload_size = helpers_request.DEFAULT_CONTENT_SIZE + helpers_request.DEFAULT_ORG_FILE_SIZE +\
                        helpers_request.DEFAULT_PACKET_NUMBER_SIZE + helpers_request.DEFAULT_TOTAL_PACKET_SIZE +\
                        + helpers_request.CLIENT_FILE_NAME_SIZE

        payload = self.conn.recv(none_file_payload_size)

        adder = 0
        enc_file_size = rh.convert_from_little_endian(payload[:helpers_request.DEFAULT_CONTENT_SIZE],
                                                        helpers_request.DEFAULT_CONTENT_SIZE)
        adder += helpers_request.DEFAULT_CONTENT_SIZE
        orig_file_size = rh.convert_from_little_endian(payload[adder: adder + helpers_request.DEFAULT_ORG_FILE_SIZE],
                                                       helpers_request.DEFAULT_ORG_FILE_SIZE)
        adder += helpers_request.DEFAULT_ORG_FILE_SIZE
        packet_number = rh.convert_from_little_endian(payload[adder: adder + helpers_request.DEFAULT_PACKET_NUMBER_SIZE],
                                                      helpers_request.DEFAULT_PACKET_NUMBER_SIZE)
        adder += helpers_request.DEFAULT_PACKET_NUMBER_SIZE
        total_packets = rh.convert_from_little_endian(payload[adder: adder + helpers_request.DEFAULT_TOTAL_PACKET_SIZE],
                                                      helpers_request.DEFAULT_TOTAL_PACKET_SIZE)
        adder += helpers_request.DEFAULT_TOTAL_PACKET_SIZE
        file_name = payload[adder: adder + helpers_request.CLIENT_FILE_NAME_SIZE].decode('utf-8').rstrip('\0')

        print(f'enc_file_size:{enc_file_size},orig_file_size:{orig_file_size},'
              f'packet_number:{packet_number},total_packets:{total_packets},\nfile_name:{file_name}')

        self.dth.update_last_seen(rh.client_id)

        client_dir = operation.create_user_directory(rh.client_id)

        client_dir_relative_path = os.path.join(operation.BACK_UP_DIR_NAME,os.path.basename(client_dir))

        self.dth.add_new_file(rh.client_id, file_name, client_dir_relative_path)

        operation.receive_file2(packet_number,total_packets,
                                rh.payload_size - none_file_payload_size,
                                os.path.join(client_dir_relative_path, file_name),
                                self.dth.fetch_aes_key(rh.client_id), self)







