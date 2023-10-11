
import mesa
import math

from shapely.geometry import Point, Polygon 

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon

import cv2

from pickers_model.strawberry_field.topological_map import TMNode, TMEdge, TopologicalMap 
from pickers_model.strawberry_field.polytunnel import Polytunnel 
from pickers_model.strawberry_field.strawberry_field import StrawberryField,SpaceType

def make_field_436( spacetype = SpaceType.CONTINUOUS2D ):

    field_polytunnels = [ ]  
    
    #Creating StrawberryField.
    field = StrawberryField( 270, 250, polytunnel_list = field_polytunnels, spacetype = spacetype )
    field.angle_phi_radians = 0
    field.origin_longitude = 1.428804
    field.origin_latitude = 52.748925 

    #From https://www.johndcook.com/lat_long_distance.html , confirmed using Google Earth    
    field.longdif_to_meters = 67.3271 / 0.001
    field.latdif_to_meters = 111.2298 / 0.001

    field.packing_stations = [  ] 
    field.packing_stations_points = [ Point( p ) for p in field.packing_stations ] 
    field.add_topological_map( )

    field.image_path = "../PlaceUK_satellite/Field_436.png" 
    field.image_dim = ( 255, 215 ) 
    
    tunnel_l = 8.5 
    tunnel_w_south = 57.2
    tunnel_w_north = 58.2 
    middle = 2.5 
    
    nw_lat = 52.750136
    nw_long = 1.429119 
    nw = field.find_xy_from_longlat( float(nw_long), float(nw_lat) )

    sw_lat = 52.749108
    sw_long = 1.429651
    sw_x,sw_y = field.find_xy_from_longlat( float(sw_long), float(sw_lat) )

    ne_lat = 52.750642
    ne_long = 1.431766
    ne = field.find_xy_from_longlat( float(ne_long), float(ne_lat) )
    
    se_lat = 52.749621 
    se_long = 1.432301
    se = field.find_xy_from_longlat( float(se_long), float(se_lat) )
    
    polytunnels_south = [ Polytunnel( ( sw_x+0*tunnel_l, sw_y ), tunnel_l, tunnel_w_south, entrance_side = "NORTH" ),
                         Polytunnel( ( sw_x+1*tunnel_l, sw_y ), tunnel_l, tunnel_w_south, entrance_side = "NORTH" ),
                         Polytunnel( ( sw_x+2*tunnel_l, sw_y ), tunnel_l, tunnel_w_south, entrance_side = "NORTH" ),
                         Polytunnel( ( sw_x+3*tunnel_l, sw_y ), tunnel_l, tunnel_w_south, entrance_side = "NORTH" ),
                         Polytunnel( ( sw_x+4*tunnel_l, sw_y ), tunnel_l, tunnel_w_south, entrance_side = "NORTH" ),
                         Polytunnel( ( sw_x+5*tunnel_l, sw_y ), tunnel_l, tunnel_w_south, entrance_side = "NORTH" ),
                         Polytunnel( ( sw_x+6*tunnel_l, sw_y ), tunnel_l, tunnel_w_south, entrance_side = "NORTH" ),
                         Polytunnel( ( sw_x+7*tunnel_l, sw_y ), tunnel_l, tunnel_w_south, entrance_side = "NORTH" ),
                         Polytunnel( ( sw_x+8*tunnel_l, sw_y ), tunnel_l, tunnel_w_south, entrance_side = "NORTH" ),
                         Polytunnel( ( sw_x+9*tunnel_l, sw_y ), tunnel_l, tunnel_w_south, entrance_side = "NORTH" ),
                         Polytunnel( ( sw_x+10*tunnel_l, sw_y ), tunnel_l, tunnel_w_south, entrance_side = "NORTH" ),
                         Polytunnel( ( sw_x+11*tunnel_l, sw_y ), tunnel_l, tunnel_w_south, entrance_side = "NORTH" ),
                         Polytunnel( ( sw_x+12*tunnel_l, sw_y ), tunnel_l, tunnel_w_south, entrance_side = "NORTH" ),
                         Polytunnel( ( sw_x+13*tunnel_l, sw_y ), tunnel_l, tunnel_w_south, entrance_side = "NORTH" ),
                         Polytunnel( ( sw_x+14*tunnel_l, sw_y ), tunnel_l, tunnel_w_south, entrance_side = "NORTH" ),
                         Polytunnel( ( sw_x+15*tunnel_l, sw_y ), tunnel_l, tunnel_w_south, entrance_side = "NORTH" ),
                         Polytunnel( ( sw_x+16*tunnel_l, sw_y ), tunnel_l, tunnel_w_south, entrance_side = "NORTH" ),
                         Polytunnel( ( sw_x+17*tunnel_l, sw_y ), tunnel_l, tunnel_w_south, entrance_side = "NORTH" ),
                         Polytunnel( ( sw_x+18*tunnel_l, sw_y ), tunnel_l, tunnel_w_south, entrance_side = "NORTH" ),
                         Polytunnel( ( sw_x+19*tunnel_l, sw_y ), tunnel_l, tunnel_w_south, entrance_side = "NORTH" ),
                         Polytunnel( ( sw_x+20*tunnel_l, sw_y ), tunnel_l, tunnel_w_south, entrance_side = "NORTH" ),
                         Polytunnel( ( sw_x+21*tunnel_l, sw_y ), tunnel_l, tunnel_w_south, entrance_side = "NORTH" ) ]

    polytunnels_north = [ Polytunnel( ( sw_x+0*tunnel_l, sw_y + middle + tunnel_w_south ), tunnel_l, tunnel_w_north, entrance_side = "SOUTH" ),
                         Polytunnel( ( sw_x+1*tunnel_l, sw_y + middle + tunnel_w_south ), tunnel_l, tunnel_w_north, entrance_side = "SOUTH" ),
                         Polytunnel( ( sw_x+2*tunnel_l, sw_y + middle + tunnel_w_south ), tunnel_l, tunnel_w_north, entrance_side = "SOUTH" ),
                         Polytunnel( ( sw_x+3*tunnel_l, sw_y + middle + tunnel_w_south ), tunnel_l, tunnel_w_north, entrance_side = "SOUTH" ),
                         Polytunnel( ( sw_x+4*tunnel_l, sw_y + middle + tunnel_w_south ), tunnel_l, tunnel_w_north, entrance_side = "SOUTH" ),
                         Polytunnel( ( sw_x+5*tunnel_l, sw_y + middle + tunnel_w_south ), tunnel_l, tunnel_w_north, entrance_side = "SOUTH" ),
                         Polytunnel( ( sw_x+6*tunnel_l, sw_y + middle + tunnel_w_south ), tunnel_l, tunnel_w_north, entrance_side = "SOUTH" ),
                         Polytunnel( ( sw_x+7*tunnel_l, sw_y + middle + tunnel_w_south ), tunnel_l, tunnel_w_north, entrance_side = "SOUTH" ),
                         Polytunnel( ( sw_x+8*tunnel_l, sw_y + middle + tunnel_w_south ), tunnel_l, tunnel_w_north, entrance_side = "SOUTH" ),
                         Polytunnel( ( sw_x+9*tunnel_l, sw_y + middle + tunnel_w_south ), tunnel_l, tunnel_w_north, entrance_side = "SOUTH" ),
                         Polytunnel( ( sw_x+10*tunnel_l, sw_y + middle + tunnel_w_south ), tunnel_l, tunnel_w_north, entrance_side = "SOUTH" ),
                         Polytunnel( ( sw_x+11*tunnel_l, sw_y + middle + tunnel_w_south ), tunnel_l, tunnel_w_north, entrance_side = "SOUTH" ),
                         Polytunnel( ( sw_x+12*tunnel_l, sw_y + middle + tunnel_w_south ), tunnel_l, tunnel_w_north, entrance_side = "SOUTH" ),
                         Polytunnel( ( sw_x+13*tunnel_l, sw_y + middle + tunnel_w_south ), tunnel_l, tunnel_w_north, entrance_side = "SOUTH" ),
                         Polytunnel( ( sw_x+14*tunnel_l, sw_y + middle + tunnel_w_south ), tunnel_l, tunnel_w_north, entrance_side = "SOUTH" ),
                         Polytunnel( ( sw_x+15*tunnel_l, sw_y + middle + tunnel_w_south ), tunnel_l, tunnel_w_north, entrance_side = "SOUTH" ),
                         Polytunnel( ( sw_x+16*tunnel_l, sw_y + middle + tunnel_w_south ), tunnel_l, tunnel_w_north, entrance_side = "SOUTH" ),
                         Polytunnel( ( sw_x+17*tunnel_l, sw_y + middle + tunnel_w_south ), tunnel_l, tunnel_w_north, entrance_side = "SOUTH" ),
                         Polytunnel( ( sw_x+18*tunnel_l, sw_y + middle + tunnel_w_south ), tunnel_l, tunnel_w_north, entrance_side = "SOUTH" ),
                         Polytunnel( ( sw_x+19*tunnel_l, sw_y + middle + tunnel_w_south ), tunnel_l, tunnel_w_north, entrance_side = "SOUTH" ),
                         Polytunnel( ( sw_x+20*tunnel_l, sw_y + middle + tunnel_w_south ), tunnel_l, tunnel_w_north, entrance_side = "SOUTH" ),
                         Polytunnel( ( sw_x+21*tunnel_l, sw_y + middle + tunnel_w_south ), tunnel_l, tunnel_w_north, entrance_side = "SOUTH" ) ]

    field.polytunnel_list = polytunnels_north + polytunnels_south 

    angle = math.atan( ( ( se_lat - sw_lat ) * field.latdif_to_meters )  / ( ( se_long - sw_long ) * field.longdif_to_meters ) )

    for t in field.polytunnel_list: 
        t.rotate_shapely( angle, origin = (sw_x,sw_y), use_radians=True )    

    packing_station_1_longitude =  1.429773
    packing_station_1_latitude = 52.749700 

    ps1_x, ps1_y = field.find_xy_from_longlat_origin( packing_station_1_longitude, packing_station_1_latitude ) 
        
    tm = TopologicalMap( field ) 
    
    field.packing_stations = [ ( ps1_x, ps1_y ) ] 
    field.packing_stations_points = [ Point( p ) for p in field.packing_stations ]
    ps1_node = TMNode( ps1_x, ps1_y )
    field.packing_stations_nodes = [ ps1_node ] 
    tm.add_node( ps1_node ) 
    
    all_north_rows = [] 
    for p in polytunnels_north:
        for r in p.list_of_rows: 

            r.add_nodes( tm )
            tm.add_edge( r.entrance_node, ps1_node )
            all_north_rows.append( r )
    
    for r0,r1 in zip( all_north_rows, all_north_rows[1:] ):
        tm.add_edge( r0.entrance_node,r1.entrance_node )

    all_south_rows = [] 
    for p in polytunnels_south:
        for r in p.list_of_rows: 

            r.add_nodes( tm )
            tm.add_edge( r.entrance_node, ps1_node )
            all_south_rows.append( r )
    
    for r0,r1 in zip( all_south_rows, all_south_rows[1:] ):
        tm.add_edge( r0.entrance_node,r1.entrance_node )

    return field 

def test_field_436( ): 

    field_map = make_field_436( )

    field_length, field_width = field_map.dimensions

    nw_lat = 52.750136
    nw_long = 1.429119 
    nw = field_map.find_xy_from_longlat( float(nw_long), float(nw_lat) )

    sw_lat = 52.749108
    sw_long = 1.429651
    sw = field_map.find_xy_from_longlat( float(sw_long), float(sw_lat) )

    ne_lat = 52.750642
    ne_long = 1.431766
    ne = field_map.find_xy_from_longlat( float(ne_long), float(ne_lat) )
    
    se_lat = 52.749621 
    se_long = 1.432301
    se = field_map.find_xy_from_longlat( float(se_long), float(se_lat) )

    four_corners = [ nw, sw, ne, se ] 
    
    fig, ax = plt.subplots() 
    ax.scatter( [ i[0] for i in four_corners ], [ i[1] for i in four_corners ]  , color = 'red' )

    px,py = field_map.find_xy_from_longlat( 1.430466, 52.750392 )
    ax.scatter( px, py  , color = 'yellow' )

    img = field_map.resized_image( )
    ax.imshow( img[::-1], origin = 'lower' ) 
    
    for t in field_map.polytunnel_list:
        ax.add_patch(Polygon( t.get_coordinates_list(),
            edgecolor = 'pink',
            facecolor = 'green',
            fill=False,
            lw=5, alpha = 0.3)) 
        ax.scatter( t.entrance_point.x, t.entrance_point.y, marker = 'x', color = 'cyan' )
    
    plt.show()

def make_field_414( spacetype = SpaceType.CONTINUOUS2D ):

    field_polytunnels = [ ]  
    
    field = StrawberryField( 215, 367, polytunnel_list = field_polytunnels, spacetype = spacetype )
    field.angle_phi_radians = 0
    field.origin_longitude = 1.399616
    field.origin_latitude = 52.733384 

    #From https://www.johndcook.com/lat_long_distance.html , confirmed using Google Earth    
    field.longdif_to_meters = 67.3524 / 0.001
    field.latdif_to_meters = 111.2298 / 0.001

    field.packing_stations = [  ] 
    field.packing_stations_points = [ Point( p ) for p in field.packing_stations ] 
    field.add_topological_map( )

    field.image_path = "../PlaceUK_satellite/Field_414.png" 
    field.image_dim = ( 212, 362 )

    northsouth_distance = 292.0
    number_of_tunnels = 35 
    tunnel_l = northsouth_distance / number_of_tunnels
    tunnel_w = 65 

    nw_lat = 52.736222
    nw_long = 1.399824 
    nw = field.find_xy_from_longlat( float(nw_long), float(nw_lat) )

    sw_lat = 52.733789
    sw_long = 1.401473
    sw_x,sw_y = field.find_xy_from_longlat( float(sw_long), float(sw_lat) )

    ne_lat = 52.734009
    ne_long = 1.402341
    ne = field.find_xy_from_longlat( float(ne_long), float(ne_lat) )
    
    se_lat = 52.736434 
    se_long = 1.400711
    se = field.find_xy_from_longlat( float(se_long), float(se_lat) )

    polytunnels = [       Polytunnel( ( sw_x-35*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-34*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-33*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-32*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-31*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-30*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-29*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-28*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-27*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-26*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-25*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-24*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-23*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-22*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-21*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-20*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-19*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-18*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-17*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-16*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-15*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-14*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-13*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-12*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-11*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-10*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-9*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-8*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-7*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-6*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-5*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-4*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-3*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-2*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ),
                          Polytunnel( ( sw_x-1*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ) ] 

    angle = math.atan( ( ( nw_lat - sw_lat ) * field.latdif_to_meters )  / ( ( nw_long - sw_long ) * field.longdif_to_meters ) )

    for t in polytunnels: 
        t.rotate_shapely( angle, origin = (sw_x,sw_y), use_radians=True )    

    field.polytunnel_list = polytunnels

    return field
    
def test_field_414( ): 
    
    field_map = make_field_414( )
    field_length, field_width = field_map.dimensions
    
    nw_lat = 52.736222
    nw_long = 1.399824 
    nw = field_map.find_xy_from_longlat( float(nw_long), float(nw_lat) )

    sw_lat = 52.733789
    sw_long = 1.401473
    sw = field_map.find_xy_from_longlat( float(sw_long), float(sw_lat) )

    ne_lat = 52.734009
    ne_long = 1.402341
    ne = field_map.find_xy_from_longlat( float(ne_long), float(ne_lat) )
    
    se_lat = 52.736434 
    se_long = 1.400711
    se = field_map.find_xy_from_longlat( float(se_long), float(se_lat) )

    four_corners = [ nw, sw, ne, se ] 
    
    print( four_corners )
    
    fig, ax = plt.subplots() 
    ax.scatter( [ i[0] for i in four_corners ], [ i[1] for i in four_corners ]  , color = 'red' )

    px,py = field_map.find_xy_from_longlat( 1.401146, 52.734199 )
    ax.scatter( px, py  , color = 'yellow' )

    px,py = field_map.find_xy_from_longlat( 1.401893, 52.734820 )
    ax.scatter( px, py  , color = 'yellow' )

    img = field_map.resized_image( )
    ax.imshow( img[::-1], origin = 'lower' ) 
    
    for t in field_map.polytunnel_list:
        ax.add_patch(Polygon( t.get_coordinates_list(),
            edgecolor = 'pink',
            facecolor = 'green',
            fill=False,
            lw=5, alpha = 0.3)) 
        ax.scatter( t.entrance_point.x, t.entrance_point.y, marker = 'x', color = 'cyan' )

    plt.show() 

def make_field_425( spacetype = SpaceType.CONTINUOUS2D ): 
        
    field_polytunnels = [ ]  
    
    #Creating StrawberryField.
    field = StrawberryField( 400, 420, polytunnel_list = field_polytunnels, spacetype = spacetype )
    field.angle_phi_radians = 0
    field.origin_longitude = 1.380776
    field.origin_latitude = 52.727591 

    #From https://www.johndcook.com/lat_long_distance.html , confirmed using Google Earth    
    field.longdif_to_meters = 67.3615 / 0.001
    field.latdif_to_meters = 111.2299 / 0.001

    field.packing_stations = [  ] 
    field.packing_stations_points = [ Point( p ) for p in field.packing_stations ] 
    field.add_topological_map( )

    field.image_path = "../PlaceUK_satellite/GFSquare_425.png" 
    field.image_dim = ( 410, 430 )

    # Adding the polytunnels,
    tunnel_l = 8.8 
    
    southgroup_eastcorner_longitude = 1.382945  
    southgroup_eastcorner_latitude = 52.729285 

    southgroup_northcorner_longitude = 1.381780
    southgroup_northcorner_latitude = 52.729792
    
    sgeast_x, sgeast_y = field.find_xy_from_longlat_origin( southgroup_eastcorner_longitude, southgroup_eastcorner_latitude )
        
    polytunnels_south = [ Polytunnel( ( sgeast_x-11*tunnel_l, sgeast_y -60 ), tunnel_l, 60, entrance_side = "NORTH" ),
                          Polytunnel( ( sgeast_x-10*tunnel_l, sgeast_y -60 ), tunnel_l, 60, entrance_side = "NORTH" ),
                          Polytunnel( ( sgeast_x-9*tunnel_l, sgeast_y -75 ), tunnel_l, 75, entrance_side = "NORTH" ),
                          Polytunnel( ( sgeast_x-8*tunnel_l, sgeast_y -75 ), tunnel_l, 75, entrance_side = "NORTH" ),
                          Polytunnel( ( sgeast_x-7*tunnel_l, sgeast_y -89 ), tunnel_l, 89, entrance_side = "NORTH" ),
                          Polytunnel( ( sgeast_x-6*tunnel_l, sgeast_y -89 ), tunnel_l, 89, entrance_side = "NORTH" ),
                          Polytunnel( ( sgeast_x-5*tunnel_l, sgeast_y -89 ), tunnel_l, 89, entrance_side = "NORTH" ),
                          Polytunnel( ( sgeast_x-4*tunnel_l, sgeast_y -89 ), tunnel_l, 89, entrance_side = "NORTH" ),
                          Polytunnel( ( sgeast_x-3*tunnel_l, sgeast_y -89 ), tunnel_l, 89, entrance_side = "NORTH" ),
                          Polytunnel( ( sgeast_x-2*tunnel_l, sgeast_y -89 ), tunnel_l, 89, entrance_side = "NORTH" ),
                          Polytunnel( ( sgeast_x-1*tunnel_l, sgeast_y -89 ), tunnel_l, 89, entrance_side = "NORTH" ) ] 
    
    # Rotate the group
    angle = math.atan( ( ( 52.729792 - 52.729285 ) * field.latdif_to_meters )  / ( ( 1.381780 - 1.382945 ) * field.longdif_to_meters ) ) 
    
    for t in polytunnels_south: 
        t.rotate_shapely( angle, origin = (sgeast_x,sgeast_y), use_radians=True )    
    
    middleroup_eastcorner_longitude = 1.383801 
    middleroup_eastcorner_latitude = 52.730000
    
    middlegroup_northcorner_longitude = 1.382635
    middlegroup_northcorner_latitude = 52.730515
    
    mgeast_x, mgeast_y = field.find_xy_from_longlat_origin( middleroup_eastcorner_longitude, middleroup_eastcorner_latitude )

    polytunnels_middle = [ 
                          Polytunnel( ( mgeast_x-11*tunnel_l, mgeast_y -89 ), tunnel_l, 89, entrance_side = "NORTH" ),
                          Polytunnel( ( mgeast_x-10*tunnel_l, mgeast_y -89 ), tunnel_l, 89, entrance_side = "NORTH" ),
                          Polytunnel( ( mgeast_x-9*tunnel_l, mgeast_y -89 ), tunnel_l, 89, entrance_side = "NORTH" ),
                          Polytunnel( ( mgeast_x-8*tunnel_l, mgeast_y -89 ), tunnel_l, 89, entrance_side = "NORTH" ),
                          Polytunnel( ( mgeast_x-7*tunnel_l, mgeast_y -89 ), tunnel_l, 89, entrance_side = "NORTH" ),
                          Polytunnel( ( mgeast_x-6*tunnel_l, mgeast_y -89 ), tunnel_l, 89, entrance_side = "NORTH" ),
                          Polytunnel( ( mgeast_x-5*tunnel_l, mgeast_y -89 ), tunnel_l, 89, entrance_side = "NORTH" ),
                          Polytunnel( ( mgeast_x-4*tunnel_l, mgeast_y -89 ), tunnel_l, 89, entrance_side = "NORTH" ),
                          Polytunnel( ( mgeast_x-3*tunnel_l, mgeast_y -89 ), tunnel_l, 89, entrance_side = "NORTH" ),
                          Polytunnel( ( mgeast_x-2*tunnel_l, mgeast_y -89 ), tunnel_l, 89, entrance_side = "NORTH" ),
                          Polytunnel( ( mgeast_x-1*tunnel_l, mgeast_y -89 ), tunnel_l, 89, entrance_side = "NORTH" ) ] 
    
    angle = math.atan( ( ( 52.730515 - 52.730000 ) * field.latdif_to_meters )  / ( ( 1.382635 - 1.383801 ) * field.longdif_to_meters ) )
    
    for t in polytunnels_middle: 
        t.rotate_shapely( angle, origin = (mgeast_x,mgeast_y), use_radians=True )    
    
    northgroup_eastcorner_longitude = 1.384667 
    northgroup_eastcorner_latitude = 52.730723 
    
    northgroup_northcorner_longitude = 1.383401 
    northgroup_northcorner_latitude = 52.731280

    ngeast_x, ngeast_y = field.find_xy_from_longlat_origin( northgroup_eastcorner_longitude, northgroup_eastcorner_latitude )

    polytunnels_north = [ Polytunnel( ( ngeast_x-12*tunnel_l, ngeast_y -88 ), tunnel_l, 88, entrance_side = "SOUTH" ),
                          Polytunnel( ( ngeast_x-11*tunnel_l, ngeast_y -88 ), tunnel_l, 88, entrance_side = "SOUTH" ),
                          Polytunnel( ( ngeast_x-10*tunnel_l, ngeast_y -88 ), tunnel_l, 88, entrance_side = "SOUTH" ),
                          Polytunnel( ( ngeast_x-9*tunnel_l, ngeast_y -88 ), tunnel_l, 88, entrance_side = "SOUTH" ),
                          Polytunnel( ( ngeast_x-8*tunnel_l, ngeast_y -88 ), tunnel_l, 88, entrance_side = "SOUTH" ),
                          Polytunnel( ( ngeast_x-7*tunnel_l, ngeast_y -88 ), tunnel_l, 88, entrance_side = "SOUTH" ),
                          Polytunnel( ( ngeast_x-6*tunnel_l, ngeast_y -88 ), tunnel_l, 88, entrance_side = "SOUTH" ),
                          Polytunnel( ( ngeast_x-5*tunnel_l, ngeast_y -88 ), tunnel_l, 88, entrance_side = "SOUTH" ),
                          Polytunnel( ( ngeast_x-4*tunnel_l, ngeast_y -88 ), tunnel_l, 88, entrance_side = "SOUTH" ),
                          Polytunnel( ( ngeast_x-3*tunnel_l, ngeast_y -88 ), tunnel_l, 88, entrance_side = "SOUTH" ),
                          Polytunnel( ( ngeast_x-2*tunnel_l, ngeast_y -88 ), tunnel_l, 88, entrance_side = "SOUTH" ),
                          Polytunnel( ( ngeast_x-1*tunnel_l, ngeast_y -88 ), tunnel_l, 88, entrance_side = "SOUTH" ) ] 
    
    field.polytunnel_list = polytunnels_north + polytunnels_middle + polytunnels_south

    angle = math.atan( ( ( 52.731280 - 52.730723 ) * field.latdif_to_meters )  / ( ( 1.383401 - 1.384667 ) * field.longdif_to_meters ) )

    for t in polytunnels_north: 
        t.rotate_shapely( angle, origin = (ngeast_x,ngeast_y), use_radians=True )    

    # Adding a topological map. 
    packing_station_1_longitude =  1.383347
    packing_station_1_latitude = 52.730232 

    ps1_x, ps1_y = field.find_xy_from_longlat_origin( packing_station_1_longitude, packing_station_1_latitude ) 

    packing_station_2_longitude = 1.382504
    packing_station_2_latitude = 52.729532 
    
    ps2_x, ps2_y = field.find_xy_from_longlat_origin( packing_station_2_longitude, packing_station_2_latitude ) 
    
    tm = TopologicalMap( field )
    
    # Packing station nodes. 
    
    field.packing_stations = [ ( ps1_x, ps1_y ) ] 
    field.packing_stations_points = [ Point( p ) for p in field.packing_stations ]
    ps1_node = TMNode( ps1_x, ps1_y )
    ps2_node = TMNode( ps2_x, ps2_y ) 
    field.packing_stations_nodes = [ ps1_node ] 
    tm.add_node( ps1_node ) 
    tm.add_node( ps2_node ) 
    tm.add_edge( ps1_node, ps2_node )
    
    all_north_rows = [] 
    for p in polytunnels_north:
        for r in p.list_of_rows: 

            r.add_nodes( tm )
            tm.add_edge( r.entrance_node, ps1_node )
            all_north_rows.append( r )
            ## r_in_node = TMNode( r.entrance_xy_point.x, r.entrance_xy_point.y )
            ## r_end_node = TMNode( r.end_xy_point.x, r.end_xy_point.y )
            
            #r.add_nodes( tm )
            #tm.add_edge( r.entrance_node, ps1_node )
            
            #tm.add_node( r_in_node ) 
            #tm.add_node( r_end_node ) 

            #tm.add_edge( r_in_node, r_end_node ) 
            #tm.add_edge( r_in_node, ps1_node ) 
    
    for r0,r1 in zip( all_north_rows, all_north_rows[1:] ):
        tm.add_edge( r0.entrance_node,r1.entrance_node )
    
    all_middle_rows = [] 
    for p in polytunnels_middle:
        for r in p.list_of_rows: 
            r.add_nodes( tm )
            tm.add_edge( r.entrance_node, ps1_node )
            all_middle_rows.append( r ) 
            #r_in_node = TMNode( r.entrance_xy_point.x, r.entrance_xy_point.y )
            #r_end_node = TMNode( r.end_xy_point.x, r.end_xy_point.y )
            #tm.add_node( r_in_node ) 
            #tm.add_node( r_end_node ) 

            #tm.add_edge( r_in_node, r_end_node ) 
            #tm.add_edge( r_in_node, ps1_node ) 

    for r0,r1 in zip( all_middle_rows, all_middle_rows[1:] ):
        tm.add_edge( r0.entrance_node,r1.entrance_node )

    all_south_rows = [] 
    for p in polytunnels_south:
        for r in p.list_of_rows: 
            r.add_nodes( tm )
            tm.add_edge( r.entrance_node, ps2_node )
            all_south_rows.append( r ) 
            #r_in_node = TMNode( r.entrance_xy_point.x, r.entrance_xy_point.y )
            #r_end_node = TMNode( r.end_xy_point.x, r.end_xy_point.y )
            #tm.add_node( r_in_node ) 
            #tm.add_node( r_end_node ) 

            #tm.add_edge( r_in_node, r_end_node ) 
            #tm.add_edge( r_in_node, ps2_node ) 
    
    for r0,r1 in zip( all_south_rows, all_south_rows[1:] ):
        tm.add_edge( r0.entrance_node,r1.entrance_node )
    
    field.topological_map = tm 
            
    return field

def test_field_425( ): 
    
    field_map = make_field_425( )
    field_length, field_width = field_map.dimensions

    # 52.729339, 1.381243
    nw_lat = 52.729339
    nw_long = 1.381243 
    nw = field_map.find_xy_from_longlat( float(nw_long), float(nw_lat) )

    #52.727834, 1.383948
    sw_lat = 52.727834
    sw_long = 1.383948
    sw = field_map.find_xy_from_longlat( float(sw_long), float(sw_lat) )

    #52.731282, 1.383390
    ne_lat = 52.731282
    ne_long = 1.383390
    ne = field_map.find_xy_from_longlat( float(ne_long), float(ne_lat) )
    
    #52.729934, 1.386458
    se_lat = 52.729934 
    se_long = 1.386458
    se = field_map.find_xy_from_longlat( float(se_long), float(se_lat) )

    four_corners = [ nw, sw, ne, se ] 
    
    print( four_corners )
    
    fig, ax = plt.subplots() 
    ax.scatter( [ i[0] for i in four_corners ], [ i[1] for i in four_corners ]  , color = 'red' )

    px,py = field_map.find_xy_from_longlat( 1.384657, 52.729633 )
    ax.scatter( px, py  , color = 'yellow' )

    px,py = field_map.find_xy_from_longlat( 1.383277, 52.730232 )
    ax.scatter( px, py  , color = 'yellow' )

    img = field_map.resized_image( )
    ax.imshow( img[::-1], origin = 'lower' ) 
    
    for t in field_map.polytunnel_list:
        ax.add_patch( Polygon( t.get_coordinates_list(),
            edgecolor = 'pink',
            facecolor = 'green',
            fill=False,
            lw=5, alpha = 0.3 ) ) 
        #ax.scatter( t.entrance_point.x, t.entrance_point.y, marker = 'x', color = 'lime' ) 
        #for r in t.list_of_rows: 
            #sc = ax.scatter( r.entrance_xy_point.x, r.entrance_xy_point.y, marker = 'x', color = 'cyan' )
            #sc = ax.scatter( r.end_xy_point.x, r.end_xy_point.y, marker = 'x', color = 'cyan' )

    # Visualise edges! 
    for e in field_map.topological_map.edges: 
        x0 = e.nodes[0].pos_x
        x1 = e.nodes[1].pos_x
        y0 = e.nodes[0].pos_y
        y1 = e.nodes[1].pos_y
        ax.plot( [x0, x1], [y0, y1], color='cyan', linestyle='-', linewidth=1 )

    plt.show() 

if __name__ == '__main__' :

    test_field_425( )
    # test_field_414( )
    # test_field_436( )
