#include "client.h"
#include "operation.h"
#include <fstream>
#include <filesystem>
#include <iostream>
#include <tuple>
#include <boost/asio.hpp>
#include "helpers_request.h"
#include "response_handler.h"


Client::Client() {
	
	version = CLIENT_VERSION;
    name = this->get_name();
    client_id.assign(DEFAULT_CLIENT_ID.begin(), DEFAULT_CLIENT_ID.end());

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

std::vector<uint8_t> Client::create_basic_header(RequestType opcode) const {

    std::vector<uint8_t> message;

    message.insert(message.end(), this->client_id.begin(), this->client_id.end()); 
    message.push_back(this->version);
    
    uint16_t value = static_cast<uint16_t>(opcode);
    value = htons(value);
    message.insert(message.end(), reinterpret_cast<uint8_t*>(&value),
        reinterpret_cast<uint8_t*>(&value) + sizeof(uint16_t));

    return message;

}

ResponseType Client::send_request(RequestType opcode) {

    std::vector<uint8_t> message = create_basic_header(opcode);
    std::string nname = this->name;

    if (nname.length() >= NAME_MAX_LENGTH - 1) {

        std::cout << "Name length too big, max allowed length = " << NAME_MAX_LENGTH << std::endl;
        return ResponseType::INTERNAL_F;
    }

    // pad the string with null terminators so it has const size no matter its original size.
       
    nname.resize(NAME_MAX_LENGTH, '\0');
    ULONG32 nname_size = static_cast<ULONG32>(NAME_MAX_LENGTH);
    nname_size = htonl(nname_size);

    message.insert(message.end(), reinterpret_cast<uint8_t*>(&nname_size),
        reinterpret_cast<uint8_t*>(&nname_size) + sizeof(uint32_t));

    message.insert(message.end(), nname.begin(), nname.end());
    
    // send request, then check what to do after.

    switch (opcode) {
    case RequestType::REGISTER:{
        boost::asio::write(this->get_socket(), boost::asio::buffer(message));
        std::cout << "Sent Request " << static_cast<int>(RequestType::REGISTER) << ":REGISTER" << std::endl;

        ResponseHandler resh;
        resh.read_minimum_header(this->get_socket());
        resh.print();
        break;

    }

    case RequestType::LOGIN: {
    
        boost::asio::write(this->get_socket(), boost::asio::buffer(message));
        std::cout << "Sent Request "<< static_cast<int>(RequestType::LOGIN) << ":Login" << std::endl;
        break;
    }

    default:
        return ResponseType::INTERNAL_F;
    }
}

ResponseType Client::send_request(RequestType opcode, std::string public_key) {

    std::vector<uint8_t> message = create_basic_header(opcode);

    switch (opcode) {
    case RequestType::SEND_PUBLIC_KEY:
    default:
        return ResponseType::INTERNAL_F;
    }
}

ResponseType Client::send_request(RequestType opcode, std::filesystem::path full_path) {

    std::vector<uint8_t> message = create_basic_header(opcode);

    switch (opcode) {
    case RequestType::CRC_APP:
    case RequestType::CRC_DEN_RE:
    case RequestType::CRC_DEN_FI:
    case RequestType::SEND_FILE:
    default:
        return ResponseType::INTERNAL_F;
    }

}