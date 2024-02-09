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
import cksum
import time
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
                received_file = self.start_receive_file_sequence()
                self.start_crc_sequence(received_file)

            elif seq_ret_code == helpers_response.Response['ERROR_F'] or \
                    seq_ret_code == helpers_response.Response['INTERNAL_F']:
                self.send_general_error_response()

        elif response_code == helpers_response.Response['LOGIN_F']:
            print(f"Login failure sending Response: {helpers_response.Response['LOGIN_F']}:'LOGIN_F' to client: {rh.name}")
            resh = response_handler.ResponseHandler(self.conn, helpers_response.Response['LOGIN_F'], "")
            resh.send_request()

        elif response_code == helpers_response.Response['LOGIN_S']:
            if self.start_login_success_sequence():
                received_file = self.start_receive_file_sequence()
                self.start_crc_sequence(received_file)

            else:
                # internal error sending general error
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
                try:
                    name_exist = self.dth.is_name_exist(rh.name)
                except Exception as e:
                    print(e)
                    return helpers_response.Response['REGISTER_F']

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
            if rh.payload_size != helpers_request.CLIENT_NAME_SIZE:
                return helpers_response.Response['ERROR_F']
            rh.name = self.conn.recv(helpers_request.CLIENT_NAME_SIZE).decode('utf-8').rstrip('\0')
            try:
                is_valid_login = self.dth.validate_login_request(rh.client_id,rh.name)
            except Exception as e:
                print(e)
                return helpers_response.Response['ERROR_F']

            if is_valid_login:
                return helpers_response.Response['LOGIN_S']
            else:
                return helpers_response.Response['LOGIN_F']

        else:
            print(f"Validate request failed due to impossible starting sequence code:{opcode} \n"
                  f"sending Response: {helpers_response.Response['ERROR_F']}")
            return helpers_response.Response['ERROR_F']

    def start_login_success_sequence(self):
        # add client to database and send register success Response
        try:
            old_uuid = self.dth.fetch_client_id(self.get_latest_req().name)
        except Exception as e:
            print(e)
            return False

        print(f"Generating aes_key for client:{old_uuid} ")
        aes_key = aes.generate_aes_key()
        try:
            self.dth.add_aeskey(aes_key=aes_key, client_id=old_uuid)
        except Exception as e:
            print(e)
            return False

        print(f"encrypting aes_key for client:{old_uuid} using his public_key")

        # Encrypt the AES key using RSA public key
        try:
            imported_public_key = RSA.import_key(self.dth.fetch_public_rsa(client_id=old_uuid))
        except Exception as e:
            print(e)
            return False
        cipher_rsa = PKCS1_OAEP.new(imported_public_key)
        encrypted_aes_key = cipher_rsa.encrypt(aes_key)

        print(f"Sending approval request: {helpers_response.Response['LOGIN_S']}:LOGIN_S")
        resh = response_handler.ResponseHandler(self.conn, helpers_response.Response['LOGIN_S'], old_uuid +
                                                encrypted_aes_key)
        try:
            resh.send_request()
            return True

        except Exception as e:
            print(e)
            return False


    def start_registration_success_sequence(self):
        # add client to database and send register success Response
        new_uuid = uuid.uuid4().bytes

        try:
            self.dth.add_new_client(id=new_uuid, name=self.get_latest_req().name)
        except Exception as e:
            print(e)
            return helpers_response.Response["INTERNAL_F"]


        print(f"Validate request accepted sending approval request: {helpers_response.Response['REGISTER_S']}:REGISTER_S")
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

            print(f'Sending Response {helpers_response.Response["REGISTER_AES_KEY"]}:REGISTER_AES_KEY')
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
        try:
            payload = self.conn.recv(none_file_payload_size)
        except Exception as e:
            print(e)
            return False


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
        try:
            self.dth.update_last_seen(rh.client_id)
        except Exception as e:
            print(e)
            return False


        client_dir = operation.create_user_directory(rh.client_id)

        client_dir_relative_path = os.path.join(operation.BACK_UP_DIR_NAME,os.path.basename(client_dir))

        try:
            self.dth.add_new_file(rh.client_id, file_name, client_dir_relative_path)
        except Exception as e:
            print(e)
            return False


        is_received_file = operation.receive_file(packet_number,total_packets,
                                rh.payload_size - none_file_payload_size,
                                os.path.join(client_dir_relative_path, file_name),
                                self.dth.fetch_aes_key(rh.client_id), self)
        if is_received_file:
            return os.path.join(client_dir_relative_path,file_name)

        return False

    def check_crc_with_client(self,received_file):
        deecrypted_tup = cksum.cksum(received_file)
        # print(deecrypted_tup)

        encrypted_file = os.path.join(os.path.dirname(received_file), 'encrypted_' + os.path.basename(received_file))
        encrypted_tup = cksum.cksum(encrypted_file)
        # print(encrypted_tup)
        rh = request_handler.RequestHandler(self.conn)
        content_size = rh.convert_to_little_endian(encrypted_tup[1],
                                                   helpers_response.DEFAULT_CONTENT_SIZE_SIZE)
        checksum = rh.convert_to_little_endian(deecrypted_tup[0],
                                               helpers_response.DEFAULT_CHECKSUM_SIZE)
        padded_file_name = os.path.basename(received_file).encode()
        padded_file_name = padded_file_name.ljust(helpers_request.CLIENT_FILE_NAME_SIZE, b'\x00')
        # print('content_size: ',content_size)
        # print('self.get_latest_req().client_id:',self.get_latest_req().client_id)
        # print('checksum: ', checksum)
        # print('padded_file_name:',padded_file_name)
        resh = response_handler.ResponseHandler(self.conn, helpers_response.Response['CHECK_CRC'],
                                                self.get_latest_req().client_id + content_size +
                                                padded_file_name + checksum)
        print(f'Checking CRC handshake with client sending Response: {resh.opcode}:CHECK_CRC')
        resh.send_request()



    def start_crc_sequence(self,received_file):
        if received_file:
            succed = False
            times = 0
            while (not succed or times == helpers_response.MAX_TRIES_TO_APPROVE_CRC):
                print('times:',times)
                self.check_crc_with_client(received_file)

                rh = request_handler.RequestHandler(self.conn)
                rh.read_minimum_header()
                self.append(rh)
                rh.file_name = self.conn.recv(helpers_request.CLIENT_NAME_SIZE).decode('utf-8').rstrip('\0')
                try:
                    self.dth.update_last_seen(rh.client_id)
                except Exception as e:
                    print(e)
                    break

                if rh.opcode == helpers_request.REQUEST['CRC_APP']:
                    succed = True
                    resh = response_handler.ResponseHandler(self.conn,
                                                            helpers_response.Response['CRC_SEQ_FINISH'],
                                                            rh.client_id)

                    print(f'successfully approved CRC handshake with client {rh.client_id}\n'
                          f'file:{rh.file_name} have been passed succefully '
                          f'sending Response {helpers_response.Response["CRC_SEQ_FINISH"]}')

                    resh.send_request()
                    self.dth.tik_file_verification(os.path.basename(received_file),rh.client_id)
                elif rh.opcode == helpers_request.REQUEST['CRC_DEN_FI']:
                    break

                else:
                    ff = self.start_receive_file_sequence()
                    times += 1
                    if ff != received_file:
                        self.send_general_error_response()



            if not succed:
                resh6 = response_handler.ResponseHandler(self.conn,
                                                        helpers_response.Response['CRC_SEQ_FINISH'],
                                                        rh.client_id)
                resh6.send_request()

                print(f'CRC handshake with client {rh.client_id}\ndenied,'
                      f'A Failure has occured in receive file:{rh.file_name} \n '
                      f'sending Response {helpers_response.Response["CRC_SEQ_FINISH"]}')




        else:
            self.send_general_error_response()
        # if not received there was an error in receving send error
        # if true we received the file succefuly
        # need to create 1603 response and send it