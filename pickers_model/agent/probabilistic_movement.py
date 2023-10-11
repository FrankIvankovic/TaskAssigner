
import math
import random
import numpy

def find_speeds_directions( strawberry_field, readings_list ):

    time_difference_cutoff = 0.01
    new_readings_list = []

    low_time_difference = []
    normal_time_difference = []

    high_speed = []

    for i,r in enumerate(readings_list):

       if i==0:

            r[ "speed" ] = 0.0
            r[ "direction" ] = (1.0,0.0)

       else:

            previous_r = readings_list[i-1]

            previous_time = previous_r[ "tseconds" ]
            previous_lat = float( previous_r[ "LATITUDE" ] )
            previous_long = float( previous_r[ "LONGITUDE" ] )

            #print( previous_time, type( previous_time ), float( previous_time ), type( float( previous_time ) ) )
            #print( previous_lat, type( previous_lat ), float( previous_lat ), type( float( previous_lat ) ) )
            #print( previous_long, type( previous_long ), float( previous_long ), type( float( previous_long ) ) )

            current_time = r[ "tseconds" ]
            current_lat = float( r[ "LATITUDE" ] )
            current_long = float( r[ "LONGITUDE" ] )

            #print( readings_list[i] )

            #print( i, previous_time, current_time, previous_lat, current_lat, previous_long, current_long )

            time_diff = current_time - previous_time

            lat_diff = (current_lat - previous_lat) * strawberry_field.latdif_to_meters
            long_diff = (current_long - previous_long) * strawberry_field.longdif_to_meters

            total_distance = math.sqrt( lat_diff**2 + long_diff**2 )

            #NOTE: Had to do this to avoid div by zero error.
            if time_diff == 0:
                current_speed = 0.0
            else:
                current_speed = total_distance / time_diff
            if total_distance == 0:
                current_direction = ( 0.0, 0.0 )
            else:
                current_direction = ( long_diff / total_distance, lat_diff /total_distance ) #unit vector

            r[ "speed" ] = current_speed
            r[ "direction" ] = current_direction

            if time_diff < time_difference_cutoff:
                low_time_difference.append( r )
            else:
                normal_time_difference.append( r )

            if current_speed > 8.0  and time_diff > time_difference_cutoff:
                print( current_speed, time_diff, lat_diff, long_diff )

            if current_speed > 8.0 and time_diff > time_difference_cutoff:
                high_speed.append( r )
                #if time_diff > time_difference_cutoff:
                #    raise Exception( "HIGH SPEED, HIGH TIME DIFF", current_speed, time_diff )

    print( "len( low_time_difference )", len( low_time_difference ), "len( normal_time_difference )", len( normal_time_difference ), "len( high_speed )", len( high_speed ) )

    print( "HIGH SPEED STUFF:")
    for r in high_speed:
        print( r )

    new_readings_list = normal_time_difference

    return new_readings_list

class PickerProbabilisticMovement:

    def __init__( self, strawberry_field, readings_list, time_step_size ) :

        self.strawberry_field = strawberry_field
        self.readings_list = find_speeds_directions( strawberry_field, readings_list ) #list of moves for a given picker

        self.all_speeds = [ i[ "speed" ] for i in readings_list ]
        self.all_speeds_mu = numpy.mean( self.all_speeds )
        self.all_speeds_sigma = numpy.std( self.all_speeds )

        self.all_directions = [ i[ "direction" ] for i in readings_list ]

    def select_move_normal_distribution( self, cucurrent_x, current_y, time_step_size ):

        #TODO: TEST AGAIN!

        random_direction = random.uniform( -math.pi, math.pi )
        direction_x = math.cos( random_direction )
        direction_y = math.sin( random_direction )

        total_speed = random.normal( self.all_speeds_mu, self.all_speeds_sigma )

        speed_x = total_speed * direction_x
        speed_y = total_speed * direction_y

        new_x = current_x + speed_x * time_step_size
        new_y = current_y + speed_y * time_step_size

        return ( new_x, new_y )

    def select_move_from_list( self, current_x, current_y, time_step_size ):

        total_speed = random.choice( self.all_speeds )
        direction_x, direction_y = random.choice( self.all_directions )

        speed_x = total_speed * direction_x
        speed_y = total_speed * direction_y

        new_x = current_x + speed_x * time_step_size
        new_y = current_y + speed_y * time_step_size

        return ( new_x, new_y )

    def select_move( self, current_x, current_y, time_step_size ):

        return self.select_move_from_list( current_x, current_y, time_step_size )

# Test.

if __name__ == '__main__' :

    #TODO: Line 158, if uncommented, acts wierd? This is because find_speeds_directions is
    #called twice, once on line 158, once by PickerProbabilisticMovement. However, see what
    # exactly happens.

    # the_field = fm.make_field_423_2020( sf.SpaceType.CONTINUOUS2D )
    picker_data = "data_logged_placeuk_day1.json"

    readings_list = pr.read_json_pickers( picker_data )

    ppms = []
    time_step_size = 1.0

    for picker in readings_list.keys():
        print( picker, len( readings_list[ picker ] ) )
        #readings_list[ picker ] = find_speeds_directions( the_field, readings_list[ picker ] )

        ppms.append( PickerProbabilisticMovement( the_field, readings_list[ picker ], time_step_size ) )

    for picker in readings_list.keys():
        for r in readings_list[ picker ]:
            if r[ "speed" ] > 1.5:
                pass
                #print( picker, r[ "speed" ], r[ "direction" ])

    for ppm in ppms:
        print( ppm.select_move( 0, 0, 1.0 ) )
