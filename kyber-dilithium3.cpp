#include <iostream>
#include <string>
#include <cstring>
#include <oqs/oqs.h>

// Function to perform XOR-based encryption/decryption
void xor_cipher(const uint8_t *key, const std::string &message, uint8_t *output) {
    size_t key_len = strlen((char*) key);  // Length of the key
    for (size_t i = 0; i < message.size(); i++) {
        output[i] = message[i] ^ key[i % key_len];  // XOR operation
    }
}

/**
 * @brief Signs a message using the Dilithium3 signature algorithm
 * 
 * @param message The message to sign
 * @param private_key The private key to sign the message
 * @param signature The resulting signature
 * @return true if the signing was successful, false otherwise
 */
bool sign_message_with_dilithium(const std::string &message, const uint8_t *private_key, uint8_t *signature) {
    OQS_SIG *sig = OQS_SIG_new(OQS_SIG_alg_dilithium_3);
    if (sig == nullptr) {
        std::cerr << "Error initializing Dilithium3 signature algorithm." << std::endl;
        return false;
    }

    size_t signature_len = sig->length_signature;

    if (OQS_SIG_sign(sig, signature, &signature_len, (uint8_t*)message.c_str(), message.size(), private_key) != OQS_SUCCESS) {
        std::cerr << "Error signing the message." << std::endl;
        OQS_SIG_free(sig);
        return false;
    }

    OQS_SIG_free(sig);
    return true;
}

/**
 * @brief Verifies the signature of a message using the Dilithium3 signature algorithm
 * 
 * @param message The message to verify
 * @param signature The signature to verify
 * @param public_key The public key to verify the signature against
 * @return true if the signature is valid, false otherwise
 */
bool verify_signature_with_dilithium(const std::string &message, const uint8_t *signature, const uint8_t *public_key) {
    OQS_SIG *sig = OQS_SIG_new(OQS_SIG_alg_dilithium_3);
    if (sig == nullptr) {
        std::cerr << "Error initializing Dilithium3 signature algorithm." << std::endl;
        return false;
    }

    size_t signature_len = sig->length_signature;

    bool valid = OQS_SIG_verify(sig, (uint8_t*)message.c_str(), message.size(), signature, signature_len, public_key) == OQS_SUCCESS;

    OQS_SIG_free(sig);

    return valid;
}

/**
 * @brief Encrypts a message using the Kyber512 algorithm with key encapsulation
 * 
 * @param message The message to encrypt
 * @param public_key The public key of Kyber512
 * @param ciphertext The encrypted message (ciphertext)
 * @param shared_secret_encap The encapsulated shared secret
 * @return true if the encryption was successful, false otherwise
 */
bool encrypt_message_with_kyber(const std::string &message, const uint8_t *public_key, uint8_t *ciphertext, uint8_t *shared_secret_encap) {
    OQS_KEM *kem = OQS_KEM_new("Kyber512"); // ML KEM 768 o 1024
    if (kem == nullptr) {
        std::cerr << "Error initializing the Kyber512 algorithm." << std::endl;
        return false;
    }

    // Perform key encapsulation for Kyber512 (shared secret)
    if (OQS_KEM_encaps(kem, ciphertext, shared_secret_encap, public_key) != OQS_SUCCESS) {
        std::cerr << "Error during key encapsulation." << std::endl;
        OQS_KEM_free(kem);
        return false;
    }

    OQS_KEM_free(kem);
    return true;
}

int main() {
    // Initialize Kyber512 KEM
    if (!OQS_KEM_alg_is_enabled("Kyber512")) {
        std::cerr << "The Kyber512 algorithm is not enabled in liboqs." << std::endl;
        return -1;
    }

    OQS_KEM *kem = OQS_KEM_new("Kyber512");
    if (kem == nullptr) {
        std::cerr << "Error initializing the Kyber512 algorithm." << std::endl;
        return -1;
    }

    // Allocate buffers for Kyber512 keys and ciphertext
    uint8_t *public_key_kyber = new uint8_t[kem->length_public_key];
    uint8_t *secret_key_kyber = new uint8_t[kem->length_secret_key];
    uint8_t *ciphertext_kyber = new uint8_t[kem->length_ciphertext];
    uint8_t *shared_secret_encap = new uint8_t[kem->length_shared_secret];
    uint8_t *shared_secret_decap = new uint8_t[kem->length_shared_secret];

    // Generate public and private keys for Kyber512
    if (OQS_KEM_keypair(kem, public_key_kyber, secret_key_kyber) != OQS_SUCCESS) {
        std::cerr << "Error generating the Kyber512 key pair." << std::endl;
        return -1;
    }

    // Create an object for the Dilithium3 signature algorithm
    OQS_SIG *sig = OQS_SIG_new(OQS_SIG_alg_dilithium_3);
    if (sig == nullptr) {
        std::cerr << "Error initializing Dilithium3 signature algorithm." << std::endl;
        return -1;
    }

    // Allocate buffers for Dilithium3 signature and keys
    uint8_t *public_key_dilithium = new uint8_t[sig->length_public_key];
    uint8_t *private_key_dilithium = new uint8_t[sig->length_secret_key];
    uint8_t *signature = new uint8_t[sig->length_signature];

    // Generate the key pair for Dilithium3
    if (OQS_SIG_keypair(sig, public_key_dilithium, private_key_dilithium) != OQS_SUCCESS) {
        std::cerr << "Error generating the Dilithium3 key pair." << std::endl;
        return -1;
    }

    // Ask the user for a message to encrypt
    std::string message;
    std::cout << "Enter the message to encrypt: ";
    std::getline(std::cin, message);

    // Sign the message with Dilithium3 private key
    if (!sign_message_with_dilithium(message, private_key_dilithium, signature)) {
        std::cerr << "Failed to sign the message." << std::endl;
        return -1;
    }

    // Encrypt the message using Kyber512
    if (!encrypt_message_with_kyber(message, public_key_kyber, ciphertext_kyber, shared_secret_encap)) {
        std::cerr << "Error encrypting the message." << std::endl;
        return -1;
    }

    // Encrypt the signed message using XOR with the shared secret from Kyber512
    uint8_t *encrypted_message = new uint8_t[message.size()];
    xor_cipher(shared_secret_encap, message, encrypted_message);

    // Display the encrypted message in hexadecimal
    std::cout << "Encrypted message: ";
    for (size_t i = 0; i < message.size(); i++) {
        std::cout << std::hex << (int)encrypted_message[i] << " ";
    }
    std::cout << std::dec << std::endl;  // Switch back to decimal formatting

    // Decrypt the message using the same shared secret
    uint8_t *decrypted_message = new uint8_t[message.size()];
    xor_cipher(shared_secret_encap, std::string((char*)encrypted_message, message.size()), decrypted_message);

    // Display the decrypted message
    std::cout << "Decrypted message: ";
    for (size_t i = 0; i < message.size(); i++) {
        std::cout << decrypted_message[i];
    }
    std::cout << std::endl;

    // Verify the signature on the decrypted message using Dilithium3
    if (verify_signature_with_dilithium(std::string((char*)decrypted_message), signature, public_key_dilithium)) {
        std::cout << "The signature is valid." << std::endl;
    } else {
        std::cerr << "The signature is invalid." << std::endl;
    }

    // Clean up dynamically allocated memory
    delete[] public_key_kyber;
    delete[] secret_key_kyber;
    delete[] ciphertext_kyber;
    delete[] shared_secret_encap;
    delete[] shared_secret_decap;
    delete[] public_key_dilithium;
    delete[] private_key_dilithium;
    delete[] signature;
    delete[] encrypted_message;
    delete[] decrypted_message;

    OQS_SIG_free(sig);  // Free the signature object
    OQS_KEM_free(kem);  // Free the KEM object

    return 0;  // End program successfully
}

