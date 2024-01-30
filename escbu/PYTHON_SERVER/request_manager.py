import request_handler
import helpers_request

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