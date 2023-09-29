import socket
import threading

IP = socket.gethostbyname(socket.gethostname())
PORT = 5566 #INPUT
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
TERMINATION_MSG = "GOODBYE"
START_MSG = "HELLO"

def handle_client(conn, addr):
    # print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    iteration = 0
    while connected:
        msg = conn.recv(SIZE).decode(FORMAT)

        to_print = msg
        if(to_print == START_MSG):
            to_print = "Session created"
        elif(to_print == TERMINATION_MSG):
            to_print = "GOODBYE from client"
        print(f"{addr} [{iteration}] {to_print}")

        if (msg != START_MSG) and (msg != TERMINATION_MSG):
            msg = "ALIVE"
        elif (iteration != 0):
            connected = False
            msg = TERMINATION_MSG
        conn.send(msg.encode(FORMAT))
        iteration += 1 
    print(f"{addr} Session closed")
    conn.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"Waiting on port {PORT}...")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        # print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    main()