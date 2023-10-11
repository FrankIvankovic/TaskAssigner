
import mesa
import math

from pickers_model.strawberry_field.polytunnel import Polytunnel
from pickers_model.strawberry_field.strawberry_field import StrawberryField,SpaceType
from shapely.geometry import Point, Polygon 

def field423_long_lat():

    """Finding longitudes and latitudes of field 423. """

    # NOTE: NOT used in creating the object, I just used it for dubugging.

    # From https://www.johndcook.com/lat_long_distance.html , confirmed using Google Earth

    #0.001 difference in latitude 111.2298 meters
    lat_diff_to_meters = 111.2298 / 0.001

    #0.001 difference in longitude is 67.3654 meters
    long_diff_to_meters = 67.3654 / 0.001

    southg_nwcorner_long = 1.390852
    southg_nwcorner_lat = 52.725319

    southg_necorner_long = 1.392655
    southg_necorner_lat = 52.725479

    southg_nwcorner_long_radians = math.radians( 1.390852 )
    southg_nwcorner_lat_radians = math.radians( 52.725319 )

    southg_necorner_long_radians = math.radians( 1.392655 )
    southg_necorner_lat_radians = math.radians( 52.725479 )

    eastwest_long_difference = southg_necorner_long - southg_nwcorner_long
    northsouth_lat_difference = southg_necorner_lat - southg_nwcorner_lat

    eastwest_long_difference_meters = long_diff_to_meters * eastwest_long_difference
    northsouth_lat_difference_meters = lat_diff_to_meters * northsouth_lat_difference

    print("eastwest_long_difference_meters: ", eastwest_long_difference_meters )
    print("northsouth_lat_difference_meters: ", northsouth_lat_difference_meters )

    average_long = (southg_nwcorner_long + southg_necorner_long)/2
    average_lat = (southg_nwcorner_lat + southg_necorner_lat)/ 2

    print("average_long: ", average_long)
    print("average_lat: ", average_lat)

    tunnel_l = 8.85

    angle_phi = math.atan( northsouth_lat_difference_meters / eastwest_long_difference_meters )
    print("angle_phi: ", angle_phi, "radians")
    print("angle_phi: ", math.degrees(angle_phi), "degrees")

    #finding lower left coordinates

    tunnel_l = 8.85

    northgroup_longest = 94.8
    middlegroup_longest = 91.6
    southgroup_longest = 89.6

    pathnorth_width = 9.0
    pathsouth_width = 9.0

    empty_north = 2.0
    empty_south = 2.0

    southg_nwcorner_x = tunnel_l
    southg_nwcorner_y = empty_south + southgroup_longest

    new_x = southg_nwcorner_x * math.cos( angle_phi )  - southg_nwcorner_y * math.sin( angle_phi )
    new_y = southg_nwcorner_x * math.sin( angle_phi )  + southg_nwcorner_y * math.cos( angle_phi )

    print( "new_x", new_x )
    print( "new_y", new_y )

    new_long = southg_nwcorner_long - new_x / long_diff_to_meters
    new_lat = southg_nwcorner_lat - new_y / lat_diff_to_meters

    print( "new_long", new_long )
    print( "new_lat", new_lat )
    print( new_lat, new_long )

    return angle_phi, new_long, new_lat

def field428_long_lat():

    # NOTE: NOT used in creating the object, I just used it for dubugging.

    """Finding longitudes and latitudes of field 428. """

    #0.001 difference in latitude 111.2298 meters
    lat_diff_to_meters = 111.2298 / 0.001

    #0.001 difference in longitude is 67.3654 meters
    long_diff_to_meters = 67.3654 / 0.001

    southg_nwcorner_lat = 52.725963
    southg_nwcorner_long = 1.388012

    southg_necorner_lat = 52.726093
    southg_necorner_long = 1.390348

    southg_nwcorner_long_radians = math.radians( 52.725963 )
    southg_nwcorner_lat_radians = math.radians( 1.388012 )

    southg_necorner_long_radians = math.radians( 52.726093 )
    southg_necorner_lat_radians = math.radians( 1.390348 )

    eastwest_long_difference = southg_necorner_long - southg_nwcorner_long
    northsouth_lat_difference = southg_necorner_lat - southg_nwcorner_lat

    eastwest_long_difference_meters = long_diff_to_meters * eastwest_long_difference
    northsouth_lat_difference_meters = lat_diff_to_meters * northsouth_lat_difference

    print("eastwest_long_difference_meters: ", eastwest_long_difference_meters )
    print("northsouth_lat_difference_meters: ", northsouth_lat_difference_meters )

    average_long = (southg_nwcorner_long + southg_necorner_long)/2
    average_lat = (southg_nwcorner_lat + southg_necorner_lat)/ 2

    print("average_long: ", average_long)
    print("average_lat: ", average_lat)

    tunnel_l = 8.85

    angle_phi = math.atan( northsouth_lat_difference_meters / eastwest_long_difference_meters )
    print("angle_phi: ", angle_phi, "radians")
    print("angle_phi: ", math.degrees(angle_phi), "degrees")

    #finding lower left coordinates
    tunnel_l = 8.85

    northgroup_longest = 130.0
    southgroup_longest = 133.0

    path_width = 9.0

    empty_north = 2.0
    empty_south = 2.0

    southg_nwcorner_x = tunnel_l
    southg_nwcorner_y = empty_south + southgroup_longest

    new_x = southg_nwcorner_x * math.cos( angle_phi )  - southg_nwcorner_y * math.sin( angle_phi )
    new_y = southg_nwcorner_x * math.sin( angle_phi )  + southg_nwcorner_y * math.cos( angle_phi )

    new_long = southg_nwcorner_long - new_x / long_diff_to_meters
    new_lat = southg_nwcorner_lat - new_y / lat_diff_to_meters

    print( "new_x", new_x )
    print( "new_y", new_y )
    
    print( "new_long", new_long )
    print( "new_lat", new_lat )
    print( new_lat, new_long )

    return angle_phi, new_long, new_lat

def make_field_larger( small_field, offset_left = 0.0, offset_bottom = 0.0, additional_right = 0.0, additional_top = 0.0 ):

    """ Adds extra space to the field. Works as intended.
    WARNING: Do not use! Does not work! Use make_field_larger from StrawberryField class!
    """

    small_field_polytunnels = small_field.polytunnel_list

    new_polytunnel_list = []
    for t in small_field_polytunnels:
        x, y = t.lower_left
        new_polytunnel_list.append( Polytunnel( ( x + offset_left, y + offset_bottom ) , t.length, t.width ) )

    original_length, original_width = small_field.dimensions
    new_field = StrawberryField( original_length + offset_left + additional_right, original_width + offset_bottom + additional_top, polytunnel_list = new_polytunnel_list, spacetype = small_field.spacetype )

    return new_field

# -------
# Only the following two functions are actually used. The ones above were used for debugging.
# -------

def make_field_423_2020( spacetype  = SpaceType.CONTINUOUS2D ):
    
    """Returns a continuous2D of 423_2020."""
    
    # polytunnel dimensions --- from the excel spreadsheets
    
    # NOTE: Used.

    tunnel_l = 8.85 
    
    northgroup_longest = 94.8 
    middlegroup_longest = 91.6 
    southgroup_longest = 89.6 
    
    pathnorth_width = 9.0 
    pathsouth_width = 9.0 

    empty_north = 10.0
    empty_south = 10.0

    # Polytunnel groups corners.
    northg_swcorner_x = 270 + tunnel_l
    northg_swcorner_y = empty_south + southgroup_longest + pathnorth_width + middlegroup_longest + pathsouth_width 

    middleg_swcorner_x = 270
    middleg_swcorner_y = empty_south + southgroup_longest + pathnorth_width 

    southg_nwcorner_x = 270
    southg_nwcorner_y = empty_south + southgroup_longest 

    # List of polytunnels, north to south, east to west.
    polytunnels_north = [ Polytunnel ( (northg_swcorner_x + 0 * tunnel_l,northg_swcorner_y), tunnel_l, 90, entrance_side = "SOUTH" ), 
                          Polytunnel ( (northg_swcorner_x + 1 * tunnel_l,northg_swcorner_y), tunnel_l, 90, entrance_side = "SOUTH" ),
                          Polytunnel ( (northg_swcorner_x + 2 * tunnel_l,northg_swcorner_y), tunnel_l, 90, entrance_side = "SOUTH" ),
                          Polytunnel ( (northg_swcorner_x + 3 * tunnel_l,northg_swcorner_y), tunnel_l, 92.6, entrance_side = "SOUTH" ),
                          Polytunnel ( (northg_swcorner_x + 4 * tunnel_l,northg_swcorner_y), tunnel_l, 92.6, entrance_side = "SOUTH" ),
                          Polytunnel ( (northg_swcorner_x + 5 * tunnel_l,northg_swcorner_y), tunnel_l, 92.6, entrance_side = "SOUTH" ),
                          Polytunnel ( (northg_swcorner_x + 6 * tunnel_l,northg_swcorner_y), tunnel_l, 94.8, entrance_side = "SOUTH" ),
                          Polytunnel ( (northg_swcorner_x + 7 * tunnel_l,northg_swcorner_y), tunnel_l, 94.8, entrance_side = "SOUTH" ),
                          Polytunnel ( (northg_swcorner_x + 8 * tunnel_l,northg_swcorner_y), tunnel_l, 94.8, entrance_side = "SOUTH" ),
                          Polytunnel ( (northg_swcorner_x + 9 * tunnel_l,northg_swcorner_y), tunnel_l, 94.8, entrance_side = "SOUTH" ) ]

    polytunnels_middle = [ Polytunnel ( (middleg_swcorner_x + 0 * tunnel_l,middleg_swcorner_y) , tunnel_l, 78.4 ), 
                           Polytunnel ( (middleg_swcorner_x + 1 * tunnel_l,middleg_swcorner_y) , tunnel_l, 78.4 ), 
                           Polytunnel ( (middleg_swcorner_x + 2 * tunnel_l,middleg_swcorner_y) , tunnel_l, 91.6 ), 
                           Polytunnel ( (middleg_swcorner_x + 3 * tunnel_l,middleg_swcorner_y) , tunnel_l, 91.6 ), 
                           Polytunnel ( (middleg_swcorner_x + 4 * tunnel_l,middleg_swcorner_y) , tunnel_l, 91.6 ), 
                           Polytunnel ( (middleg_swcorner_x + 5 * tunnel_l,middleg_swcorner_y) , tunnel_l, 91.6 ), 
                           Polytunnel ( (middleg_swcorner_x + 6 * tunnel_l,middleg_swcorner_y) , tunnel_l, 91.6 ) ]
                          
    polytunnels_south = [ Polytunnel ( (southg_nwcorner_x + 0*tunnel_l,southg_nwcorner_y - 71.8) , tunnel_l, 71.8 ),
                          Polytunnel ( (southg_nwcorner_x + 1*tunnel_l,southg_nwcorner_y - 71.8) , tunnel_l, 71.8 ), 
                          Polytunnel ( (southg_nwcorner_x + 2*tunnel_l,southg_nwcorner_y - 80.8) , tunnel_l, 80.8 ),
                          Polytunnel ( (southg_nwcorner_x + 3*tunnel_l,southg_nwcorner_y - 80.8) , tunnel_l, 80.8 ),
                          Polytunnel ( (southg_nwcorner_x + 4*tunnel_l,southg_nwcorner_y - 89.6) , tunnel_l, 89.6 ),
                          Polytunnel ( (southg_nwcorner_x + 5*tunnel_l,southg_nwcorner_y - 89.6) , tunnel_l, 89.6 ),
                          Polytunnel ( (southg_nwcorner_x + 6*tunnel_l,southg_nwcorner_y - 89.6) , tunnel_l, 89.6 ),
                          Polytunnel ( (southg_nwcorner_x + 7*tunnel_l,southg_nwcorner_y - 89.6) , tunnel_l, 89.6 ),
                          Polytunnel ( (southg_nwcorner_x + 8*tunnel_l,southg_nwcorner_y - 82.4) , tunnel_l, 82.4 ),
                          Polytunnel ( (southg_nwcorner_x + 9*tunnel_l,southg_nwcorner_y - 82.4) , tunnel_l, 82.4 ),
                          Polytunnel ( (southg_nwcorner_x + 10*tunnel_l,southg_nwcorner_y - 82.4) , tunnel_l, 82.4 ),
                          Polytunnel ( (southg_nwcorner_x + 11*tunnel_l,southg_nwcorner_y - 82.4) , tunnel_l, 82.4 ),
                          Polytunnel ( (southg_nwcorner_x + 12*tunnel_l,southg_nwcorner_y - 67.2) , tunnel_l, 67.2 ),
                          Polytunnel ( (southg_nwcorner_x + 13*tunnel_l,southg_nwcorner_y - 67.2) , tunnel_l, 67.2 ) ]

    field423_polytunnels = polytunnels_north + polytunnels_middle + polytunnels_south 
    
    
    
    #From https://www.johndcook.com/lat_long_distance.html , confirmed using Google Earth

    #0.001 difference in latitude 111.2298 meters
    lat_diff_to_meters = 111.2298 / 0.001

    #0.001 difference in longitude is 67.3654 meters
    long_diff_to_meters = 67.3654 / 0.001

    # Using the southgroup of polytunnels to find the angle phi.

    southg_nwcorner_long = 1.390852
    southg_nwcorner_lat = 52.725319

    southg_necorner_long = 1.392655
    southg_necorner_lat = 52.725479

    eastwest_long_difference = southg_necorner_long - southg_nwcorner_long
    northsouth_lat_difference = southg_necorner_lat - southg_nwcorner_lat

    eastwest_long_difference_meters = long_diff_to_meters * eastwest_long_difference
    northsouth_lat_difference_meters = lat_diff_to_meters * northsouth_lat_difference 
    
    angle_phi = math.atan( northsouth_lat_difference_meters / eastwest_long_difference_meters )

    # Using the angle phi to find longitude and latitude of the origin. 
    new_x = southg_nwcorner_x * math.cos( angle_phi )  - southg_nwcorner_y * math.sin( angle_phi )
    new_y = southg_nwcorner_x * math.sin( angle_phi )  + southg_nwcorner_y * math.cos( angle_phi )

    origin_long = southg_nwcorner_long - new_x / long_diff_to_meters
    origin_lat = southg_nwcorner_lat - new_y / lat_diff_to_meters



    #Creating StrawberryField.
    field423 = StrawberryField( 500, 380, polytunnel_list = field423_polytunnels, spacetype = spacetype )
    field423.angle_phi_radians = angle_phi
    field423.origin_longitude = origin_long
    field423.origin_latitude = origin_lat 
    
    field423.packing_stations = [ ( 280, 200 ) ] 
    field423.packing_stations_points = [ Point( p ) for p in field423.packing_stations ] 
    field423.add_topological_map( )

    return field423

def make_field_428_2020( spacetype = SpaceType.CONTINUOUS2D ):

    """Returns a continuous2D of 428_2020."""
    
    # NOTE: Used.

    # polytunnel dimensions --- from the excel spreadsheets
    tunnel_l = 8.85 
    
    northgroup_longest = 130.0
    southgroup_longest = 133.0 
    
    path_width = 9.0
    
    empty_north = 2.0    
    empty_south = 70.0
    
    #Polytunnel groups corners.
    northg_swcorner_x = 50.0
    northg_swcorner_y = empty_south + southgroup_longest + path_width 

    southg_nwcorner_x = 50.0
    southg_nwcorner_y = empty_south + southgroup_longest
    
    # List of polytunnels.
    polytunnels_north = [ Polytunnel ( (northg_swcorner_x +  0 * tunnel_l,northg_swcorner_y), tunnel_l, 67.0, entrance_side = "SOUTH" ),
                          Polytunnel ( (northg_swcorner_x +  1 * tunnel_l,northg_swcorner_y), tunnel_l, 67.0, entrance_side = "SOUTH" ),
                          Polytunnel ( (northg_swcorner_x +  2 * tunnel_l,northg_swcorner_y), tunnel_l, 70.0, entrance_side = "SOUTH" ),
                          Polytunnel ( (northg_swcorner_x +  3 * tunnel_l,northg_swcorner_y), tunnel_l, 70.0, entrance_side = "SOUTH" ),
                          Polytunnel ( (northg_swcorner_x +  4 * tunnel_l,northg_swcorner_y), tunnel_l, 76.0, entrance_side = "SOUTH" ),
                          Polytunnel ( (northg_swcorner_x +  5 * tunnel_l,northg_swcorner_y), tunnel_l, 82.0, entrance_side = "SOUTH" ),
                          Polytunnel ( (northg_swcorner_x +  6 * tunnel_l,northg_swcorner_y), tunnel_l, 88.0, entrance_side = "SOUTH" ),
                          Polytunnel ( (northg_swcorner_x +  7 * tunnel_l,northg_swcorner_y), tunnel_l, 94.0, entrance_side = "SOUTH" ),
                          Polytunnel ( (northg_swcorner_x +  8 * tunnel_l,northg_swcorner_y), tunnel_l, 100.0, entrance_side = "SOUTH" ),
                          Polytunnel ( (northg_swcorner_x +  9 * tunnel_l,northg_swcorner_y), tunnel_l, 103.0, entrance_side = "SOUTH" ),
                          Polytunnel ( (northg_swcorner_x + 10 * tunnel_l,northg_swcorner_y), tunnel_l, 109.0, entrance_side = "SOUTH" ),
                          Polytunnel ( (northg_swcorner_x + 11 * tunnel_l,northg_swcorner_y), tunnel_l, 112.0, entrance_side = "SOUTH" ),
                          Polytunnel ( (northg_swcorner_x + 12 * tunnel_l,northg_swcorner_y), tunnel_l, 118.0, entrance_side = "SOUTH" ),
                          Polytunnel ( (northg_swcorner_x + 13 * tunnel_l,northg_swcorner_y), tunnel_l, 124.0, entrance_side = "SOUTH" ),
                          Polytunnel ( (northg_swcorner_x + 14 * tunnel_l,northg_swcorner_y), tunnel_l, 127.0, entrance_side = "SOUTH" ),
                          Polytunnel ( (northg_swcorner_x + 15 * tunnel_l,northg_swcorner_y), tunnel_l, 130.0, entrance_side = "SOUTH" ),
                          Polytunnel ( (northg_swcorner_x + 16 * tunnel_l,northg_swcorner_y), tunnel_l, 130.0, entrance_side = "SOUTH" ),
                          Polytunnel ( (northg_swcorner_x + 17 * tunnel_l,northg_swcorner_y), tunnel_l, 130.0, entrance_side = "SOUTH" ) ]
    
    polytunnels_south = [ Polytunnel ( (southg_nwcorner_x +  0 * tunnel_l,southg_nwcorner_y - 73.0), tunnel_l, 73.0 ), 
                          Polytunnel ( (southg_nwcorner_x +  1 * tunnel_l,southg_nwcorner_y - 76.0), tunnel_l, 76.0 ),
                          Polytunnel ( (southg_nwcorner_x +  2 * tunnel_l,southg_nwcorner_y - 79.0), tunnel_l, 79.0 ),
                          Polytunnel ( (southg_nwcorner_x +  3 * tunnel_l,southg_nwcorner_y - 82.0), tunnel_l, 82.0 ),
                          Polytunnel ( (southg_nwcorner_x +  4 * tunnel_l,southg_nwcorner_y - 85.0), tunnel_l, 85.0 ),
                          Polytunnel ( (southg_nwcorner_x +  5 * tunnel_l,southg_nwcorner_y - 91.0), tunnel_l, 91.0 ),
                          Polytunnel ( (southg_nwcorner_x +  6 * tunnel_l,southg_nwcorner_y - 94.0), tunnel_l, 94.0 ),
                          Polytunnel ( (southg_nwcorner_x +  7 * tunnel_l,southg_nwcorner_y - 97.0), tunnel_l, 97.0 ),
                          Polytunnel ( (southg_nwcorner_x +  8 * tunnel_l,southg_nwcorner_y - 103.0), tunnel_l, 103.0 ),
                          Polytunnel ( (southg_nwcorner_x +  9 * tunnel_l,southg_nwcorner_y - 106.0), tunnel_l, 106.0 ),
                          Polytunnel ( (southg_nwcorner_x + 10 * tunnel_l,southg_nwcorner_y - 112.0), tunnel_l, 112.0 ),
                          Polytunnel ( (southg_nwcorner_x + 11 * tunnel_l,southg_nwcorner_y - 115.0), tunnel_l, 115.0 ),
                          Polytunnel ( (southg_nwcorner_x + 12 * tunnel_l,southg_nwcorner_y - 118.0), tunnel_l, 118.0 ),
                          Polytunnel ( (southg_nwcorner_x + 13 * tunnel_l,southg_nwcorner_y - 121.0), tunnel_l, 121.0 ),
                          Polytunnel ( (southg_nwcorner_x + 14 * tunnel_l,southg_nwcorner_y - 127.0), tunnel_l, 127.0 ),
                          Polytunnel ( (southg_nwcorner_x + 15 * tunnel_l,southg_nwcorner_y - 130.0), tunnel_l, 130.0 ),
                          Polytunnel ( (southg_nwcorner_x + 16 * tunnel_l,southg_nwcorner_y - 133.0), tunnel_l, 133.0 ),
                          Polytunnel ( (southg_nwcorner_x + 17 * tunnel_l,southg_nwcorner_y - 133.0), tunnel_l, 133.0 ) ] 

    field428_polytunnels = polytunnels_north + polytunnels_south 

    for p in field428_polytunnels: 
        p.add_random_point( ) 

    #0.001 difference in latitude 111.2298 meters
    lat_diff_to_meters = 111.2298 / 0.001

    #0.001 difference in longitude is 67.3654 meters
    long_diff_to_meters = 67.3654 / 0.001

    # Using the southgroup of polytunnels to find the angle phi.

    southg_nwcorner_lat = 52.725963
    southg_nwcorner_long = 1.388012

    southg_necorner_lat = 52.726093
    southg_necorner_long = 1.390348
    
    eastwest_long_difference = southg_necorner_long - southg_nwcorner_long
    northsouth_lat_difference = southg_necorner_lat - southg_nwcorner_lat

    eastwest_long_difference_meters = long_diff_to_meters * eastwest_long_difference
    northsouth_lat_difference_meters = lat_diff_to_meters * northsouth_lat_difference

    angle_phi = math.atan( northsouth_lat_difference_meters / eastwest_long_difference_meters )
    
    # Using the angle phi to find longitude and latitude of the origin. 
    new_x = southg_nwcorner_x * math.cos( angle_phi )  - southg_nwcorner_y * math.sin( angle_phi )
    new_y = southg_nwcorner_x * math.sin( angle_phi )  + southg_nwcorner_y * math.cos( angle_phi )

    origin_long = southg_nwcorner_long - new_x / long_diff_to_meters
    origin_lat = southg_nwcorner_lat - new_y / lat_diff_to_meters

    
    
    #Creating StrawberryField.
    #field428 = StrawberryField( math.ceil( 20.0 * tunnel_l), 300.0, polytunnel_list = field428_polytunnels, spacetype = spacetype )
    field428 = StrawberryField( 500, 380, polytunnel_list = field428_polytunnels, spacetype = spacetype )
    field428.angle_phi_radians = angle_phi
    field428.origin_longitude = origin_long
    field428.origin_latitude = origin_lat

    field428.packing_stations = [ ( 150, 220 ) ] 
    field428.packing_stations_points = [ Point( p ) for p in field428.packing_stations ] 
    
    field428.add_topological_map( )

    return field428

def make_combined_fields( spacetype = SpaceType.CONTINUOUS2D ):

    field423 = make_field_423_2020( spacetype )
    field428 = make_field_428_2020( spacetype )

    longdiff = field428.origin_longitude - field423.origin_longitude #should positive
    latdiff = field428.origin_latitude - field423.origin_latitude #should be negative

    x423, y423 = field428.find_xy_from_longlat( field423.origin_longitude, field423.origin_latitude )
    x428, y428 = field428.find_xy_from_longlat( field428.origin_longitude, field428.origin_latitude )

    field428_tunnels = field428.polytunnel_list
    field423_tunnels = field423.polytunnel_list

    additional_x_offset_423 = 2
    additional_y_offset_423 = 1.5
    
    for t in field423_tunnels:
        t.move_xy( x423 + additional_x_offset_423, y423 + additional_y_offset_423)

    # rotate tunnels 423 and 428
    for t in field423_tunnels:
        t.rotate_shapely( field423.angle_phi_radians )

    for t in field428_tunnels:
        t.rotate_shapely( field428.angle_phi_radians )

    combined_polytunnels = field428_tunnels + field423_tunnels

    new_field = StrawberryField( 500, 380, polytunnel_list = combined_polytunnels, spacetype = spacetype )
    new_field.angle_phi_radians = 0
    new_field.origin_longitude = field428.origin_longitude
    new_field.origin_latitude = field428.origin_latitude 

    new_field.packing_stations = field428.packing_stations
    new_field.packing_stations_points = field428.packing_stations_points 
    new_field.topological_map = field428.topological_map 
    new_field.packing_stations_nodes = field428.packing_stations_nodes

    for n in new_field.topological_map.nodes[1:]: 
        n.rotate_shapely( field428.angle_phi_radians ) 

    new_field.image_path = "../PlaceUK_satellite/Fields_423_and_428.png" 
    new_field.image_dim = ( 378, 395 )

    return new_field

# Testing ... 

if __name__ == '__main__' :

    print("Field 423")
    field423_long_lat()

    print("Field 428")
    field428_long_lat()
    
    field423 = make_field_423_2020( SpaceType.CONTINUOUS2D )
    print("field423: ", field423.angle_phi_radians, field423.origin_latitude, field423.origin_longitude )

    field428 = make_field_428_2020( SpaceType.CONTINUOUS2D )
    print("field428: ", field428.angle_phi_radians, field428.origin_latitude, field428.origin_longitude )

