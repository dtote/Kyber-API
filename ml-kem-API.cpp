#include <iostream>
#include <string>
#include <cstring>
#include <oqs/oqs.h>
#include "crow.h"  // Biblioteca Crow para la API REST
#include <base64.h>  // Biblioteca de codificación Base64

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

            uint8_t *xor_encrypted_message = new uint8_t[message.size()];
            xor_cipher(shared_secret, message, xor_encrypted_message);

            std::string xor_encrypted_base64 = base64_encode(xor_encrypted_message, message.size());
            std::string shared_secret_base64 = base64_encode(shared_secret, shared_secret_len);

            delete[] public_key;
            delete[] ciphertext;
            delete[] shared_secret;
            delete[] xor_encrypted_message;

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
        std::string ciphertext_base64 = params["ciphertext"].s();
        std::string shared_secret_base64 = params["shared_secret"].s();

        try {
            std::string xor_encrypted_str = base64_decode(ciphertext_base64);
            std::string shared_secret_str = base64_decode(shared_secret_base64);

            size_t xor_encrypted_len = xor_encrypted_str.size();
            size_t shared_secret_len = shared_secret_str.size();

            uint8_t *xor_encrypted = new uint8_t[xor_encrypted_len];
            std::memcpy(xor_encrypted, xor_encrypted_str.data(), xor_encrypted_len);

            uint8_t *shared_secret = new uint8_t[shared_secret_len];
            std::memcpy(shared_secret, shared_secret_str.data(), shared_secret_len);

            uint8_t *decrypted_message = new uint8_t[xor_encrypted_len];
            xor_cipher(shared_secret, std::string((char*)xor_encrypted, xor_encrypted_len), decrypted_message);

            std::string original_message(reinterpret_cast<char *>(decrypted_message), xor_encrypted_len);

            delete[] xor_encrypted;
            delete[] shared_secret;
            delete[] decrypted_message;

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
