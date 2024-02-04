from data_helpers import clients_keys,files_keys

class RamHandler:

    def __init__(self):

        self.clients = {}
        self.files = {}

    def __str__(self):
        return f"clients: {self.clients}\n files:{self.files}"


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

    def is_name_exist(self, name):
        for key, value in self.clients.items():
            if value['Name'] == name:
                return True

        return False

    def add_new_client(self, id, name, publickey, lastseen, aeskey):
        inner_dict = {clients_keys[1]: name, clients_keys[2]: publickey,
                      clients_keys[3]: lastseen, clients_keys[4]: aeskey}
        self.clients[id] = inner_dict

    def add_publickey(self, public_key, client_id, lastseen):
        self.clients[client_id]['Public_key'] = public_key
        self.clients[client_id]['Last_seen'] = lastseen

    def add_aeskey(self, aes_key, client_id, lastseen):
        self.clients[client_id]['AES_key'] = aes_key
        self.clients[client_id]['Last_seen'] = lastseen

    def fetch_public_rsa(self, client_id):
        return self.clients[client_id]['Public_key']