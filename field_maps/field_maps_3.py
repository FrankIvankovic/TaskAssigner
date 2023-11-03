
# Should be Riseholme.

import mesa
import math

from shapely.geometry import Point, Polygon 

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon

import cv2

from pickers_model.strawberry_field.topological_map import TMNode, TMEdge, TopologicalMap 
from field_maps.topological_map_from_yaml import create_tmap_from_yamls
from pickers_model.strawberry_field.polytunnel import Polytunnel 
from pickers_model.strawberry_field.strawberry_field import StrawberryField,SpaceType

def guess_topological_map( field ):
    
    packing_station_1_latitude = 53.268594 
    packing_station_1_longitude =  -0.524220

    ps1_x, ps1_y = field.find_xy_from_longlat_origin( packing_station_1_longitude, packing_station_1_latitude ) 
        
    tm = TopologicalMap( field ) 
    
    field.packing_stations = [ ( ps1_x, ps1_y ) ] 
    field.packing_stations_points = [ Point( p ) for p in field.packing_stations ]
    ps1_node = TMNode( ps1_x, ps1_y )
    field.packing_stations_nodes = [ ps1_node ] 
    tm.add_node( ps1_node ) 
    
    all_rows = [] 
    for p in field.polytunnel_list:
        for r in p.list_of_rows: 
            r.add_nodes( tm, number_of_nodes = 10 )
            tm.add_edge( r.entrance_node, ps1_node )
            all_rows.append( r )
    
    for r0,r1 in zip( all_rows, all_rows[1:] ):
        tm.add_edge( r0.entrance_node,r1.entrance_node )

    for n in tm.nodes:
        n.node_id = 'WayPoint68'

    field.topological_map = tm 
    
    return tm

def make_Riseholme_1( spacetype = SpaceType.CONTINUOUS2D ):
    
    field = StrawberryField( 49, 58, polytunnel_list = [ ], spacetype = spacetype )
    field.angle_phi_radians = 0
    field.origin_longitude = -0.524356
    field.origin_latitude = 53.268248 

    #From https://www.johndcook.com/lat_long_distance.html , confirmed using Google Earth    
    field.longdif_to_meters = 66.5232 / 0.001
    field.latdif_to_meters = 111.2298 / 0.001
    
    field.image_path = "../PlaceUK_satellite/Riseholme_1.png" 
    field.image_dim = ( 49, 58 ) 
    
    tunnel_l = 8.0 
    tunnel_w = 24.0 
    
    # 53.268317, -0.524267
    
    sw_lat = 53.268317
    sw_long = -0.524267
    sw_x,sw_y = field.find_xy_from_longlat( float(sw_long), float(sw_lat) )
    
    # 53.268337, -0.524033
    
    se_lat = 53.268337
    se_long = -0.524033 
    
    field_polytunnels = [ Polytunnel( ( sw_x+0*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ), 
                   Polytunnel( ( sw_x+1*tunnel_l, sw_y ), tunnel_l, tunnel_w, entrance_side = "NORTH" ) ] 

    angle = math.atan( ( ( se_lat - sw_lat ) * field.latdif_to_meters )  / ( ( se_long - sw_long ) * field.longdif_to_meters ) )

    field.polytunnel_list = field_polytunnels 

    for t in field.polytunnel_list: 
        t.rotate_shapely( angle, origin = (sw_x,sw_y), use_radians=True )    

    datumfile = '../TopologicalMaps/datum.yaml'
    # filename = '../TopologicalMaps/tmap.yaml'
    filename = '../TopologicalMaps/network.tmap2'

    field.topological_map = guess_topological_map( field ) 

    #field.topological_map = create_tmap_from_yamls( filename, datumfile, field.longdif_to_meters , field.latdif_to_meters )
    #packing_station_1_latitude = 53.268594 
    #packing_station_1_longitude =  -0.524220 
    #ps_x, ps_y = field.find_xy_from_longlat( packing_station_1_longitude, packing_station_1_latitude )
    #n = field.topological_map.find_closest_node( ps_x, ps_y )
    #nx = n.pos_x
    #ny = n.pos_y
    #field.packing_stations = [ ( nx, ny ) ] 
    #field.packing_stations_nodes = [ n ]
    
    #print( 'PACKING STATIONS:', field.packing_stations )

    #for n in field.topological_map.nodes: 
        
        ## turn x and y
        #x,y = field.find_xy_from_longlat_origin( n.longitude, n.latitude )
        #n.pos_x = x
        #n.pos_y = y

    return field

