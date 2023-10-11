
import mesa
import math 
import random 
import numpy

from shapely.geometry import Point, Polygon
from shapely.affinity import translate,rotate 

from pickers_model.strawberry_field.topological_map import TMNode,TMEdge,TopologicalMap

class PolytunnelRow : 
    
    def __init__( self, polytunnel, i ): 
        
        self.polytunnel = polytunnel
        self.i = i
        self.assigned_pickers = [] 
        self.fruit_yield = self.polytunnel.fruit_yield 
        self.length = self.polytunnel.length
        
        self.nodes = [] 
        
        #Portion picked -- as pickers pick, the value goes up. Starts at 0.0, ends with 1.0. 
        self.fruit_picked = 0.0 
        self.fruit_picked_portion = 0.0 
        
        self.entrance_xy_point = None 
        self.end_xy_point = None 
        
        self.entrance_node = None
        
    def pick( self, amount ): 
        
        self.fruit_picked += amount
        self.fruit_picked_portion = self.fruit_picked / self.fruit_yield 
        if self.fruit_picked >= self.fruit_yield:
            self.fruit_picked = self.fruit_yield 
            self.fruit_picked_portion = 1.0 
    
    def add_nodes( self, topological_map, number_of_nodes = 50 ): 
        entrance_x,entrance_y = self.entrance_xy_point.x,self.entrance_xy_point.y
        end_x, end_y = self.end_xy_point.x,self.end_xy_point.y
        points = zip ( numpy.linspace( entrance_x, end_x, number_of_nodes ), numpy.linspace( entrance_y, end_y, number_of_nodes ) )
        
        self.nodes = [ TMNode( px,py ) for px,py in points ]
        self.entrance_node = self.nodes[0] 
        for n in self.nodes:
            topological_map.add_node( n )
        
        for n0,n1 in zip( self.nodes, self.nodes[1:] ):
            topological_map.add_edge( n0,n1 )
    
    def find_picking_node( self ):
        
        #Find picking point
        entrance_x,entrance_y = self.entrance_xy_point.x,self.entrance_xy_point.y
        end_x,end_y = self.end_xy_point.x,self.end_xy_point.y
        #print( 'Entrance: ', entrance_x,entrance_y, 'End:', end_x,end_y )
        x = entrance_x + self.fruit_picked_portion * ( end_x - entrance_x ) 
        y = entrance_y + self.fruit_picked_portion * ( end_y - entrance_y )
        
        #Find closest node
        closest_node = self.nodes[ 0 ] 
        shortest_distance = math.sqrt( ( closest_node.pos_x - x )**2 + ( closest_node.pos_y - y )**2 ) 
        for n in self.nodes: 
            #print( 'Looking for a closer node. Current: ', closest_node.pos_x,closest_node.pos_y, 'Wanted: ',x,y, 'n', n.pos_x, n.pos_y)
            new_distance = math.sqrt( ( n.pos_x - x )**2 + ( n.pos_y - y )**2 )
            if new_distance < shortest_distance:
                #print( 'Found a closer node' )
                shortest_distance = new_distance
                closest_node = n
        return closest_node

class Polytunnel : 
    
    def __init__( self, lower_left, length, width, angle = 0, number_of_rows = 6, entrance_side = "NORTH", fruit_yield = 1000 ):
        
        self.lower_left = lower_left # (x,y) coordinates of the lower left corner

        self.length = length
        self.width = width 
        self.angle = angle
        
        self.fruit_yield = fruit_yield 
        
        # 
        ll_x, ll_y = lower_left 

        coords = ( ( ll_x, ll_y ), ( ll_x, ll_y + width), ( ll_x + length, ll_y + width ), ( ll_x + length, ll_y ), ( ll_x, ll_y ) )
        p = Polygon( coords )
        self.polygon = rotate( p, self.angle, origin = lower_left, use_radians = True )
        b = self.polygon.boundary.coords

        #entrance coordinates
        # NOTE! The whole polytunnel was previously treated as having one entrance.
        # Now, we have an entrance to each row. 
        entrance_x = ll_x + length/2
        if entrance_side == "NORTH": 
            entrance_y = ll_y + width + 1 
            polygon_entry_line_endpoints = ( b[1] , b[2] )
            polygon_end_line_endpoints = ( b[-1] , b[-2] )
        else:
            entrance_y = ll_y -1
            polygon_entry_line_endpoints = ( b[-1] , b[-2] )
            polygon_end_line_endpoints = ( b[1] , b[2] )

        e = Point( entrance_x, entrance_y )
        self.entrance_point = rotate( e, self.angle, origin = lower_left, use_radians = True ) 
        self.entrance_point_node = None 

        # Create rows 
        self.number_of_rows = number_of_rows 
        entry_corner1,entry_corner2 = polygon_entry_line_endpoints
        entry_line_array = numpy.linspace( entry_corner1, entry_corner2, num= 2*self.number_of_rows+1)
        entry_points = entry_line_array[ 1::2 ]
        end_corner1,end_corner2 = polygon_end_line_endpoints
        end_line_array = numpy.linspace( end_corner1, end_corner2, num= 2*self.number_of_rows+1)
        end_points = end_line_array[ 1::2 ] 
        
        assert( len( entry_points ) == self.number_of_rows )
        assert( len( end_points ) == self.number_of_rows )
        
        self.list_of_rows = [] 
        for r in range( number_of_rows ): 
            new_r = PolytunnelRow( self, r )
            new_r.entrance_xy_point = Point( entry_points[r] )
            new_r.end_xy_point = Point( end_points[r] )
            self.list_of_rows.append( new_r )

        # Create entrance to each row. 
        
        #Arbitrary point is a point in the polytunnel used for testing. 
        self.arbitrary_point = None 
        self.arbitrary_point_node = None 
        
        self.points_in_polytunnel = [  ] # a list of points, used in creating a topological map
        self.points_in_polytunnel_nodes = [  ] # nodes corresponding to the points 

        self.ll_longitude = None
        self.ll_latitude = None
        self.lr_longitude = None
        self.lr_latitude = None

        if self.angle==0:
            self.xmin = ll_x
            self.xmax = ll_x + length
            self.ymin = ll_y
            self.ymax = ll_y + width
            self.mesa_space = mesa.space.ContinuousSpace( self.xmax, self.ymax, False, self.xmin, self.ymin )
            #self.mesa_space = mesa.space.SingleGrid( self.xmax, self.ymax, False, self.xmin, self.ymin )
        else:
            xmin, ymin, xmax, ymax = self.polygon.bounds
            self.xmin = xmin
            self.xmax = ymin
            self.ymin = xmax
            self.ymax = ymax
            
    def position_in_polytunnel_simple( self, position ): 
        x, y = position
        if angle!=0:
            raise("Object at an angle!")
        return not( x < self.xmin or x >= self.xmax or y < self.ymin or y >= self.ymax )
        
    def position_in_polytunnel_mesa( self, position ): 
        if angle!=0:
            raise("Object at an angle!")
        return not ( self.mesa_space.out_of_bounds( position ) ) 

    def position_in_polytunnel_geometry( self, position ):
        return self.polygon.contains( Point ( position ) )

    def position_in_polytunnel( self, position ):
        return self.position_in_polytunnel_geometry( position )

    def get_coordinates_list( self ):
        return list( self.polygon.boundary.coords )
    
    def move_xy( self, move_by_x, move_by_y ): 
        old_x, old_y = self.lower_left
        new_x = old_x + move_by_x 
        new_y = old_y + move_by_y
        self.lower_left = new_x, new_y

        self.polygon = translate( self.polygon, move_by_x, move_by_y )
        self.entrance_point = translate( self.entrance_point, move_by_x, move_by_y ) 
        
        for r in self.list_of_rows:
            r.entrance_xy_point = translate( r.entrance_xy_point, move_by_x, move_by_y )
            r.end_xy_point = translate( r.end_xy_point, move_by_x, move_by_y )

    def rotate_shapely( self, angle, origin = (0,0), use_radians=True ):

        self.angle += angle
        self.polygon = rotate( self.polygon, angle, origin = origin, use_radians = use_radians )

        xmin, ymin, xmax, ymax = self.polygon.bounds
        self.xmin = xmin
        self.xmax = ymin
        self.ymin = xmax
        self.ymax = ymax

        point = rotate( Point(self.lower_left), angle, origin = origin, use_radians = use_radians )
        self.lower_left = point.x, point.y
        e = rotate( self.entrance_point, angle, origin = origin, use_radians = use_radians )
        self.entrance_point = e 
        
        for r in self.list_of_rows:
            r.entrance_xy_point = rotate( r.entrance_xy_point, angle, origin = origin, use_radians = use_radians )
            r.end_xy_point = rotate( r.end_xy_point, angle, origin = origin, use_radians = use_radians )

    def add_random_point( self ): 
        
        ll_x, ll_y = self.lower_left 
        arbitrary_point_x = ll_x + random.randint( 0, math.floor( self.length ) )  
        arbitrary_point_y = ll_y + random.randint( 0, math.floor( self.width ) )  
        # ap = Point( arbitrary_point_x, arbitrary_point_y ) 
        # self.arbitrary_point = rotate( ap, self.angle, origin = lower_left, use_radians = True ) 
        
        self.points_in_polytunnel.append( ( arbitrary_point_x, arbitrary_point_y ) ) 
