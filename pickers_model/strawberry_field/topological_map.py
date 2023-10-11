
import math
import numpy as np

import collections

from astar import AStar
from shapely.geometry import Point, LineString
from shapely.affinity import translate,rotate

class TMNode : 
    
    def __init__( self, pos_x, pos_y, node_id = '' ): 
        
        self.pos_x = pos_x 
        self.pos_y = pos_y 
        
        self.node_id = node_id
        
        self.tmap_x = pos_x
        self.tmap_y = pos_y

        self.point = Point( pos_x, pos_y ) 
        
        self.longitude = None 
        self.latitude = None 
        
        self.edges = [] 
        self.neighbors = [] 
        
    def xy_at_node( self, x, y ): 
        if x==self.pos_x and y==self.pos_y:
            return True
        else:
            return False
        
    def rotate_shapely( self, angle, origin = (0,0), use_radians = True ):
        self.point = rotate( self.point , angle , origin = origin, use_radians = use_radians ) 
        self.pos_x = self.point.x
        self.pos_y = self.point.y 
        
    def __str__( self ): 
        return ' ( '+str( self.pos_x )+' , '+str( self.pos_y )+' ) ' 
    
    def string_xy_json( self ): 
        return '"X": "'+str( self.tmap_x )+'", "Y": "'+str( self.tmap_y )+'"'
    
    def get_distance_to_neighbor( self, other_node ): 
        assert( other_node in self.neighbors )
        for e in self.edges: 
            if e.get_other_node( self )==other_node: 
                return e.distance
    
    def get_edge_to_neighbor( self, other_node ): 
        assert( other_node in self.neighbors )
        for e in self.edges: 
            if e.get_other_node( self )==other_node: 
                return e
            
    def find_closest_from_list( self, list_of_points ): 
        
        closest_point = list_of_points[ 0 ]
        smallest_stance = self.point.distance( list_of_points[ 0 ].point ) 
        for p in list_of_points[1:]: 
            if self.point.distance( p.point ) < smallest_stance: 
                closest_point = p 
                smallest_stance = self.point.distance( p.point )  
        
        return closest_point 
        
class TMEdge : 
    
    def __init__( self, n1, n2, edge_id = '' ): 
        
        self.nodes = [ n1, n2 ] 
        self.edge_id = edge_id
        self.distance = math.sqrt(  ( n1.pos_x - n2.pos_x )**2 + ( n1.pos_y - n2.pos_y )**2 )

    def get_other_node( self, n1 ): 
        for n in self.nodes: 
            if n!=n1: 
                return n 

    def make_points_list( self, current_node, speed, time_step ): 
        
        total_time = self.distance / speed 
        number_of_time_steps = math.ceil( total_time / time_step ) 

        #TODO: Add other points here. 
        other_node = self.get_other_node( current_node )
        other_node_xy = ( other_node.point.x , other_node.point.y )
        
        return [ other_node_xy ] 
    
    def __str__( self ): 
        s = ''
        for n in self.nodes: 
            s += 'n: '+n.__str__()
        return s 

    def already_exists( self, list_of_edges ): 
        
        for e in list_of_edges: 
            if collections.Counter( self.nodes ) == collections.Counter( e.nodes ):
                return True
        return False 

class TopologicalMap : 
    
    def __init__( self, field = None ): 
        
        self.field = field
        
        self.nodes = [] 
        self.edges = []
    
    def find_node_with_xy( self, x, y ): 
        
        for n in self.nodes: 
            if n.xy_at_node( x, y ): 
                return n 
        return None
    
    def find_node_by_id( self, node_id ): 
        for n in self.nodes:
            if n.node_id==node_id:
                return n
        return None
    
    def add_node( self, node ): 
        
        self.nodes.append( node )  
        if self.field!=None : 
            longs,lats = self.field.find_longlat_from_xy( node.pos_x , node.pos_y ) 
            self.longitude = longs
            self.latitude = lats
    
    def add_edge( self, n1, n2, edge_id = '' ): 
        
        n1.neighbors.append(n2) 
        n2.neighbors.append(n1) 
        
        new_edge = TMEdge( n1, n2, edge_id )
        self.edges.append( new_edge ) 
        n1.edges.append( new_edge ) 
        n2.edges.append( new_edge ) 
        
    def rotate_shapely( self, angle, origin = (0,0), use_radians = True ): 
        
        for n in self.nodes: 
            n.rotate_shapely( angle, origin, use_radians ) 
            
    def string_edges( self ): 
        se = ''
        for e in self.edges: 
            se += e.__str__() +'\n'
        return se
    
    def find_path( self, current_node, target_node ): 
        a = PathAStar( self ) 
        return list( a.astar( current_node, target_node ) ) 
    
    def find_time_to_reach( self, current_node, target_node, speed ): 
        list_of_nodes = self.find_path( current_node, target_node )
        if len( list_of_nodes ) < 2: 
            return 0
        else: 
            line = LineString( [ ( n.point.x, n.point.y ) for n in list_of_nodes ] ) 
            return line.length / speed
    
    def find_timesteps_to_reach( self, current_node, target_node, speed, time_step ): 
        time_to_reach = self.find_time_to_reach( current_node, target_node, speed )
        return math.ceil( time_to_reach / time_step )
    
    def find_points_on_path( self, current_node, target_node, speed, time_step ): 
        
        list_of_nodes = self.find_path( current_node, target_node ) 
        if len( list_of_nodes ) < 2: 
            return [ ( current_node.point.x, current_node.point.y ) ]

        line = LineString( [ ( n.point.x, n.point.y ) for n in list_of_nodes ] ) 
        distance_delta = speed * time_step 
        distances = np.arange( 0, line.length, distance_delta ) 
        points =  [ line.interpolate(d) for d in distances ] 
        
        return [ ( p.x, p.y ) for p in points ] + [ ( target_node.point.x , target_node.point.y ) ] 
        
class PathAStar(AStar): 
    
    def __init__( self, tmap ): 
        
        self.topological_map = tmap
    
    def heuristic_cost_estimate(self, n1, n2): 
        return n1.point.distance( n2.point ) 
    
    def distance_between(self, n1, n2):
        return n1.get_distance_to_neighbor( n2 ) 
    
    def neighbors(self, node): 
        return node.neighbors 
        
    
    
            
    
    
