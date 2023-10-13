
import enum 
import mesa 
import math
import random

import numpy as np
from shapely.geometry import LineString, Point

import pickers_model.picker_routes as pr
from pickers_model.agent.picking_agent import PickingAgent,PickerType,time_within_range
from pickers_model.agent.status import Status,RobotStatus

class PTrackerTrolley( PickingAgent ):

    def __init__(self, unique_id, model, picker_id = "", predefined_moves = [] ):
        super().__init__(unique_id, model, picker_id, PickerType.DETERMINISTIC, predefined_moves)

        self.payroll_n = None #3 digit ID from the farm         
        self.picker_id_short = ''
        self.polytunnel_count = 0
        self.status_state = 'INIT'
        self.battery_message = None 
        self.time_in_polytunnels = 0.0
        self.start_time_in_polytunnels = 0.0
        self.last_reading = None 
        
        self.picking_speed = 50.0 #grams per second
        self.fruit_basket_capacity = 30000 #grams 
        self.time_from_empty_to_full = self.fruit_basket_capacity / self.picking_speed

    # display message 

    def display_message_simple( self ): 
        
        if self.model.field_map.position_in_polytunnels( self.pos ): 
            polytunnel_message = "In polytunnel.\t"
        else: 
            polytunnel_message = "NOT in a polytunnel.\t"
        speed_message = "Speed : "+ format( self.speed )
        status_message = " Status : "+ format( self.status )

        if len( self.scanning_records )>0:
                nextscan = format( self.scanning_records[ 0 ][ 'weight' ] )
                fruit_picked_message = "Picker " + self.payroll_n + " Next scan: "+ nextscan + " at "+format( self.scanning_records[ 0 ][ 'datetime' ] )
        else: 
                fruit_picked_message = ''

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

    # picking, choosing the move and step

    def pick_predefined( self ): 
        
        if len( self.scanning_records )>0: 
            if self.model.time_counter > self.scanning_records[0][ 'datetime' ]: 
                new_record = self.scanning_records.pop( 0 )
                self.total_fruit_picked += new_record['weight']

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

    def step(self):

        #See if the agent is supposed to be on bnreak. 
        if self.model.field_map.position_in_polytunnels( self.pos ): 
            polytunnel_message = "In polytunnel.\t"
        else: 
            polytunnel_message = "NOT in a polytunnel.\t"
        
        self.pick_predefined( )
        new_x, new_y = self.choose_move_predefined()
        
        if self.model.spacetype_discrete:
            new_x = int( new_x )
            new_y = int( new_y )

        self.find_speed( new_x, new_y )
        self.find_status( )
        self.update_ts( ) 
                    
        self.display_message( )
        self.model.field_map.mesa_space.move_agent( self, ( new_x, new_y ) ) 
        
