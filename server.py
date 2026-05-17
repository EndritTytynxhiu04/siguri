import socket
import struct
import os
from rsa_utils import (
    generate_rsa_key_pair,
    serialize_public_key,
    load_public_key,
    decrypt_aes_key
)
from aes_utils import generate_aes_key, encrypt_data, decrypt_data

HOST = "127.0.0.1"
PORT = 5000
SERVER_DIR = "server_files"

if not os.path.exists(SERVER_DIR):
    os.makedirs(SERVER_DIR)

# RSA KEYS
server_private_key, server_public_key = generate_rsa_key_pair()

print("[+] Server RSA key pair generated.")   

def send_msg(sock, msg):
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)

def recv_msg(sock):
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    return recvall(sock, msglen)

def recvall(sock, n):
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return bytes(data)

def handle_client(client_socket, address):
    print(f"\n[+] New connection from {address}")

    client_public_pem = recv_msg(client_socket)
    client_public_key = load_public_key(client_public_pem)

    server_public_pem = serialize_public_key(server_public_key)
    send_msg(client_socket, server_public_pem)

    print("[+] RSA public keys exchanged successfully.")
    
    try:
        # Receive the command from the client
        command_data = recv_msg(client_socket)
        if not command_data:
            return
            
        command_str = command_data.decode('utf-8')
        parts = command_str.split('|')
        command = parts[0]
        filename = parts[1]
        
        filepath = os.path.join(SERVER_DIR, filename)

        if command == "UPLOAD":
            print(f"[*] Preparing to receive file: {filename}")
            
            # Receive AES key and Encrypted Data
            encrypted_aes_key = recv_msg(client_socket)
            aes_key = decrypt_aes_key(
            encrypted_aes_key,
            server_private_key
            )

            print("[+] AES key decrypted successfully.")
            encrypted_data = recv_msg(client_socket)
            
            # Decrypt Data
            file_data = decrypt_data(encrypted_data, aes_key)
            
            # File Saving Logic
            with open(filepath, "wb") as f:
                f.write(file_data)
                
            print(f"[+] File saved successfully to {filepath}")
            send_msg(client_socket, b"SUCCESS: File uploaded and saved.")

        elif command == "DOWNLOAD":
            print(f"[*] Client requested file: {filename}")
            
            if not os.path.exists(filepath):
                send_msg(client_socket, b"ERROR: File not found on server.")
                return
            
            send_msg(client_socket, b"FOUND")
            
            # Read the file from server disk
            with open(filepath, "rb") as f:
                file_data = f.read()
                
            # Encrypt Data
            aes_key = generate_aes_key()
            encrypted_data = encrypt_data(file_data, aes_key)
            
            # Send AES Key and Encrypted Data
            send_msg(client_socket, aes_key)
            send_msg(client_socket, encrypted_data)
            print(f"[+] File '{filename}' encrypted and sent to client.")

    except Exception as e:
        print(f"[-] Error handling client {address}: {e}")
    finally:
        client_socket.close()
        print(f"[-] Connection closed for {address}")

def main():
    print("=========================================")
    print(" 🔒 Secure File Transfer Server 🔒 ")
    print("=========================================")
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    
    print(f"\n[+] Server is listening on {HOST}:{PORT}")
    print("[+] Awaiting client connections...\n")

    while True:
        try:
            client_socket, address = server_socket.accept()
            handle_client(client_socket, address)
        except KeyboardInterrupt:
            print("\n[!] Server shutting down...")
            break

    server_socket.close()

if __name__ == "__main__":
    main()