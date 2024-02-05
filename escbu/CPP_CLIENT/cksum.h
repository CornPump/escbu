#ifndef CKSUM_H
#define CKSUM_H

#include <filesystem>

extern uint_fast32_t const crctab[8][256];
unsigned long memcrc(char* b, size_t n);
std::tuple<unsigned long, unsigned long> check_sum(std::string fname);


#endif //CKSUM_H
