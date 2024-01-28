#include "client.h"
#include "operation.h"
#include <fstream>
#include <filesystem>
#include <iostream>
#include <tuple>
#include <boost/asio.hpp>
#include "helpers_request.h"



Client::Client() {
	
	version = CLIENT_VERSION;
    name = this->get_name();

    if (name.empty()) {

        throw std::runtime_error("can't create Client instance due to problem with \
            extracting name from transfer.info file");

    }

    std::tuple<std::string, std::string> tup = this->get_socket_params();

    if (std::get<0>(tup).empty() or std::get<1>(tup).empty()) {

        throw std::runtime_error("can't create Client instance due to problem with \
            extracting host or port from transfer.info file");
        
    }

    sock = std::make_unique<boost::asio::ip::tcp::socket>(io_context);
    boost::asio::ip::tcp::resolver resolver(io_context);
    boost::asio::connect(*sock, resolver.resolve(std::get<0>(tup), std::get<1>(tup)));

}

Client::~Client() {

    sock->close();

}


std::string Client::get_name() {

	std::filesystem::path full_path = std::filesystem::current_path() / INFO_FILE;

    std::ifstream infile(full_path.string());

    std::string line;

    if (!infile.is_open()) {
        std::cout << "Unable to open the file" << std::endl;
    }

    // get name line
    else {
    std::getline(infile, line);
    std::getline(infile, line);
    } 

    // Close the file
    infile.close();

    return line;
    
}

std::tuple<std::string, std::string> Client::get_socket_params() {

    std::filesystem::path full_path = std::filesystem::current_path() / INFO_FILE;

    std::ifstream infile(full_path.string());

    std::tuple<std::string, std::string> tup = std::make_tuple("", "");

    if (!infile.is_open()) {
        std::cout << "Unable to open the file" << std::endl;
    }

    // get name line
    else {
        
        std::string line;
        std::getline(infile, line);

        std::istringstream iss(line);

        std::getline(iss, std::get<0>(tup), ':');
        iss >> std::get<1>(tup);
        
    }

    // Close the file
    infile.close();

    return tup;

}

boost::asio::ip::tcp::socket& Client::get_socket() {
    return *sock;
}

ResponseType Client::send_request(RequestType opcode, std::string name) {

    switch (opcode) {
    case RequestType::REGISTER:
    case RequestType::LOGIN:
    default:
        return ResponseType::INTERNAL_F;
    }
}

ResponseType Client::send_request(RequestType opcode, std::string name, std::string public_key) {

    switch (opcode) {
    case RequestType::SEND_PUBLIC_KEY:
    default:
        return ResponseType::INTERNAL_F;
    }
}

ResponseType Client::send_request(RequestType opcode, std::filesystem::path full_path) {

    switch (opcode) {
    case RequestType::CRC_APP:
    case RequestType::CRC_DEN_RE:
    case RequestType::CRC_DEN_FI:
    case RequestType::SEND_FILE:
    default:
        return ResponseType::INTERNAL_F;
    }

}