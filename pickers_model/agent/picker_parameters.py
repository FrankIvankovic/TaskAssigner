
import random
import numpy 

class PickerParameterGenerator:
    
    def __init__( self ):
        
        self.list_of_speeds = [ 7.3438466295609155,
                               6.608747308234944,
                               11.96227283183805,
                               6.360777587192682,
                               10.786444498108347,
                               9.144741773480249,
                               9.755716850074144,
                               9.191852342083976,
                               8.650260999254288,
                               9.508093666509508,
                               7.76982844834218,
                               9.456801331517628 ]
        
        self.mu = numpy.mean( self.list_of_speeds )
        self.sigma = numpy.std( self.list_of_speeds )
        
    def random_picking_speed( self ): 
        
        return abs( random.gauss( self.mu, self.sigma ) ) 
    
    def random_max_walking_speed( self ): 
        
        return abs( random.gauss( 0.85, 0.05 ) ) 
