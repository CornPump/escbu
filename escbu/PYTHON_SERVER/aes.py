from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


DEFUALT_KEY_SIZE = int(256 / 8)


def generate_zero_iv():
    # Create an IV with all zeros
    zero_iv = bytes([0] * AES.block_size)
    return zero_iv


def generate_aes_key():
    aes_key = get_random_bytes(DEFUALT_KEY_SIZE)
    return aes_key


def pad(data):
    # Calculate the number of bytes to pad
    padding_size = AES.block_size - (len(data) % AES.block_size)

    # Pad the data using zero padding scheme
    padding = bytes([0] * padding_size)
    padded_data = data + padding

    return padded_data

def unpad(data):
    # Find the index of the last non-zero byte, which indicates the end of the data
    last_nonzero_index = max(i for i, byte in enumerate(data) if byte != 0)

    # Trim the zeros after the last non-zero byte
    unpadded_data = data[:last_nonzero_index + 1]

    return unpadded_data


def encrypt_data(data, aes_key, iv):
    # Create an AES cipher object with CBC mode
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)

    # Pad the data using PKCS#7 scheme
    padded_data = pad(data)

    # Encrypt the data
    encrypted_data = cipher.encrypt(padded_data)

    return encrypted_data


def decrypt_data(encrypted_data, aes_key, iv):
    # Create an AES cipher object with CBC mode
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)

    # Decrypt the data
    decrypted_data = cipher.decrypt(encrypted_data)
    # Remove padding using PKCS#7 scheme
    unpadded_data = unpad(decrypted_data)

    return unpadded_data

"""
# Example usage:
# Generate a new AES key
aes_key = generate_aes_key()
print('aes_key',aes_key)
print(len(aes_key))
# Generate a new random IV
iv = get_random_bytes(AES.block_size)

# Example data to encrypt
data_to_encrypt = b"Hello, PyCryptodome!"

# Encrypt the data
encrypted_data = encrypt_data(data_to_encrypt, aes_key, iv)
print("Encrypted Data:", encrypted_data)

# Decrypt the data
decrypted_data = decrypt_data(encrypted_data, aes_key, iv)
print("Decrypted Data:", decrypted_data.decode())
"""