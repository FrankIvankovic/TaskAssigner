#!/usr/bin/env python3

import paho.mqtt.client as mqtt # pip3 install paho-mqtt
import os, json
import msgpack

import run_Riseholme_tests
import time 
import datetime
import random

import field_maps.field_maps_3 as fm3
import pickers_model.agent.picking_agent as pick
import pickers_model.pickers_model as pmodel 
import pickers_model.pickers_model_coordinated as pmodelc
#import pickers_model.pickers_model_gpslocations as pmodelg
import matplotlib.pyplot as plt
import pickers_model.agent.agent_portrayal as ap
# import pickers_model.strawberry_field
from matplotlib.patches import Rectangle, Polygon
from pickers_model.pickers_model import PickerType,PickersModel,Status

from update_plot import update_plot, simulation_step

#========================================= 
class MqttCommandSender:

    ROBOT_ID = 'gofar' #os.getenv('ROBOT_ID') # ENVIRONMENT VARIABLE
    MQTT_BROKER_IP = 'mqtt.lcas.group'#'127.0.0.1' thats right
    # MQTT_BROKER_IP = '10.101.8.31'
    # MQTT_BROKER_IP = '10.101.12.68'
    MQTT_BROKER_PORT = 1883 #Thats right.
    CLIENT_ID = "cofruit_scheduler"

    #------
        
    def __init__(self, mesa_model, fig):  #setup_connections(self)

        self.mesa_model = mesa_model 
        self.figure = fig
        self.time_of_last_gps_message = None
        self.connect_to_mqtt()

    #------
    
    def connect_to_mqtt(self):    
        
        self.mqtt_client = mqtt.Client( self.CLIENT_ID ) # client ID "mqtt-test"
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        #client.username_pw_set("myusername", "aeNg8aibai0oiloo7xiad1iaju1uch")
        self.mqtt_client.connect(self.MQTT_BROKER_IP, self.MQTT_BROKER_PORT, keepalive = 3000)
        
        #self.mqtt_client.loop_forever()  
        self.mqtt_client.loop_start() 
        
        #Create the model and the figure.
        #model = create_Riseholme_simulation() 
        #fig = create_Riseholme_figure( model )
        show_visual = False
        number_of_steps = 1000 

        #Run the simulation.
        for i in range( number_of_steps ): 

            # print( model.step_number )            
            simulation_step( i, self.mesa_model )
            if model.all_pickers_finished():
                #print('All pickers finished.' )
                break
            if show_visual:
                update_plot( i, self.mesa_model )
                self.figure.canvas.draw_idle()
            
            plt.pause( 1.0 ) 
                
            #for trolley in self.mesa_model.pickers: 
                #print( trolley.mqtt_message_gps() )
            
            self.send_all_trolley_gps_messages( )

    #------
    
    # When this client connects to mqtt, subscribe to the robot's topic
    def on_connect(self, client, userdata, flags, rc):    
        
        print(f"Connected with result code {rc}")
        
        # subscribe:
        self.mqtt_client.subscribe("trolley/status")
        self.mqtt_client.subscribe("trolley/gps")
        self.mqtt_client.subscribe("trolley/register")
        self.mqtt_client.subscribe("trolley/battery")
        self.mqtt_client.subscribe("trolley/method") 

        # NOTE: rohi2 for simulation, riseholme_strawberry_polytunnel for real thing.
        # NOTE: json for real thing msgpack for simulation.

        # self.mqtt_client.subscribe("rohi2/rasberry_coordination/fleet_monitoring/fleet") 
        self.mqtt_client.subscribe("riseholme_strawberry_polytunnel/rasberry_coordination/fleet_monitoring/fleet")
        # self.call_for_client_id( 'Bob' )
                        
    #------
    
    def on_message(self, client, userdata, msg):
        
        print(f"Message received [{msg.topic}]")
        
        #if msg.topic=='rohi2/rasberry_coordination/fleet_monitoring/fleet': 
        if msg.topic=='riseholme_strawberry_polytunnel/rasberry_coordination/fleet_monitoring/fleet': 
            #msg_content = msgpack.loads(msg.payload)['list']
            msg_content = json.loads(msg.payload)['list']
            # print( msg_content )
            for a in msg_content: 
                #print(a['id'], 'Content: ', msg_content)
                #print(a['id'], ' Location: ', a['location']['current_node'])
                pass
            
            # self.mesa_model.update_robot( msg_content )
        
        if msg.topic=='trolley/battery':
            
            msg_content = json.loads(msg.payload) # has to be here as rohi2 is using message packs rather than json            
            self.mesa_model.update_picker_battery( msg_content )            
            
        if msg.topic=='trolley/status':
            
            msg_content = json.loads(msg.payload) # has to be here as rohi2 is using message packs rather than json            
            self.mesa_model.update_picker_status( msg_content )            

        if msg.topic=='trolley/gps':
            
            msg_content = json.loads(msg.payload) # has to be here as rohi2 is using message packs rather than json
       
            print( msg_content['user'], 'Latitude: ', msg_content['LATITUDE'], 'Longitude: ', msg_content['LONGITUDE'] ) 
            
            self.mesa_model.update_picker_gps( msg_content ) # to actually update the model
            picker_id = self.mesa_model.call_required( )
            
            if picker_id!='':
                self.call_for_client_id( picker_id )
            
            for picker in self.mesa_model.pickers:
                x,y = picker.pos
                picker.scatterplot.set_offsets( (x,y) )
                picker.scatterplot.set_color( 'orange' )

            for robot in self.mesa_model.robots:
                x,y = robot.pos
                robot.scatterplot.set_offsets( (x,y) )
                robot.scatterplot.set_color( "cyan" )
                
            self.figure.canvas.draw_idle()
            plt.pause(0.000001) 

    #------
                
    def call_for_client_id( self, client_id ): 
        
        print('Calling ', client_id)
        
        new_mqtt_message = { "user": "STD_v2_" + client_id, "method": "call", "CLIENT_ID": client_id }
        json_data = json.dumps( new_mqtt_message )
        self.mqtt_client.publish( "trolley/method", json_data) 
    
    def send_all_trolley_gps_messages( self ): 
        
        for trolley in self.mesa_model.pickers:
            #self.send_trolley_gps_message( self, trolley )
            json_data = trolley.mqtt_message_gps()
            print( 'SENDING:', json_data )
            self.mqtt_client.publish( "trolley/gps", json_data ) 

    def send_trolley_gps_message( self, trolley ): 
        
        #get the location and time data... 
        current_time = datetime.datetime.now()
        longitude,latitude = self.mesa_model.find_longlat_from_xy( trolley.pos )
        user = trolley.picker_id
        client_id = trolley.picker_id_short
        
        #send the message...
        new_gps_mqtt_message = { "RESERVED_3": "", "HDOP": "0.6", "RESERVED_1": "", "HOUR": format( current_time.hour ), "YEAR": format( current_time.year ), "VPA": "", "LATITUDE": format( latitude ), "UTC_DATE_TIME": current_time.strftime( "%Y%m%d%H%M%S.%f" )[:-3], "ERROR": False, "MSL_ALTITUDE": "17.000", "FIX_STATUS": "1", "PDOP_RATING": "ideal", "MONTH": format( current_time.month ), "SECOND": format( current_time.second ), "C/N0_MAX": "37", "GNSS_SATELITES_IN_VIEW": "23", "HPA": "", "HDOP_RATING": "ideal", "LONGITUDE": format( longitude ), "CSQ": "Wifi", "MEAN_DOP_RATING": "ideal", "DAY": format( current_time.day ), "GPS_SATELITES_USED": "9", "VDOP": "0.7", "PDOP": "0.9", "VDOP_RATING": "ideal", "user": user, "CLIENT_ID": client_id, "COURSE_OVER_GROUND": "101.7", "FIX_MODE": "1", "GNSS_RUN_STATUS": "1", "SPEED_OVER_GROUND": "0.00", "MINUTE": format( current_time.minute ), "GLONASS_SATELITES_USED": "8", "RESERVED_2": "" } 
        
        json_data = json.dumps( new_gps_mqtt_message )
        self.mqtt_client.publish( "trolley/gps", json_data ) 

#------

def update_model( model, reading ): 
    
    picker = next(( x for x in model.pickers if x.picker_id == reading['user'] ), None)
    
    picker_long = reading[ 'LONGITUDE' ]
    picker_lat = reading[ 'LATITUDE' ] 
    date_and_time = reading[ 'UTC_DATE_TIME' ]
    
    if picker_long=='' or picker_lat=='':
        return
    
    picker.pos = model.field_map.find_xy_from_longlat( float(picker_long), float(picker_lat) ) 

def create_Riseholme_simulation(): 

    field_map = fm3.make_Riseholme_1(  ) 
    start_datetime = datetime.datetime(2023,11,3,10,00,00)

    number_of_pickers = 3
    picker_type = PickerType.WAITING3
    step_size = 1.0

    model = PickersModel( field_map, 
                         number_of_pickers, 
                         picker_type = picker_type, 
                         step_size = step_size ) 
    
    #model.add_n_robots_orr2( number_of_robots ) 
    #model.add_n_robots_orr2( number_of_robots ) 
    model.messagetype = 'None'    
    model.set_start_datetime( start_datetime ) 

    time_to_require_robot_1 =  180 #every 3 minutes
    time_to_require_robot_2 =  300 #every 5 minutes
    time_to_require_robot_3 =  420 #every 7 minutes
    picking_rate_1 = 5000 / time_to_require_robot_1
    picking_rate_2 = 5000 / time_to_require_robot_2
    picking_rate_3 = 5000 / time_to_require_robot_3

    model.pickers[0].picker_id = 'STD_v2_e831cd35d0f4'
    model.pickers[0].picker_id_short = 'e831cd35d0f4'
    model.pickers[0].picking_speed = picking_rate_3
    model.pickers[0].fruit_in_basket = 0.0
    model.pickers[0].polytunnel_count = 0
    model.pickers[0].time_in_polytunnels = 130.0
    model.pickers[0].start_time_in_polytunnels = model.pickers[2].time_in_polytunnels
    model.pickers[0].fruit_basket_capacity = 18000 
    model.pickers[1].picker_id = 'STD_v2_70b8f606c710'
    model.pickers[1].picker_id_short = '70b8f606c710'
    model.pickers[1].picking_speed = 20
    model.pickers[1].fruit_in_basket = 0.0
    model.pickers[1].polytunnel_count = 0
    model.pickers[1].time_in_polytunnels = 120.0
    model.pickers[1].start_time_in_polytunnels = model.pickers[3].time_in_polytunnels
    model.pickers[1].fruit_basket_capacity = 18000 
    model.pickers[2].picker_id = 'STD_v2_0cb8158460c0'
    model.pickers[2].picker_id_short = '0cb8158460c0'
    model.pickers[2].picking_speed = 20
    model.pickers[2].fruit_in_basket = 0.0
    model.pickers[2].polytunnel_count = 0
    model.pickers[2].time_in_polytunnels = 0.0
    model.pickers[2].start_time_in_polytunnels = model.pickers[4].time_in_polytunnels
    model.pickers[2].fruit_basket_capacity = 18000 
    #model.pickers[0].picker_id = 'STD_v2_bcddc2cfcb68'
    #model.pickers[0].picker_id_short = 'bcddc2cfcb68'
    #model.pickers[0].picking_speed = picking_rate_1
    #model.pickers[0].fruit_in_basket = 0.0
    #model.pickers[0].polytunnel_count = 0
    #model.pickers[0].time_in_polytunnels = 150.0
    #model.pickers[0].start_time_in_polytunnels = model.pickers[0].time_in_polytunnels
    #model.pickers[0].fruit_basket_capacity = 18000
    #model.pickers[1].picker_id = 'STD_v2_246f284a6c94'
    #model.pickers[1].picker_id_short = '246f284a6c94'
    #model.pickers[1].picking_speed = picking_rate_2
    #model.pickers[1].fruit_in_basket = 0.0
    #model.pickers[1].polytunnel_count = 0
    #model.pickers[1].time_in_polytunnels = 10.0
    #model.pickers[1].start_time_in_polytunnels = model.pickers[1].time_in_polytunnels
    #model.pickers[1].fruit_basket_capacity = 18000 

    for p in model.field_map.polytunnel_list: 
        model.field_map.unpicked_rows_list += p.list_of_rows
    
    grams_per_row = 36000 
    for r in model.field_map.unpicked_rows_list:
        r.fruit_yield = grams_per_row

    return model

def create_Riseholme_figure( model ): 
    
    field_map = model.field_map
    
    # Drawing the field.
    field_length, field_width = field_map.dimensions
    plt.ion()
    fig, ax = plt.subplots()
    plt.xlim( 0, field_length )
    plt.ylim( 0, field_width )
    img = field_map.resized_image( ) 
    ax.imshow( img[::-1], origin = 'lower' ) 

    # Drawing the polytunnels.
    for tunnel in field_map.polytunnel_list:
        ax.add_patch(Polygon( tunnel.get_coordinates_list(),
            edgecolor = 'pink',
            facecolor = 'green',
            fill=False,
            lw=5, alpha = 0.3))

    # Drawing the topological map. 
    show_topological_map = False
    if field_map.topological_map != None and show_topological_map: 
        for n in field_map.topological_map.nodes: 
            sc = ax.scatter( n.pos_x, n.pos_y, marker = 'x' )
            sc.set_color( 'cyan' )

    # Drawing the robots and the pickers.
    for robot in model.robots: 
        x,y = robot.pos
        robot.scatterplot = ax.scatter( x,y, marker = 's' )

    for picker in model.pickers:
        x,y = picker.pos
        picker.scatterplot = ax.scatter( x,y, marker = 'x' )

    xlim,ylim = field_map.image_dim
    ax.set_xlim( [ 0, xlim ] )
    ax.set_ylim( [ 0, ylim ] )

    plt.show() 

    return fig

def test_1(): 
    
    #Create the model and the figure.
    model = create_Riseholme_simulation() 
    fig = create_Riseholme_figure( model )
    show_visual = True
    number_of_steps = 1000 
    
    #mqttCommandSender = MqttCommandSender(model, fig)    
    
    #Run the simulation.
    for i in range( number_of_steps ): 

        # print( model.step_number )            
        simulation_step( i, model )
        if model.all_pickers_finished():
                #print('All pickers finished.' )
                break
        if show_visual:
                update_plot( i, model )
                fig.canvas.draw_idle()
                plt.pause( 1.0 ) 
                
        for trolley in model.pickers: 
            print( trolley.mqtt_message_gps() )
    
#========================================= 
if __name__ == '__main__':

    #test_1() 

    #mesa_model, fig = create_Riseholme_model()
    model = create_Riseholme_simulation() 
    #fig = create_Riseholme_figure( model )
    fig = None
    mqttCommandSender = MqttCommandSender(model, fig)    

 
#========================================= 
    
