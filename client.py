import socket
import os
import struct
from rsa_utils import (
    generate_rsa_key_pair,
    serialize_public_key,
    load_public_key,
    encrypt_aes_key
)
from aes_utils import generate_aes_key, encrypt_data, decrypt_data, generate_hash

HOST = "127.0.0.1"
PORT = 5000
CLIENT_DIR = "client_files"

if not os.path.exists(CLIENT_DIR):
    os.makedirs(CLIENT_DIR)

# RSA KEYS
client_private_key, client_public_key = generate_rsa_key_pair()
print("[+] Client RSA key pair generated.")

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

def upload_file():
    filepath = input("\nEnter the path of the file to send: ").strip()
    if not os.path.exists(filepath):
        print("[-] Error: File not found! Please check the path and try again.")
        return

    print(f"\n[+] Reading '{filepath}'...")
    filename = os.path.basename(filepath)

    with open(filepath, "rb") as file:
        file_data = file.read()

    file_hash = generate_hash(file_data)
    aes_key = generate_aes_key()
    encrypted_data = encrypt_data(file_data, aes_key)

    print("[+] File hashed and encrypted with AES.")
    print(f"[+] Connecting to server at {HOST}:{PORT}...")
    
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))

        # Send client public key
        client_public_pem = serialize_public_key(client_public_key)
        send_msg(client_socket, client_public_pem)

        # Receive server public key
        server_public_pem = recv_msg(client_socket)
        server_public_key = load_public_key(server_public_pem)

        print("[+] RSA public keys exchanged successfully.")
        
        # 1. Send Command and Filename
        send_msg(client_socket, f"UPLOAD|{filename}".encode('utf-8'))
        
        # 2. Send AES Key and Encrypted Data 
        # (Member 2 will add RSA encryption to this aes_key later)
        encrypted_aes_key = encrypt_aes_key(
        aes_key,
        server_public_key
        )

        send_msg(client_socket, encrypted_aes_key)
        send_msg(client_socket, encrypted_data)

        print("[+] AES key encrypted with RSA public key.")
        
        # Wait for Server Response
        response = recv_msg(client_socket)
        if response:
            print(f"[+] Server response: {response.decode('utf-8')}")

    except ConnectionRefusedError:
        print("[-] Connection failed. Make sure the server is running.")
    except Exception as e:
        print(f"[-] An unexpected error occurred: {e}")
    finally:
        if 'client_socket' in locals():
            client_socket.close()

def download_file():
    filename = input("\nEnter the name of the file to download: ").strip()
    print(f"\n[+] Connecting to server at {HOST}:{PORT} to request '{filename}'...")
    
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))

        # 1. Send Download Command
        send_msg(client_socket, f"DOWNLOAD|{filename}".encode('utf-8'))
        
        # 2. Check if file exists on server
        status = recv_msg(client_socket)
        if not status or status.startswith(b"ERROR"):
            print(f"[-] Server error: {status.decode('utf-8') if status else 'Unknown Error'}")
            return
            
        # 3. Receive AES Key and Encrypted Data
        aes_key = recv_msg(client_socket)
        encrypted_data = recv_msg(client_socket)
        
        # 4. Decrypt Data
        file_data = decrypt_data(encrypted_data, aes_key)
        
        # 5. File Saving Logic
        save_path = os.path.join(CLIENT_DIR, filename)
        with open(save_path, "wb") as f:
            f.write(file_data)
            
        print(f"[+] File '{filename}' successfully downloaded and saved to {save_path}")

    except ConnectionRefusedError:
        print("[-] Connection failed. Make sure the server is running.")
    except Exception as e:
        print(f"[-] An unexpected error occurred: {e}")
    finally:
        if 'client_socket' in locals():
            client_socket.close()

def main():
    while True:
        print("\n" + "="*40)
        print(" 🔒 Secure File Transfer Client 🔒")
        print("="*40)
        print("  1. Upload a file to Server")
        print("  2. Download a file from Server")
        print("  3. Exit")
        print("="*40)
        
        choice = input("Select an option (1-3): ").strip()
        
        if choice == '1':
            upload_file()
        elif choice == '2':
            download_file()
        elif choice == '3':
            print("\nExiting client. Goodbye!")
            break
        else:
            print("\n[-] Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()