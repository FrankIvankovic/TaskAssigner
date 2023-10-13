
import enum 
import mesa 
import math
import random

import numpy as np
from shapely.geometry import LineString, Point

from pickers_model.agent.status import Status,RobotStatus

class PickerType(enum.Enum):
    RANDOM = 1
    DETERMINISTIC = 2
    TRACKERTROLLEY = 3
    PROBABILISTIC = 4
    PROBABILISTIC_ROBOTS = 5
    PATIENT_PICKER = 6
    WAITING1 = 7
    WAITING2 = 8 
    WAITING3 = 9
    WAITING4 = 10
    WAITING5 = 11
    

def time_within_range( time, interval_dict ): 
    
    if interval_dict[ "start" ] <= time < interval_dict[ "end" ]: 
        return True
    else:
        return False 

class PickingAgent(mesa.Agent):

    def __init__(self, unique_id, model, picker_id = "", picker_type = PickerType.RANDOM, predefined_moves = [], probabilistic_model = None ):
        super().__init__(unique_id, model)

        self.picker_id = picker_id 
        self.payroll_n = None #3 digit ID from the farm 
        self.picker_type = picker_type
        self.predefined_moves = predefined_moves
        self.probabilistic_model = probabilistic_model
        self.max_speed = 0.8
        self.finished = False #Is the picker done for the day?

        self.speed = 0.0
        self.status = Status.MOVING_ROWS 
        self.scatterplot = None 
        
        # picking related stuff
        self.picking_speed = 500.0 
        self.fruit_basket_capacity = 15000 #grams 
        self.fruit_in_basket = 0.0 
        self.one_tray_capacity = 5000.0
        self.total_fruit_picked = 0.0 
        self.total_fruit_delivered = 0.0 
        self.current_node = None 
        self.target_node = None 
        self.robot_assigned = False
        self.assigned_row = None

        # assignment of actions
        self.breaks = [] 
        self.moves_assigned = [] 
        self.scanning_records = [] # scanning records have a form { "datetime": datetime, "weight": weight }
        
        # related to trays
        self.time_till_full = 0 
        self.timesteps_till_full = 0
        self.find_timesteps_till_full( ) 
        
        # values used in analysing the time spent on different activities 
        self.current_period_picking_time = 0.0
        self.current_period_waiting_time = 0.0 
        self.current_period_running_time = 0.0 
        
        self.picking_times_list = [ ] 
        self.waiting_times_list = [ ] 
        self.running_times_list = [ ] 
        
        self.total_picking_time = 0 
        self.total_waiting_time = 0 
        self.total_running_time = 0 
        self.total_break_time = 0 
        self.total_droppingoff_time = 0 
        self.total_movingrows_time = 0 
        self.total_goingback_time = 0

    def find_timesteps_till_full( self ): 

        if self.picking_speed !=0: 
            self.time_till_full = ( self.fruit_basket_capacity - self.fruit_in_basket ) / self.picking_speed 
            self.timesteps_till_full = math.floor( self.time_till_full / self.model.step_size )

    def find_speed( self, new_x, new_y ):

        current_x, current_y = self.pos
        distance = math.sqrt( ( current_x - new_x )**2 + ( current_y - new_y )**2 )
        time = self.model.step_size
        self.speed = distance / time

    def fruit_basket_full( self ): 
        
        return self.fruit_in_basket + self.picking_speed * self.model.step_size > self.fruit_basket_capacity
    
    def find_if_waiting( self ): 
        
        # if continuing to pick for another time step would fill the capacity, return TRUE 
        if self.speed < 1.0 and self.fruit_in_basket + self.picking_speed * self.model.step_size > self.fruit_basket_capacity: 
            return True
        else:
            return False

    def find_status( self ): 
        # self.find_status_1( )
        self.find_status_2( ) 

    def find_status_1( self ):

        #TODO: Write a bit better model.

        in_polytunnels = self.model.field_map.position_in_polytunnels( self.pos )
        if self.speed > 1.0 :
            self.status = Status.RUNNING
        elif in_polytunnels:
            if self.fruit_in_basket < self.fruit_basket_capacity : 
                self.status = Status.PICKING 
            #elif self.robot_assigned:
                #self.status = Status.WAITING_ASSIGNED
            else:
                self.status = Status.WAITING
        else:
            self.status = Status.BREAK 
    
    def find_status_2( self ): 

        in_polytunnels = self.model.field_map.position_in_polytunnels( self.pos )
        if self.status_on_break( ) or self.finished:
            self.status = Status.BREAK 
        elif self.find_if_waiting( ): 
            self.status = Status.WAITING
        elif in_polytunnels and self.speed < 0.7 : 
            self.status = Status.PICKING 
        else: 
            self.status = Status.RUNNING
    
    def update_ts( self ): 
        
        if self.status == Status.RUNNING: 
            self.current_period_running_time += self.model.step_size 
            self.total_running_time += self.model.step_size
        elif self.status == Status.WAITING: 
            self.current_period_waiting_time += self.model.step_size 
            self.total_waiting_time += self.model.step_size
        elif self.status == Status.PICKING: 
            self.current_period_picking_time += self.model.step_size 
            self.total_picking_time += self.model.step_size
        elif self.status == Status.BREAK: 
            self.total_break_time += self.model.step_size
        elif self.status == Status.DROPPINGOFF:
            self.total_droppingoff_time += self.model.step_size
        elif self.status == Status.MOVING_ROWS: 
            self.total_movingrows_time += self.model.step_size
        elif self.status == Status.GOING_BACK:
            self.total_goingback_time += self.model.step_size 
    
    def status_on_break( self ): 
        for b in self.breaks: 
            if time_within_range(  self.model.time_counter, b ): 
                return True
        return False
    
    def find_status_with_robots( self ): 
        
        #TODO: Method not used????????
        
        in_polytunnels = self.model.field_map.position_in_polytunnels( self.pos )
        if self.speed > 1.0 :
            self.status = Status.RUNNING
        elif self.find_if_waiting( ):
            self.status = Status.WAITING
        elif in_polytunnels:
            self.status = Status.PICKING
        else:
            self.status = Status.BREAK 
        
    def choose_move_random(self):

        """ Random move left, right, up or down. """

        current_x, current_y = self.pos
        possible_steps = [ (current_x, current_y) ]
        for ps in [ (current_x + self.max_speed, current_y) , ( current_x - self.max_speed, current_y) , (current_x, current_y + self.max_speed) , (current_x, current_y- self.max_speed) ]:
            if not self.model.field_map.mesa_space.out_of_bounds( ps ):
                possible_steps.append( ps )
        new_x, new_y = random.choice( possible_steps )

        return (new_x, new_y)

    def choose_move_predefined(self):

        """ Move in a predefined way (e.g. reading from GPS data). """

        next_entry = self.predefined_moves.pop( 0 )

        #\print( "PREDEFINED.", next_entry[ "LONGITUDE" ], next_entry[ "LATITUDE" ] )

        next_entry_x = next_entry[ "x" ]
        next_entry_y = next_entry[ "y" ]

        print( next_entry )

        if self.model.field_map.mesa_space.out_of_bounds( ( next_entry_x , next_entry_y ) ):
            next_move = self.pos
        else:
            next_move = ( next_entry_x , next_entry_y )

        return ( next_move )

    def choose_move_probabilistic(self):

        """ Choose a move based on a probabilistic model. """

        current_x, current_y = self.pos
        next_move_chosen = False

        while not next_move_chosen:
            next_move_x, next_move_y = self.probabilistic_model.select_move( current_x, current_y, self.model.step_size )
            if not self.model.field_map.mesa_space.out_of_bounds( (next_move_x, next_move_y) ):
                next_move_chosen = True
        return ( next_move_x, next_move_y ) 
    
    def choose_move_probabilistic_robots(self): 
        
        current_x, current_y = self.pos
        next_move_chosen = False

        if self.find_if_waiting( ): 
            return ( current_x, current_y )

        while not next_move_chosen:
            next_move_x, next_move_y = self.probabilistic_model.select_move( current_x, current_y, self.model.step_size )
            if not self.model.field_map.mesa_space.out_of_bounds( (next_move_x, next_move_y) ):
                next_move_chosen = True
        
        return ( next_move_x, next_move_y ) 

    def move_random(self):

        """ Random move left, right, up or down. """

        current_x, current_y = self.pos
        possible_steps = [ (current_x, current_y) ] 
        for ps in [ (current_x + self.max_speed, current_y) , ( current_x - self.max_speed, current_y) , (current_x, current_y + self.max_speed) , (current_x, current_y- self.max_speed) ]:
            if not self.model.field_map.mesa_space.out_of_bounds( ps ): 
                possible_steps.append( ps )
                #print( "APPENDING" )
        new_position_x, new_position_y = random.choice( possible_steps )
        
        if self.model.spacetype_discrete:
            new_position = ( int(new_position_x), int(new_position_y) )
        else:
            new_position = ( new_position_x, new_position_y )

        self.model.field_map.mesa_space.move_agent(self, new_position)

    def move_predefined(self):

        """ Move in a predefined way (e.g. reading from GPS data). """

        next_move = self.predefined_moves.pop( 0 )
        if self.model.field_map.mesa_space.out_of_bounds( ps ):
            new_position = self.pos
        else:
            new_position = ( next_move[ "x" ], next_move[ "y" ] )
            
        self.model.field_map.mesa_space.move_agent( self, new_position )

    def go_to_break( self ): 
        
        self.status = Status.BREAK

    def pick_fruit( self ): 
        
        self.fruit_in_basket += self.picking_speed * self.model.step_size 
        
        #TODO -- a line here that updates the amount of unpicked fruit in the tunnel. 
        
        # self.time_till_full = ( self.fruit_basket_capacity - self.fruit_in_basket ) / self.picking_speed 
        # self.timesteps_till_full = math.floor( self.time_till_full / self.model.step_size ) 
        self.find_timesteps_till_full( )
        
    def find_nearest_robot( self, robot_list ): 
        
        robot_time_dicts = [] 
        for r in robot: 
            d = self.model.field_map.find_distance( robot.pos, self.pos )
            t = d / robot.average_speed
            robot_time_dicts.append( { "robot" : r, "distance" : d, "time" : t } ) 
        return min( robot_time_dicts , key=lambda x:x['time'] )

    # Methods for displaying messages.

    def display_message_records( self ): 
        
        nextscan = format( self.scanning_records[ 0 ][ 'weight' ] )
        
        print( "Picker "+ self.payroll_n + " Records_length: "+ format( len( self.scanning_records ) ) + " Next scan: " + nextscan + " at " +  format( self.scanning_records[ 0 ][ 'datetime' ] ) )

    def display_message_simple( self ): 
        
        if self.model.field_map.position_in_polytunnels( self.pos ): 
            polytunnel_message = "In polytunnel.\t"
        else: 
            polytunnel_message = "NOT in a polytunnel.\t"
        speed_message = "Speed : "+ format( self.speed )
        status_message = " Status : "+ format( self.status )
        if self.picker_type == PickerType.DETERMINISTIC: 
            if len( self.scanning_records )>0:
                nextscan = format( self.scanning_records[ 0 ][ 'weight' ] )
                fruit_picked_message = "Picker " + self.payroll_n + " Next scan: "+ nextscan + " at "+format( self.scanning_records[ 0 ][ 'datetime' ] )
            else: 
                fruit_picked_message = ''
        else:
            fruit_picked_message = "Fruit picked : "+ format( self.fruit_in_basket )
        # print("Hi, I am picker " + str(self.unique_id) + " located at " + str(self.pos) + polytunnel_message+speed_message+status_message )
        print("Picker " + str(self.unique_id) + ". \t Location: " + str(self.pos) +'.\t'+ polytunnel_message+speed_message+'\t'+status_message +'\t'+ fruit_picked_message ) 
        if self.assigned_row is not None: 
            print( 'Assigned rowfruit picked and percentage:', self.assigned_row.fruit_picked , self.assigned_row.fruit_picked_portion ) 
        
    #Example MQTT message: {"RESERVED_3": "", "HDOP": "0.7", "RESERVED_1": "", "HOUR": "05", "YEAR": "2023", "VPA": "", "LATITUDE": "52.749698", "UTC_DATE_TIME": "20230523051819.000", "ERROR": false, "MSL_ALTITUDE": "22.100", "FIX_STATUS": "1", "PDOP_RATING": "excellent", "MONTH": "05", "SECOND": "19.000", "C/N0_MAX": "48", "GNSS_SATELITES_IN_VIEW": "18", "HPA": "", "HDOP_RATING": "ideal", "LONGITUDE": "1.429846", "CSQ": "Wifi", "MEAN_DOP_RATING": "ideal", "DAY": "23", "GPS_SATELITES_USED": "9", "VDOP": "0.7", "PDOP": "1.0", "VDOP_RATING": "ideal", "user": "STD_v2_246f284a6c94", "CLIENT_ID": "246f284a6c94", "COURSE_OVER_GROUND": "330.9", "FIX_MODE": "1", "GNSS_RUN_STATUS": "1", "SPEED_OVER_GROUND": "0.00", "MINUTE": "18", "GLONASS_SATELITES_USED": "6", "RESERVED_2": ""}

    def display_message_MQTT( self ): 
        
        current_datetime = self.model.time_counter
        # utcdatetime_string = str( current_datetime.year ) + str( current_datetime.month ) + str( current_datetime.day ) + str( current_datetime.hour ) + str( current_datetime.minute ) + str( current_datetime.second ) 
        x,y = self.pos 
        utcdatetime_string = current_datetime.strftime( "%Y%m%d%H%M%S.%f" )
        longitude,latitude = self.model.field_map.find_longlat_from_xy_origin( x,y )
        
        hour = '"HOUR": "'+format( current_datetime.hour )+'"'
        year = '"YEAR": "'+format( current_datetime.year )+'"'
        latitude = '"LATITUDE": "'+format( latitude )+'"'
        utcdateandtime = '"UTC_DATE_TIME": "'+format( utcdatetime_string )+'"'
        month = '"MONTH": "'+format( current_datetime.month )+'"'
        second = '"SECOND": "'+format( current_datetime.second )+'"'
        longitude = '"LONGITUDE": "'+format( longitude )+'"'
        day = '"DAY": "'+format( current_datetime.day )+'"' 
        clientid = '"CLIENTID": "'+format( self.picker_id )+'"'
        minute = '"MINUTE": "'+format( current_datetime.minute )+'"'
        print( '{' + hour + ', ' + year + ', ' + latitude + ', ' + utcdateandtime + ', ' + month + ', ' + second + ', ' + longitude + ', ' + day + ', ' + clientid + ', ' + minute + '}' )

    def display_message(self):
        
        if self.model.messagetype=="None": 
            return
        elif self.model.messagetype=="Simple":
            self.display_message_simple( ) 
        elif self.model.messagetype=="MQTT":
            self.display_message_MQTT( )
        elif self.model.messagetype=="Records":
            self.display_message_records( )

    def w1_pick_row( self ): 
        
        picking_node = self.assigned_row.find_picking_node( ) 
        if self.current_node != picking_node: 
            self.target_node = picking_node 
            print('current:', self.current_node, 'target:', self.target_node)
            self.moves_assigned = self.model.field_map.topological_map.find_points_on_path( self.current_node, self.target_node, self.max_speed, self.model.step_size )
        else: 
            self.fruit_in_basket += self.picking_speed * self.model.step_size 
            self.total_fruit_picked += self.picking_speed * self.model.step_size
            self.find_timesteps_till_full( ) 
            self.assigned_row.pick( self.picking_speed * self.model.step_size )

        #TODO -- a line here that updates the amount of unpicked fruit in the tunnel. 
        
        # self.time_till_full = ( self.fruit_basket_capacity - self.fruit_in_basket ) / self.picking_speed 
        # self.timesteps_till_full = math.floor( self.time_till_full / self.model.step_size ) 
        
        if len( self.moves_assigned ) > 0: 
            return self.moves_assigned.pop( 0 )
        else: 
            return self.pos 
        
    def w1_step( self ): 
        
        if len( self.moves_assigned )>0: 
            print( 'Moving predefined' )
            return self.moves_assigned.pop( 0 )
        else: 
            self.current_node = self.target_node
        
        # 1. Check if your basket is full. 
        if self.fruit_basket_full(  ): 
            # If it is, wait. Return current position.         
            return self.pos 
        # 2. Elif check if there is no assigned row.         
        elif self.assigned_row is None:
            # If no rows available, wait. Return current position.
            print( 'Assigning row' )
            if len(self.model.field_map.unpicked_rows_list)==0: 
                self.finished = True
                return self.pos 
            else: 
                # Assign row. 
                for r in self.model.field_map.unpicked_rows_list: 
                    if len(r.assigned_pickers)>0:
                        continue
                    else:
                        r.assigned_pickers.append( self ) 
                        self.assigned_row = r 
                        break
        
        # 3. If assigned row is fully picked, unassign the row. Return current position. 
        if self.assigned_row.fruit_picked_portion==1.0: 
            self.model.field_map.unpicked_rows_list.remove( self.assigned_row ) 
            self.model.field_map.picked_rows_list.append( self.assigned_row ) 
            self.assigned_row = None 
            return self.pos
        else: 
            print( 'Going picking' )
            return self.w1_pick_row( ) 

        new_x, new_y = self.pos        
        return new_x, new_y 

    # Step. Modifies position and other attributes, decides what the picker will do next.

    def pick_predefined( self ): 
        
        if len( self.scanning_records )>0: 
            if self.model.time_counter > self.scanning_records[0][ 'datetime' ]: 
                new_record = self.scanning_records.pop( 0 )
                self.total_fruit_picked += new_record['weight']

    def move_to_node( self, node_id ): 
        
        for n in self.model.field_map.topological_map.nodes:
            if node_id==n.node_id: 
                self.current_node = n 
                self.pos = ( n.pos_x, n.pos_y )

    def step(self):

        if self.model.field_map.position_in_polytunnels( self.pos ): 
            polytunnel_message = "In polytunnel.\t"
        else: 
            polytunnel_message = "NOT in a polytunnel.\t"

        if self.picker_type == PickerType.DETERMINISTIC:
            self.pick_predefined( )
            new_x, new_y = self.choose_move_predefined()
        elif self.picker_type == PickerType.PROBABILISTIC:
            new_x, new_y = self.choose_move_probabilistic()
        elif self.picker_type == PickerType.PATIENT_PICKER: 
            new_x, new_y = self.pos
        elif self.picker_type == PickerType.WAITING1: 
            new_x, new_y = self.w1_step( ) 
        else:
            new_x, new_y = self.choose_move_random( )

        if self.model.spacetype_discrete:
            new_x = int( new_x )
            new_y = int( new_y )

        self.find_speed( new_x, new_y )
        self.find_status( )
        self.update_ts( ) 

        if self.picker_type == PickerType.PATIENT_PICKER:
            if self.status == Status.PICKING: 
                self.pick_fruit( ) 
            if self.status == Status.WAITING:
                self.total_waiting_time += self.model.step_size
                    
        self.display_message( )
        self.model.field_map.mesa_space.move_agent( self, ( new_x, new_y ) ) 
        
