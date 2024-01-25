#ifndef OPERATION_H
#define OPERATION_H

#include <boost/asio.hpp>



long long get_file_size(const std::string& filename);
void send_file(const std::string& filename, boost::asio::ip::tcp::socket& socket, uint32_t size);
void receive_file(const std::string& filename, boost::asio::ip::tcp::socket& socket, uint32_t size);
bool check_file_exist(std::filesystem::path file_path);

#endif // OPERATION_H