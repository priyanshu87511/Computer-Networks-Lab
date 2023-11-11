from datetime import datetime

class HttpHeader:
    def __init__(self, req):
        self.request = req

    def __str__(self):
        return self.request

    def get_start_line(self):
        idx = self.request.find('\n')
        if idx == -1:
            idx = len(self.request)
        return self.request[:idx]
    
    def get_start_line_without_version(self):
        line = self.get_start_line()
        idx = self.request.lower().find('http')
        if idx == -1:
            return line
        return self.request[:idx]

    def get_host_line(self):
        idx = self.request.lower().find("host")
        if idx == -1:
            return None
        tmp = self.request[idx:]
        idx2 = tmp.find('\n')
        return tmp[:idx2]

    def transform_request_header(self):
        tmp = self.request.replace("/1.1", "/1.0").replace("keep-alive", "close")
        return HttpHeader(tmp)

    def is_connect(self):
        return self.request.split(' ')[0].lower() == 'connect'

    def get_request(self):
        return self.request

    def get_version(self):
        idx = self.request.lower().find("http/")
        return self.request[idx:idx+8]

    def get_host(self):
        host_line = self.get_host_line()
        if host_line is None:
            return host_line
        start = host_line.lower().find("host:")
        return host_line[start + 6:-1]
    
    def get_port_num(self):
        request = self.request
        port = 80
        l_request = request.lower()
        lines = l_request.split('\n')
        line = lines[0]
        splits = line.split(" ")
        splits = splits[1].split(":")
        last_part = splits[-1].strip()
        try:
            port = (int)(last_part)
        except:
            pass
        for i in range(1, len(lines)):
            line = lines[i].replace(" ", "")
            if line.startswith("host"):
                parts = line.split(":")
                last_part = parts[-1].strip()
                try:
                    port = (int)(last_part)
                except:
                    pass
        return port

    @staticmethod
    def print_date_stamp():
        now = datetime.now()
        time = now.strftime("%H:%M:%S")
        print(f"{now.day} {now.strftime('%b')} {time} - ", end="")
