import sqlite_handler
import ram_handler
from data_helpers import State
class DataHandler:

    def __init__(self,db_name: str,use_ram: bool = False, use_db: bool = True):

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
                self.state = State['TT'] # True RAM, True DB
                self.ram_h = ram_handler.RamHandler()

            else:
                self.state = State['FT'] # False RAM, True DB

        else:
            self.state = State['TF'] # True RAM, False DB
            self.ram_h = ram_handler.RamHandler()
            self.load_db_to_ram()

    def load_db_to_ram(self):
        self.ram_h.set_clients_dict(self.sql_h.load_entire_table('clients'))
        self.ram_h.set_files_dict(self.sql_h.load_entire_table('files'))





