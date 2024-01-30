#include "response_handler.h"
#include "helpers_response.h"
#include <iostream>


ResponseType ResponseHandler::read_minimum_header(boost::asio::ip::tcp::socket& sock) {

	std::cout << "no compiler crying";

}


uint8_t ResponseHandler::get_s_version() {

	return this->s_version;
}
ResponseType ResponseHandler::get_opcode() {

	return this->opcode;

}
uint32_t ResponseHandler::get_payload() {

	return this->payload_size

}