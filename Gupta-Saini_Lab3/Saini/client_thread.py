import socket
import sys
import threading
import time
from random import random
from struct import pack, unpack, calcsize

IP = socket.gethostbyname(sys.argv[1])
PORT = int(sys.argv[2])
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
PACK_FORMAT = "!HBBII"
TERMINATION_MSG = "GOODBYE"
ALIVE_MSG = "ALIVE"
DISCONNECT_MSG = "eof"
MAGIC_NUMBER = 50273
VERSION = 1
START_MSG = "HELLO"
TIMEOUT_SECONDS = 5

def encodeHeaderData(dataFormat, data, headerFormat, *headers):
    return pack(headerFormat, *headers) + data.encode(dataFormat)

def getHeaderData(dataFormat, headerFormat, encoded):
    header_size = calcsize(headerFormat)
    header = unpack(headerFormat, encoded[:header_size])
    data = encoded[header_size:].decode(dataFormat)
    return header, data

def getSessionId():
    return int(random() * pow(2, 30))

def getCommand(message):
    command = 1
    if message == START_MSG:
        command = 0
    elif message == ALIVE_MSG:
        command = 2
    elif message == TERMINATION_MSG:
        command = 3
    return command

def send_messages(client_socket, sent_timestamp):
    sequnceNumber = 0
    while True:
        if sequnceNumber == 0:
            msg = START_MSG
        else:
<<<<<<< HEAD
            msg = input(">")
=======
            try:
                msg = input()
            except EOFError:
                # Handle EOF (end of file) from input
                msg = DISCONNECT_MSG
>>>>>>> 9ea82388fb9fa687f02f630a02d5464de3b83382

        if msg == TERMINATION_MSG or msg == DISCONNECT_MSG:
            msg = TERMINATION_MSG
            command = getCommand(msg)
            sessionId = getSessionId()
            headerData = encodeHeaderData(FORMAT, msg, PACK_FORMAT, MAGIC_NUMBER, VERSION, command, sequnceNumber, sessionId)
            client_socket.send(headerData.decode('latin-1').encode(FORMAT))
            break

        try:
            command = getCommand(msg)
            sessionId = getSessionId()
            headerData = encodeHeaderData(FORMAT, msg, PACK_FORMAT, MAGIC_NUMBER, VERSION, command, sequnceNumber, sessionId)
            client_socket.send(headerData.decode('latin-1').encode(FORMAT))
            sent_timestamp[0] = time.time()
<<<<<<< HEAD
            sequnceNumber += 1
=======
            iteration += 1
        
>>>>>>> 9ea82388fb9fa687f02f630a02d5464de3b83382
        except:
            break

def receive_messages(client_socket, sent_timestamp):
    while True:
        try:
            msg = client_socket.recv(SIZE).decode(FORMAT)
            if not msg:
                break

            print(f"[SERVER] {msg}")

            if msg == TERMINATION_MSG:
                print("Received 'GOODBYE' from server. Exiting...")
                client_socket.close()  # Close the socket
                exit(1)  # Terminate the program

            received_timestamp = time.time()
            time_diff = received_timestamp - sent_timestamp[0]

            if time_diff > TIMEOUT_SECONDS:
                print("Timeout exceeded. Exiting...")
                msg = TERMINATION_MSG
                command = getCommand(msg)
                sessionId = getSessionId()
                headerData = encodeHeaderData(FORMAT, msg, PACK_FORMAT, MAGIC_NUMBER, VERSION, command, sequnceNumber, sessionId)
                client_socket.send(headerData.decode('latin-1').encode(FORMAT))
                client_socket.close()  # Close the socket
                sys.exit(0)  # Terminate the program

        except:
            break

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    print(f"[CONNECTED] Client connected to server at {IP}:{PORT}")

    sent_timestamp = [0]  # Store the timestamp of the last sent message

    send_thread = threading.Thread(target=send_messages, args=(client, sent_timestamp))
    receive_thread = threading.Thread(target=receive_messages, args=(client, sent_timestamp))

    send_thread.start()
    receive_thread.start()

    send_thread.join()  # Wait for the send thread to finish
    receive_thread.join()  # Wait for the receive thread to finish

    client.close()  # Close the socket when both threads are done

if __name__ == "__main__":
    main()
