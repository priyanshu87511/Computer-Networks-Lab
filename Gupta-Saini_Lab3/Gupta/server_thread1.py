import socket
import threading
import sys
import time
import signal
import os
from struct import pack, unpack, calcsize

IP = socket.gethostbyname(socket.gethostname())
PORT = int(sys.argv[1])
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
TERMINATION_MSG = "GOODBYE"
PACK_FORMAT = "!HBBII"
START_MSG = "HELLO"
TIMEOUT_SECONDS = 5  # Set the initial timeout to 60 seconds

# List to store all connected client connections
connected_clients = []
server = None  # To store the server socket

def encode(dataFormat, data, headerFormat, *headers):
    return pack(headerFormat, *headers) + data.encode(dataFormat)

def getHeaderData(dataFormat, headerFormat, encoded):
    header_size = calcsize(PACK_FORMAT)
    header = unpack(headerFormat, encoded[:header_size])
    data = encoded[header_size:].decode(dataFormat)
    return header, data

def handle_client(conn, addr):
    connected_clients.append(conn)
    # print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    iteration = 0
    last_msg_time = time.time()  # Track the time of the last received message

    while connected:
        try:
            conn.settimeout(TIMEOUT_SECONDS)  # Set the timeout for this connection
<<<<<<< HEAD
            data = conn.recv(SIZE).decode(FORMAT)
            data = data.encode('latin-1')
            header, msg = getHeaderData(FORMAT, PACK_FORMAT, data)
            print(header)
=======
            msg = conn.recv(SIZE).decode(FORMAT)

>>>>>>> 9ea82388fb9fa687f02f630a02d5464de3b83382
        except socket.timeout:
            print(f"{addr} Connection timed out. GOODBYE from server.")
            msg = TERMINATION_MSG
            conn.send(msg.encode(FORMAT))
            connected = False
            continue
        except Exception as e:
            print(f"{addr} EOF Spotted")
            connected = False
            continue

        to_print = msg
        if to_print == START_MSG:
            to_print = "Session created"
        elif to_print == TERMINATION_MSG:
            to_print = "GOODBYE from client"
        print(f"{addr} [{iteration}] {to_print}")

        if msg != START_MSG and msg != TERMINATION_MSG:
            msg = "ALIVE"
        elif iteration != 0:
            connected = False
            msg = TERMINATION_MSG
        conn.send(msg.encode(FORMAT))
        iteration += 1
        last_msg_time = time.time()  # Update the last message time

        # Check if the time since the last message exceeds the timeout
        if time.time() - last_msg_time > TIMEOUT_SECONDS:
            print(f"{addr} Connection timed out (no message received). Closing session.")
            connected = False

    print(f"{addr} Session closed")
    conn.close()
    connected_clients.remove(conn)

def close_server_and_connections(signal, frame):
    print("Closing server and all connections, then exiting...")
    for conn in connected_clients:
        try:
            conn.send(TERMINATION_MSG.encode(FORMAT))
            conn.close()
        except Exception as e:
            pass
    if server:
        server.close()
    sys.exit(0)

def input_listener():
    while True:
        user_input = input()
        if user_input.lower() == 'q':
            print("Sending 'GOODBYE' message to all clients and closing connections...")
            for conn in connected_clients:
                try:
                    conn.send(TERMINATION_MSG.encode(FORMAT))
                    conn.close()
                except Exception as e:
                    pass
            if server:
                server.close()
                os._exit(0)  # Terminate the program immediately

def main():
    global server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"Waiting on port {PORT}...")

    signal.signal(signal.SIGINT, close_server_and_connections)

    # Create a thread for input listener
    input_thread = threading.Thread(target=input_listener)
    input_thread.daemon = True
    input_thread.start()

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        # print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    main()
