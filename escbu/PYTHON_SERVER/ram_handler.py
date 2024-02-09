from data_helpers import clients_keys, files_keys


class RamHandler:

    def __init__(self):

        self.clients = {}
        self.files = {}

    def __str__(self):
        return f"clients: {self.clients}\n files:{self.files}"

    def set_clients_dict(self, rows_lst):

        if rows_lst:

            for row in rows_lst:
                inner_dict = {clients_keys[1]: row[1], clients_keys[2]: row[2],
                              clients_keys[3]: row[3], clients_keys[3]: row[4]}
                self.clients[row[0]] = inner_dict

    def set_files_dict(self, rows_lst):
        if rows_lst:

            for row in rows_lst:
                inner_dict = {files_keys[1]: row[1], files_keys[2]: row[2], files_keys[3]: row[3]}
                if not row[0] in self.files:
                    self.files[row[0]] = []
                    self.files[row[0]].append(inner_dict)
                else:
                    self.files[row[0]].append(inner_dict)


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

    def fetch_aes_key(self, client_id):
        return self.clients[client_id]['AES_key']
    def update_last_seen(self, client_id, lastseen):
        self.clients[client_id]['Last_seen'] = lastseen

    def add_new_file(self, client_id, file_name, client_dir_relative_path):
        inner_dict = {files_keys[1]: file_name, files_keys[2]: client_dir_relative_path,
                      files_keys[3]: False}
        if not client_id in self.files:
            self.files[client_id] = []
            self.files[client_id].append(inner_dict)
        else:
            self.files[client_id].append(inner_dict)

    def tik_file_verification(self,received_file,client_id):
        for file_dict in self.files[client_id]:
            if file_dict['Name'] == received_file:
                file_dict['Verified'] = 1

    def fetch_client_id(self, name):
        for key, item in self.clients.items():
            if item["Name"] == name:
                return key



