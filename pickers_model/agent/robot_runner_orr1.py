
import mesa
import datetime

from shapely.geometry import LineString, Point

from pickers_model.agent.status import Status,RobotStatus
from pickers_model.agent.robot_schedule import RobotAssignment
from pickers_model.agent.robot_runner import RobotRunner

class RobotRunnerOrderedRR1(RobotRunner): 
    
    def __init__(self, unique_id, model ):
        super().__init__(unique_id, model)
        
        # print( 'Adding ORR1 robot runner.' )
        
        self.robot_id = unique_id
        self.robot_id_name = ''
        self.model = model 
        self.max_speed = 0.7   
        
        self.pos = self.model.field_map.packing_stations[0]
        self.fruit_in_basket = 1 
        self.total_fruit_delivered = 0 

        self.moves_assigned = [] 
        
        # print( 'self.model.field_map.packing_stations_nodes:', self.model.field_map.packing_stations_nodes )
        
        self.current_node = self.model.field_map.packing_stations_nodes[ 0 ]  
        self.target_node = None 
        self.target_picker = None 
        self.target_row = None

        self.scatterplot = None 
        
        self.status = RobotStatus.WAITING
        self.total_waiting_time = 0 
        self.total_running_time = 0
    
    def at_packing_station( self ): 
        if self.current_node in self.model.field_map.packing_stations_nodes: 
            return True
        else:
            return False 
    
    def at_picker( self ): 
        selfpoint = Point( self.pos ) 
        if self.target_picker is None: 
            return False
        elif selfpoint.distance( Point( self.target_picker.pos ) ) < 2.0: 
            return True
        else:
            return False 
    
    def at_polytunnel_entrace( self ): 
        
        # print( 'Is it at polytunnel entrance?' )
        if self.target_picker is None:
            return False
        elif self.current_node == self.target_picker.assigned_row.entrance_node:
            # print( 'Yes, it is.' )
            return True
        else:
            return False
    
    def assign_picker_anticipating( self ): 
    
        subset_of_pickers = [] 
        for picker in self.model.pickers:
            if not picker.robot_assigned and picker.status in [ Status.PICKING , Status.WAITING ]: 
                subset_of_pickers.append( picker )
        
        for picker in subset_of_pickers: 
            timesteps_to_reach = self.model.field_map.topological_map.find_timesteps_to_reach( self.current_node, picker.current_node, self.max_speed, self.model.step_size )
            if picker.timesteps_till_full < timesteps_to_reach: 
                self.target_picker = picker 
                self.target_node = picker.current_node 
                self.target_row = picker.assigned_row
                self.moves_assigned = self.model.field_map.topological_map.find_points_on_path( self.current_node, self.target_node, self.max_speed, self.model.step_size ) 
                # picker.status = Status.WAITING_ASSIGNED 
                picker.robot_assigned = True 
                self.status = RobotStatus.PICKINGUP
                break

    def assign_picker_simple( self ): 
    
        subset_of_pickers = [] 
        for picker in self.model.pickers:
            if not picker.robot_assigned and picker.status in [ Status.WAITING ]: 
                subset_of_pickers.append( picker )
        
        for picker in subset_of_pickers: 
                self.target_picker = picker 
                self.target_node = picker.current_node 
                self.moves_assigned = self.model.field_map.topological_map.find_points_on_path( self.current_node, self.target_node, self.max_speed, self.model.step_size ) 
                # picker.status = Status.WAITING_ASSIGNED 
                picker.robot_assigned = True 
                self.status = RobotStatus.PICKINGUP 
                
                #Adding a RobotAssignment 
                dt = self.model.time_counter
                new_assignment = RobotAssignment( dt, self, self.target_picker, self.target_node )
                self.model.robot_schedule.append( new_assignment )
                
                break

    def assign_picker_orr1( self ):
        
        subset_of_pickers = [] 
        for picker in self.model.pickers:
            if not picker.robot_assigned and picker.fruit_in_basket > picker.fruit_basket_capacity/2.0: 
                subset_of_pickers.append( picker )

        subset_of_pickers.sort( key=lambda x: x.fruit_in_basket, reverse=True )

        #print('List of pickers:')

        #for p in subset_of_pickers:
            #print( p.unique_id, p.fruit_in_basket )
            
        #if self.target_picker!=None:
            #print( 'Target picker before choosing: ', self.target_picker.unique_id )
        #else:
            #print( 'Target picker before choosing: ', self.target_picker )

        for picker in subset_of_pickers: 
            
                self.target_picker = picker 
                # self.target_node = picker.assigned_row.entrance_node
                self.target_node = picker.current_node
                picker.robot_assigned = True 
                self.status = RobotStatus.PICKINGUP 

                self.moves_assigned = self.model.field_map.topological_map.find_points_on_path( self.current_node, self.target_node, self.max_speed, self.model.step_size ) 
                # picker.status = Status.WAITING_ASSIGNED 
                
                #Adding a RobotAssignment 
                dt = self.model.time_counter
                new_assignment = RobotAssignment( dt, self, self.target_picker, self.target_node )
                self.model.robot_schedule.append( new_assignment )
                
                break
        
        #if self.target_picker!=None:
            #print( 'Target picker after choosing: ', self.target_picker.unique_id )
        #else:
            #print( 'Target picker after choosing: ', self.target_picker )
        
    def assign_picker( self ):
        # self.assign_picker_simple( )
        self.assign_picker_orr1( )
    
    def go_to_packing_station( self ): 

        # If you're at the packing station, deliver fruit.
        if self.at_packing_station( ): 
            self.total_fruit_delivered += self.fruit_in_basket
            self.fruit_in_basket = 0 
            self.moves_assigned = [  ] 
        # Otherwise populate the moves_assigned list. 
        else: 
            nearest_packing_station_node = self.model.field_map.find_nearest_packing_station( self.current_node ) 
            self.target_node = nearest_packing_station_node
            self.moves_assigned = self.model.field_map.topological_map.find_points_on_path( self.current_node, self.target_node, self.max_speed, self.model.step_size ) 
            self.status = RobotStatus.DROPPINGOFF
    
    def go_to_picker( self ): 
        
        if self.at_picker( ): 
            self.fruit_in_basket = self.target_picker.fruit_in_basket
            self.target_picker.fruit_in_basket = 0 
            self.target_picker.robot_assigned = False 
            self.target_picker.status = Status.PICKING 
            self.target_picker.find_timesteps_till_full( ) 
            self.target_picker = None 
            self.moves_assigned = [  ]
        elif self.target_picker != None: 
            # print( 'At polytunnel entrance' )
            self.target_node = self.target_picker.current_node
            self.moves_assigned = self.model.field_map.topological_map.find_points_on_path( self.current_node, self.target_node, self.max_speed, self.model.step_size ) 
        else: 
            self.assign_picker( ) 
    
    def decide_next_move_simple_1 ( self ) : 
        
        #If PICKINGUP, go towards the assigned picker. If DROPPINGOFF, go to the packing_station. Else, see if there are any pickers who will need assistance soon. 
        
        # If picker is assigned, adjust the course to make sure you go towards the picker.
        #if self.target_picker != None: 
            #self.target_node = self.target_picker.current_node 
            #self.status = RobotStatus.PICKINGUP 
            
            #print( 'Reasigning moves...' )
            #self.moves_assigned = self.model.field_map.topological_map.find_points_on_path( self.current_node, self.target_node, self.max_speed, self.model.step_size ) 
            #print( 'Removig the start...' )
            ## self.moves_assigned.pop( 0 )
            
        if len( self.moves_assigned ) == 0: 
            if self.fruit_in_basket > 0: 
                self.go_to_packing_station( )
            else:
                self.go_to_picker( ) 
        
        # print( 'Moves in the list?', len( self.moves_assigned ) > 1 )        
        if len( self.moves_assigned ) == 0: 
            self.status = RobotStatus.WAITING
            return self.pos
        elif len( self.moves_assigned ) == 1: 
            # print( 'Current node is target node' )
            self.current_node = self.target_node
            self.target_node = None 
            return self.moves_assigned.pop( 0 ) 
            
        elif len( self.moves_assigned ) > 1: 
            # print( 'Next move on the list.' )
            next_move = self.moves_assigned.pop( 0 ) 
            # print(  'Pop move: ',  next_move )
        else:
            next_move = self.pos
        
        return next_move
    
    def display_message_simple( self ): 
        
        print( "Robot "+format(self.unique_id)+'\t'+ format(self.status) +".\t Location: "+ format(self.pos)+"\t Fruit: "+format(self.fruit_in_basket) + "\t Fruit delivered: "+format(self.total_fruit_delivered ) + '\t Picker assigned : ' + format( self. target_picker ) + '\t Len(moves assigned ):' +format(len(self.moves_assigned)) )
    
    def display_message_MQTT( self ): 
        
        current_datetime = self.model.time_counter
        # utcdatetime_string = str( current_datetime.year ) + str( current_datetime.month ) + str( current_datetime.day ) + str( current_datetime.hour ) + str( current_datetime.minute ) + str( current_datetime.second )
        utcdatetime_string = current_datetime.strftime( "%Y%m%d%H%M%S.%f" )
        x,y = self.pos 
        longitude,latitude = self.model.field_map.find_longlat_from_xy_origin( x,y )
        
        hour = '"HOUR": "'+format( current_datetime.hour )+'"'
        year = '"YEAR": "'+format( current_datetime.year )+'"'
        latitude = '"LATITUDE": "'+format( latitude )+'"'
        utcdateandtime = '"UTC_DATE_TIME": "'+format( utcdatetime_string )+'"'
        month = '"MONTH": "'+format( current_datetime.month )+'"'
        second = '"SECOND": "'+format( current_datetime.second )+'"'
        longitude = '"LONGITUDE": "'+format( longitude )+'"'
        day = '"DAY": "'+format( current_datetime.day )+'"' 
        clientid = '"CLIENTID": "'+format( self.robot_id )+'"'
        minute = '"MINUTE": "'+format( current_datetime.minute )+'"'
        print( '{' + hour + ', ' + year + ', ' + latitude + ', ' + utcdateandtime + ', ' + month + ', ' + second + ', ' + longitude + ', ' + day + ', ' + clientid + ', ' + minute + '}' )
    
    def display_message( self ): 
        
        if self.model.messagetype=="None": 
            return
        elif self.model.messagetype=="Simple":
            self.display_message_simple( ) 
        elif self.model.messagetype=="MQTT":
            self.display_message_MQTT( )
    
    def step( self ): 
        
        self.display_message( ) 
        
        new_x,new_y = self.decide_next_move_simple_1( ) 
        # if self.model.spacetype==sf.SpaceType.GRID2D:
        if self.model.spacetype_discrete:
            new_x = int( new_x )
            new_y = int( new_y ) 
            
        if self.status == RobotStatus.WAITING:
            self.total_waiting_time += self.model.step_size
        else:
            self.total_running_time += self.model.step_size

        #print( 'Current pos: ', self.pos )        
        #print( 'New pos: ' , new_x, new_y )
        
        self.pos = ( new_x, new_y )
