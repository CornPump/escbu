#ifndef CLIENT_H
#define CLIENT_H

#include <vector>
#include <string>
#include <boost/asio.hpp>


const uint8_t CLIENT_VERSION = 3;

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
	std::tuple<std::string, std::string> get_socket_params();
	boost::asio::ip::tcp::socket& get_socket();

};


#endif //CLIENT_H
