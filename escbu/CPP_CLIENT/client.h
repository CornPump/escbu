#ifndef CLIENT_H
#define CLIENT_H

#include <vector>
#include <string>
#include <boost/asio.hpp>
#include "helpers_request.h"
#include "helpers_response.h"
#include <filesystem>
#include "aes_wrapper.h"

class Client {

	std::vector<uint8_t> client_id;
	uint8_t version;
	std::string name;
	boost::asio::io_context io_context;
	std::unique_ptr<boost::asio::ip::tcp::socket> sock;
	AESWrapper* aes_ptr;

	ResponseType write_general_error_message();
	std::vector<uint8_t> convert_uuid_from_binary(std::vector<uint8_t> uuid_buff);
	std::string convert_uuid_to_string(std::vector<uint8_t> vec);
	std::vector<uint8_t> append_name_to_message(std::vector<uint8_t>& message, std::string& str);
	ResponseType start_registration_second_phase();
	void set_aes_wrapper(AESWrapper* aes_wrapper);
	

public:
	Client();
	~Client();
	void print() const;
	std::string get_name();
	std::tuple <std::string, std::string> get_socket_params();
	boost::asio::ip::tcp::socket& get_socket();
	void set_client_id(const std::vector<uint8_t>& client_id);
	ResponseType send_request(RequestType opcode);
	ResponseType send_request(RequestType opcode, std::string public_key);
	ResponseType send_request(RequestType opcode, std::filesystem::path full_path);
	std::vector<uint8_t> create_basic_header(RequestType opcode) const;

};


#endif //CLIENT_H
