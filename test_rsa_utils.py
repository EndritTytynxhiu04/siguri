from aes_utils import generate_aes_key, generate_hash
from rsa_utils import (
    generate_rsa_key_pair,
    serialize_public_key,
    load_public_key,
    encrypt_aes_key,
    decrypt_aes_key,
    sign_hash,
    verify_hash_signature
)

server_private_key, server_public_key = generate_rsa_key_pair()
client_private_key, client_public_key = generate_rsa_key_pair()

print("RSA key pairs generated successfully.")


server_public_pem = serialize_public_key(server_public_key)
received_server_public_key = load_public_key(server_public_pem)

print("Public key exchange completed.")

aes_key = generate_aes_key()

encrypted_aes_key = encrypt_aes_key(
    aes_key,
    received_server_public_key
)

print("AES key encrypted using RSA public key.")

decrypted_aes_key = decrypt_aes_key(
    encrypted_aes_key,
    server_private_key
)

if aes_key == decrypted_aes_key:
    print("AES key decrypted successfully.")
else:
    print("AES key decryption failed.")


with open("test.txt", "rb") as file:
    file_data = file.read()

file_hash = generate_hash(file_data)

signature = sign_hash(
    file_hash,
    client_private_key
)

print("SHA-256 hash signed successfully.")

is_valid = verify_hash_signature(
    file_hash,
    signature,
    client_public_key
)

if is_valid:
    print("Digital signature verified successfully.")
else:
    print("Digital signature verification failed.")