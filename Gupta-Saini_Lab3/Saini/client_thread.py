import socket
import sys

IP = socket.gethostbyname(sys.argv[1])
PORT = int(sys.argv[2])
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
TERMINATION_MSG = "GOODBYE"
DISCONNECT_MSG = "eof"
START_MSG = "HELLO"
TIMEOUT_SECONDS = 5  # Set the initial timeout to 60 seconds

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    # client.settimeout(TIMEOUT_SECONDS)
    print(f"[CONNECTED] Client connected to server at {IP}:{PORT}")

    connected = True
    iteration = 0
    while connected:
        # try:
        #     msg = client.recv(SIZE).decode(FORMAT)
        #     print('after', iteration, msg)
        #     if msg == TERMINATION_MSG:
        #         connected = False
        #         continue
        # except:
        #     pass    
        if (iteration == 0):
            msg = START_MSG
        else:
            msg = input("> ")

        if msg == TERMINATION_MSG or msg == DISCONNECT_MSG:
            connected = False
            msg = TERMINATION_MSG
        try:
            client.send(msg.encode(FORMAT))
            msg = client.recv(SIZE).decode(FORMAT)
            print(f"[SERVER] {msg}")
            iteration += 1
        except:
            pass

if __name__ == "__main__":
    main()