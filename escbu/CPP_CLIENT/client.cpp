#include "client.h"
#include "operation.h"
#include <fstream>
#include <filesystem>
#include <iostream>
#include <tuple>
#include <boost/asio.hpp>
#include "helpers_request.h"
#include "response_handler.h"
#include "base_64_wrapper.h"
#include "rsa_wrapper.h"
#include <boost/uuid/uuid.hpp>
#include <boost/uuid/uuid_io.hpp>
#include <boost/uuid/uuid_generators.hpp>
#include "aes_wrapper.h"
#include "cksum.h"
#include "cstdio"
#include <bitset>


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
    delete aes_ptr;

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

    if (line.length() >= NAME_MAX_LENGTH - 1) {

        std::cout << "Name length too big, max allowed length = " << NAME_MAX_LENGTH << std::endl;
        exit(1);
    }

    return line;
    
}

std::vector<uint8_t> Client::get_client_id() {
 
    std::filesystem::path full_path = std::filesystem::current_path() / ME_FILE;

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

    if (line.length() >= NAME_MAX_LENGTH - 1) {

        std::cout << "Name length too big, max allowed length = " << NAME_MAX_LENGTH << std::endl;
        exit(1);
    }

    std::vector<uint8_t> vec = hex_string_to_bytes(line);

    return vec;

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

std::string get_transfer_file_name() {

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
        std::getline(infile, line);
    }

    // Close the file
    infile.close();

    if (line.length() >= NAME_MAX_LENGTH - 1) {

        std::cout << "Name length too big, max allowed length = " << NAME_MAX_LENGTH << std::endl;
        exit(1);
    }

    return line;

}


boost::asio::ip::tcp::socket& Client::get_socket() {
    return *sock;
}

void Client::set_aes_wrapper(AESWrapper* aes_wrapper) {

    this->aes_ptr = aes_wrapper;

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

std::vector<uint8_t> Client::append_name_to_message(std::vector<uint8_t>& message, std::string& str) {

    if (str.length() > NAME_MAX_LENGTH && str.back() != '\0') {

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

        
    // send request, then check what to do after.

    switch (opcode) {
    case RequestType::REGISTER:{

        std::vector<uint8_t> tmp_msg = create_basic_header(opcode);
        std::vector<uint8_t> message = append_name_to_message(tmp_msg, this->name);
        if (message.empty()) { return ResponseType::INTERNAL_F; }

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
            ResponseType res2 = this->start_registration_second_phase();

            if (res2 == ResponseType::REGISTER_AES_KEY) {

                ResponseType res3 = this->send_file_sequence();

                if (res3 == ResponseType::CRC_SEQ_FINISH_S) {

                    std::cout << "File sent succefully!" << std::endl;
                    return res3;

                }

                if (res3 == ResponseType::CRC_SEQ_FINISH_F) {

                    std::cout << "Server couldn't encrypt the file, sending file operation failed." << std::endl;
                    return res3;

                }

                else { return this->write_general_error_message(res3); }
            }
            else { return this->write_general_error_message(res2); }

        }

        // register sequence fail, can't continue
        else {

            if (res == ResponseType::REGISTER_F) {          
                std::cout << "Registeration failure due to code: " << static_cast<int>(ResponseType::REGISTER_F) << std::endl;
                return ResponseType::REGISTER_F;
            }
            else { return this->write_general_error_message(res);}
        
        }
        break;

    }

    case RequestType::LOGIN: {

        this->set_client_id(this->get_client_id());
        std::vector<uint8_t> tmp_msg = create_basic_header(opcode);
        std::vector<uint8_t> message = append_name_to_message(tmp_msg, this->name);
        if (message.empty()) { return ResponseType::INTERNAL_F; }
        boost::asio::write(this->get_socket(), boost::asio::buffer(message));
        std::cout << "Sent Request "<< static_cast<int>(RequestType::LOGIN) << ":LOGIN" << std::endl;
        ResponseHandler resh;
        resh.read_minimum_header(this->get_socket());
        resh.print();
        ResponseType res = resh.get_opcode();
        if (res == ResponseType::LOGIN_S) {
            
            bool aes_success = start_loging_second_phase(resh);
            if (aes_success) {

                ResponseType res3 = this->send_file_sequence();

                if (res3 == ResponseType::CRC_SEQ_FINISH_S) {

                    std::cout << "File sent succefully!" << std::endl;
                    return res3;

                }

                if (res3 == ResponseType::CRC_SEQ_FINISH_F) {

                    std::cout << "Server couldn't encrypt the file, sending file operation failed." << std::endl;
                    return res3;

                }

                else { return this->write_general_error_message(res3); }
            }
            else { return this->write_general_error_message(ResponseType::INTERNAL_F); }

        
        }
        else {
        
            if (res == ResponseType::LOGIN_F) {
                std::cout << "Registeration failure due to code: " << static_cast<int>(ResponseType::LOGIN_F) <<
                    ":LOGIN_F" <<std::endl;
                return ResponseType::LOGIN_F;
            }
            else { return this->write_general_error_message(res); }

        }
        break;
    }

    default:
        return ResponseType::INTERNAL_F;
    }
}


ResponseType Client::write_general_error_message(ResponseType res) {
    if (res == ResponseType::ERROR_F) {
        std::cout << "Registeration failure due to server general error code: " << static_cast<int>(ResponseType::ERROR_F) << std::endl;
    }

    if (res == ResponseType::INTERNAL_F) {
        std::cout << "Registeration failure due to inernal error code: " << static_cast<int>(ResponseType::INTERNAL_F) << std::endl;
    }

    return res;

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


std::string Client::get_private_key() {

    std::filesystem::path full_path = std::filesystem::current_path() / PRIVATE_KEY_FILE;

    std::ifstream infile(full_path.string());

    std::string line;

    if (!infile.is_open()) {
        std::cout << "Unable to open the file" << std::endl;
    }

    std::stringstream buffer;
    while (std::getline(infile, line)) {
        buffer << line;
    }

    return buffer.str();

}

bool Client::start_loging_second_phase(ResponseHandler &resh) {

    try {
        std::cout << "Received AES_key, decrypting it using private_key" << std::endl;
        std::vector<uint8_t> payload = resh.read_payload(this->get_socket());
        std::vector<uint8_t> aes_key = { payload.begin() + DEFAULT_CLIENT_ID_SIZE, payload.end() };

        // Convert to std::string
        std::string str_aes_key(aes_key.begin(), aes_key.end());
        const unsigned char* aes_key_ = reinterpret_cast<const unsigned char*>(str_aes_key.data());

        std::string p_key_64 = this->get_private_key();
        std::string p_key = Base64Wrapper::decode(p_key_64);
        RSAPrivateWrapper privateWrapper(p_key);
        std::string decrypted_aes_key = privateWrapper.decrypt(str_aes_key);
        const unsigned char* aes_key_final = reinterpret_cast<const unsigned char*>(decrypted_aes_key.data());

        // Create an AESWrapper with the provided key
        AESWrapper* aes = new AESWrapper(aes_key_final, AESWrapper::DEFAULT_KEYLENGTH);

        // set aes_wrapper param on client
        this->set_aes_wrapper(aes);
        return true;
    }

    catch (const std::exception& e) {
        std::cerr << "Error opening file: " << e.what() << std::endl;
        return false;
    }
}


ResponseType Client::start_registration_second_phase() {

    // Create RSA key pair
    std::cout << "Creating RSA key pair.." << std::endl;
    RSAPrivateWrapper privateWrapper;
    RSAPublicWrapper publicWrapper(privateWrapper.getPublicKey());

    // Get the public and private keys
    std::string publicKey = publicWrapper.getPublicKey();
    std::string privateKey = privateWrapper.getPrivateKey();

    std::string codedpublickey = Base64Wrapper::encode(publicKey);

    // Create me.info and privkey files
    create_me_file(this->name, convert_uuid_to_string(this->client_id), privateKey);
    create_privkey_file(privateKey);

    // send public key request
    std::vector<uint8_t> message = create_basic_header(RequestType::SEND_PUBLIC_KEY);

    ULONG32 payload_size = static_cast<ULONG32>(NAME_MAX_LENGTH + PUBLIC_KEY_SIZE);
    payload_size = htonl(payload_size);
    message.insert(message.end(), reinterpret_cast<uint8_t*>(&payload_size),
        reinterpret_cast<uint8_t*>(&payload_size) + sizeof(uint32_t));

    message.insert(message.end(), this->name.begin(), this->name.end());

    if (message.empty()) { return ResponseType::INTERNAL_F; }
    message.insert(message.end(), publicKey.begin(), publicKey.end());

    boost::asio::write(this->get_socket(), boost::asio::buffer(message));
    std::cout << "Sent Request " << std::dec <<static_cast<int>(RequestType::SEND_PUBLIC_KEY) << ":SEND_PUBLIC_KEY" << std::endl;

    // receive response
    ResponseHandler resh;
    resh.read_minimum_header(this->get_socket());
    resh.print();
    ResponseType res = resh.get_opcode();

    // if success response receive AES key from server decrypt it using private RSA key
    if (res == ResponseType::REGISTER_AES_KEY) {
        
        std::cout << "Received AES_key, decrypting it using private_key" << std::endl;
        std::vector<uint8_t> payload = resh.read_payload(this->get_socket());
        std::vector<uint8_t> aes_key = { payload.begin() + DEFAULT_CLIENT_ID_SIZE, payload.end() };

      // Convert to std::string
        std::string str_aes_key(aes_key.begin(), aes_key.end());
        const unsigned char* aes_key_ = reinterpret_cast<const unsigned char*>(str_aes_key.data());
       
        std::string decrypted_aes_key = privateWrapper.decrypt(str_aes_key);
        const unsigned char* aes_key_final = reinterpret_cast<const unsigned char*>(decrypted_aes_key.data());

        // Create an AESWrapper with the provided key
        AESWrapper* aes = new AESWrapper(aes_key_final, AESWrapper::DEFAULT_KEYLENGTH);

        // set aes_wrapper param on client
        this->set_aes_wrapper(aes);


        return ResponseType::REGISTER_AES_KEY;
    }

    else { return ResponseType::ERROR_F; }

}

bool Client::send_my_file() {

    std::string encrypted_file = create_encrypted_file(get_transfer_file_name(), this->aes_ptr);

    std::tuple<uint32_t, uint32_t> tup = check_sum(get_transfer_file_name());
    uint32_t cksum = std::get<0>(tup);
    uint32_t orig_file_size = std::get<1>(tup);
    //std::cout << "check_sum_original:" << cksum << std::endl;
    std::tuple<uint32_t, uint32_t> tup2 = check_sum(encrypted_file);
    uint32_t cksum_enc = std::get<0>(tup2);
    uint32_t enc_file_size = std::get<1>(tup2);
    //std::cout << "check_sum_encrypted:" << cksum_enc << std::endl;


    std::string padded_original_file_name = get_transfer_file_name();
    padded_original_file_name.resize(NAME_MAX_LENGTH, '\0');

    int header_size = DEFAULT_CLIENT_ID_SIZE + DEFAULT_CLIENT_VERSION_SIZE + DEFAULT_CLIENT_CODE_SIZE +
        DEFAULT_CLIENT_PAYLOAD_SIZE_SIZE + DEFAULT_CONTENT_SIZE + DEFAULT_ORG_FILE_SIZE +
        DEFAULT_PACKET_NUMBER_SIZE + DEFAULT_TOTAL_PACKET_SIZE + NAME_MAX_LENGTH;

    uint16_t number_of_packets = std::ceil(enc_file_size / static_cast<float>(MESSAGE_MAX_LENGTH));

    try {
        std::ifstream infile(encrypted_file, std::ios::binary);
        if (!infile.is_open()) {
            std::cerr << "Error opening file: " << encrypted_file << std::endl;
            return false;
        }

        // Send file content in chunks 
        uint16_t cur_packet_num = 1;
        std::string buffer(MESSAGE_MAX_LENGTH, '\0');

        while (infile.read(&buffer[0], MESSAGE_MAX_LENGTH) || infile.gcount() > 0) {
            buffer.resize(static_cast<size_t>(infile.gcount()));

            // creating the Request header
            std::vector<uint8_t> message = create_basic_header(RequestType::SEND_FILE);

            uint32_t payload_size = header_size + static_cast<size_t>(infile.gcount()) - DEFAULT_CLIENT_ID_SIZE
                - DEFAULT_CLIENT_VERSION_SIZE - DEFAULT_CLIENT_CODE_SIZE - DEFAULT_CLIENT_PAYLOAD_SIZE_SIZE;

            //std::cout << "payload_size:" << payload_size << std::endl;
            payload_size = htonl(payload_size);
            message.insert(message.end(), reinterpret_cast<uint8_t*>(&payload_size),
                reinterpret_cast<uint8_t*>(&payload_size) + sizeof(uint32_t));

            //std::cout << "encrypted_file_size:" << enc_file_size << std::endl;
            enc_file_size = htonl(enc_file_size);
            message.insert(message.end(), reinterpret_cast<uint8_t*>(&enc_file_size),
                reinterpret_cast<uint8_t*>(&enc_file_size) + sizeof(uint32_t));

            //std::cout << "orig_file_size:" << orig_file_size << std::endl;
            orig_file_size = htonl(orig_file_size);
            message.insert(message.end(), reinterpret_cast<uint8_t*>(&orig_file_size),
                reinterpret_cast<uint8_t*>(&orig_file_size) + sizeof(uint32_t));

            //std::cout << "cur_packet_num:" << cur_packet_num << std::endl;
            cur_packet_num = htons(cur_packet_num);
            message.insert(message.end(), reinterpret_cast<uint8_t*>(&cur_packet_num),
                reinterpret_cast<uint8_t*>(&cur_packet_num) + sizeof(uint16_t));

            //std::cout << "number_of_packets:" << number_of_packets << std::endl;
            number_of_packets = htons(number_of_packets);
            message.insert(message.end(), reinterpret_cast<uint8_t*>(&number_of_packets),
                reinterpret_cast<uint8_t*>(&number_of_packets) + sizeof(uint16_t));


            message.insert(message.end(), padded_original_file_name.begin(), padded_original_file_name.end());
            //std::cout << "padded_original_file_name:" << padded_original_file_name << std::endl;

            message.insert(message.end(), buffer.begin(), buffer.end());

            boost::asio::write(this->get_socket(), boost::asio::buffer(message));
            //std::cout << "Sent Request " << static_cast<int>(RequestType::SEND_FILE) << ":SEND_FILE" << std::endl;
            cur_packet_num++;
        }

    }
    catch (const std::exception& e) {
        std::cerr << "Error opening file: " << e.what() << std::endl;
        return false;
    }



    std::remove(encrypted_file.c_str());

}

ResponseType Client::send_file_sequence() {
      
    bool is_send_file_succed = send_my_file();

    if (!is_send_file_succed) { return ResponseType::INTERNAL_F; }
        


    
        for (int i = 1; i <= TIMES; i++) {
            ResponseHandler resh;
            resh.read_minimum_header(this->get_socket());
            resh.print();
            ResponseType res = resh.get_opcode();
            if (res == ResponseType::CHECK_CRC) {
                bool valid = is_checksum_valid(resh);
                if (valid) {
                
                    std::cout << "CRC Approved by user-server handshake, sending code:"
                        << static_cast<int>(RequestType::CRC_APP) << ":CRC_APP" << std::endl;

                    std::vector<uint8_t> tmp_msg = create_basic_header(RequestType::CRC_APP);
                    std::string file = get_transfer_file_name();
                    std::vector<uint8_t> msg = append_name_to_message(tmp_msg, file);
                    boost::asio::write(this->get_socket(), boost::asio::buffer(msg));

              
                    return ResponseType::CRC_SEQ_FINISH_S; }
                else { 
                
                    if (i < TIMES){
                        std::cout << "CRC denied #" << i + 1 << " by user-server handshake,trying again sending code:"
                            << static_cast<int>(RequestType::CRC_DEN_RE) << ":CRC_DEN_RE" << std::endl;
                    
                        std::vector<uint8_t> tmp_msg = create_basic_header(RequestType::CRC_DEN_RE);
                        std::string file = get_transfer_file_name();
                        std::vector<uint8_t> msg = append_name_to_message(tmp_msg, file);
                        boost::asio::write(this->get_socket(), boost::asio::buffer(msg));
                        bool is_send_file_succed = send_my_file();

                        if (!is_send_file_succed) { return ResponseType::INTERNAL_F; }
                    
                    }
                    // if i == TIMES
                    else {
                        std::cout << "[FATAL] CRC denied by user-server handshake too many times #" << TIMES << ", sending code:"
                            << static_cast<int>(RequestType::CRC_DEN_FI) << ":CRC_DEN_FI" << std::endl;

                        std::vector<uint8_t> tmp_msg = create_basic_header(RequestType::CRC_DEN_FI);
                        std::string file = get_transfer_file_name();
                        std::vector<uint8_t> msg = append_name_to_message(tmp_msg, file);
                        boost::asio::write(this->get_socket(), boost::asio::buffer(msg));

                        std::cout << "Reading [FATAL] acceptance Response from server";
                        ResponseHandler resh5;
                        resh5.read_minimum_header(this->get_socket());
                        std::vector<uint8_t> payload = resh5.read_payload(this->get_socket());
                        std::cout << " Received Response:" << static_cast<int>(resh5.get_opcode()) << std::endl;
                    
                        return ResponseType::CRC_SEQ_FINISH_F;
                    }
                
                }
            
            }   
            else { return ResponseType::ERROR_F; }
    }

    
}

bool Client::is_checksum_valid(ResponseHandler& resh) {
    
    std::vector<uint8_t> payload = resh.read_payload(this->get_socket());
    int adder = 0;

    std::string client_id = { payload.begin() , payload.begin() + DEFAULT_CLIENT_ID_SIZE };
    adder += DEFAULT_CLIENT_ID_SIZE;

    uint32_t encrypted_file_size = 0;
    std::copy(payload.begin() + adder, payload.begin() + adder + DEFAULT_ECNRYPTED_CONTENT_SIZE,
        reinterpret_cast<uint8_t*>(&encrypted_file_size));
    adder += DEFAULT_ECNRYPTED_CONTENT_SIZE;
    encrypted_file_size = htonl(encrypted_file_size);
    //std::cout << "encrypted_file_size:" << encrypted_file_size << std::endl;

    std::string file_name(payload.begin() + adder, payload.begin() + adder + NAME_MAX_LENGTH);
    adder += NAME_MAX_LENGTH;
    //std::cout << "file_name:" << file_name << std::endl;

    uint32_t server_checksum = 0;
    std::copy(payload.begin() + adder, payload.end(),
        reinterpret_cast<uint8_t*>(&server_checksum));
    server_checksum = htonl(server_checksum);
    //std::cout << "server_checksum:" << server_checksum << std::endl;

    std::tuple<uint32_t, uint32_t> tup = check_sum(get_transfer_file_name());
    uint32_t cksum = std::get<0>(tup);
    
    if (server_checksum == cksum) { return true; }
    else { return false; }


}