import sqlite3
from data_helpers import clients_keys,files_keys

class SqlDbHandler:

    def __init__(self,db_name):

        self.db_name = db_name
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                {} BLOB PRIMARY KEY,
                {} TEXT,
                {} BLOB,
                {} DATE,
                {} BLOB
            )
        '''.format(clients_keys[0],clients_keys[1],clients_keys[2],clients_keys[3],clients_keys[4]))

        # Create the second table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                {} BLOB PRIMARY KEY,
                {} TEXT,
                {} TEXT,
                {} BOOLEAN
            )
        '''.format(files_keys[0],files_keys[1],files_keys[2],files_keys[3]))

        conn.commit()
        conn.close()

    def load_entire_table(self,table_name):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM {table_name}')
        rows = cursor.fetchall()

        lst = []
        for row in rows:
            lst.append(row)

        cursor.close()
        conn.close()
        return lst

    def is_name_exist(self,name):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute('''
                    SELECT * FROM clients
                    WHERE Name = ?
                ''', (name,))

        results = cursor.fetchone()
        conn.close()

        if results:
            return True

        return False

    def add_new_client(self, id, name, publickey, lastseen, aeskey):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        columns = [clients_keys[0],clients_keys[1],clients_keys[2],clients_keys[3],clients_keys[4]]
        sql_query = f'''
            INSERT INTO clients ({', '.join(columns)})
            VALUES (?, ?, ?, ?, ?)
        '''
        cursor.execute(sql_query, (id, name, publickey, lastseen, aeskey))

        conn.commit()
        conn.close()

"""
    def part_entry(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO files (ID, Filename)
            VALUES (?, ?)
        ''', (b'sheeeeeeeeeeeesh', 'thatsomecrazypath'))
        conn.commit()
        cursor.close()
        conn.close()
"""