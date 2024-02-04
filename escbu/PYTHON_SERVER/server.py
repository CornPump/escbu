import socket
import os
import operation
import request_manager
import data_handler
import time

HOST = '127.0.0.1'
PORT = 1256

if __name__ == "__main__":

    # Create backup directory
    print("Creating back-up dir.. ")
    backup_dir = operation.create_dir(os.getcwd(), operation.BACK_UP_DIR_NAME)
    # pull port info
    try:
        with open('port.info', 'r') as f:
            PORT = int(f.readline())
    except Exception as e:
        print(e)

    # load sqlite data here!
    dth = data_handler.DataHandler('defensive.db', use_ram=True, use_db=True)

    print(f"Connecting to socket on port:{PORT}, host:{HOST} .. ")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((HOST, PORT))
        except Exception as e:
            print(e)
            exit()
        print("Listening and waiting for clients..")
        s.listen()
        conn, addr = s.accept()
        print('Connected by user', addr)
        with conn:
            s.settimeout(5)
            rm = request_manager.RequestManager(conn,dth)

            rm.start_request_sequence()
            #print(rm)



