
import random
import numpy 

class PatienceTime:
    
    def __init__( self, percentage, max_waiting_time ):
        
        self.wait_until = max_waiting_time * percentage
        self.waited_so_far = 0.0
        
    def add_time( self, t ):
        
        self.waited_so_far += t
    
    def reset_waiting( self ): 
        
        self.waited_so_far = 0.0 
        
    def waited_too_long( self ): 
        
        return self.waited_so_far > self.wait_until

#TODO: A model that incorporates the distance to the packing station as well. 
class PatienceDistance:
    
    def __init__( self, percentage, max_waiting_time ):
        
        self.wait_until = max_waiting_time * percentage
        self.waited_so_far = 0.0
        
    def add_time( self, t ):
        
        self.waited_so_far += t
    
    def reset_waiting( self ): 
        
        self.waited_so_far = 0.0 
        
    def waited_too_long( self ): 
        
        return self.waited_so_far > self.wait_until

class PatienceTimeRandom( PatienceTime ): 
    
    def __init__( self, percentage, max_waiting_time, sigma = 6.0 ):
        super().__init__(percentage, max_waiting_time)
        self.wait_until = abs( random.gauss( percentage*max_waiting_time, sigma ) )

        
