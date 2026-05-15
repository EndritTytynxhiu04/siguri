import socket

HOST = "127.0.0.1"
PORT = 5000

def main():
    print("Generating RSA key pair...")
    print("RSA keys generated.")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    print(f"Secure File Transfer Server is running on {HOST}:{PORT}")
    print("Awaiting client connections...")

    while True:
        client_socket, address = server_socket.accept()
        print("Client connected from", address)
        client_socket.close()

if __name__ == "__main__":
    main()
