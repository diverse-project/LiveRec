import time
import numpy as np
import subprocess
from debugpy.common.messaging import JsonIOStream
from debugpy.common import sockets

class ProcessClient:
    def __init__(self, cmd : str, iterations : int = 100):
        self.cmd = cmd
        self.iterations = iterations
        self.stats = []
        
    def run(self):
        """Launch the process from the cmd, create a buffer reader from stdout and read the output"""
        self.process = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        buffer = self.process.stdout
        if buffer is None:
            return
        i = 0
        while i < self.iterations:
            i += 1
            t1 = time.time()
            print("RR :", buffer.readline())
            t2 = time.time()
            self.stats.append(t2 - t1)
        # shutdown the process
        self.process.terminate()
        
class DebugPyClient:
    def __init__(self, cmd : str, iterations : int = 100):
        self.cmd = cmd
        self.iterations = iterations
        self.stats = []
        
    def run(self):
        """Launch the process from the cmd, create a buffer reader from stdout and read the output"""
        self.process = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        buffer = JsonIOStream.from_process(self.process)
        if buffer is None:
            return
        i = 0
        print("step ", i, end="")
        while i < self.iterations:
            print("\rstep ", i, end="")
            i += 1
            t1 = time.time()
            line = buffer.read_json()
            t2 = time.time()
            self.stats.append(t2 - t1)
            if not line:
                break
        # shutdown the process
        self.process.terminate()
        
class DebugPySocketClient:
    def __init__(self, cmd : str, iterations : int = 100):
        self.cmd = cmd
        self.iterations = iterations
        self.stats = []
        
    def run(self):
        """Launch the process from the cmd, create a buffer reader from stdout and read the output"""
        self.process = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        time.sleep(1)
        port = 5678
        host = "localhost"
        main_server = sockets.create_client()
        main_server.connect((host, port))
        buffer = JsonIOStream.from_socket(main_server)
        if buffer is None:
            return
        i = 0
        print("step ", i, end="")
        while i < self.iterations:
            print("\rstep ", i, end="")
            i += 1
            t1 = time.time()
            line = buffer.read_json()
            t2 = time.time()
            self.stats.append(t2 - t1)
            if not line:
                break
        # shutdown the process
        self.process.terminate()
    
            
if __name__ == "__main__":
    #p = ProcessClient("python server.py")
    #p = DebugPyClient("python server.py")
    p = DebugPySocketClient("python server.py")
    p.run()
    delay = 0.001 # delay of message generation in server.py
    json_overhead = [(t-delay)*1000 for t in p.stats[1:]] # in ms
    print("Mean: ", np.mean(json_overhead))
    print("Std: ", np.std(json_overhead))
    print("Min: ", np.min(json_overhead))
    print("Max: ", np.max(json_overhead))