
import enum 
import mesa 
import math
import random

import numpy as np
from shapely.geometry import LineString, Point

from pickers_model.agent.status import Status,RobotStatus
from pickers_model.agent.picking_agent import PickingAgent, PickerType, time_within_range

from pickers_model.agent.picker_parameters import PickerParameterGenerator

# Implements pickers that is waiting, but if the robot does not arrive by some time, it goes to the packing station.

class PCancelW2( PickingAgent ):

    def __init__(self, unique_id, model, picker_id = "" ):
        super().__init__( unique_id, model, picker_id, picker_type = PickerType.CANCELW2  )
                        
        ppgenerator = PickerParameterGenerator()                 
        self.picking_speed = ppgenerator.random_picking_speed() 
        self.max_speed = ppgenerator.random_max_walking_speed() 
        self.patience_model = None
                
        self.cancel_message_required = False
                
    def find_timesteps_till_full( self ): 

        if self.picking_speed != 0: 
            self.time_till_full = ( self.fruit_basket_capacity - self.fruit_in_basket ) / self.picking_speed 
            self.timesteps_till_full = math.floor( self.time_till_full / self.model.step_size )

    def fruit_basket_full( self ): 
        
        return self.fruit_in_basket + self.picking_speed * self.model.step_size > self.fruit_basket_capacity
    
    def find_if_waiting( self ): 
        
        # if continuing to pick for another time step would fill the capacity, return TRUE 
        if self.speed < 1.0 and self.fruit_in_basket + self.picking_speed * self.model.step_size > self.fruit_basket_capacity: 
            return True
        else:
            return False
                
    def find_nearest_robot( self, robot_list ): 
        
        robot_time_dicts = [] 
        for r in robot: 
            d = self.model.field_map.find_distance( robot.pos, self.pos )
            t = d / robot.average_speed
            robot_time_dicts.append( { "robot" : r, "distance" : d, "time" : t } ) 
        return min( robot_time_dicts , key=lambda x:x['time'] )

    # Methods for displaying messages.

    def display_message_simple( self ): 
        
        #if self.model.field_map.position_in_polytunnels( self.pos ): 
            #polytunnel_message = "In polytunnel.\t"
        #else: 
            #polytunnel_message = "NOT in a polytunnel.\t"
        speed_message = "Speed : "+ format( self.speed )
        status_message = " Status : "+ format( self.status )

        fruit_picked_message = "Basket : "+ format( self.fruit_in_basket )
        # print("Hi, I am picker " + str(self.unique_id) + " located at " + str(self.pos) + polytunnel_message+speed_message+status_message )
        print("Picker " + str(self.unique_id) + ". \t Location: " + str(self.pos) +'.\t'+ speed_message+'\t'+status_message +'\t'+ fruit_picked_message + '\t' + format( self.total_fruit_delivered ) ) 
        if self.assigned_row is not None: 
            print( 'Assigned rowfruit picked and percentage:', self.assigned_row.fruit_picked , self.assigned_row.fruit_picked_portion ) 
        
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

    # picking, moving and step

    def w2_pick_row( self ): 
        
        picking_node = self.assigned_row.find_picking_node( ) 
        if self.current_node != picking_node: 
            self.target_node = picking_node 
            # print('current:', self.current_node, 'target:', self.target_node)
            self.moves_assigned = self.model.field_map.topological_map.find_points_on_path( self.current_node, self.target_node, self.max_speed, self.model.step_size ) 
            # self.status = Status.MOVING_ROWS
        else: 
            self.fruit_in_basket += self.picking_speed * self.model.step_size 
            self.total_fruit_picked += self.picking_speed * self.model.step_size
            self.find_timesteps_till_full( ) 
            self.assigned_row.pick( self.picking_speed * self.model.step_size ) 
            # print('Setting status to PICKING.')
            self.status = Status.PICKING

        #TODO -- a line here that updates the amount of unpicked fruit in the tunnel. 
        
        # self.time_till_full = ( self.fruit_basket_capacity - self.fruit_in_basket ) / self.picking_speed 
        # self.timesteps_till_full = math.floor( self.time_till_full / self.model.step_size ) 
        
        if len( self.moves_assigned ) > 0: 
            return self.moves_assigned.pop( 0 )
        else: 
            return self.pos 
    
    def at_packing_station( self ): 
        if self.current_node in self.model.field_map.packing_stations_nodes: 
            return True
        else:
            return False 
    
    def go_to_packing_station( self ): 
        
        # If you're at the packing station, deliver fruit.
        if self.at_packing_station( ): 
            self.total_fruit_delivered += self.fruit_in_basket
            self.fruit_in_basket = 0 
            self.moves_assigned = [  ] 
            # print('Setting status to GOING_BACK.')
            self.status = Status.GOING_BACK
        # Otherwise populate the moves_assigned list. 
        else: 
            nearest_packing_station_node = self.model.field_map.find_nearest_packing_station( self.current_node ) 
            self.target_node = nearest_packing_station_node
            self.moves_assigned = self.model.field_map.topological_map.find_points_on_path( self.current_node, self.target_node, self.max_speed, self.model.step_size ) 
            # print('Setting status to DROPPINGOFF.')
            self.status = Status.DROPPINGOFF
    
    def w2_waiting_too_long( self, model ): 
        
        # get robot waiting time estimate from the model
        if self.robot_assigned:
            return False
        else:
            self.cancel_message_required = True
            return True
    
    def task_finished( self ): 
        
        if len(self.model.field_map.unpicked_rows_list)==0: 
            return True
        else: 
            for r in self.model.field_map.unpicked_rows_list: 
                if len(r.assigned_pickers)==0:
                    return False
            return True
    
    def w2_step( self ): 
        
        if len( self.moves_assigned )>0: 
            # print('Moving moves assigned.')
            return self.moves_assigned.pop( 0 )
        else: 
            self.current_node = self.target_node
        
        # 1. Check if your basket is full. 
        if self.fruit_basket_full(  ): 
            # print('Fruit basket full!')
            # If it is, check whether a robot is coming.  
            if self.w2_waiting_too_long( self.model):
                # print('Setting status to DROPPINGOFF.')
                self.status = Status.DROPPINGOFF 
                self.go_to_packing_station( )
            else:
                # print('Setting status to WAITING.')
                self.status = Status.WAITING
                return self.pos 
        
        # 2. Check whether the task is finished.         
        elif self.task_finished( ): 
            
            #print('Task finished.')
            self.finished = True
            self.status = Status.FINISHED
            return self.pos
        
        # 3. Assign a row. 
        elif self.assigned_row is None:
            # If no rows available, wait. Return current position.
            # print( 'Assigning row' )
            if self.robot_assigned: 
                # print('Setting status to WAITING.')
                self.status = Status.WAITING
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
        
        if self.assigned_row is None:
            self.status = Status.FINISHED
            self.finished = True
            return self.pos
        
        # 3. If assigned row is fully picked, unassign the row. Return current position. 
        if self.assigned_row.fruit_picked_portion==1.0: 
            self.model.field_map.unpicked_rows_list.remove( self.assigned_row ) 
            self.model.field_map.picked_rows_list.append( self.assigned_row ) 
            self.assigned_row = None 
            # print('Setting status to MOVING_ROWS.')
            self.status = Status.MOVING_ROWS
            return self.pos
        elif not self.fruit_basket_full( ): 
            # print( 'Going picking' )
            return self.w2_pick_row( ) 

        new_x, new_y = self.pos        
        return new_x, new_y 

    def move_to_node( self, node_id ): 
        
        for n in self.model.field_map.topological_map.nodes:
            if node_id==n.node_id: 
                self.current_node = n 
                self.pos = ( n.pos_x, n.pos_y )

    def step(self):
        
        if not self.model.all_pickers_registered:
            return

        new_x, new_y = self.w2_step( ) 

        if self.model.spacetype_discrete:
            new_x = int( new_x )
            new_y = int( new_y )

        self.find_speed( new_x, new_y )
        # self.find_status( )
        self.update_ts( ) 
                    
        self.display_message( )
        self.model.field_map.mesa_space.move_agent( self, ( new_x, new_y ) ) 
        
