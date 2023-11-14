
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
    
    # Topological map.
    
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
            #tm.add_edge( r.entrance_node, ps1_node )
            all_north_rows.append( r )
    
    for r0,r1 in zip( all_north_rows, all_north_rows[1:] ):
        tm.add_edge( r0.entrance_node,r1.entrance_node )

    north_entrance_nodes = [] 
    for i,p in enumerate(polytunnels_north):
        for j,r in enumerate(p.list_of_rows):
            tm.add_line( r.nodes, line_name = 'Northrows_'+format(i)+'_'+format(j) )
            north_entrance_nodes.append( r.entrance_node )
    
    tm.add_line( north_entrance_nodes, line_name = 'Northpath' )
    
    all_south_rows = [] 
    for p in polytunnels_south:
        for r in p.list_of_rows: 
            r.add_nodes( tm )
            #tm.add_edge( r.entrance_node, ps1_node )
            all_south_rows.append( r )
    
    for r0,r1 in zip( all_south_rows, all_south_rows[1:] ):
        tm.add_edge( r0.entrance_node,r1.entrance_node )

    south_entrance_nodes = [] 
    for i,p in enumerate(polytunnels_south):
        for j,r in enumerate(p.list_of_rows):
            tm.add_line( r.nodes, line_name = 'Southrows_'+format(i)+'_'+format(j) )
            south_entrance_nodes.append( r.entrance_node )

    tm.add_line( south_entrance_nodes, line_name = 'Southpath' )
        
    print('len(tm.nodes)',len(tm.nodes))
    print('len(field.topological_map.nodes)',len(field.topological_map.nodes))

    for i,p in enumerate(polytunnels_south):
        first_row_south_node = p.list_of_rows[0].entrance_node
        first_row_north_node = polytunnels_north[i].list_of_rows[0].entrance_node
        tm.add_line( [first_row_north_node, first_row_south_node], line_name='Northsouth_'+format(i) )
        
    for n in tm.nodes: 
        n.add_longitude_latitude( field )

    field.topological_map = tm

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

if __name__ == '__main__' :

    # test_field_425( )
    # test_field_414( )
    test_field_436( )
