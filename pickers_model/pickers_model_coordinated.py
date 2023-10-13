
import sys

import mesa
import math
import random
import datetime

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from shapely.geometry import LineString, Point
import datetime

import pickers_model.strawberry_field.strawberry_field as sf
import pickers_model.picker_routes as pr
import pickers_model.agent.probabilistic_movement as pmove 

from pickers_model.agent.robot_runner import RobotRunner
from pickers_model.agent.robot_schedule import RobotAssignment 
from pickers_model.agent.picking_agent import PickerType
from pickers_model.agent.picking_agent_coordinated import PTrackerTrolley
from pickers_model.agent.status import Status,RobotStatus
from pickers_model.pickers_model import PickersModel
            
class PickersModelTaskAssigner( PickersModel ):
    """A model with some number of agents."""

    def __init__( self, field_map, pickers ):
        super().__init__( field_map, len( pickers ) , picker_type = PickerType.TRACKERTROLLEY )
        
        self.pickers = [] 
        self.robots = [] 
                
        #self.schedule = mesa.time.RandomActivation(self)
        self.schedule = mesa.time.BaseScheduler(self)

        # Create agents
        i = 0
        for picker in pickers:
            if len( self.pickers ) >= self.num_agents:
                    break
            self.add_TaskAssigner_picker( i, picker )
            i += 1            
    
    def add_TaskAssigner_picker( self, i, p_id ):
        
        # print("Adding a TaskAssigner picker.")
        a = PTrackerTrolley( i, self, picker_id = p_id )
        self.schedule.add(a)
        self.pickers.append(a) 
        starting_x, starting_y = 0,0        
        self.field_map.mesa_space.place_agent( a, ( starting_x, starting_y ) ) 
        
    def update_robot( self, reading ): # to actually update the model
        
        print("Updating robot")
        #TODO: Add update.

    def update_picker_battery( self, reading ): # to actually update the model
        
        for p in self.pickers:
            if p.picker_id == reading["user"]:
                #print('Here: ', p.picker_id, reading) 
                p.battery_message = reading
                #print('Updated: ', p.battery_message)

    def update_picker_status( self, msg_content ): # to actually update the model
        
        states = msg_content[ 'states' ]  
        for p in self.pickers:
            if p.picker_id in states.keys():
                #print('Here: ', p.picker_id, states[ p.picker_id ] ) 
                p.status_state = states[ p.picker_id ]
                print('Updated: ', p.picker_id, p.status_state)
                #if states[ p.picker_id ]=='INIT': 
                if states[ p.picker_id ]=='ARRIVED': #TODO: Change to something else, but not INIT, as that would reset them all the time.
                    print('Robot arrived, reseting time counter')
                    p.time_in_polytunnels = 0.0
                    p.polytunnel_count = 0
                #elif states[ p.picker_id ]=='REGISTERED':
                    #print('Reseting to default time')
                    #p.time_in_polytunnels = p.start_time_in_polytunnels

    def update_picker_gps( self, reading ): # to actually update the model
        
        print("Updating picker") 

        picker_long = reading[ 'LONGITUDE' ]
        picker_lat = reading[ 'LATITUDE' ] 
        date_and_time = reading[ 'UTC_DATE_TIME' ]
        if picker_long=='' or picker_lat=='' or date_and_time=='':
            return

        #print(reading['user'])
        
        picker = next(( x for x in self.pickers if x.picker_id == reading['user'] ), None)
        picker.pos = self.field_map.find_xy_from_longlat( float(picker_long), float(picker_lat) ) 
        # print( 'In polytunnel?', self.field_map.position_in_polytunnels( picker.pos ))
    
        dt = datetime.datetime.strptime( reading[ 'UTC_DATE_TIME' ], '%Y%m%d%H%M%S.%f' )        
        
        if picker.last_reading!=None and self.field_map.position_in_polytunnels( picker.pos ):
            dt0 = datetime.datetime.strptime( picker.last_reading[ 'UTC_DATE_TIME' ], '%Y%m%d%H%M%S.%f' ) 
            tdelta = dt - dt0 #seconds since last reading
            picker.time_in_polytunnels += tdelta.seconds 
            picker.polytunnel_count += 1
        picker.last_reading = reading
        print('Picker', picker.picker_id, ' In polytunnel?', self.field_map.position_in_polytunnels( picker.pos ),' Polytunnel count:', picker.polytunnel_count, ' picker.time_in_polytunnels:', picker.time_in_polytunnels )
    
    def call_required( self ): 
        # return self.call_required_PolytunnelCount()
        return self.call_required_SRR_TimeInPolytunnel( self )
    
    def call_required_PolytunnelCount( self ):
        
        print("Call required?") 
        
        pickers_with_full_baskets = [] 
        for p in self.pickers: 
            if p.polytunnel_count > 0:
                pickers_with_full_baskets.append( p )
        
        if len( pickers_with_full_baskets )>0:
        
            p = random.choice( pickers_with_full_baskets )
            print( 'Returning', p.picker_id )
            p.polytunnel_count = 0
            return p.picker_id_short
        else:
            return ''
    
    def call_required_TimeInPolytunnel( self ):

        print("Call required?") 

        states_that_can_call = [ 'INIT', 'REGISTERED' ] 
        time_threshold = 150.0 
        
        for p in self.pickers:
            print( p.picker_id, p.status_state, p.status_state in states_that_can_call )
        
        pickers_that_can_call = [ p for p in self.pickers if p.status_state in states_that_can_call ] 
        pickers_with_full_baskets = [ p for p in pickers_that_can_call if p.time_in_polytunnels > time_threshold ] 
        
        print( 'Pirckers that can call:', pickers_that_can_call, '  Pickers with full baskets: ', pickers_with_full_baskets )
        
        if len( pickers_with_full_baskets )>0: 
            p = pickers_with_full_baskets[0]
            #p.time_in_polytunnels = 0.0 
            return p.picker_id_short
        else:
            return ''
    
    def find_pickers_considered_TimeInPolytunnel( self ):
        
        states_that_can_call = [ 'INIT', 'REGISTERED' ] 
        pickers_that_can_call = [ p for p in self.pickers if p.status_state in states_that_can_call ] 
        # we only consider the pickers we believe have at least one full tray
        pickers_considered = [ p for p in pickers_that_can_call if p.fruit_in_basket > p.one_tray_capacity ] 
        
        for p in self.pickers:
            print( p.picker_id, p.status_state, p.status_state in states_that_can_call )
        print( 'Pirckers that can call:', pickers_that_can_call, '  Pickers with full baskets: ', pickers_considered ) 
        
        return pickers_considered
    
    def return_first_picker_id_from_list( pickers_list ): 
        if len( pickers_list )>0:
            return pickers_list[0].picker_id_short 
        else: 
            return ''
    
    def call_required_SRR_TimeInPolytunnel( self ): 
        
        pickers_considered = self.find_pickers_considered_TimeInPolytunnel( )
        if len( pickers_considered )>0: 
            p = pickers_considered[0]
            #p.time_in_polytunnels = 0.0 
            return pickers_considered[0].picker_id_short
        else:
            return ''

    def call_required_ORR1_TimeInPolytunnel( self ): 
        
        #returns the picker with most fruit in basket
        subset_of_pickers = self.find_pickers_considered_TimeInPolytunnel( )
        subset_of_pickers.sort( key=lambda x: x.fruit_in_basket, reverse=True )
        return return_first_picker_id_from_list( subset_of_pickers )

    def call_required_ORR1I_TimeInPolytunnel( self ): 
        
        #returns the picker with most fruit in basket
        subset_of_pickers = self.find_pickers_considered_TimeInPolytunnel( )
        subset_of_pickers.sort( key=lambda x: x.fruit_in_basket, reverse=False )
        return return_first_picker_id_from_list( subset_of_pickers )

    def call_required_ORR2_TimeInPolytunnel( self ): 

        subset_of_pickers = self.find_pickers_considered_TimeInPolytunnel( )
        if len( subset_of_pickers )<1:
            return ''
        pickers_times = [  ] 
        for picker in subset_of_pickers: 
            x,y = picker.pos
            picker.current_node = self.field_map.topological_map.find_closest_node( x,y )
            t = self.field_map.topological_map.find_time_to_reach( picker.current_node, picker.model.field_map.find_nearest_packing_station( picker.current_node ), picker.max_speed )
            pickers_times.append( { 'picker': picker, 'time_to_packing_station': t } )
        pickers_times.sort( key=lambda x: x[ 'time_to_packing_station' ], reverse=True )
        p = pickers_times[ 0 ]
        return p[ 'picker' ].picker_id_short

    def call_required_ORR2I_TimeInPolytunnel( self ): 

        subset_of_pickers = self.find_pickers_considered_TimeInPolytunnel( )
        if len( subset_of_pickers )<1:
            return ''
        pickers_times = [  ] 
        for picker in subset_of_pickers: 
            x,y = picker.pos
            picker.current_node = self.field_map.topological_map.find_closest_node( x,y )
            t = self.field_map.topological_map.find_time_to_reach( picker.current_node, picker.model.field_map.find_nearest_packing_station( picker.current_node ), picker.max_speed )
            pickers_times.append( { 'picker': picker, 'time_to_packing_station': t } )
        pickers_times.sort( key=lambda x: x[ 'time_to_packing_station' ], reverse=False )
        p = pickers_times[ 0 ]
        return p[ 'picker' ].picker_id_short
    
    def call_required_DistanceCovered( self ):
        pass 
    
    def step(self):
    
        self.packing_station_step( ) 
        self.schedule.step()
        self.move_robots()
        self.step_number += 1 
        self.time_counter += datetime.timedelta( seconds = self.step_size )
        
