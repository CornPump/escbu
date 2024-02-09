import sqlite_handler
import ram_handler
import datetime
from data_helpers import State


class DataHandler:

    def __init__(self, db_name: str, use_ram: bool = False, use_db: bool = True):

        self.db_name = db_name
        self.use_ram = use_ram
        self.use_db = use_db
        self.state = State['FF']

        if not use_db and not use_ram:
            print("Program must have use_ram or use_db set as true")
            exit(1)

        if use_db:
            # check if tables exists and create them if not
            self.sql_h = sqlite_handler.SqlDbHandler(self.db_name)

            # load db to ram
            if use_ram:
                self.state = State['TT']  # True RAM, True DB
                self.ram_h = ram_handler.RamHandler()
                self.load_db_to_ram()

            else:
                self.state = State['FT']  # False RAM, True DB

        else:
            self.state = State['TF']  # True RAM, False DB
            self.ram_h = ram_handler.RamHandler()


    def load_db_to_ram(self):
        self.ram_h.set_clients_dict(self.sql_h.load_entire_table('clients'))
        self.ram_h.set_files_dict(self.sql_h.load_entire_table('files'))

    def is_name_exist(self, name):

        if self.state == State['FT']:
            return self.sql_h.is_name_exist(name)

        elif self.state == State['TF']:
            return self.ram_h.is_name_exist(name)

        elif self.state == State['TT']:

            sql_bool = self.sql_h.is_name_exist(name)
            ram_bool = self.ram_h.is_name_exist(name)
            to_ret_bool = sql_bool and ram_bool

            if ram_bool != sql_bool:
                print(f'[WARNING] Missmatch in is_name_exist() sql_h return:{sql_bool} ram_h: return{ram_bool}')

            return to_ret_bool

    def add_new_client(self,id=None,name=None,publickey=None,aeskey=None):
        lastseen = datetime.datetime.now()
        if self.state == State['FT']:
            self.sql_h.add_new_client(id,name,publickey,lastseen,aeskey)

        elif self.state == State['TF']:
            self.ram_h.add_new_client(id,name,publickey,lastseen,aeskey)

        elif self.state == State['TT']:
            self.sql_h.add_new_client(id,name,publickey,lastseen,aeskey)
            self.ram_h.add_new_client(id,name,publickey,lastseen,aeskey)

    def add_publickey(self,public_key,client_id):
        lastseen = datetime.datetime.now()
        if self.state == State['FT']:
            self.sql_h.add_publickey(public_key,client_id,lastseen)

        elif self.state == State['TF']:
            self.ram_h.add_publickey(public_key,client_id,lastseen)

        elif self.state == State['TT']:
            self.sql_h.add_publickey(public_key,client_id,lastseen)
            self.ram_h.add_publickey(public_key,client_id,lastseen)

    def add_aeskey(self, aes_key,client_id):
        lastseen = datetime.datetime.now()

        if self.state == State['FT']:
            self.sql_h.add_aeskey(aes_key, client_id, lastseen)

        elif self.state == State['TF']:
            self.ram_h.add_aeskey(aes_key, client_id, lastseen)

        elif self.state == State['TT']:
            self.sql_h.add_aeskey(aes_key, client_id, lastseen)
            self.ram_h.add_aeskey(aes_key, client_id, lastseen)

    def fetch_public_rsa(self,client_id):
        if self.state == State['FT']:
            return self.sql_h.fetch_public_rsa(client_id)

        elif self.state == State['TF']:
            return self.ram_h.fetch_public_rsa(client_id)

        elif self.state == State['TT']:
            sql_pub_key = self.sql_h.fetch_public_rsa(client_id)
            ram_pub_key = self.ram_h.fetch_public_rsa(client_id)

            if (ram_pub_key != ram_pub_key):
                print(f'[WARNING] Missmatch in fetch_public_rsa() sql_h return:{sql_pub_key}\n ram_h: return{ram_pub_key}')

            return ram_pub_key

    def fetch_aes_key(self,client_id):
        if self.state == State['FT']:
            return self.sql_h.fetch_aes_key(client_id)

        elif self.state == State['TF']:
            return self.ram_h.fetch_aes_key(client_id)

        elif self.state == State['TT']:
            sql_aes_key = self.sql_h.fetch_aes_key(client_id)
            ram_aes_key = self.ram_h.fetch_aes_key(client_id)

            if (sql_aes_key != ram_aes_key):
                print(f'[WARNING] Missmatch in fetch_aes_key() sql_h return:{sql_aes_key}\n ram_h: return{ram_aes_key}')

            return ram_aes_key


    def update_last_seen(self,client_id):
        lastseen = datetime.datetime.now()
        if self.state == State['FT']:
            self.sql_h.update_last_seen(client_id, lastseen)

        elif self.state == State['TF']:
            self.ram_h.update_last_seen(client_id, lastseen)

        elif self.state == State['TT']:
            self.sql_h.update_last_seen(client_id, lastseen)
            self.ram_h.update_last_seen(client_id, lastseen)


    def add_new_file(self,client_id, file_name, client_dir_relative_path):
        if self.state == State['FT']:
            self.sql_h.add_new_file(client_id, file_name, client_dir_relative_path)

        elif self.state == State['TF']:
            self.add_new_file(client_id, file_name, client_dir_relative_path)

        elif self.state == State['TT']:
            self.sql_h.add_new_file(client_id, file_name, client_dir_relative_path)
            self.ram_h.add_new_file(client_id, file_name, client_dir_relative_path)


    def fetch_client_id(self,name):
        if self.state == State['FT']:
            return self.sql_h.fetch_client_id(name)

        elif self.state == State['TF']:
            return self.ram_h.fetch_client_id(name)

        elif self.state == State['TT']:
            sql_client_id = self.sql_h.fetch_client_id(name)
            ram_client_id = self.ram_h.fetch_client_id(name)

            if (sql_client_id != ram_client_id):
                print(f'[WARNING] Missmatch in fetch_client_id() sql_h return:{sql_client_id}\n ram_h: return{ram_client_id}')

            return ram_client_id

    def validate_login_request(self,client_id_from_client,name):
        name_exist = self.is_name_exist(name)
        if name_exist:
            client_id_db = self.fetch_client_id(name)
            if client_id_db == client_id_from_client:
                public_key = self.fetch_public_rsa(client_id_db)
                return public_key


        return False

    def tik_file_verification(self,received_file,client_id):
        if self.state == State['FT']:
            self.sql_h.tik_file_verification(received_file,client_id)

        elif self.state == State['TF']:
            self.tik_file_verification(received_file,client_id)

        elif self.state == State['TT']:
            self.sql_h.tik_file_verification(received_file,client_id)
            self.ram_h.tik_file_verification(received_file,client_id)









