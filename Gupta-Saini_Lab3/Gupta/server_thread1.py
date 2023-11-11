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
TERMINATION_MSG = "GOODBYE"
PACK_FORMAT = "!HBBII"
START_MSG = "HELLO"
TIMEOUT_SECONDS = 60  # Set the initial timeout to 60 seconds

# List to store all connected client connections
connected_clients = []
server = None  # To store the server socket

def encodeHeaderData( data, headerFormat, *headers):

    return pack(headerFormat, *headers) + data.encode()

def getHeaderData( headerFormat, encoded):
    header_size = calcsize(PACK_FORMAT)
    # print(encoded)
    header = unpack(headerFormat, encoded[:header_size])
    # print(encoded[header_size:].decode())
    data = encoded[header_size:]
    # msg = data.decode("latin-1")
    # print(data)
    return header, data 

def handle_client(conn, addr):
    connected_clients.append(conn)
    # print(f"[NEW CONNECTION] {addr} connected.")
    latest_msg = 0
    connected = True
    iteration = 0
    last_msg_time = time.time()  # Track the time of the last received message
    header = ""
    while connected:
        # try:
            # conn.settimeout(TIMEOUT_SECONDS)  # Set the timeout for this connection
        data = conn.recv(SIZE)
            # # data = data.encode('latin-1')
        # header, msg = getHeaderData( PACK_FORMAT, data)
            # continue
            # pass 
        print(calcsize(PACK_FORMAT))
        msg = data[12:]
        print(msg)
        msg = msg.decode('utf-8')
        
        # print(msg)
        # msg = msg.decode()
        # except socket.timeout:
            # print(f"{hex(int(str(header[4])))} Connection timed out. GOODBYE from server.")
        #     msg = TERMINATION_MSG
            
        #     conn.send(msg.encode())
        #     connected = False
        #     continue
        # except Exception as e:
            # print(f"{hex(int(str(header[4])))} {e} EOF Spotted")
            
        #     connected = False
        #     continue

        to_print = msg
        if to_print == START_MSG:
            to_print = "Session created"
        elif to_print == TERMINATION_MSG:
            to_print = "GOODBYE from client"
        # print(f"{hex(int(str(header[4])))} [{int(str(header[3]))}] {to_print}")
        # if(int(str(header[3])) > latest_msg + 1):
        #     print("Packet lost : ", end="")
        #     for i in range (latest_msg + 1, int(str(header[3]))):
        #         print(i, end=" ")
        # latest_msg = int(str(header[3]))
        if msg != START_MSG and msg != TERMINATION_MSG:
            msg = "ALIVE"
        elif iteration != 0:
            connected = False
            msg = TERMINATION_MSG
        send_msg = encodeHeaderData( msg, PACK_FORMAT, 5, 6,7,8,9)
        conn.send(send_msg)
        iteration += 1
        last_msg_time = time.time()  # Update the last message time

        # Check if the time since the last message exceeds the timeout
    #     if time.time() - last_msg_time > TIMEOUT_SECONDS:
    #         print(f"{hex(int(str(header[4])))} Connection timed out (no message received). Closing session.")
    #         connected = False

    # print(f"{hex(int(str(header[4])))} Session closed")
    conn.close()
    connected_clients.remove(conn)

def close_server_and_connections(signal, frame):
    print("Closing server and all connections, then exiting...")
    for conn in connected_clients:
        try:
            conn.send(TERMINATION_MSG.encode())
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
                    conn.send(TERMINATION_MSG.encode())
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
