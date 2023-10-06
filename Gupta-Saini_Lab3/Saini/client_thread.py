import socket
import sys
import threading
import time

IP = socket.gethostbyname(sys.argv[1])
PORT = int(sys.argv[2])
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
TERMINATION_MSG = "GOODBYE"
DISCONNECT_MSG = "eof"
START_MSG = "HELLO"
TIMEOUT_SECONDS = 5

def send_messages(client_socket, sent_timestamp):
    iteration = 0
    while True:
        if iteration == 0:
            msg = START_MSG
        else:
            msg = input("")

        if msg == TERMINATION_MSG or msg == DISCONNECT_MSG:
            msg = TERMINATION_MSG
            client_socket.send(msg.encode(FORMAT))
            break

        try:
            client_socket.send(msg.encode(FORMAT))
            sent_timestamp[0] = time.time()
            iteration += 1
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
                client_socket.send(TERMINATION_MSG.encode(FORMAT))
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
