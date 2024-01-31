from data_helpers import clients_keys,files_keys

class RamHandler:

    def __init__(self):

        self.clients = {}
        self.files = {}


    def set_clients_dict(self,rows_lst):

        if rows_lst:

            for row in rows_lst:
                inner_dict = {clients_keys[1]: row[1], clients_keys[2]: row[2],
                              clients_keys[3]: row[3], clients_keys[3]: row[4]}
                self.clients[row[0]] = inner_dict

    def set_files_dict(self,rows_lst):
        if rows_lst:

            for row in rows_lst:
                inner_dict = {files_keys[1]: row[1], files_keys[2]: row[2], files_keys[3]: row[3]}
                self.files[row[0]] = inner_dict
