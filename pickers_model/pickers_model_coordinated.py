
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
        self.packing_station = None 
        
        self.packing_station_schedule = [ ]  
        self.packing_station_i = 0  
                
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
                if states[ p.picker_id ]=='INIT': 
                    print('Robot arrived, reseting time counter')
                    p.time_in_polytunnels = 0.0
                    p.polytunnel_count = 0

    def update_picker_gps( self, reading ): # to actually update the model
        
        print("Updating picker") 

        picker_long = reading[ 'LONGITUDE' ]
        picker_lat = reading[ 'LATITUDE' ] 
        date_and_time = reading[ 'UTC_DATE_TIME' ]
        if picker_long=='' or picker_lat=='' or date_and_time=='':
            return

        print(reading['user'])
        
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
        return self.call_required_TimeInPolytunnel()
    
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
        time_threshold = 90.0 
        
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
    
    def call_required_DistanceCovered( self ):
        pass 
    
    def step(self):
    
        self.packing_station_step( ) 
        
        self.schedule.step()
        self.move_robots()
        self.step_number += 1 
        self.time_counter += datetime.timedelta( seconds = self.step_size )
        
        #x.append(np.random.rand(1)*10)
        #y.append(np.random.rand(1)*10)
        #sc.set_offsets(np.c_[x,y])
        #fig.canvas.draw_idle()
        #plt.pause(0.1)
