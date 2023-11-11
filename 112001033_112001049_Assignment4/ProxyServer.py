import sys
import socket
from datetime import datetime
from threading import Thread
from HttpHeader import HttpHeader

class ProxyServer:
    def main(self, args):
        if len(args) != 1:
            raise ValueError("Insufficient arguments")
        
        port = int(args[0])
        
        if not (1024 <= port <= 65535):
            raise ValueError("Invalid port number")
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
                tcp_socket.bind(('localhost', port))
                tcp_socket.listen()
                print("Proxy listening on", tcp_socket.getsockname())
                
                while True:
                    connection, _ = tcp_socket.accept()
                    task = Proxy(connection)
                    task.start()
        except OSError as ex:
            print("Couldn't start server:", ex)

class Proxy(Thread):
    TIMEOUT = 20  

    def __init__(self, connection):
        super().__init__()
        self.connection = connection

    def parse_port_num(self, request):
        return 80

    def run(self):
        try:
            request_bytes = self.connection.recv(2048)
            
            if not request_bytes:
                self.connection.close()
                return
            
            request_string = request_bytes.decode('utf-8', errors='replace')
            request = HttpHeader(request_string)
            
            host = request.get_host()
            if host is None:
                return
            HttpHeader.print_date_stamp()
            print(">>>", request.get_start_line())
            port = self.parse_port_num(request)
            if ':' in host:
                host = host.split(':')[0]

            proxy_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            if not request.is_connect():
                request = request.transform_request_header()
                proxy_to_server.connect((host, request.get_port_num()))
                
                data = request.get_request().encode()

                proxy_to_server.send(data)
                forward = Forward(proxy_to_server, self.connection)
                forward.start()
            else:
                if not proxy_to_server:
                    response_to_browser = "HTTP/1.0 502 Bad Gateway\r\n\r\n"
                    self.connection.sendall(response_to_browser.encode())
                    return
                proxy_to_server.connect((host, request.get_port_num()))
                response = "HTTP/1.0 200 OK\r\n\r\n"
                self.connection.sendall(response.encode())

                read_from_server = Forward(proxy_to_server, self.connection)
                read_from_client = Forward(self.connection, proxy_to_server)
                read_from_client.start()
                read_from_server.start()

        except Exception as e:
            pass

class Forward(Thread):
    def __init__(self, source, destination):
        super().__init__()
        self.source = source
        self.destination = destination

    def run(self):
        while True:
            try:
                data = self.source.recv(2048)
                if data:
                    self.destination.sendall(data)
                else:
                    self.source.close()
                    self.destination.close()
                    break
            except Exception as e:
                break

if __name__ == "__main__":
    PORT = sys.argv[1]
    proxy_server = ProxyServer()
    proxy_server.main([f'{PORT}'])
