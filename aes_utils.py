from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import hashlib


def generate_aes_key():
    return get_random_bytes(32)


def encrypt_data(data, aes_key):
    cipher = AES.new(aes_key, AES.MODE_CBC)
    encrypted_data = cipher.encrypt(pad(data, AES.block_size))
    return cipher.iv + encrypted_data


def decrypt_data(encrypted_data, aes_key):
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]

    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ciphertext), AES.block_size)


def generate_hash(data):
    return hashlib.sha256(data).hexdigest()


def verify_hash(original_hash, decrypted_data):
    return original_hash == generate_hash(decrypted_data)


if __name__ == "__main__":
    aes_key = generate_aes_key()

    with open("test.txt", "rb") as file:
        original_data = file.read()

    original_hash = generate_hash(original_data)

    encrypted_data = encrypt_data(original_data, aes_key)

    with open("encrypted.bin", "wb") as file:
        file.write(encrypted_data)

    decrypted_data = decrypt_data(encrypted_data, aes_key)

    with open("decrypted.txt", "wb") as file:
        file.write(decrypted_data)

    print("AES key generated successfully.")
    print("Original file loaded: test.txt")
    print("Encrypted file saved: encrypted.bin")
    print("Decrypted file saved: decrypted.txt")
    print("SHA-256 hash:", original_hash)
    print("Integrity verification result:", verify_hash(original_hash, decrypted_data))