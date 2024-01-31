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
        self.validate_request()


    def get_latest_req(self):
        return self.request_lst[self.num_requests - 1]

    def validate_request(self):
        print('Validating Request..')
        rh = self.get_latest_req()

        opcode = rh.opcode
        #if first request in the sequence
        if self.num_requests == 1:
            if opcode == helpers_request.REQUEST['REGISTER']:
                if rh.payload_size == helpers_request.CLIENT_NAME_SIZE:
                    rh.name = self.conn.recv(helpers_request.CLIENT_NAME_SIZE).decode('utf-8').rstrip('\0')

                    # check if client name already exists, if it is send REGISTER_F
                    name_exist = self.dth.is_name_exist(rh.name)

                    if name_exist:
                        resh = response_handler.ResponseHandler(self.conn, helpers_response.Response['REGISTER_F'], "")
                        resh.send_request()

                    else:
                        # add client to database and send register success Response
                        new_uuid = uuid.uuid4().bytes
                        self.dth.add_new_client(id=new_uuid, name=rh.name)

                        print(f"Validate request accepted sending approval request: {helpers_response.Response['REGISTER_S']}")
                        resh = response_handler.ResponseHandler(self.conn, helpers_response.Response['REGISTER_S'], "")
                        resh.send_request()

                    # receive request with public key
                    # generate AES key
                    # create entry in table for client (SQLITE & RAM)
                    # encrpyt AES key with public key
                    # send to client


                # invalid request, sending general error
                else:
                    print(f"Validate request failed sending error: {helpers_response.Response['ERROR_F']}")
                    resh = response_handler.ResponseHandler(self.conn, helpers_response.Response['ERROR_F'], "")
                    resh.send_request()
            elif opcode == helpers_request.REQUEST['LOGIN']:
                pass
            else:
                print(f"Validate request failed sending error: {helpers_response.Response['ERROR_F']}")
                resh = response_handler.ResponseHandler(self.conn, helpers_response.Response['ERROR_F'], "")
                resh.send_request()

