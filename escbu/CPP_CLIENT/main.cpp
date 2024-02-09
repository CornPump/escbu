#include "base_64_wrapper.h"
#include "rsa_wrapper.h"
#include "aes_wrapper.h"
#include <boost/asio.hpp>
#include <iostream>
#include <iomanip>
#include "operation.h"
#include "client.h"
#include "helpers_request.h"


using boost::asio::ip::tcp;


int main()
{
	try{
		Client client;
		ResponseType response = client.send_request(RequestType::REGISTER);
		//ResponseType response2 = client.send_request(RequestType::LOGIN);

	}
	catch (const std::exception& e) {
		std::cerr << "Exception in main in creating client: " << e.what() << std::endl;
	}
	
	
	return 0;
}
