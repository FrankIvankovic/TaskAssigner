
import json
import datetime
import numpy
import math
# import cv2

# import pickers_model.strawberry_field 

# -------
# Functions for reading a json file and adding time in seconds.
# -------

def has_long_and_lat( data_dict ): 
    
    """Checks whether data contains longitude and latitude."""

    # NOTE: Used by read_json_pickers.

    data_payload = data_dict[ "payload" ]
    
    if "LATITUDE" not in data_payload.keys():
        return False
    elif data_payload[ "LATITUDE" ]=="": 
        return False
    
    if "LONGITUDE" not in data_payload.keys(): 
        return False
    elif data_payload["LONGITUDE"]=="":
        return False
    
    return True

def has_long_and_lat_format2( data_dict ): 
    
    """Checks whether data contains longitude and latitude."""

    # NOTE: Used by read_json_pickers.
    
    if "LATITUDE" not in data_dict.keys():
        return False
    elif data_dict[ "LATITUDE" ]=="": 
        return False
    
    if "LONGITUDE" not in data_dict.keys(): 
        return False
    elif data_dict["LONGITUDE"]=="":
        return False
    
    return True

def has_utc_date_time( data_dict ): 
    
    if "UTC_DATE_TIME" not in data_dict.keys():
        return False
    elif data_dict[ "UTC_DATE_TIME" ]=="":
        return False
    
    return True

def add_one_hour( data_dict ):
    
    #Used when UTC time is one hour behind.
    for picker in data_dict: 
        for entry in data_dict[ picker ] :
            entry[ 'datetime' ] += datetime.timedelta( hours = 1 )  
    return data_dict
    

def create_datetime_from_string( datetime_string ) : 

    # NOTE: Used by read_json_pickers.

    return datetime.datetime.strptime( datetime_string, '%Y-%m-%dT%H:%M:%S.%f' )

    #assert( len(datetime_string.split( "T" ) ) == 2 )    
    #date_string, time_string = datetime_string.split( "T" )
    #assert( date_string == "2022-10-18" )
    #assert( len(time_string.split( ":" ) ) == 3 )     
    #hours, minutes, seconds_and_microseconds = time_string.split( ":" )    
    #seconds, microseconds = seconds_and_microseconds.split( "." )
    #return datetime.time( int(hours), int(minutes), int(seconds), int( microseconds) )

def create_datetime_from_string_format2( datetime_string ) : 

    # NOTE: Used by read_json_pickers.

    return datetime.datetime.strptime( datetime_string, '%Y%m%d%H%M%S.%f' )

def find_min_datetime_format2( data_msg ):
    
    datetimelist = [ ] 
    for d in data_msg: 
        if not has_utc_date_time( d ):
            continue
        datetimelist.append( create_datetime_from_string_format2( d[ "UTC_DATE_TIME" ] ) )
    return min( datetimelist )

def read_json_test( json_file ):

    """ Counts a number of entries for each picker, stores it in a dictionary. """

    # NOTE: Not used. It was used for testing.

    picker_locations_dict = {}

    f = open( json_file )
    data = json.load(f)

    for i in data[ "msg" ] :

        i_payload = i[ "payload" ]
        if i_payload[ "CLIENT_ID" ] in picker_locations_dict.keys():
            picker_locations_dict[ i_payload[ "CLIENT_ID" ] ] += 1
        else:
            picker_locations_dict[ i_payload[ "CLIENT_ID" ] ] = 0

    return picker_locations_dict

#Given a dict of pickers, each with a list of entries, find the overall minimum and maximum datetime.
def find_min_and_max_datetime( all_pickers_data ):

    # NOTE: Used by interpolation functions.

    all_entries = sum( all_pickers_data.values(), [] )
    all_datetimes = [ i[ "datetime" ] for i in all_entries ]
    min_datetime = min( all_datetimes )
    max_datetime = max( all_datetimes )
    return min_datetime, max_datetime

def read_json_pickers_format1( data ): 
    
    picker_locations_dict = {}

    datetimelist = [ create_datetime_from_string( i[ "datetime" ] ) for i in data[ "msg" ] ]
    min_datetime = min(datetimelist)

    for i in data[ "msg" ] :

        #eliminate enrtries without longitude and latitude
        if not has_long_and_lat(i):
            continue

        #create entry with { dt_string, datetime, tseconds, LONGITUDE, LATITUDE }
        i_payload = i[ "payload" ]
        new_datetime = create_datetime_from_string( i[ "datetime" ] ) #create datetime
        new_entry = { "dt_string" : i[ "datetime" ], "datetime" : new_datetime, "tseconds" : (new_datetime-min_datetime).total_seconds(), "LONGITUDE" : i_payload["LONGITUDE"], "LATITUDE": i_payload["LATITUDE"] }

        #add it to the right picker
        if i_payload[ "CLIENT_ID" ] in picker_locations_dict.keys():
            picker_locations_dict[ i_payload[ "CLIENT_ID" ] ].append( new_entry )
        else:
            picker_locations_dict[ i_payload[ "CLIENT_ID" ] ] = [ new_entry ]

    return picker_locations_dict    

def read_json_pickers_format2( data ): 
    
    """ Returns a dictionary of lists of the form { picker_id : [ { dt_string, datetime, tseconds, LONGITUDE, LATITUDE } ] }. """

    # NOTE: Used.

    #f = open( json_file )
    #data = json.load(f)

    picker_locations_dict = {}

    min_datetime = find_min_datetime_format2( data[ "msg" ] )

    for i in data[ "msg" ] :

        #eliminate enrtries without longitude and latitude
        if not has_long_and_lat_format2(i):
            continue

        #create entry with { dt_string, datetime, tseconds, LONGITUDE, LATITUDE }
        new_datetime = create_datetime_from_string_format2 ( i[ "UTC_DATE_TIME" ] ) #create datetime
                
        new_entry = { "dt_string" : i[ "UTC_DATE_TIME" ], "datetime" : new_datetime, "tseconds" : (new_datetime-min_datetime).total_seconds(), "LONGITUDE" : i["LONGITUDE"], "LATITUDE": i["LATITUDE"] }

        #add it to the right picker
        if i[ "CLIENT_ID" ] in picker_locations_dict.keys():
            picker_locations_dict[ i[ "CLIENT_ID" ] ].append( new_entry )
        else:
            picker_locations_dict[ i[ "CLIENT_ID" ] ] = [ new_entry ]

    return picker_locations_dict

#Reads pickers data, returns a dict
#format1 refers to the format used in October data.
#format2 refers to the format used in May data.

def read_json_pickers( json_file ): 
    
    """ Returns a dictionary of lists of the form { picker_id : [ { dt_string, datetime, tseconds, LONGITUDE, LATITUDE } ] }. """

    # NOTE: Used.
    
    f = open( json_file )
    data = json.load(f) 
    first_entry = data[ "msg" ][0]
    if "payload" in first_entry.keys(): 
        return read_json_pickers_format1( data )
    else:
        return read_json_pickers_format2( data )

# -------
# Functions for adding an x, y location.
# -------

def add_xy_fake( strawberry_field, time_location_dict ) :

    """ Produces fake values for testing."""

    # NOTE: Not used. It was used for testing.

    picker1_x = [29, 3, 69, 2, 131, 129, 19, 13, 78, 108]
    picker1_y = [35, 81, 181, 63, 137, 33, 96, 182, 239, 317]

    picker2_x = [62, 71, 42, 44, 65, 101, 121, 1, 54, 85]
    picker2_y = [203, 167, 64, 106, 206, 185, 39, 107, 39, 145]

    picker3_x = [54, 15, 102, 94, 26, 38, 8, 49, 87, 91]
    picker3_y = [203, 167, 64, 106, 206, 185, 39, 107, 39, 145]

    picker4_x = [54, 15, 102, 94, 26, 38, 8, 49, 87, 91]
    picker4_y = [35, 81, 181, 63, 137, 33, 96, 182, 239, 317]

    picker1 = list( time_location_dict.keys() )[0]

    for i,entry in enumerate(time_location_dict[ picker1 ]):
        entry[ "x" ] = picker1_x[ i % len(picker1_x) ]
        entry[ "y" ] = picker1_y[ i % len(picker1_y) ]

    picker2 = list( time_location_dict.keys() )[1]

    for i,entry in enumerate(time_location_dict[ picker2 ]):
        entry[ "x" ] = picker2_x[ i % len(picker2_x) ]
        entry[ "y" ] = picker2_y[ i % len(picker2_y) ]

    picker3 = list( time_location_dict.keys() )[2]

    for i,entry in enumerate(time_location_dict[ picker3 ]):
        entry[ "x" ] = picker3_x[ i % len(picker3_x) ]
        entry[ "y" ] = picker3_y[ i % len(picker3_y) ]

    picker4 = list( time_location_dict.keys() )[3]

    for i,entry in enumerate(time_location_dict[ picker4 ]):
        entry[ "x" ] = picker4_x[ i % len(picker4_x) ]
        entry[ "y" ] = picker4_y[ i % len(picker4_y) ]

    return time_location_dict

def transform_longlat_xy( strawberry_field, longitude, latitude ):

    # NOTE: Used by add_xy_picker.

    x,y = strawberry_field.find_xy_from_longlat( float(longitude), float(latitude) )
    return (x, y)

def add_xy_picker( strawberry_field, picker_location_list ):

    # NOTE: Used by add_xy.

    for entry in picker_location_list:
        new_x, new_y = transform_longlat_xy( strawberry_field, entry[ "LONGITUDE" ], entry[ "LATITUDE" ] )
        entry[ "x" ] = new_x
        entry[ "y" ] = new_y
    return picker_location_list

def add_xy( strawberry_field, time_location_dict ) :

    # NOTE: Used.

    for picker in time_location_dict.keys():
        time_location_dict[picker] = add_xy_picker( strawberry_field, time_location_dict[ picker ] )
    return time_location_dict

# -------
# Interpolation.
# -------

# Given a list ( time, (x,y) ) and a size of a time step, interpolate positions. Return new list ( time, (x,y) ).
def interpolate_positions( picker_data, time_step_size, min_datetime, max_datetime ):

    # NOTE: Used by interpolate_positions_pickers.

    #f = open( json_file )
    #data = json.load(f)

    #Create a list of timepoints
    # datetimelist = [ create_datetime_from_string( i[ "datetime" ] ) for i in data[ "msg" ] ]
    # min_datetime = min(datetimelist)
    # max_datetime = max(datetimelist)

    number_of_seconds = (max_datetime - min_datetime).total_seconds()
    timepoints = numpy.arange(0.0, number_of_seconds, time_step_size)

    #print(min_datetime, max_datetime, (max_datetime-min_datetime).total_seconds())

    #Interpolate x and y
    tp = numpy.array( [ pd[ "tseconds" ] for pd in picker_data ] )
    xp = numpy.array( [ pd[ "x" ] for pd in picker_data ] )
    yp = numpy.array( [ pd[ "y" ] for pd in picker_data ] )

    x_start = picker_data[ 0 ][ "x" ]
    x_end = picker_data[ -1 ][ "x" ]
    y_start = picker_data[ 0 ][ "y" ]
    y_end = picker_data[ -1 ][ "y" ]

    interpolated_x = numpy.interp( timepoints, tp, xp, left = x_start , right = x_end )
    interpolated_y = numpy.interp( timepoints, tp, yp, left = y_start , right = y_end )

    #Return a list of dicts { tseconds, x, y }
    interpolated = []
    for i,t in enumerate( timepoints ):
        interpolated.append( { "tseconds" : t , "x" : interpolated_x[i] , "y" : interpolated_y[i] } )

    return interpolated

    #for i in timepoints:
    #    print( i )

def interpolate_positions_pickers( pickers, time_step_size ):

    # NOTE: Used.

    interpolated_picker_data = {}
    min_datetime, max_datetime = find_min_and_max_datetime( pickers )

    for picker in pickers.keys():

        picker_data = pickers[ picker ]
        interpolated = interpolate_positions( picker_data, time_step_size, min_datetime, max_datetime ) #3
        interpolated_picker_data[ picker ] = interpolated

    return interpolated_picker_data

def read_json_interpolate( strawberry_field, time_step_size, json_data ):

    # NOTE: No longer used.

    pickers_data = read_json_pickers( json_data ) #1
    
    print("READ JSON, CREATE A LIST OF dt_string, datetime, tseconds, LONGITUDE, LATITUDE." )
    for picker in pickers_data.keys(): 
        for entry in pickers_data[picker]: 
            print( entry )

    # assert( False )
    
    #pickers_data_xy = add_xy_fake( strawberry_field, pickers_data ) #2
    pickers_data_xy = add_xy( strawberry_field, pickers_data ) #2

    print("AFTER ADDING X AND Y TO ALL ENTRIES.")
    for picker in pickers_data_xy.keys(): 
        for entry in pickers_data_xy[picker]: 
            print( entry )

    # assert( False )

    interpolated_picker_data = {}
    min_datetime, max_datetime = find_min_and_max_datetime( pickers_data_xy )

    for picker in pickers_data_xy.keys():

        picker_data = pickers_data_xy[ picker ]
        interpolated = interpolate_positions( picker_data, time_step_size, min_datetime, max_datetime ) #3
        interpolated_picker_data[ picker ] = interpolated

    return interpolated_picker_data

def adjust_xy_offset( picker_data, x_offset, y_offset ):

    # NOTE: Used.

    for picker in picker_data.keys():
        for entry in picker_data[ picker ]: 
            entry[ "x" ] = entry[ "x" ] + x_offset
            entry[ "y" ] = entry[ "y" ] + y_offset

    return picker_data

def print_reading_readable( reading ):

    # NOTE: Used by print_maxandmin_positions.

    print( reading['dt_string'] )
    print( 'tseconds: ', reading['tseconds'] )
    print( "\nLongitude and latitude:" )
    print( str( reading['LATITUDE'] ) +',' + str( reading['LONGITUDE'] ) )
    print( "\n", reading['y'], reading['y'], "\n" )

def find_maxandmin_positions( picker ):

    # NOTE: Not used. Used for testing.

    max_long = max( picker, key = lambda x:x['LONGITUDE'] )
    min_long = min( picker, key = lambda x:x['LONGITUDE'] )

    max_lat = max( picker, key = lambda x:x['LATITUDE'] )
    min_lat = min( picker, key = lambda x:x['LATITUDE'] )

    xs = [ max_long['x'], min_long['x'], max_lat['x'], min_lat['x'] ]
    ys = [ max_long['y'], min_long['y'], max_lat['y'], min_lat['y'] ]

    print( "MAX LONGIITUDE" )
    print_reading_readable( max_long )

    print( "MIN LONGIITUDE" )
    print_reading_readable( min_long )

    print( "MAX LATITUDE" )
    print_reading_readable( max_lat )

    print( "MIN LATITUDE" )
    print_reading_readable( min_lat )

    return xs,ys



# ===== Tests =====


if __name__ == '__main__' :

    #pickers_data = read_json_test( "data_logged_placeuk_day1.json" )
    #print( pickers_data )

    #1 Read json
    #2 Add xy
    #3 Interpolate
    
    offset_x0 = 300.0
    offset_y0 = 50.0
    offset_x1 = 300.0
    offset_y1 = 50.0

    time_step = 3.0

    # the_field = field_maps.make_field_423_2020( strawberry_field.SpaceType.CONTINUOUS2D )
    # the_field = field_maps.make_field_428_2020( strawberry_field.SpaceType.CONTINUOUS2D )
    # the_field.make_field_larger( offset_left = 300.0, offset_bottom = 50.0, additional_right = 300.0, additional_top = 50.0 )
    # the_field = field_maps.make_combined_fields( strawberry_field.SpaceType.CONTINUOUS2D )

    picker_data = "data_logged_placeuk_day1.json"

    pickers_data = read_json_pickers( picker_data ) #1
    pickers_data_xy = add_xy( the_field, pickers_data ) #2
    # pickers_data_xy = adjust_xy_offset( pickers_data_xy, offset_x0, offset_y0 ) #3

    pickers_interpolated = interpolate_positions_pickers( pickers_data_xy, time_step ) #4

    #print("AFTER ADDING X AND Y TO ALL ENTRIES.")
    #for i,picker in enumerate(pickers_data_xy.keys()):
    for i,picker in enumerate(pickers_interpolated.keys()):
        print( "\nPICKER: ", picker)
        for entry in pickers_interpolated[picker]:
            #print( i, picker, entry['dt_string'], ', tseconds: ', entry['tseconds'], ', LONGUTUDE: ', entry['LONGITUDE'], ', LATITUDE: ', entry['LATITUDE'], ', x: ', entry['x'], ', y: ', entry['y'] )
            #print( i, picker, ', tseconds: ', entry['tseconds'], ', x: ', entry['x'], ', y: ', entry['y'] )
            pass

    ###

    #assert(False)

    new_pickers_data = pickers_data_xy

    print("\nPICKER 1")
    picker1 = list( new_pickers_data.keys() )[0]
    picker1_list = new_pickers_data[ picker1 ]

    p1_xs,p1_ys = find_maxandmin_positions( picker1_list )

    print("\nPICKER 2")
    picker2 = list( new_pickers_data.keys() )[1]
    picker2_list = new_pickers_data[ picker2 ]

    p2_xs,p2_ys = find_maxandmin_positions( picker2_list )

    print("\nPICKER 3")
    picker3 = list( new_pickers_data.keys() )[2]
    picker3_list = new_pickers_data[ picker3 ]

    p3_xs,p3_ys = find_maxandmin_positions( picker3_list )

    print("\nPICKER 4")
    picker4 = list( new_pickers_data.keys() )[3]
    picker4_list = new_pickers_data[ picker4 ]

    p4_xs,p4_ys = find_maxandmin_positions( picker4_list )

    #This code was used in debugging the coordinate transformations.
    #picker1_west = min( picker1_list, key = lambda x:x['LONGITUDE'] )

    #picker1_west_long = picker1_west['LONGITUDE']
    #picker1_west_lat = picker1_west['LATITUDE']

    #ll_long = the_field.origin_longitude
    #ll_lat = the_field.origin_latitude

    #print("The field lat and long:")
    #print(str(ll_lat)+' , '+str(ll_long))
    #print("\nPicker1_west lat and long:")
    #print(str(picker1_west_lat)+' , '+str(picker1_west_long))

    #long_m = the_field.longdif_to_meters * ( float(picker1_west_long) - ll_long )
    #lat_m = the_field.latdif_to_meters * ( float(picker1_west_lat) - ll_lat )

    #print("Multipliers long lat", the_field.longdif_to_meters, the_field.latdif_to_meters)
    #print("Distances long lat:", long_m, lat_m )

    #plotting
    from matplotlib import pyplot as plt
    from matplotlib.patches import Rectangle, Polygon

    fig, ax = plt.subplots()

    ax.scatter( p1_xs,p1_ys, color='red')
    ax.scatter( p2_xs,p2_ys, color='orange')
    ax.scatter( p3_xs,p3_ys, color='violet')
    ax.scatter( p4_xs,p4_ys, color='cyan')

    # img = plt.imread( "../PlaceUK_satellite/GoogleMaps.png")
    img = cv2.imread( "../PlaceUK_satellite/GoogleMaps.png" )
    # ax.imshow( numpy.flipud( img ), origin = 'lower' ) 
    dim = ( 420, 385 )
    img = cv2.resize( img, dim )
    
    ax.imshow( img[::-1], origin = 'lower' ) 

    for tunnel in the_field.polytunnel_list:
        #ax.add_patch(Rectangle( tunnel.lower_left, tunnel.length, tunnel.width,
                #edgecolor = 'pink',
                #facecolor = 'green',
                #fill=False,
                #lw=5, alpha = 0.3))

            ax.add_patch(Polygon( tunnel.get_coordinates_list(),
                edgecolor = 'pink',
                facecolor = 'green',
                fill=False,
                lw=5, alpha = 0.3)) 
            
            ax.scatter( tunnel.entrance_point.x,tunnel.entrance_point.y, color='violet' )
    
    psx = the_field.packing_stations_points[0].x
    psy = the_field.packing_stations_points[0].y
    
    ax.scatter( psx,psy, color='yellow' )
            
    plt.show()


