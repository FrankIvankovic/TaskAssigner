
import sys

import mesa
import math
import random
import datetime

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from shapely.geometry import LineString, Point

import pickers_model.strawberry_field.strawberry_field as sf
import pickers_model.picker_routes as pr
import pickers_model.agent.probabilistic_movement as pmove 

from pickers_model.agent.robot_runner import RobotRunner
from pickers_model.agent.robot_schedule import RobotAssignment 
from pickers_model.agent.picking_agent import PickingAgent,PickerType,time_within_range
from pickers_model.agent.picking_agent_deterministic import PDeterministic
from pickers_model.agent.status import Status,RobotStatus
from pickers_model.pickers_model import PickersModel

def choose_picker_subset( picker_data, picker_subset ): 
    
    if picker_subset is None: 
        return picker_data 
    picker_subset_dict = dict( (k, picker_data[ k ]) for k in picker_subset )
    return picker_subset_dict
            
class PickersModelDeterministic( PickersModel ):
    """A model with some number of agents."""

    def __init__(self, field_map, pdata, step = 3.0, picker_subset = None ):
        pdata = choose_picker_subset( pdata, picker_subset )
        super().__init__( field_map, len( pdata.keys() ) , picker_type = PickerType.DETERMINISTIC, picker_data = pdata, step_size = step )
        
        self.pickers = [] 
        self.robots = [] 
        self.packing_station = None 
        
        #TODO: Account for the fact that the location of the packing station changes.
        self.packing_station_schedule = [ ]  
        self.packing_station_i = 0  
        
        # Time related stuff
        
        # TODO: Change stuff here to find the start!
        self.step_number = 0
        
        #self.schedule = mesa.time.RandomActivation(self)
        self.schedule = mesa.time.BaseScheduler(self)

        # pickers_routes = pr.read_json_interpolate( self.field_map, 3.0, picker_data )
        # offset_x0, offset_y0, offset_x1, offset_y1 = self.offsets
        # pickers_routes = pr.adjust_xy_offset( pickers_routes, offset_x0, offset_y0 )
        picker_routes = pdata

        # Create agents
        i = 0
        mintime, _ = pr.find_min_and_max_datetime( picker_routes )
        self.start_time_datetime = mintime
        self.time_counter = mintime

        interpolated_picker_routes = pr.interpolate_positions_pickers( picker_routes, self.step_size )

        for picker in interpolated_picker_routes.keys():
            if len( self.pickers ) >= self.num_agents:
                    break
            route = interpolated_picker_routes[ picker ]
            self.add_deterministic_picker( i, picker, route )
            i += 1            
            
    def add_deterministic_picker( self, i, picker, route ):

        print("Adding a deterministic picker.")

        # a = PickingAgent( i, self, picker_id = picker, picker_type = PickerType.DETERMINISTIC, predefined_moves = route )
        a = PDeterministic( i, self, picker_id = picker, predefined_moves = route )
        a.picking_speed = 0
        self.schedule.add(a)
        self.pickers.append(a)

        x = route[ 0 ][ "x" ]
        y = route[ 0 ][ "y" ]

        if self.field_map.mesa_space.out_of_bounds( ( x , y ) ):
            x = 0
            y = 0

        self.field_map.mesa_space.place_agent(a, (x, y))
    
    def step(self):
        """Advance the model by one step."""
        #self.datacollector.collect(self) 
        
        #Moves the packing station in the right location. 
        # print( self.time_counter )
        
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

    def robot_schedule_messages( self, output_file = None ): 
        
        s = ""
        for r in self.robot_schedule[:-1]: 
            s += r.assignment_string( )+',\n'
            
        r = self.robot_schedule[-1]    
        s += r.assignment_string( )
        if output_file is None:
            print( s )
        else: 
            print( s, file = open( output_file, 'w' ) ) 
            
    def robot_schedule_messages_dicts( self ):
        
        list_of_assignments = [ r.assignment_dict() for r in self.robot_schedule ]
        return list_of_assignments

#Small test.

if __name__ == '__main__' :

    spacetype = sf.SpaceType.CONTINUOUS2D

    # field_map = fm.make_field_423_2020( spacetype )
    # field_map = fm.make_field_428_2020( spacetype )

    number_of_pickers = 4
    picker_type = PickerType.DETERMINISTIC

    picker_data = "data_logged_placeuk_day1.json"

    model = PickersModel( field_map, number_of_pickers, picker_type = picker_type, picker_data = picker_data )

    for a in model.pickers:
        print(a.picker_id)

        times_out_of_bounds = 0
        times_in_bounds = 0

        for move in a.predefined_moves:
            x = move[ "x" ]
            y = move[ "y" ]
            out_of_bounds = a.model.field_map.mesa_space.out_of_bounds( ( x , y ) )

            if out_of_bounds:
                times_out_of_bounds += 1
            else:
                times_in_bounds += 1

        print( "times_in_bounds:" , times_in_bounds , " times_out_of_bounds: ", times_out_of_bounds )
