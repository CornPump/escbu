#include <string>
#include <iostream>
#include <fstream>
#include <boost/asio.hpp>
#include <filesystem>
#include "helpers_request.h"
#include "base_64_wrapper.h"
#include "aes_wrapper.h"
#include "aes.h"


// Default transfer.info file ; file that represent the info about the client
extern const std::string INFO_FILE = "transfer.info";
extern const std::string ME_FILE = "me.info";
extern const std::string PRIVATE_KEY_FILE = "priv.key";
extern const std::string DEFAULT_HOST = "127.0.0.1";
extern const int DEFAULT_PORT = 1234;
extern const std::string DEFAULT_CLIENT_NAME = "It's always darkest before the dawn";
extern const std::string DEFAULT_FILE_TO_TRANSFER = "test";

void hexify(const unsigned char* buffer, unsigned int length)
{
    std::ios::fmtflags f(std::cout.flags());
    std::cout << std::hex;
    for (size_t i = 0; i < length; i++)
        std::cout << std::setfill('0') << std::setw(2) << (0xFF & buffer[i]) << (((i + 1) % 16 == 0) ? "\n" : " ");
    std::cout << std::endl;
    std::cout.flags(f);
}

long long get_file_size(const std::string& filename) {
    try {
        std::ifstream file(filename, std::ios::binary | std::ios::ate);
        if (!file.is_open()) {
            std::cerr << "Error opening file: " << filename << std::endl;
            return -1;
        }
        else {
            std::streamsize file_size = file.tellg();

            return file_size;
        }
    }
    catch (...) {
        return -1;
    }
}

std::string create_encrypted_file(const std::string& filename, AESWrapper*& aes_wrapper) {


    std::filesystem::path full_path = std::filesystem::current_path() / filename;

    std::string add = filename + "_encrypted.txt";
    std::filesystem::path output_file = std::filesystem::current_path() / add;

    std::string empty;
    std::cout << "file " << full_path.string() << " exist: " << std::filesystem::exists(full_path.string()) << std::endl;
    try {
        std::ifstream infile(full_path.string(), std::ios::binary);
        if (!infile.is_open()) {
            std::cerr << "Error opening file: " << filename << std::endl;
            return empty;
        }

        // Send file content in chunks 
        std::string buffer(1024,'\0');

        while (infile.read(&buffer[0], 1024) || infile.gcount() > 0) {
            buffer.resize(static_cast<size_t>(infile.gcount()));

            std::cout << "bytesRead = " << infile.gcount() << std::endl;
            std::cout << "buffer = " << buffer << std::endl;

            std::string ciphertext = aes_wrapper->encrypt(buffer.c_str(), buffer.length());
            std::cout << "ciphertext = " << ciphertext << std::endl;
            hexify(reinterpret_cast<const unsigned char*>(ciphertext.c_str()), ciphertext.length());
            std::string decrypttext = aes_wrapper->decrypt(ciphertext.c_str(), ciphertext.length());
            std::cout << "Decrypted:" << std::endl << decrypttext << std::endl;



            std::ofstream outfile(output_file, std::ios::binary | std::ios::app);
            if (!outfile.is_open()) {
                std::cerr << "Error opening file for writing: " << filename << std::endl;

                return empty;
            }

            outfile.write(ciphertext.data(), ciphertext.length());


        }

        std::cout << "File encrypted successfully: " << filename << std::endl;
    }
    catch (const std::exception& e) {
        std::cerr << "Error encrypting file: " << e.what() << std::endl;
    }

    return output_file.string();
}


void send_file(const std::string& filename, boost::asio::ip::tcp::socket& socket, uint32_t size) {
    try {
        std::ifstream file(filename, std::ios::binary);
        if (!file.is_open()) {
            std::cerr << "Error opening file: " << filename << std::endl;
            return;
        }

        // Send file content in chunks 
        std::vector<char> buffer(MESSAGE_MAX_LENGTH);

        while (!file.eof()) {
            file.read(buffer.data(), static_cast<std::streamsize>(buffer.size()));
            boost::asio::write(socket, boost::asio::buffer(buffer.data(), file.gcount()));
        }

        std::cout << "File sent successfully: " << filename << std::endl;
    }
    catch (const std::exception& e) {
        std::cerr << "Error sending file: " << e.what() << std::endl;
    }
}

void receive_file(const std::string& filename, boost::asio::ip::tcp::socket& socket, uint32_t size) {
    try {
        std::ofstream file(filename, std::ios::binary);
        if (!file.is_open()) {
            std::cerr << "Error opening file for writing: " << filename << std::endl;
            return;
        }

        std::vector<char> buffer(MESSAGE_MAX_LENGTH);

        std::size_t total_received = 0;
        while (total_received < static_cast<std::size_t>(size)) {

            std::size_t bytes_to_receive = std::min(static_cast<std::size_t>(MESSAGE_MAX_LENGTH),
                static_cast<std::size_t>(size - total_received));
            boost::asio::read(socket, boost::asio::buffer(buffer.data(), bytes_to_receive));
            file.write(buffer.data(), static_cast<std::streamsize>(bytes_to_receive));
            total_received += bytes_to_receive;

        }

        std::cout << "File received successfully: " << filename << std::endl;
    }
    catch (const std::exception& e) {
        std::cerr << "Error receiving file: " << e.what() << std::endl;
    }
}

bool check_file_exist(std::filesystem::path file_path) {

    if (std::filesystem::exists(file_path)) {
        return true;
    }
    return false;

}

void create_info_file(const std::string& file_name, const std::string& host, int port,
    const std::string& client_name, const std::string& file_to_transfer) {

    std::filesystem::path full_path = std::filesystem::current_path() / file_name;

    std::ofstream infoFileStream(full_path);

    if (infoFileStream.is_open()) {

        infoFileStream << host << ":" << port << std::endl;
        infoFileStream << client_name << std::endl;
        infoFileStream << file_to_transfer << std::endl;

        std::cout << "Info file created successfully." << std::endl;
    }
    else {
        std::cerr << "Error: Unable to create info file." << std::endl;
    }
}

void create_me_file(const std::string& name, const std::string& uuid, const std::string& privkey) {

    std::filesystem::path full_path = std::filesystem::current_path() / ME_FILE;

    std::ofstream infoFileStream(full_path);

    if (infoFileStream.is_open()) {

        infoFileStream << name << std::endl;
        infoFileStream << uuid << std::endl;
        infoFileStream << Base64Wrapper::encode(privkey) << std::endl;

        std::cout << "Created " << ME_FILE << " file succefully" << std::endl;
    }
    else {
        std::cout << "Unable to create file: " << ME_FILE << std::endl;
    }

}

void create_privkey_file(const std::string& privkey) {


    std::filesystem::path full_path = std::filesystem::current_path() / PRIVATE_KEY_FILE;

    std::ofstream infoFileStream(full_path);

    if (infoFileStream.is_open()) {

        infoFileStream << Base64Wrapper::encode(privkey) << std::endl;

        std::cout << "Created " << PRIVATE_KEY_FILE << " file succefully" << std::endl;
    }
    else {
        std::cout << "Unable to create file: " << PRIVATE_KEY_FILE << std::endl;
    }
}


void clear(uint8_t message[], int length) {
    for (int i = 0; i < length; i++)
        message[i] = '\0';
}


void printHex(const std::vector<uint8_t>& data) {
    for (const auto& byte : data) {
        std::cout << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(byte);
    }
    std::cout << std::dec << std::endl;
}
