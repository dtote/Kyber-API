/**
 * Universidad de La Laguna
 * Escuela Superior de Ingeniería y Tecnología
 * Grado en Ingeniería Informática
 * Trabajo de Fin de Grado - Kleptographic Attacks on Lattice-Based CryptoSystems
 *
 * @author Omar Suárez Doro
 * @date September 29 2024
 * @version v0.1.0
 * @brief This file contains the definition of the methods of the FRODOKEM-640-shake cypher class
 */

#include <iostream>
#include <vector>
#include <utility>
// #include "./KYBER-KEM-512.h"
#include <oqs/oqs.h>
#include "kyberkem.h" 


/**
 * @brief Construct a new KyberKEM_512::KyberKEM_512 object
 */
using Bytes = std::vector<uint8_t>;

KyberKEM_512::KyberKEM_512() {
  // First, we need to initialize the FRODOKEM-640-shake cypher
  kem = OQS_KEM_new(OQS_KEM_alg_kyber_512);
  if (kem == nullptr) {
    throw std::runtime_error("ERROR: Unable to initialize the KyberKEM_512 cypher.");
  }
  
  // We need to assign the length of the public and secret keys
  public_key_.resize(kem->length_public_key);
  secret_key_.resize(kem->length_secret_key);

  // Generate the keypair
  OQS_STATUS status = OQS_KEM_keypair(kem, public_key_.data(), secret_key_.data());
  if (status != OQS_SUCCESS) {
    OQS_KEM_free(kem);
    throw std::runtime_error("ERROR: Unable to generate the keypair for the KyberKEM_512 cypher.");
  }
}

/**
 * @brief Encrypts a message using the FRODOKEM-512-shake cypher
 * @param pk The pk to be encrypted
 * @return Bytes The cyphertext
 */
std::pair<Bytes, Bytes> KyberKEM_512::Encrypt(const Bytes& pk) {
  // We need to assign the length of the cyphertext
  std::vector<uint8_t> ciphertext(kem->length_ciphertext);   
  std::vector<uint8_t> shared_secret(kem->length_shared_secret);

  std::vector<uint8_t> aux_pk = pk.GetBytes();
  
  // Encrypt the message
  OQS_STATUS status = OQS_KEM_kyber_512_encaps(ciphertext.data(), shared_secret.data(), aux_pk.data());
  if (status != OQS_SUCCESS) {
    throw std::runtime_error("ERROR: Unable to encrypt the message using the FRODOKEM-512-shake cypher.");
  }
 
  Bytes cyphertext(ciphertext);
  Bytes shared_secret_bytes(shared_secret);
  return {cyphertext, shared_secret_bytes};
}


/**
 * @brief Decrypts a cyphertext using the FRODOKEM-512-shake cypher
 * @param cyphertext The cyphertext to be decrypted
 * @return Bytes The decrypted message
 */
Bytes KyberKEM_512::Decrypt(const Bytes& cyphertext, const Bytes& sk) {
  std::vector<uint8_t> aux_cyphertext = cyphertext.GetBytes();
  std::vector<uint8_t> shared_secret(kem->length_shared_secret);
  // Decrypt the message
  OQS_STATUS status = OQS_KEM_kyber_512_decaps(shared_secret.data(), aux_cyphertext.data(), secret_key_.data());
  if (status != OQS_SUCCESS) {
    throw std::runtime_error("ERROR: Unable to decrypt the message using the FRODOKEM-512-shake cypher.");
  }

  Bytes shared_secret_bytes(shared_secret);
  return shared_secret_bytes;
}

int main() {
    try {
        // Inicializar el objeto KyberKEM_512
        KyberKEM_512 kyber;

        // Crear un mensaje que se desea encriptar
        std::string mensaje = "Hola, este es un mensaje secreto!";
        Bytes mensaje_bytes(std::vector<uint8_t>(mensaje.begin(), mensaje.end()));

        // Encriptar el mensaje utilizando la clave pública
        std::pair<Bytes, Bytes> resultado = kyber.Encrypt(mensaje_bytes);

        // Obtener el cifrado y la clave compartida
        Bytes cyphertext = resultado.first;
        Bytes shared_secret_enc = resultado.second;

        // Mostrar los resultados de la encriptación
        std::cout << "Mensaje original: " << mensaje << std::endl;
        std::cout << "Cifrado: ";
        for (uint8_t byte : cyphertext.GetBytes()) {
            std::cout << std::hex << (int)byte << " ";
        }
        std::cout << std::endl;

        std::cout << "Clave compartida (encriptada): ";
        for (uint8_t byte : shared_secret_enc.GetBytes()) {
            std::cout << std::hex << (int)byte << " ";
        }
        std::cout << std::endl;

        // Desencriptar el mensaje utilizando la clave privada
        Bytes shared_secret_dec = kyber.Decrypt(cyphertext, mensaje_bytes);

        // Mostrar la clave compartida obtenida al desencriptar
        std::cout << "Clave compartida (desencriptada): ";
        for (uint8_t byte : shared_secret_dec.GetBytes()) {
            std::cout << std::hex << (int)byte << " ";
        }
        std::cout << std::endl;

    } catch (const std::exception& e) {
        std::cerr << e.what() << std::endl;
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}