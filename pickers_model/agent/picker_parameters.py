
import random
import numpy 

class PickerParameterGenerator:
    
    def __init__( self ):
        
        self.list_of_speeds = [ 32.31292517006803,
                          45.31051964512041,
                          43.84268214055448,
                          58.265582655826556,
                          54.91024287222809,
                          34.83106931382793,
                          41.457706452691404,
                          41.25230202578269,
                          51.11354508944871,
                          46.322378716744915,
                          29.875797247398456,
                          43.02168021680217 ]
        
        self.mu = numpy.mean( self.list_of_speeds )
        self.sigma = numpy.std( self.list_of_speeds )
        
    def random_picking_speed( self ): 
        
        return abs( random.gauss( self.mu, self.sigma ) ) 
    
    def random_max_walking_speed( self ): 
        
        return abs( random.gauss( 0.85, 0.05 ) ) 
