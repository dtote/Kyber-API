#include <iostream>
#include <oqs/oqs.h>

int main() {
    const char *kem_name = nullptr;
    std::cout << "Available KEM algorithms:" << std::endl;
    for (size_t i = 0; (kem_name = OQS_KEM_alg_identifier(i)) != nullptr; i++) {
        std::cout << "  - " << kem_name << std::endl;
    }
    return 0;
}