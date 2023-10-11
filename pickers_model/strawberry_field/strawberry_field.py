
import mesa
import enum
import math 
import random 
import numpy

from shapely.geometry import Point, Polygon
from shapely.affinity import translate,rotate

import pickers_model.strawberry_field.topological_map as tmap 
import cv2

class SpaceType(enum.Enum):
    GRID2D = "GRID2D"
    CONTINUOUS2D = "CONTINUOUS2D"

class StrawberryField : 
    
    def __init__( self, length, width, polytunnel_list = [], obstacles = [], spacetype = SpaceType.CONTINUOUS2D ):
        
        self.dimensions = (length,width) 
        self.polytunnel_list = polytunnel_list 
        self.obstacles = obstacles #e.g. a reservoir in field 423 
        
        self.unpicked_rows_list = [] 
        self.picked_rows_list = [] 
        
        #self.packing_stations = [ ( round(length/2) , round(width/2) ) ]
        #self.packing_stations_points = [ Point( p ) for p in self.packing_stations ] 

        self.packing_stations = None
        self.packing_stations_points = None 
        self.packing_stations_nodes = [ ] 

        # self.lower_left_coordinates = ( 0, 0 ) 
        #self.upper_right_coordinates = ( 0, 0 )

        self.origin_longitude = 0.0
        self.origin_latitude = 0.0 

        self.spacetype = spacetype

        #Estimated from Google maps for PlaceUK.
        self.longdif_to_meters = 67.3654 / 0.001
        self.latdif_to_meters = 111.2298 / 0.001
        self.angle_phi_radians = 0.0 
        
        # Reference point --- point with known x,y and long,lat.
        # Use it, for example, for a corner of polytunnels.
        
        self.rp_x = 0.0
        self.rp_y = 0.0
        self.rp_longitude = self.origin_longitude
        self.rp_latitude = self.origin_latitude
        
        # If using more than one reference point.
        # Should be a dict { "x":x , "y":y, "LONGITUDE": longitude , "LATITUDE", latitude }.
        self.rp_list = [] 
        
        self.topological_map = None 

        #Mesa space
        if self.spacetype == SpaceType.CONTINUOUS2D:
            self.mesa_space = mesa.space.ContinuousSpace( length, width, False )
        elif self.spacetype == SpaceType.GRID2D:
            self.mesa_space = mesa.space.SingleGrid( int(round(length)), int(round(width)), False )
        else:
            raise Exception( "Invalid spacetype specified." ) 
        
        self.image_path = None 
        self.image_dim = None 

    def resized_image( self ): 

        img = cv2.imread(  self.image_path )
        return cv2.resize( img, self.image_dim )        

    def move_xy_packing_stations( self, move_by_x, move_by_y ): 
        
        new_packing_stations = [] 
        for p in self.packing_stations: 
            px , py = p
            new_packing_stations.append( ( px + move_by_x, py + move_by_y ) )
        self.packing_stations = new_packing_stations 
        self.packing_stations_points = [ Point( p ) for p in self.packing_stations ] 

    def rotate_shapely_packing_stations( self, angle, origin = (0,0), use_radians=True ): 
        
        new_packing_stations = []
        new_packing_stations_points = [] 
        for p in self.packing_stations_points: 
            new_p = rotate( p, angle, origin = origin, use_radians = use_radians ) 
            new_packing_stations.append( ( new_p.x, new_p.y ) )
            new_packing_stations_points.append( new_p ) 

    def find_xy_from_longlat_origin( self, longitude, latitude ):

        ll_long = self.origin_longitude 
        ll_lat = self.origin_latitude

        long_m = self.longdif_to_meters * ( longitude - ll_long )
        lat_m = self.latdif_to_meters * ( latitude - ll_lat )

        x = long_m * math.cos( self.angle_phi_radians ) + lat_m * math.sin( self.angle_phi_radians )
        y = -1 * long_m * math.sin( self.angle_phi_radians ) + lat_m * math.cos( self.angle_phi_radians )

        return x,y

    def find_xy_from_longlat_rpoint( self, rpoint, longitude, latitude ): 
        
        rpoint_long = rpoint[ "LONGITUDE" ] 
        rpoint_lat = rpoint[ "LATITUDE" ]
        
        long_m = self.longdif_to_meters * ( longitude - rpoint_long )
        lat_m = self.latdif_to_meters * ( latitude - rpoint_lat )
        
        xdiff = long_m * math.cos( self.angle_phi_radians ) + lat_m * math.sin( self.angle_phi_radians )
        ydiff = -1 * long_m * math.sin( self.angle_phi_radians ) + lat_m * math.cos( self.angle_phi_radians )
        
        x = xdiff + rpoint[ "x" ] 
        y = ydiff + rpoint[ "y" ]
        
        return x,y

    def find_xy_from_longlat_rp( self, longitude, latitude ): 
        
        rp_dict = { "LONGITUDE": self.rp_longitude, "LATITUDE": self.rp_latitude, "x": self.rp_x, "y": self.rp_y }
        return self.find_xy_from_longlat_rpoint( rp_dict, longitude, latitude )

    def find_xy_from_longlat( self, longitude, latitude ): 
        return self.find_xy_from_longlat_origin( longitude, latitude )

    def find_longlat_from_xy( self, x, y ): 
        return self.find_longlat_from_xy_origin( x, y )
    
    def find_longlat_from_xy_origin( self, x, y ):

        # Find the x and y coordinates in a coordinate system where x axis is parallel with the equator and y axis with meridians.
        # Should be equal to x and y if angle_phi_radians is zero. 
        xdiff = x * math.cos( -1 * self.angle_phi_radians ) + y * math.sin( -1 * self.angle_phi_radians )
        ydiff = -1 * x *  math.sin( -1 * self.angle_phi_radians ) + y * math.cos( -1 * self.angle_phi_radians )
        
        # Turn them into longitude and latitude. 
        x_degrees = xdiff / self.longdif_to_meters
        y_degrees = ydiff / self.latdif_to_meters
        
        longitude = self.origin_longitude + x_degrees
        latitude = self.origin_latitude + y_degrees
        
        return longitude,latitude

    def position_in_polytunnels(self, position):
        
        """ Takes a position pair (x,y) and determines whether it's within any of the polytunnels."""
        
        for p in self.polytunnel_list: 
            if p.position_in_polytunnel( position ):
                return True
        return False 
    
    def position_return_polytunnel( self, position ): 
        
        """ Takes a position pair (x,y) and determines which polytunnel it is in. Returns None if the position is outside the tunnels."""
        
        for p in self.polytunnel_list: 
            if p.position_in_polytunnel( position ):
                return p
        return None 
            
    def make_field_larger( self, offset_left = 0.0, offset_bottom = 0.0, additional_right = 0.0, additional_top = 0.0 ):
    
        #Adjust polytunnels
        for t in self.polytunnel_list:
            t.move_xy( offset_left, offset_bottom ) 
            
        #Adjsut rp
        self.rp_x = self.rp_x + offset_left 
        self.rp_y = self.rp_y + offset_bottom

        for rp in self.rp_list: 
            rp[ "x" ] = rp[ "x" ] + offset_left
            rp[ "y" ] = rp[ "y" ] + offset_bottom

        #Adjust length and width
        original_length, original_width = self.dimensions
        new_length = original_length + offset_left + additional_right
        new_width = original_width + offset_bottom + additional_top
        
        self.dimensions = (new_length, new_width)

    def add_topological_map( self ): 
        
        tm = tmap.TopologicalMap( self )
        
        #Add a node to each packing station. 
        for ps in self.packing_stations: 
            ps_x, ps_y = ps
            ps_node = tmap.TMNode( ps_x, ps_y ) 
            self.packing_stations_nodes.append( ps_node ) 
            tm.add_node( ps_node ) 
        
        #For each polytunnel... 
        for p in self.polytunnel_list: 
            
            # Add an etrance point node. 
            e_x = p.entrance_point.x 
            e_y = p.entrance_point.y
            e_node = tmap.TMNode( e_x, e_y ) 
            tm.add_node( e_node ) 
            
            # Add an edge between each entrance point node and each packing station. 
            for ps_node in self.packing_stations_nodes: 
                tm.add_edge( e_node, ps_node ) 

            # For each point in the polytunnel, make a node. 
            for point in p.points_in_polytunnel: 
                p_x , p_y = point
                p_node = tmap.TMNode( p_x, p_y )
                p.points_in_polytunnel_nodes.append( p_node )
                tm.add_node( p_node ) 

            # Connect the points in the polytunnel. 
            if len( p.points_in_polytunnel_nodes ) > 0:
                tm.add_edge( e_node, p.points_in_polytunnel_nodes[ 0 ] ) 
                for i,n in enumerate( p.points_in_polytunnel_nodes[1:] ): 
                    tm.add_edge( p.points_in_polytunnel_nodes[ i-1 ], n ) 
        
        #print( 'self.model.field_map.packing_stations_nodes:', self.packing_stations_nodes )
        
        self.topological_map = tm 
        
    def find_nearest_packing_station( self, current_node ): 
        return current_node.find_closest_from_list( self.packing_stations_nodes )

    def add_yields_to_rows_uniform( self, total_yield ): 
        
        # NOTE: Total yield should be in grams. 
        
        #1. Find the number of rows and their lengths
        number_of_rows = 0 
        total_row_length = 0 
        
        for p in self.polytunnels_list: 
            for r in p.list_of_rows: 
                number_of_rows += 1 
                total_row_length += r.length 
            
        for p in self.polytunnel_list: 
            for r in p.list_of_rows: 
                r.fruit_yield = round( total_yield * ( r.length / total_row_length ) ) 
            p.fruit_yield = sum( r.fruit_yield for r in p.list_of_rows ) 
            
