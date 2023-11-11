import socket
from threading import Thread

class Forward(Thread):
    def __init__(self, sender, receiver):
        super().__init__()
        self.sender = sender
        self.receiver = receiver

        try:
            self.sender.settimeout(60)
            self.receiver.settimeout(60)
        except socket.error as e:
            pass

    def run(self):
        try:
            from_sender = self.sender.makefile('rb')
            out_to_receiver = self.receiver.makefile('wb')

            while True:
                data = from_sender.read(4096)
                if not data:
                    break
                out_to_receiver.write(data)
                out_to_receiver.flush()

            from_sender.close()
            out_to_receiver.close()

        except socket.error as e:
            pass

    @staticmethod
    def byte_array_to_hex(a):
        return ' '.join(format(x, '02x') for x in a)
