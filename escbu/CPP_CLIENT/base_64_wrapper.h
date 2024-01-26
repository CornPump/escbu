#ifndef BASE_64_WRAPPER_H
#define BASE_64_WRAPPER_H


#include <string>
#include <base64.h>


class Base64Wrapper
{
public:
	static std::string encode(const std::string& str);
	static std::string decode(const std::string& str);
};



#endif //BASE_64_WRAPPER_H
