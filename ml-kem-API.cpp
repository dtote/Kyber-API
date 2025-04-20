#include <iostream>
#include <string>
#include <cstring>
#include <oqs/oqs.h>
#include "crow.h"  // Library Crow to make the API REST
#include <base64.h>  // Library to encode Base64

// Function to generate keys for ML-DSA (ML-DSA-44, ML-DSA-65, ML-DSA-87)
std::pair<std::string, std::string> generate_ml_dsa_keys(const std::string &ml_dsa_variant) {
    // Initialize the ML-DSA algorithm with the specified variant (ML-DSA-44, ML-DSA-65, ML-DSA-87)
    OQS_SIG *sig = OQS_SIG_new(ml_dsa_variant.c_str());
    if (!sig) {
        throw std::runtime_error("Error initializing the ML-DSA algorithm");
    }

    // Define key lengths for public and private keys
    size_t public_key_len = sig->length_public_key;
    size_t private_key_len = sig->length_secret_key;

    // Create buffers to hold the public and private keys
    uint8_t *public_key = new uint8_t[public_key_len];
    uint8_t *private_key = new uint8_t[private_key_len];

    // Generate the key pair (public and private keys)
    if (OQS_SIG_keypair(sig, public_key, private_key) != OQS_SUCCESS) {
        OQS_SIG_free(sig);
        throw std::runtime_error("Error generating the key pair for ML-DSA");
    }

    // Encode the keys in Base64 to facilitate handling
    std::string public_key_base64 = base64_encode(public_key, public_key_len);
    std::string private_key_base64 = base64_encode(private_key, private_key_len);

    // Free the allocated memory for the keys
    delete[] public_key;
    delete[] private_key;
    OQS_SIG_free(sig);

    // Return the encoded keys
    return {public_key_base64, private_key_base64};
}

// Function to sign a message using ML-DSA (from liboqs)
std::string sign_message_with_mldsa(const std::string &message, uint8_t *private_key, size_t private_key_len, const std::string &ml_dsa_variant) {
    // Map the variant string to the corresponding OQS_SIG algorithm
    const char* sig_alg = nullptr;
    if (ml_dsa_variant == "ML-DSA-44") {
        sig_alg = OQS_SIG_alg_ml_dsa_44;
    } else if (ml_dsa_variant == "ML-DSA-65") {
        sig_alg = OQS_SIG_alg_ml_dsa_65;
    } else if (ml_dsa_variant == "ML-DSA-87") {
        sig_alg = OQS_SIG_alg_ml_dsa_87;
    } else {
        throw std::runtime_error("Invalid ML-DSA variant provided.");
    }

    // Initialize the signature algorithm
    OQS_SIG *sig = OQS_SIG_new(sig_alg);
    if (sig == nullptr) {
        throw std::runtime_error("Error initializing the ML-DSA signature algorithm.");
    }

    // Sign the message
    size_t signature_len = sig->length_signature;
    uint8_t *signature = new uint8_t[signature_len];

    if (OQS_SIG_sign(sig, signature, &signature_len, (uint8_t*)message.c_str(), message.size(), private_key) != OQS_SUCCESS) {
        OQS_SIG_free(sig);
        delete[] signature;
        throw std::runtime_error("Signing failed.");
    }

    // Convert the signature to Base64 for easy transmission
    std::string signature_base64 = base64_encode(signature, signature_len);

    // Clean up
    OQS_SIG_free(sig);
    delete[] signature;

    return signature_base64;
}

// Function to verify the signature using ML-DSA
bool verify_message_with_mldsa(const std::string &message, const std::string &signature_base64, uint8_t *public_key, size_t public_key_len, const std::string &ml_dsa_variant) {
    // Map the variant string to the corresponding OQS_SIG algorithm
    const char* sig_alg = nullptr;
    if (ml_dsa_variant == "ML-DSA-44") {
        sig_alg = OQS_SIG_alg_ml_dsa_44;
    } else if (ml_dsa_variant == "ML-DSA-65") {
        sig_alg = OQS_SIG_alg_ml_dsa_65;
    } else if (ml_dsa_variant == "ML-DSA-87") {
        sig_alg = OQS_SIG_alg_ml_dsa_87;
    } else {
        throw std::runtime_error("Invalid ML-DSA variant provided.");
    }

    // Initialize the signature algorithm
    OQS_SIG *sig = OQS_SIG_new(sig_alg);
    if (sig == nullptr) {
        throw std::runtime_error("Error initializing the ML-DSA signature algorithm.");
    }

    // Decode the signature from Base64
    std::string decoded_signature = base64_decode(signature_base64);
    uint8_t *signature = new uint8_t[decoded_signature.size()];
    std::memcpy(signature, decoded_signature.data(), decoded_signature.size());

    // Verify the signature
    bool result = OQS_SIG_verify(sig, (uint8_t*)message.c_str(), message.size(), signature, decoded_signature.size(), public_key) == OQS_SUCCESS;

    // Clean up
    OQS_SIG_free(sig);
    delete[] signature;

    return result;
}

// Function to perform XOR-based encryption/decryption
void xor_cipher(const uint8_t *key, const std::string &message, uint8_t *output) {
    size_t key_len = strlen((char*) key);
    for (size_t i = 0; i < message.size(); i++) {
        output[i] = message[i] ^ key[i % key_len];
    }
}

bool encrypt_message_with_mlkem(const std::string &kem_name, const std::string &message, const uint8_t *public_key, uint8_t *ciphertext, uint8_t *shared_secret_encap) {
    OQS_KEM *kem = OQS_KEM_new(kem_name.c_str());
    if (kem == nullptr) {
        std::cerr << "Error initializing the " << kem_name << " algorithm." << std::endl;
        return false;
    }

    if (OQS_KEM_encaps(kem, ciphertext, shared_secret_encap, public_key) != OQS_SUCCESS) {
        std::cerr << "Error during key encapsulation." << std::endl;
        OQS_KEM_free(kem);
        return false;
    }

    OQS_KEM_free(kem);
    return true;
}

std::pair<uint8_t*, uint8_t*> generate_keys(const std::string &kem_name, size_t &public_key_len, size_t &secret_key_len) {
    OQS_KEM *kem = OQS_KEM_new(kem_name.c_str());
    if (!kem) {
        throw std::runtime_error("Failed to initialize KEM");
    }

    public_key_len = kem->length_public_key;
    secret_key_len = kem->length_secret_key;
    uint8_t *public_key = new uint8_t[public_key_len];
    uint8_t *secret_key = new uint8_t[secret_key_len];

    if (OQS_KEM_keypair(kem, public_key, secret_key) != OQS_SUCCESS) {
        OQS_KEM_free(kem);
        throw std::runtime_error("Failed to generate key pair");
    }

    OQS_KEM_free(kem);
    return {public_key, secret_key};
}

int main() {
    crow::SimpleApp app;

    // Define the route to generate ML-DSA keys
    app.route_dynamic("/generate_ml_dsa_keys").methods(crow::HTTPMethod::POST)([&](const crow::request &req) -> crow::response {
        // Extract the ml_dsa_variant from the request body
        auto params = crow::json::load(req.body);
        if (!params.has("ml_dsa_variant")) {
            return crow::response(400, "ml_dsa_variant is required");
        }

        std::string ml_dsa_variant = params["ml_dsa_variant"].s();
        
        try {
            // Generate keys using the provided variant (e.g., ML-DSA-44)
            auto [public_key, private_key] = generate_ml_dsa_keys(ml_dsa_variant);

            // Return the keys as a JSON response
            return crow::response(crow::json::wvalue({
                {"public_key", public_key},
                {"private_key", private_key}
            }));
        } catch (const std::exception &e) {
            // If there was an error, return a 500 status code with the error message
            return crow::response(500, e.what());
        }
    });

    app.route_dynamic("/sign").methods(crow::HTTPMethod::POST)([&](const crow::request &req) -> crow::response {
        auto params = crow::json::load(req.body);

        if (!params.has("message") || !params.has("private_key") || !params.has("ml_dsa_variant")) {
            return crow::response(400, "Message, private_key, and ml_dsa_variant are required");
        }

        std::string message = params["message"].s();
        std::string private_key_base64 = params["private_key"].s();
        std::string ml_dsa_variant = params["ml_dsa_variant"].s();

        try {
            // Decode private key from Base64
            std::string decoded_private_key = base64_decode(private_key_base64);
            uint8_t *private_key = new uint8_t[decoded_private_key.size()];
            std::memcpy(private_key, decoded_private_key.data(), decoded_private_key.size());

            // Sign the message
            std::string signature_base64 = sign_message_with_mldsa(message, private_key, decoded_private_key.size(), ml_dsa_variant);

            delete[] private_key;

            return crow::response(crow::json::wvalue({
                {"signature", signature_base64}
            }));
        } catch (const std::exception &e) {
            return crow::response(500, e.what());
        }
    });

    app.route_dynamic("/verify").methods(crow::HTTPMethod::POST)([&](const crow::request &req) -> crow::response {
        auto params = crow::json::load(req.body);

        if (!params.has("message") || !params.has("signature") || !params.has("public_key") || !params.has("ml_dsa_variant")) {
            return crow::response(400, "Message, signature, public_key, and ml_dsa_variant are required");
        }

        std::string message = params["message"].s();
        std::string signature_base64 = params["signature"].s();
        std::string public_key_base64 = params["public_key"].s();
        std::string ml_dsa_variant = params["ml_dsa_variant"].s();

        try {
            // Decode public key from Base64
            std::string decoded_public_key = base64_decode(public_key_base64);
            uint8_t *public_key = new uint8_t[decoded_public_key.size()];
            std::memcpy(public_key, decoded_public_key.data(), decoded_public_key.size());

            // Verify the signature
            bool verified = verify_message_with_mldsa(message, signature_base64, public_key, decoded_public_key.size(), ml_dsa_variant);

            delete[] public_key;

            if (verified) {
                return crow::response(crow::json::wvalue({
                    {"status", "verified"}
                }));
            } else {
                return crow::response(400, "Signature verification failed");
            }
        } catch (const std::exception &e) {
            return crow::response(500, e.what());
        }
    });

    app.route_dynamic("/generate_keys").methods(crow::HTTPMethod::POST)([&](const crow::request &req) -> crow::response {
        auto params = crow::json::load(req.body);
        if (!params.has("kem_name")) {
          return crow::response(400, "kem_name is required");
        }
        std::string kem_name = params["kem_name"].s();
        size_t public_key_len, secret_key_len;
        try {
            auto [public_key, secret_key] = generate_keys(kem_name, public_key_len, secret_key_len);
            std::string public_key_base64 = base64_encode(public_key, public_key_len);
            std::string shared_secret_base64 = base64_encode(secret_key, secret_key_len);
            delete[] public_key;
            delete[] secret_key;
            return crow::response(crow::json::wvalue({
                {"public_key", public_key_base64},
                {"secret_key", shared_secret_base64}
            }));
        } catch (const std::exception &e) {
            return crow::response(500, e.what());
        }
    });

    app.route_dynamic("/encrypt").methods(crow::HTTPMethod::POST)([&](const crow::request &req) -> crow::response {
        auto params = crow::json::load(req.body);
    
        if (!params.has("kem_name") || !params.has("message") || !params.has("public_key")) {
            return crow::response(400, "kem_name, message, and public_key are required");
        }
    
        std::string kem_name = params["kem_name"].s();
        std::string message = params["message"].s();
        std::string public_key_base64 = params["public_key"].s();
    
        size_t public_key_len = 0, ciphertext_len = 0, shared_secret_len = 0;
        uint8_t *ciphertext = nullptr, *shared_secret = nullptr;
    
        try {
            OQS_KEM *kem = OQS_KEM_new(kem_name.c_str());
            if (!kem) throw std::runtime_error("Failed to initialize KEM");
    
            public_key_len = kem->length_public_key;
            ciphertext_len = kem->length_ciphertext;
            shared_secret_len = kem->length_shared_secret;
    
            std::string public_key_str = base64_decode(public_key_base64);
            uint8_t *public_key = new uint8_t[public_key_str.size()];
            std::memcpy(public_key, public_key_str.data(), public_key_str.size());
            ciphertext = new uint8_t[ciphertext_len];
            shared_secret = new uint8_t[shared_secret_len];
    
            if (!encrypt_message_with_mlkem(kem_name, message, public_key, ciphertext, shared_secret)) {
                throw std::runtime_error("Encryption failed");
            }
    
            size_t block_size = 32;
            std::vector<std::string> encrypted_blocks;
    
            for (size_t i = 0; i < message.size(); i += block_size) {
                std::string block = message.substr(i, block_size);
                uint8_t *xor_encrypted_block = new uint8_t[block.size()];
                xor_cipher(shared_secret, block, xor_encrypted_block);
                std::string encoded = base64_encode(xor_encrypted_block, block.size());
                encrypted_blocks.push_back(encoded);
                delete[] xor_encrypted_block;
            }
    
            // 🔗 Concatenar bloques con delimitador "::"
            std::string xor_encrypted_base64 = "";
            for (size_t i = 0; i < encrypted_blocks.size(); ++i) {
                xor_encrypted_base64 += encrypted_blocks[i];
                if (i != encrypted_blocks.size() - 1) xor_encrypted_base64 += "::";
            }
    
            std::string shared_secret_base64 = base64_encode(shared_secret, shared_secret_len);
    
            delete[] public_key;
            delete[] ciphertext;
            delete[] shared_secret;
    
            return crow::response(crow::json::wvalue({
                {"ciphertext", xor_encrypted_base64},
                {"shared_secret", shared_secret_base64}
            }));
        } catch (const std::exception &e) {
            delete[] ciphertext;
            delete[] shared_secret;
            return crow::response(500, e.what());
        }
    });
    
    app.route_dynamic("/decrypt").methods(crow::HTTPMethod::POST)([&](const crow::request &req) -> crow::response {
        auto params = crow::json::load(req.body);
    
        if (!params.has("kem_name") || !params.has("ciphertext") || !params.has("shared_secret")) {
            return crow::response(400, "kem_name, ciphertext, and shared_secret are required");
        }
    
        std::string kem_name = params["kem_name"].s();
        std::string ciphertext_combined = params["ciphertext"].s();
        std::string shared_secret_base64 = params["shared_secret"].s();
    
        try {
            std::string shared_secret_str = base64_decode(shared_secret_base64);
            size_t shared_secret_len = shared_secret_str.size();
    
            uint8_t *shared_secret = new uint8_t[shared_secret_len];
            std::memcpy(shared_secret, shared_secret_str.data(), shared_secret_len);
    
            std::vector<std::string> encrypted_blocks;
            size_t pos = 0, next;
            while ((next = ciphertext_combined.find("::", pos)) != std::string::npos) {
                encrypted_blocks.push_back(ciphertext_combined.substr(pos, next - pos));
                pos = next + 2;
            }
            encrypted_blocks.push_back(ciphertext_combined.substr(pos));
    
            std::string original_message = "";
    
            for (const auto& encoded_block : encrypted_blocks) {
                std::string decoded = base64_decode(encoded_block);
                size_t block_size = decoded.size();
                uint8_t *xor_encrypted = new uint8_t[block_size];
                std::memcpy(xor_encrypted, decoded.data(), block_size);
    
                uint8_t *decrypted_block = new uint8_t[block_size];
                xor_cipher(shared_secret, std::string((char*)xor_encrypted, block_size), decrypted_block);
                original_message += std::string(reinterpret_cast<char *>(decrypted_block), block_size);
    
                delete[] xor_encrypted;
                delete[] decrypted_block;
            }
    
            delete[] shared_secret;
    
            return crow::response(crow::json::wvalue({
                {"original_message", original_message}
            }));
        } catch (const std::exception &e) {
            return crow::response(500, e.what());
        }
    });
    


    app.port(5001).multithreaded().run();

    return 0;
}
