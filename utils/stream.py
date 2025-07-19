import threading
from time import sleep

class Stream:    
    def __init__(self):                   
        self.list = []
        self.action_func = None
        self.next_stream = None
        self.thread = threading.Thread(target=self._run)       
        self.stop_flag = False                
        self.thread.start()
    
    # Processing
    def _run(self):
        while not self.stop_flag: 
            if self.action_func and self.list:                
                item = self.list.pop(0)
                self.action_func(item)
            else:
                pass # Wait

    # Add a new functon to the list  
    def add(self, x):        
        self.list.append(x)            

    # Create a new stream and add an item to it depending on the result
    def apply(self, f):
        self.next_stream = Stream()

        def apply_func(item):
            result = f(item)
            if result is True:
                self.next_stream.add(item)
            elif result is False:
                pass
            elif result is not None:
                self.next_stream.add(result)        
        
        self.action_func = apply_func
        return self.next_stream             
    
    # Consumer-style function for processing
    def forEach(self, f):
        self.action_func = f

    # Stop all threads
    def stop(self):
        self.stop_flag = True
        if self.next_stream:
            self.next_stream.stop()
