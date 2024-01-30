#ifndef OPERATION_H
#define OPERATION_H

#include <boost/asio.hpp>
#include <filesystem>


long long get_file_size(const std::string& filename);
void send_file(const std::string& filename, boost::asio::ip::tcp::socket& socket, uint32_t size);
void receive_file(const std::string& filename, boost::asio::ip::tcp::socket& socket, uint32_t size);
bool check_file_exist(std::filesystem::path file_path);
void create_info_file(const std::string& file_name, const std::string& host, int port,
						const std::string& client_name, const std::string& file_to_transfer);
void clear(uint8_t message[], int length);

// Default transfer.info file ; file that represent the info about the client
extern const std::string INFO_FILE;
extern const std::string DEFAULT_HOST;
extern const int DEFAULT_PORT;
extern const std::string DEFAULT_CLIENT_NAME;
extern const std::string DEFAULT_FILE_TO_TRANSFER;

#endif // OPERATION_H