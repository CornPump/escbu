#ifndef HELPERS_RESPONSE_H
#define HELPERS_RESPONSE_H	


#include <cstdint>


enum class ResponseType :uint16_t {

    // First step of registeration succeed (response to 1025)
    REGISTER_S = 1600,
    // First step of registeration failed (response to 1025)
    REGISTER_F = 1601,
    // Second step of registeration succefully received public key sending AES key (response to 1026)
    REGISTER_AES_KEY = 1602,
    // Third step of registeration - server send CRC that client need to check
    CHECK_CRC = 1603,
    // Client finishes CRC sequence either it failed or succeed depdends on number of times tried 
    CRC_SEQ_FINISH = 1604,
    // Login successfully
    LOGIN_S = 1605,
    // Client didn't register or the public key wasn't registered with the server
    LOGIN_F = 1606,
    // General error
    ERROR_F = 1607,
    // Internal error; wrong usage of client app didn't send request to server
    INTERNAL_F = 1


};
#endif //HELPERS_RESPONSE_H