import os
import helpers_request


BACK_UP_DIR_NAME = "backup_server"


def create_dir(path: str, name: str) -> str:
    new_dir = os.path.join(path, name)
    if not (os.path.isdir(new_dir)):
        os.mkdir(new_dir)

    return new_dir

def receive_file(file_name, socket, size):

    try:
        with open(file_name,'w') as f:

            total_received = 0

            while total_received < size:
                bytes_to_receive = min(helpers_request.MESSAGE_MAX_SIZE, size - total_received)
                data = socket.recv(bytes_to_receive)
                f.write(data.decode('utf-8'))
                total_received += len(data)

    except Exception as e:
        print(f"Couldn't read file {file_name} in receive_file() due to error:\n",e)


def get_file_size(file):
    with open(file, 'rb') as file:
        file.seek(0, 2)
        file_size = file.tell()
        return file_size


def send_file(filename, socket):
    try:
        with open(filename, 'rb') as file:

            while True:
                data = file.read(helpers_request.MESSAGE_MAX_SIZE)
                if not data:
                    break
                socket.sendall(data)

            print(f"File sent successfully: {filename}")

    except Exception as e:
        print(f"Error sending file in send_file():\n {e}")
