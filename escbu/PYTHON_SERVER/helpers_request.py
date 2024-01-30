MESSAGE_MAX_SIZE = 1024

# Size in bytes of request params, -1 = unlimited
DEFAULT_CLIENT_ID_SIZE = 16
DEFAULT_CLIENT_VERSION_SIZE = 1
DEFAULT_CLIENT_CODE_SIZE = 2
DEFAULT_CLIENT_PAYLOAD_SIZE_SIZE = 4
DEFAULT_CLIENT_PAYLOAD_SIZE = -1



# Possible client requests
REQUEST = {
    # REGISTER with the server
    'REGISTER': 1025,
    # SEND_PUBLIC_KEY to the server
    'SEND_PUBLIC_KEY': 1026,
    # LOGIN to server
    'LOGIN': 1027,
    # SEND_FILE to the server
    'SEND_FILE': 1028,
    # CRC is approved by the client, Client-Server caluclated the same CRC
    'CRC_APP': 1029,
    # CRC is denied by the client, Client-Server caluclated different CRC, trying the sequence again (up to  # TIMES total)
    'CRC_DEN_RE': 1030,
    # CRC is denied by the client, Client-Server caluclated different CRC  # TIMES, client give up
    'CRC_DEN_FI': 1031
}
