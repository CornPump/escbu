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

    def add_publickey(self, public_key, client_id, lastseen):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        query = '''
            UPDATE clients
            SET Public_key = ?,
                Last_seen = ?
            WHERE ID = ?
        '''
        cursor.execute(query, (public_key, lastseen, client_id))

        conn.commit()
        conn.close()

    def add_aeskey(self, aes_key, client_id, lastseen):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        query = '''
                    UPDATE clients
                    SET AES_key = ?,
                        Last_seen = ?
                    WHERE ID = ?
                '''
        cursor.execute(query, (aes_key, lastseen, client_id))

        conn.commit()
        conn.close()

    def update_last_seen(self,client_id,lastseen):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        query = '''
                            UPDATE clients
                            SET Last_seen = ?
                            WHERE ID = ?
                        '''
        cursor.execute(query, (lastseen, client_id))

        conn.commit()
        conn.close()

    def fetch_public_rsa(self, client_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        query = 'SELECT Public_key FROM clients WHERE ID = ?'
        cursor.execute(query, (client_id,))

        result = cursor.fetchone()
        conn.close()

        return result

    def fetch_aes_key(self, client_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        query = 'SELECT AES_key FROM clients WHERE ID = ?'
        cursor.execute(query, (client_id,))

        result = cursor.fetchone()
        conn.close()

        return result[0]

    def add_new_file(self, client_id, file_name, client_dir_relative_path):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        columns = [files_keys[0],files_keys[1],files_keys[2],files_keys[3]]
        sql_query = f'''
            INSERT OR IGNORE INTO files ({', '.join(columns)})
            VALUES (?, ?, ?, ?)
        '''
        cursor.execute(sql_query, (client_id, file_name, client_dir_relative_path, False))

        conn.commit()
        conn.close()
