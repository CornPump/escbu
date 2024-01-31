import sqlite_handler
import ram_handler
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

    def add_new_client(self,id=None,name=None,publickey=None,lastseen=None,aeskey=None):
        if self.state == State['FT']:
            return self.sql_h.add_new_client(id,name,publickey,lastseen,aeskey)

        elif self.state == State['TF']:
            return self.ram_h.add_new_client(id,name,publickey,lastseen,aeskey)

        elif self.state == State['TT']:
            print('in TT')
            self.sql_h.add_new_client(id,name,publickey,lastseen,aeskey)
            self.ram_h.add_new_client(id,name,publickey,lastseen,aeskey)



