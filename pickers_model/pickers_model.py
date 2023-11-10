
import sys

import mesa
import math
import random
import datetime

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from shapely.geometry import LineString, Point

import pickers_model.strawberry_field as sf
import pickers_model.picker_routes as pr
import pickers_model.agent.probabilistic_movement as pmove 

from pickers_model.agent.robot_runner import RobotRunner
from pickers_model.agent.robot_runner_orr1 import RobotRunnerOrderedRR1
from pickers_model.agent.robot_runner_orr2 import RobotRunnerOrderedRR2
from pickers_model.agent.robot_schedule import RobotAssignment 

from pickers_model.agent.picking_agent import PickingAgent,PickerType,time_within_range
from pickers_model.agent.picking_agent_deterministic import PDeterministic
from pickers_model.agent.picking_agent_waiting1 import PWaiting1
from pickers_model.agent.picking_agent_waiting2 import PWaiting2
from pickers_model.agent.picking_agent_waiting3 import PWaiting3
from pickers_model.agent.picking_agent_waiting4 import PWaiting4
from pickers_model.agent.picking_agent_waiting5 import PWaiting5
from pickers_model.agent.status import Status,RobotStatus
            
class PickersModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, field_map, N, picker_type = PickerType.RANDOM, picker_data = "", step_size = 3.0, picker_patience = 0.0, max_waiting_time = 180.0 ):

        self.num_agents = N
        self.num_robots = 3
        self.field_map = field_map
        # self.spacetype = field_map.spacetype
        self.spacetype_discrete = False
        self.step_size = step_size #Assumed seconds
        
        self.pickers = [] 
        self.robots = [] 
        self.packing_station = None 
        
        #TODO: Account for the fact that the location of the packing station changes.
        self.packing_station_schedule = [ ]  
        self.packing_station_i = 0  
        
        # time related stuff
        self.step_number = 0
        self.start_time_datetime = datetime.datetime(2023,6,1,7,00,00) 
        self.time_counter = self.start_time_datetime 
        
        self.messagetype = "Simple"
        
        # A list of robot schedule events. 
        self.robot_schedule = [  ] 
        
        # TODO: Move this!!!!!
        self.list_of_speeds = [ 91.6892502258356, 45.31722054380665, 72.61345852895148, 54.33646812957158, 78.13070463672874, 62.18655967903711, 67.49049429657795, 77.43752199929602, 63.35174953959484 ]
        
        # self.list_of_speeds = [ 7.3438466295609155, 9.144741773480249, 9.191852342083976, 9.755716850074144, 11.96227283183805, 6.360777587192682, 9.508093666509508, 7.76982844834218, 9.456801331517628, 10.786444498108347, 6.608747308234944, 8.650260999254288 ]
        
        #Temporary fix for visualisation.
        if self.spacetype_discrete:
            self.grid = self.field_map.mesa_space
        else:
            self.grid = None

        #self.schedule = mesa.time.RandomActivation(self)
        self.schedule = mesa.time.BaseScheduler(self)

        # pickers_routes = pr.read_json_interpolate( self.field_map, 3.0, picker_data )
        # offset_x0, offset_y0, offset_x1, offset_y1 = self.offsets
        # pickers_routes = pr.adjust_xy_offset( pickers_routes, offset_x0, offset_y0 )
        
        # Here is where the pickers are added!
        picker_routes = picker_data

        # Create agents
        i = 0

        if picker_type in [ PickerType.PROBABILISTIC_ROBOTS , PickerType.PATIENT_PICKER, PickerType.WAITING1, PickerType.WAITING2 ]: 
            for r in range(self.num_robots):
                self.add_robot( r )

        if picker_type == PickerType.DETERMINISTIC:

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

        elif picker_type == PickerType.PROBABILISTIC or picker_type == PickerType.PROBABILISTIC_ROBOTS:

            # picker_readings = pr.read_json_pickers( picker_data )
            # offset_x0, offset_y0, offset_x1, offset_y1 = self.offsets
            # picker_readings = pr.adjust_xy_offset( picker_readings, offset_x0, offset_y0 )

            for picker in picker_routes.keys():
                if len( self.pickers ) >= self.num_agents:
                    break
                readings_list = picker_routes[ picker ]
                ppm = pmove.PickerProbabilisticMovement( self.field_map, readings_list, self.step_size )
                # self.add_probabilistic_picker( i, picker, ppm )
                self.add_probabilistic_picker_in_tunnel( i, picker, ppm )
                i += 1
        
        elif picker_type == PickerType.PATIENT_PICKER: 
            
            while len( self.pickers ) < self.num_agents:
                self.add_patient_picker_in_tunnel( i )
                i += 1
        
        elif picker_type == PickerType.WAITING1: 

            while len( self.pickers ) < self.num_agents:
                self.add_waiting1_picker( i )
                i += 1
        
        elif picker_type == PickerType.WAITING2: 

            while len( self.pickers ) < self.num_agents:
                self.add_waiting2_picker( i )
                i += 1        

        elif picker_type == PickerType.WAITING3: 

            while len( self.pickers ) < self.num_agents:
                self.add_waiting3_picker( i )
                i += 1        

        elif picker_type == PickerType.WAITING4: 

            while len( self.pickers ) < self.num_agents:
                self.add_waiting4_picker( i, picker_patience, max_waiting_time )
                i += 1        

        elif picker_type == PickerType.WAITING5: 

            while len( self.pickers ) < self.num_agents:
                self.add_waiting5_picker( i, picker_patience, max_waiting_time )
                i += 1        
        
        while len( self.pickers ) < self.num_agents:
            self.add_random_picker( i )
            i += 1
    
    def update_picker_battery( self, reading ): # to actually update the model
        
        for p in self.pickers:
            if p.picker_id == reading["user"]:
                #print('Here: ', p.picker_id, reading) 
                p.battery_message = reading
                print('Updated batter level for: ', p.picker_id, ' Battery level: ', reading["Status"], ' Voltage: ', reading["Voltage"])

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
                    p.fruit_in_basket = 0.0
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
            picker.fruit_in_basket += picker.picking_speed * tdelta.seconds
        picker.last_reading = reading
        print('Picker', picker.picker_id, ' In polytunnel?', self.field_map.position_in_polytunnels( picker.pos ),' Polytunnel count:', picker.polytunnel_count, ' picker.time_in_polytunnels:', picker.time_in_polytunnels, ' picker.fruit_in_basket:', picker.fruit_in_basket )
    
    def set_start_datetime( self, dt ): 
        
        self.start_time_datetime = dt 
        self.time_counter = self.start_time_datetime         
    
    def add_n_robots( self, n_robots ): 
        self.num_robots = n_robots
        self.robots = [ ] 
    
        for r in range(self.num_robots):
            self.add_robot( r )
    
    def add_robot( self, r ): 
        self.robots.append( RobotRunner( r, self ) ) 

    def add_n_robots_orr1( self, n_robots ): 
        self.num_robots = n_robots
        self.robots = [ ] 
    
        for r in range(self.num_robots):
            self.add_robot_orr1( r )

    def add_robot_orr1( self, r ): 
        self.robots.append( RobotRunnerOrderedRR1( r, self ) ) 

    def add_n_robots_orr2( self, n_robots ): 
        self.num_robots = n_robots
        self.robots = [ ] 
    
        for r in range(self.num_robots):
            self.add_robot_orr2( r )

    def add_robot_orr2( self, r ): 
        self.robots.append( RobotRunnerOrderedRR2( r, self ) ) 
        
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

    def add_probabilistic_picker( self, i, picker, ppm ):

        a = PickingAgent( i, self, picker_id = picker, picker_type = PickerType.PROBABILISTIC, probabilistic_model = ppm )
        self.schedule.add(a)
        self.pickers.append(a)
        x = random.randrange(self.field_map.mesa_space.width)
        y = random.randrange(self.field_map.mesa_space.height)
        self.field_map.mesa_space.place_agent(a, (x, y)) 
        
    def add_probabilistic_picker_in_tunnel( self, i, picker, ppm ):

        a = PickingAgent( i, self, picker_id = picker, picker_type = PickerType.PROBABILISTIC, probabilistic_model = ppm ) 
        self.schedule.add(a)
        self.pickers.append(a) 
        
        position_picked = False 
        while not position_picked: 
            x = random.randrange(self.field_map.mesa_space.width)
            y = random.randrange(self.field_map.mesa_space.height)
            if self.field_map.position_in_polytunnels( (x,y) ): 
                position_picked = True
                self.field_map.mesa_space.place_agent(a, (x, y))

    def add_patient_picker_in_tunnel( self, i ):

        a = PickingAgent( i, self, picker_type = PickerType.PATIENT_PICKER ) 
        
        picking_speed_kgph = random.choice( [ 6, 18, 23, 26, 28, 35 ] ) 
        a.picking_speed = picking_speed_kgph * 5 / 18  
        self.schedule.add(a)
        self.pickers.append(a) 
        
        polytunnels_with_points = [] 
        for p in self.field_map.polytunnel_list: 
            if len( p.points_in_polytunnel_nodes ) > 0 : 
                polytunnels_with_points.append( p ) 
        
        if len( polytunnels_with_points ) == 0: 
            self.add_picker_in_tunnel( i )
        else: 
            tunnel = random.choice( polytunnels_with_points ) 
            tunnel_point = random.choice( tunnel.points_in_polytunnel_nodes ) 
            self.field_map.mesa_space.place_agent( a, ( tunnel_point.point.x, tunnel_point.point.y ) ) 
            a.current_node = tunnel_point

    def add_waiting5_picker( self, i, p, max_wait ): 
        
        # a = PickingAgent( i, self, picker_type = PickerType.WAITING1 ) 
        a = PWaiting5( i, self, patience = p, max_waiting_time = max_wait )
        
        #if len( self.list_of_speeds ) > 0:
            #picking_speed = self.list_of_speeds.pop( ) 
        #else: 
            #picking_speed = random.choice( [ 91.6892502258356, 45.31722054380665, 72.61345852895148, 54.33646812957158, 78.13070463672874, 62.18655967903711, 67.49049429657795, 77.43752199929602, 63.35174953959484 ] )
        
        ## picking_speed_kgph = 200
        ## a.picking_speed = picking_speed_kgph * 5 / 18  
        #a.picking_speed = picking_speed
        self.schedule.add(a)
        self.pickers.append(a) 
        
        starting_x, starting_y = self.field_map.packing_stations[ 0 ]
        
        self.field_map.mesa_space.place_agent( a, ( starting_x, starting_y ) ) 
        a.current_node = self.field_map.packing_stations_nodes[ 0 ] 
        a.target_node = a.current_node

    def add_waiting4_picker( self, i, p, max_wait ): 
        
        # a = PickingAgent( i, self, picker_type = PickerType.WAITING1 ) 
        a = PWaiting4( i, self, patience = p, max_waiting_time = max_wait )
        
        #if len( self.list_of_speeds ) > 0:
            #picking_speed = self.list_of_speeds.pop( ) 
        #else: 
            #picking_speed = random.choice( [ 91.6892502258356, 45.31722054380665, 72.61345852895148, 54.33646812957158, 78.13070463672874, 62.18655967903711, 67.49049429657795, 77.43752199929602, 63.35174953959484 ] )
        
        ## picking_speed_kgph = 200
        ## a.picking_speed = picking_speed_kgph * 5 / 18  
        #a.picking_speed = picking_speed
        self.schedule.add(a)
        self.pickers.append(a) 
        
        starting_x, starting_y = self.field_map.packing_stations[ 0 ]
        
        self.field_map.mesa_space.place_agent( a, ( starting_x, starting_y ) ) 
        a.current_node = self.field_map.packing_stations_nodes[ 0 ] 
        a.target_node = a.current_node

    def add_waiting3_picker( self, i ): 
        
        # a = PickingAgent( i, self, picker_type = PickerType.WAITING1 ) 
        a = PWaiting3( i, self )
        
        #if len( self.list_of_speeds ) > 0:
            #picking_speed = self.list_of_speeds.pop( ) 
        #else: 
            #picking_speed = random.choice( [ 91.6892502258356, 45.31722054380665, 72.61345852895148, 54.33646812957158, 78.13070463672874, 62.18655967903711, 67.49049429657795, 77.43752199929602, 63.35174953959484 ] )
        
        ## picking_speed_kgph = 200
        ## a.picking_speed = picking_speed_kgph * 5 / 18  
        #a.picking_speed = picking_speed
        self.schedule.add(a)
        self.pickers.append(a) 
        
        starting_x, starting_y = self.field_map.packing_stations[ 0 ]
        
        self.field_map.mesa_space.place_agent( a, ( starting_x, starting_y ) ) 
        a.current_node = self.field_map.packing_stations_nodes[ 0 ] 
        a.target_node = a.current_node

    def add_waiting2_picker( self, i ): 
        
        # a = PickingAgent( i, self, picker_type = PickerType.WAITING1 ) 
        a = PWaiting2( i, self )
        
        #if len( self.list_of_speeds ) > 0:
            #picking_speed = self.list_of_speeds.pop( ) 
        #else: 
            #picking_speed = random.choice( [ 91.6892502258356, 45.31722054380665, 72.61345852895148, 54.33646812957158, 78.13070463672874, 62.18655967903711, 67.49049429657795, 77.43752199929602, 63.35174953959484 ] )
        
        ## picking_speed_kgph = 200
        ## a.picking_speed = picking_speed_kgph * 5 / 18  
        #a.picking_speed = picking_speed
        self.schedule.add(a)
        self.pickers.append(a) 
        
        starting_x, starting_y = self.field_map.packing_stations[ 0 ]
        
        self.field_map.mesa_space.place_agent( a, ( starting_x, starting_y ) ) 
        a.current_node = self.field_map.packing_stations_nodes[ 0 ] 
        a.target_node = a.current_node
    
    def add_waiting1_picker( self, i ): 
        
        # a = PickingAgent( i, self, picker_type = PickerType.WAITING1 ) 
        a = PWaiting1( i, self )
        
        #if len( self.list_of_speeds ) > 0:
            #picking_speed = self.list_of_speeds.pop( ) 
        #else: 
            #picking_speed = random.choice( [ 91.6892502258356, 45.31722054380665, 72.61345852895148, 54.33646812957158, 78.13070463672874, 62.18655967903711, 67.49049429657795, 77.43752199929602, 63.35174953959484 ] )
        
        ## picking_speed_kgph = 200
        ## a.picking_speed = picking_speed_kgph * 5 / 18  
        #a.picking_speed = picking_speed
        self.schedule.add(a)
        self.pickers.append(a) 
        
        starting_x, starting_y = self.field_map.packing_stations[ 0 ]
        
        self.field_map.mesa_space.place_agent( a, ( starting_x, starting_y ) ) 
        a.current_node = self.field_map.packing_stations_nodes[ 0 ] 
        a.target_node = a.current_node
            
    def add_picker_in_tunnel( self, i ): 
        
        a = PickingAgent( i, self, picker_type = PickerType.PATIENT_PICKER ) 
        self.schedule.add(a)
        self.pickers.append(a) 
        
        position_picked = False 
        while not position_picked: 
            x = random.randrange(self.field_map.mesa_space.width)
            y = random.randrange(self.field_map.mesa_space.height)
            if self.field_map.position_in_polytunnels( (x,y) ): 
                position_picked = True
                self.field_map.mesa_space.place_agent(a, (x, y))
        
    def add_random_picker( self, i ):

        #print("Adding a random picker.")

        a = PickingAgent( i, self )
        self.schedule.add(a)
        self.pickers.append(a)
        x = random.randrange(self.field_map.mesa_space.width)
        y = random.randrange(self.field_map.mesa_space.height)
        self.field_map.mesa_space.place_agent(a, (x, y)) 
        
    def move_robots(self): 
        for r in self.robots: 
            r.step( )

    def packing_station_step( self ):
        
        #Packing station schedule is a dictionary of the form { "location": i, "start": datetime, "end": datetime, "x": x, "y": y }
        for p in self.packing_station_schedule: 
            if time_within_range( self.current_datetime , p ) and p[ "location" ] != self.packing_station_i: 
                self.packing_station_i = p[ "location" ] 
                self.field_map.packing_stations = [ ( p["x"], p["y"] ) ]     
                self.field_map.packing_stations_points = [ Point( p ) for p in field423.packing_stations ] 
                self.field_map.add_topological_map( ) 

    def all_pickers_finished(self): 
        
        for p in self.pickers:
            if not p.finished:
                #print('picker not finished:', p.status)
                return False
        
        # print('All pickers finished.')
        return True
    
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

    field_map = fm.make_field_423_2020( spacetype )
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
