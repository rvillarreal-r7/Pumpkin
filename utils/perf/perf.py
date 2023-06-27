#!/usr/bin/env python3

# upon load make sure the time package is installed
try:
    time.time() # can I do this? 
except:
    import time


class Perf():
    def __init__(self):
        self.start_time = None
        self.stop_time = None
        self.duration_time = None
    
    def measure(self):
        self.start_time = time.time()

    def stop_timer(self):
        return time.time()
    
    def duration(self):
        print(f'Time (seconds): {self.stop_timer() - self.start_time}')


if __name__ == "__main__":
    # testing perf measuring
    performance = Perf()
    performance.measure()
    time.sleep(5)
    performance.duration()


# class Perf():
#     def __init__(self):
#         self.msg = str()
#         self.start_time = None
#         self.stop_time = None
#         self.duration_time = None

#     def __call__(self):
#         print('uhhhk')

#     def set_duration(self,value):
#         self.duration_time = value # using the constructor format for accuracy 
    
#     def get_duration(self):
#         return self.duration_time
    
#     def stop(self):
#         stop_time = time.time() # get time first for closer execution
#         self.set_duration(stop_time - self.start_time)

#     def measure(self):
#         print(self.duration_time)

#     def start(self,msg=None):
#         # handle messages first, since we can remove the overhead before start timer
#         if msg:
#             self.msg = self.msg + msg
#         # this has to be last. 
#         self.start_time = time.time()

#         # print('{0:1f}'.format(self.get_duration()))
#         #print(f"Duration: {:.10f} seconds")
#         #print(f'duration: {self.stop_timer() - self.start_time} sec')