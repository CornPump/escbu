import request_handler
import response_handler
import helpers_request
import helpers_response
class RequestManager:

    def __init__(self, connection):
        self.conn = connection
        self.request_lst = []
        self.num_requests = 0

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

        rh = self.get_latest_req()

        opcode = rh.opcode
        #if first request in the sequence
        if self.num_requests == 1:
            if opcode == helpers_request.REQUEST['REGISTER']:
                print(f"Validate request failed sending error: {helpers_response.Response['ERROR_F']}")
                resh = response_handler.ResponseHandler(self.conn, helpers_response.Response['ERROR_F'], "")
                resh.send_request()
            elif opcode == helpers_request.REQUEST['LOGIN']:
                pass
            else:
                print(f"Validate request failed sending error: {helpers_response.Response['ERROR_F']}")
                resh = response_handler.ResponseHandler(self.conn, helpers_response.Response['ERROR_F'], "")
                resh.send_request()

