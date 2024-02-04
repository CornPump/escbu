#ifndef HELPERS_REQUEST_H
#define HELPERS_REQUEST_H	

#include <string.h>
#include <cstdint>

// Max LENGTHS FOR VARIOUS THINGS
const int MESSAGE_MAX_LENGTH = 1024;
const size_t NAME_MAX_LENGTH = 255;
const size_t PUBLIC_KEY_SIZE = 160;

// Basic and minimal header's params for request, this table represents their size, -1 = unlimited
const int DEFAULT_CLIENT_ID_SIZE = 16;
const int DEFAULT_CLIENT_VERSION_SIZE = 1;
const int DEFAULT_CLIENT_CODE_SIZE = 2;
const int DEFAULT_CLIENT_PAYLOAD_SIZE_SIZE = 4;
const int DEFAULT_CLIENT_PAYLOAD_SIZE = -1;


// Default values to request header
const std::string DEFAULT_CLIENT_ID(16, '\x00');
const uint8_t CLIENT_VERSION = 3;


// How many times to try for checksum for CRC
const int TIMES = 4;

// Request codes
enum class RequestType :uint16_t {

    // REGISTER with the server
    REGISTER = 1025,
    // SEND_PUBLIC_KEY to the server
    SEND_PUBLIC_KEY = 1026,
    // LOGIN to server
    LOGIN = 1027,
    // SEND_FILE to the server
    SEND_FILE = 1028,
    // CRC is approved by the client, Client-Server caluclated the same CRC
    CRC_APP = 1029,
    // CRC is denied by the client, Client-Server caluclated different CRC, trying the sequence again (up to #TIMES total)
    CRC_DEN_RE = 1030,
    // CRC is denied by the client, Client-Server caluclated different CRC #TIMES, client give up 
    CRC_DEN_FI = 1031
};


#endif //HELPERS_REQUEST_H