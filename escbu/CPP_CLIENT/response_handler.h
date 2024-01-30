#ifndef RESPONSE_HANDLER_H
#define RESPONSE_HANDLER_H	


#include <cstdint>
#include "helpers_response.h"

class ResponseHandler {

    uint8_t s_version;
    ResponseType opcode;
    uint32_t payload_size;

};

#endif //RESPONSE_HANDLER_H