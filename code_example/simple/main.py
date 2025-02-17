from monitoringpy import init_monitoring
init_monitoring()

class Test:
    def __init__(self):
        self.inside = 10
    
    def long_function(self,x):
        i = 0
        for i in range(30):
            i += 1
        return i
    
    def normal_function(self, x):
        a = 0
        b = 0
        if x > 100:
            a = x+1
            b = x-1
        else:
            a = x + self.long_function(x+1)
            b = x + self.long_function(x)
        return a+b

def add(a,b):
    return a+b

if __name__ == "__main__":
    tt1 = Test()
    tt1.normal_function(2)
    tt1.normal_function(20)
    add(1,2)