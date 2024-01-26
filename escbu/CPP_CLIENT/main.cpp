#include "base_64_wrapper.h"
#include "rsa_wrapper.h"
#include "aes_wrapper.h"
#include <boost/asio.hpp>
#include <iostream>
#include <iomanip>
#include "operation.h"
#include "client.h"


using boost::asio::ip::tcp;

void hexify(const unsigned char* buffer, unsigned int length)
{
	std::ios::fmtflags f(std::cout.flags());
	std::cout << std::hex;
	for (size_t i = 0; i < length; i++)
		std::cout << std::setfill('0') << std::setw(2) << (0xFF & buffer[i]) << (((i + 1) % 16 == 0) ? "\n" : " ");
	std::cout << std::endl;
	std::cout.flags(f);
}


int aes_example()
{
	std::cout << std::endl << std::endl << "----- AES EXAMPLE -----" << std::endl << std::endl;

	std::string plaintext = "Once upon a time, a plain text dreamed to become a cipher";
	std::cout << "Plain:" << std::endl << plaintext << std::endl;

	// 1. Generate a key and initialize an AESWrapper. You can also create AESWrapper with default constructor which will automatically generates a random key.
	unsigned char key[AESWrapper::DEFAULT_KEYLENGTH];
	AESWrapper aes(AESWrapper::GenerateKey(key, AESWrapper::DEFAULT_KEYLENGTH), AESWrapper::DEFAULT_KEYLENGTH);

	// 2. encrypt a message (plain text)
	std::string ciphertext = aes.encrypt(plaintext.c_str(), plaintext.length());
	std::cout << "Cipher:" << std::endl;
	hexify(reinterpret_cast<const unsigned char*>(ciphertext.c_str()), ciphertext.length());	// print binary data nicely

	// 3. decrypt a message (cipher text)
	std::string decrypttext = aes.decrypt(ciphertext.c_str(), ciphertext.length());
	std::cout << "Decrypted:" << std::endl << decrypttext << std::endl;

	return 0;
}


int rsa_example()
{
	std::cout << std::endl << std::endl << "----- RSA EXAMPLE -----" << std::endl << std::endl;

	// plain text (could be binary data as well)
	unsigned char plain[] = { 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF };
	std::cout << "plain:" << std::endl;
	hexify(plain, sizeof(plain));		// print binary data nicely

	// 1. Create an RSA decryptor. this is done here to generate a new private/public key pair
	RSAPrivateWrapper rsapriv;

	// 2. get the public key
	std::string pubkey = rsapriv.getPublicKey();	// you can get it as std::string ...

	char pubkeybuff[RSAPublicWrapper::KEYSIZE];
	rsapriv.getPublicKey(pubkeybuff, RSAPublicWrapper::KEYSIZE);	// ...or as a char* buffer

	// 3. create an RSA encryptor
	RSAPublicWrapper rsapub(pubkey);
	std::string cipher = rsapub.encrypt((const char*)plain, sizeof(plain));	// you can encrypt a const char* or an std::string 
	std::cout << "cipher:" << std::endl;
	hexify((unsigned char*)cipher.c_str(), cipher.length());	// print binary data nicely


	// 4. get the private key and encode it as base64 (base64 in not necessary for an RSA decryptor.)
	std::string base64key = Base64Wrapper::encode(rsapriv.getPrivateKey());

	// 5. create another RSA decryptor using an existing private key (decode the base64 key to an std::string first)
	RSAPrivateWrapper rsapriv_other(Base64Wrapper::decode(base64key));

	std::string decrypted = rsapriv_other.decrypt(cipher);		// 6. you can decrypt an std::string or a const char* buffer
	std::cout << "decrypted:" << std::endl;
	hexify((unsigned char*)decrypted.c_str(), decrypted.length());	// print binary data nicely

	return 0;
}

void my_rsa_example()
{
	// Create RSA key pair
	RSAPrivateWrapper privateWrapper;
	RSAPublicWrapper publicWrapper(privateWrapper.getPublicKey());

	// Get the public and private keys
	std::string publicKey = publicWrapper.getPublicKey();
	std::string privateKey = privateWrapper.getPrivateKey();

	// Display the keys
	std::cout << "Public Key: " << Base64Wrapper::encode(publicKey) << std::endl;
	std::cout << "Private Key: " << Base64Wrapper::encode(privateKey) << std::endl;

	// Data to be encrypted
	std::string myData = "I'm gonna win this";

	// Encrypt the data using the public key
	std::string encryptedData = publicWrapper.encrypt(myData);

	// Display the encrypted data
	std::cout << "Encrypted Data: " << encryptedData << std::endl;

	// Decrypt the data using the private key
	std::string decryptedData = privateWrapper.decrypt(encryptedData);

	// Display the decrypted data
	std::cout << "Decrypted Data: " << decryptedData << std::endl;

}

int main()
{
	//aes_example();

	//my_rsa_example();

	create_info_file(INFO_FILE, DEFAULT_HOST, DEFAULT_PORT, DEFAULT_CLIENT_NAME, DEFAULT_FILE_TO_TRANSFER);

	Client client;
	std::string msg = "WORK YOU HOLE-MOL";
	std::cout << "Sending message.. " << msg << std::endl;
	boost::asio::write(client.get_socket(), boost::asio::buffer(msg));
	std::cout << "Message sent" <<  std::endl;
	return 0;
}
