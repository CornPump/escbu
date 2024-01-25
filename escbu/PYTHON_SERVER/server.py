import socket
import os
import operation


HOST = '127.0.0.1'
PORT = 1256

if __name__ == "__main__":

    # Create backup directory
    backup_dir = operation.create_dir(os.getcwd(), operation.BACK_UP_DIR_NAME)
    # pull port info
    try:
        with open('port.info', 'r') as f:
            PORT = int(f.readline())
    except Exception as e:
        print(e)

    # load sqlite data here!

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))



