#include "response_handler.h"
#include "helpers_response.h"
#include <iostream>
#include "helpers_request.h"
#include "operation.h"



void ResponseHandler::print() const {

    std::cout << "(c_version:" << static_cast<int>(this->s_version) <<
        " ,opcode:" << static_cast<int>(this->opcode) 
        << " ,payload_size:" << this->payload_size   << ")" << std::endl;
}


ResponseType ResponseHandler::read_minimum_header(boost::asio::ip::tcp::socket& sock) {

    uint8_t data[MESSAGE_MAX_LENGTH];
    clear(data, MESSAGE_MAX_LENGTH);
    try {
        boost::asio::read(sock, boost::asio::buffer(data, MIN_RESPONSE_SIZE));
    }
    // If error or time out send client error message and retorn 0

    catch (const boost::system::system_error& e) {
        std::cerr << "Boost.Asio read error: " << e.what() << std::endl;
    }
    /*catch (...) {
        std::cout << "Error in reading minimum header" << std::endl;
        return ResponseType::INTERNAL_F;

    }*/
    // if no error fetch minimum header
    
    std::memcpy(&this->s_version, data, sizeof(uint8_t));
    std::memcpy(&this->opcode, data + sizeof(uint8_t), sizeof(uint16_t));
    this->opcode = static_cast<ResponseType>(htons(static_cast<uint16_t>(this->opcode)));
    std::memcpy(&this->payload_size, data + sizeof(uint8_t) + sizeof(uint16_t), sizeof(uint32_t));
    this->payload_size = htonl(this->payload_size);
    return this->opcode;

}


uint8_t ResponseHandler::get_s_version() {

	return this->s_version;
}
ResponseType ResponseHandler::get_opcode() {

	return this->opcode;

}
uint32_t ResponseHandler::get_payload() {

    return this->payload_size;

}