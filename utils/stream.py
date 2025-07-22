import threading
from time import sleep

class Stream:
    """
    A simple asynchronous stream processor for handling queued tasks in a background thread.

    Methods:
        add(x): Add an item to the stream queue.
        apply(f): Create a new stream and apply a function to each item.
        forEach(f): Set a consumer-style function for processing items.
        stop(): Stop the stream and any chained streams.
    """    
    def __init__(self):
        """
        Initialize the stream, start the background thread, and set up internal state.
        """                   
        self.list = []
        self.action_func = None
        self.next_stream = None
        self.thread = threading.Thread(target=self._run)       
        self.stop_flag = False                
        self.thread.start()
    
    # Processing
    def _run(self):
        """
        Internal method: Continuously process items in the queue using the action function.
        """
        while not self.stop_flag: 
            if self.action_func and self.list:                
                item = self.list.pop(0)
                self.action_func(item)
            else:
                pass # Wait

    # Add a new functon to the list  
    def add(self, x):   
        """
        Add an item to the stream queue.

        Args:
            x: The item to add.
        """     
        self.list.append(x)            

    # Create a new stream and add an item to it depending on the result
    def apply(self, f):
        """
        Create a new stream and apply a function to each item.
        If the function returns True, the item is passed to the next stream.
        If it returns False, the item is dropped.
        If it returns another value, that value is passed to the next stream.

        Args:
            f (callable): Function to apply to each item.

        Returns:
            Stream: The next stream in the chain.
        """
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
        """
        Set a consumer-style function for processing items in the stream.

        Args:
            f (callable): Function to process each item.
        """
        self.action_func = f

    # Stop all threads
    def stop(self):
        """
        Stop the stream and any chained streams.
        """
        self.stop_flag = True
        if self.next_stream:
            self.next_stream.stop()
