#include <string>
#include <iostream>
#include <fstream>
#include <boost/asio.hpp>
#include <filesystem>
#include "helpers_request.h"


// Default transfer.info file ; file that represent the info about the client
extern const std::string INFO_FILE = "transfer.info";
extern const std::string DEFAULT_HOST = "127.0.0.1";
extern const int DEFAULT_PORT = 1234;
extern const std::string DEFAULT_CLIENT_NAME = "It's always darkest before the dawn";
extern const std::string DEFAULT_FILE_TO_TRANSFER = "test.txt";



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

    std::cout << full_path.string();
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
