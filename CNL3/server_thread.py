import socket
import threading

IP = socket.gethostbyname(socket.gethostname())
PORT = 5566 #INPUT
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
TERMINATION_MSG = "GOODBYE"

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        msg = conn.recv(SIZE).decode(FORMAT)
        if (msg == TERMINATION_MSG):
            connected = False

        print(f"[{addr}] {msg}")
        msg = "ALIVE"
        conn.send(msg.encode(FORMAT))

    conn.close()

def main():
    print("[STARTING] Server is starting...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Server is listening on {IP}:{PORT}")

    while True:
        conn, addr = server.accept()
        print(conn, addr)
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

if __name__ == "__main__":
    main()