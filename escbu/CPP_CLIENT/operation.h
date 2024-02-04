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
void create_me_file(const std::string& name, const std::string& uuid, const std::string& privkey);
void create_privkey_file(const std::string& privkey);
void clear(uint8_t message[], int length);
void hexify(const unsigned char* buffer, unsigned int length);
void printHex(const std::vector<uint8_t>& data);

// Default transfer.info file ; file that represent the info about the client
extern const std::string INFO_FILE;
// Default ME.info file ; file that saves privkey data and uuid data
extern const std::string ME_FILE;
// Default ME.info file ; file that saves privkey data 
extern const std::string PRIVATE_KEY_FILE;
extern const std::string DEFAULT_HOST;
extern const int DEFAULT_PORT;
extern const std::string DEFAULT_CLIENT_NAME;
extern const std::string DEFAULT_FILE_TO_TRANSFER;

#endif // OPERATION_H