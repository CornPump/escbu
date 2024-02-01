#include "client.h"
#include "operation.h"
#include <fstream>
#include <filesystem>
#include <iostream>
#include <tuple>
#include <boost/asio.hpp>
#include "helpers_request.h"
#include "response_handler.h"
#include <boost/uuid/uuid.hpp>
#include <boost/uuid/uuid_io.hpp>
#include <boost/uuid/uuid_generators.hpp>


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


void Client::print() const{

    std::cout << "(client_id:";
    for (uint8_t byte : this->client_id) {
        std::cout << std::hex << static_cast<int>(byte);
    }
    std::cout << " ,client_version:" << static_cast<int>(this->version) << " ,name:" << this->name << ")" << std::endl;
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

std::vector<uint8_t> Client::append_fixed_size_string_to_message(std::vector<uint8_t>& message, std::string& str) {

    if (str.length() >= NAME_MAX_LENGTH - 1) {

        std::cout << "Name length too big, max allowed length = " << NAME_MAX_LENGTH << std::endl;
        std::vector<uint8_t> empty;
        return empty;
    }

    // pad the string with null terminators so it has const size no matter its original size.

    str.resize(NAME_MAX_LENGTH, '\0');
    ULONG32 nname_size = static_cast<ULONG32>(NAME_MAX_LENGTH);
    nname_size = htonl(nname_size);

    message.insert(message.end(), reinterpret_cast<uint8_t*>(&nname_size),
        reinterpret_cast<uint8_t*>(&nname_size) + sizeof(uint32_t));

    message.insert(message.end(), str.begin(), str.end());

    return message;

}

ResponseType Client::send_request(RequestType opcode) {

    std::vector<uint8_t> tmp_msg = create_basic_header(opcode);
    //std::string nname = this->name;
    std::vector<uint8_t> message = append_fixed_size_string_to_message(tmp_msg, this->name);
    if (message.empty()) {return ResponseType::INTERNAL_F;}
    
    
    // send request, then check what to do after.

    switch (opcode) {
    case RequestType::REGISTER:{
        boost::asio::write(this->get_socket(), boost::asio::buffer(message));
        std::cout << "Sent Request " << static_cast<int>(RequestType::REGISTER) << ":REGISTER" << std::endl;

        ResponseHandler resh;
        resh.read_minimum_header(this->get_socket());
        resh.print();
        ResponseType res = resh.get_opcode();

        // register sequence success, can continue
        if (res == ResponseType::REGISTER_S) {
            
            set_client_id(convert_uuid_from_binary(resh.read_payload(this->get_socket())));
            std::cout << "Received and set uuid" << std::endl;
            this->print();

            //generate RSA pair , create me.info & priv.key files , send request 1026
            //this->start_registration_second_phase();
            

        }

        // register sequence fail, can't continue
        else {

            if (res == ResponseType::REGISTER_F) {          
                std::cout << "Registeration failure due to code: " << static_cast<int>(ResponseType::REGISTER_F) << std::endl;
                return ResponseType::REGISTER_F;
            }
            else { return this->write_general_error_message();}
        
        }
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

ResponseType Client::write_general_error_message() {

    std::cout << "Registeration failure due to general error code: " << static_cast<int>(ResponseType::ERROR_F) << std::endl;
    return ResponseType::ERROR_F;

}

void Client::set_client_id(const std::vector<uint8_t>& client_id) {
    this->client_id = client_id;
}

std::vector<uint8_t> Client::convert_uuid_from_binary(std::vector<uint8_t> uuid_buff) {

    boost::uuids::uuid uuid;
    std::copy(uuid_buff.begin(), uuid_buff.end(), uuid.begin());

    // Convert the UUID to a binary representation
    std::vector<uint8_t> to_ret(uuid.begin(), uuid.end());

    return to_ret;
}

std::string Client::convert_uuid_to_string(std::vector<uint8_t> vec) {

    // Convert the UUID bytes to a string
    std::ostringstream oss;
    for (uint8_t byte : vec) {
        oss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(byte);
    }
    std::string uuid_s = oss.str();

    // Remove hyphens from the string
    uuid_s.erase(std::remove(uuid_s.begin(), uuid_s.end(), '-'), uuid_s.end());

    return uuid_s;
}

/*void Client::start_registration_second_phase() {

    

}*/