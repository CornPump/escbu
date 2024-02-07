import os
import helpers_request
import binascii
import aes
import request_handler
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


def create_user_directory(client_id):
    dir_client_id = convert_uuid_to_dir_name(client_id)
    backup_dir = create_dir(os.getcwd(), BACK_UP_DIR_NAME)
    client_dir = create_dir(backup_dir, dir_client_id)
    return client_dir


def convert_uuid_to_dir_name(uuid):

    return binascii.hexlify(uuid).decode('utf-8')


def receive_file2(cur_packet,total_packets,read_size,file,aes_key,rm):
    print(read_size)
    print(cur_packet)
    if cur_packet <= 0 or total_packets <= 0:
        return False

    enc_file_name = os.path.join(os.path.dirname(file),'encrypted_'+os.path.basename(file))
    # first time
    if cur_packet == 1:
        data = rm.conn.recv(read_size)
        print('data:',data)
        with open(enc_file_name, 'wb') as encrypted_file:
            encrypted_file.write(data)

        with open(file, 'wb') as f:
            iv = aes.generate_zero_iv()
            decrypted_data = aes.decrypt_data(data, aes_key, iv)
            print('decrypted_data:', decrypted_data)
            f.write(decrypted_data)

        if total_packets == 1:
            return True
        else:
            receive_file2(cur_packet + 1, total_packets, read_size, file, aes_key, rm)
    else:
        # create RequestHandler instance
        rh = request_handler.RequestHandler(rm.conn)
        # read minimum header into it
        rh.read_minimum_header()
        if rh.opcode == helpers_request.REQUEST['SEND_FILE']:
            none_file_payload_size = helpers_request.DEFAULT_CONTENT_SIZE + helpers_request.DEFAULT_ORG_FILE_SIZE + \
                                     helpers_request.DEFAULT_PACKET_NUMBER_SIZE + helpers_request.DEFAULT_TOTAL_PACKET_SIZE + \
                                     + helpers_request.CLIENT_FILE_NAME_SIZE

            payload = rm.conn.recv(none_file_payload_size)
            read_size = rh.payload_size - none_file_payload_size

            data = rm.conn.recv(read_size)
            with open(enc_file_name, 'ab') as encrypted_file:
                encrypted_file.write(data)

            with open(file, 'ab') as f:
                iv = aes.generate_zero_iv()
                decrypted_data = aes.decrypt_data(data, aes_key, iv)
                f.write(decrypted_data)

            if cur_packet == total_packets:
                return True
            else:
                receive_file2(cur_packet+1, total_packets, 0, file, aes_key, rm)
        else:
            return False
