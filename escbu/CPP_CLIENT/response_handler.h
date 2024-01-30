#ifndef RESPONSE_HANDLER_H
#define RESPONSE_HANDLER_H	


#include <cstdint>
#include "helpers_response.h"
#include <boost/asio.hpp>

class ResponseHandler {

    uint8_t s_version;
    ResponseType opcode;
    uint32_t payload_size;

public:

    ResponseType read_minimum_header(boost::asio::ip::tcp::socket& sock);
    uint8_t get_s_version();
    ResponseType get_opcode();
    uint32_t get_payload();
    void print() const;

};

#endif //RESPONSE_HANDLER_H