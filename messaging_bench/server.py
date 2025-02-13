
import socket
import sys
import time
import json
from debugpy.common.messaging import JsonIOStream

class ProcessServer:
    def __init__(self, delay : float):
        self.delay = delay
        message = {
            "seq": 0,
            "type": "request",
            "command": "ping",
            "arguments": {}
        }
        body = json.dumps(message).encode("utf-8")
        header = f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")
        self.payload = header + body
        
        
    def run(self):
        while True:
            #write the payload to stdout
            sys.stdout.buffer.write(self.payload)
            time.sleep(self.delay)
            
class DebugPyServer:
    def __init__(self, delay : float):
        self.delay = delay
        self.message = {
            "seq": 0,
            "type": "request",
            "command": "ping",
            "arguments": {}
        }
        # create a JSON stream from stdin and stdout of this prrgram
        self.server_stream = JsonIOStream.from_stdio()
        
        
    def run(self):
        while True:
            #write the payload to stdout
            self.server_stream.write_json(self.message)
            time.sleep(self.delay)
            
class DebugPySocketServer:
    def __init__(self, delay : float):
        self.delay = delay
        self.message = {
            "seq": 0,
            "type": "request",
            "command": "ping",
            "arguments": {}
        }
        host = 'localhost'
        port = 5678
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen()
        # Accept incoming connections
        print("Server is listening on port %d" % port)
        client_socket, _ = self.server_socket.accept()
        print("Accepted connection from client")
        # create a JSON stream from this socket
        self.buffer = JsonIOStream.from_socket(client_socket)
        
        
    def run(self):
        while True:
            #write the payload to stdout
            self.buffer.write_json(self.message)
            time.sleep(self.delay)       

            
if __name__ == "__main__":
    #s = ProcessServer(0.01) # 10ms delay  
    #s = DebugPyServer(0.03) # 30ms delay
    s = DebugPySocketServer(0.001) # 1ms delay
    s.run()