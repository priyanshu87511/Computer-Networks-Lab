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
PACK_FORMAT = "!HBBII"
TERMINATION_MSG = "GOODBYE"
ALIVE_MSG = "ALIVE"
DISCONNECT_MSG = "eof"
MAGIC_NUMBER = 50273
VERSION = 1
START_MSG = "HELLO"
TIMEOUT_SECONDS = 5
sequnceNumber = 0
sessionId = None

def encodeHeaderData( data, headerFormat, *headers):

    return pack(headerFormat, *headers) + data.encode('utf-8')

def getHeaderData( headerFormat, encoded):
    header_size = calcsize(headerFormat)
    header = unpack(headerFormat, encoded[:header_size])
    # print(encoded[header_size:])
    data = encoded[header_size:].decode()
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
    global sequnceNumber
    while True:
        if sequnceNumber == 0:
            msg = START_MSG
        else:
            try:
                # print("HII")
                # msg = sys.stdin.readline().strip()
                msg = input()
                msg = msg.replace('\n', 'a')
                msg = msg.replace('\r', 'b')
                msg = msg.replace('\r\n', 'c')
                # print(msg)
                # print('input', msg)
            except EOFError:
                # print("hii")
                # Handle EOF (end of file) from input
                msg = DISCONNECT_MSG

        if msg == TERMINATION_MSG or msg == DISCONNECT_MSG:
            msg = TERMINATION_MSG
            command = getCommand(msg)
            headerData = encodeHeaderData( msg, PACK_FORMAT, MAGIC_NUMBER, VERSION, command, sequnceNumber, sessionId)
            client_socket.send(headerData)
            break

        try:
            command = getCommand(msg)
            headerData = encodeHeaderData( msg, PACK_FORMAT, MAGIC_NUMBER, VERSION, command, sequnceNumber, sessionId)
            client_socket.send(headerData)
            sent_timestamp[0] = time.time()
            sequnceNumber += 1
        except:
            break

def receive_messages(client_socket, sent_timestamp):
    global sequnceNumber
    while True:
        try:
            msg = client_socket.recv(SIZE)
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
                headerData = encodeHeaderData( msg, PACK_FORMAT, MAGIC_NUMBER, VERSION, command, sequnceNumber, sessionId)
                client_socket.send(headerData)
                client_socket.close()  # Close the socket
                sys.exit(0)  # Terminate the program

        except:
            break

def main():
    global sessionId
    sessionId = getSessionId()
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
