#ifndef CLIENT_H
#define CLIENT_H

#include <vector>
#include <string>
#include <boost/asio.hpp>
#include "helpers_request.h"
#include "helpers_response.h"
#include <filesystem>

class Client {

	std::vector<uint8_t> client_id;
	uint8_t version;
	std::string name;
	boost::asio::io_context io_context;
	std::unique_ptr<boost::asio::ip::tcp::socket> sock;

public:
	Client();
	~Client();
	std::string get_name();
	std::tuple <std::string, std::string> get_socket_params();
	boost::asio::ip::tcp::socket& get_socket();
	ResponseType send_request(RequestType opcode);
	ResponseType send_request(RequestType opcode, std::string public_key);
	ResponseType send_request(RequestType opcode, std::filesystem::path full_path);
	std::vector<uint8_t> create_basic_header(RequestType opcode) const;

};


#endif //CLIENT_H
