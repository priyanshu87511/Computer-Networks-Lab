from http.server import HTTPServer, BaseHTTPRequestHandler
from http.client import HTTPConnection

class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.proxy_request()

    def do_POST(self):
        self.proxy_request()

    def proxy_request(self):
        # Extract the destination host and port from the request
        destination_host = self.headers['Host']
        destination_port = 80  # Default HTTP port

        # Connect to the destination server
        with HTTPConnection(destination_host, destination_port) as connection:
            # Forward the client request to the destination server
            connection.request(self.command, self.path, body=self.rfile.read(), headers=self.headers)

            # Get the response from the destination server
            response = connection.getresponse()

            # Send the response back to the client
            self.send_response(response.status)
            for header, value in response.getheaders():
                self.send_header(header, value)
            self.end_headers()
            self.wfile.write(response.read())

if __name__ == '__main__':
    # Set the host and port for the proxy server
    proxy_host = 'localhost'
    proxy_port = 8080

    # Create and start the proxy server
    proxy_server = HTTPServer((proxy_host, proxy_port), ProxyHandler)
    print(f"Proxy server is running on {proxy_host}:{proxy_port}")
    proxy_server.serve_forever()
