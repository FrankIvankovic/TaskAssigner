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
import matplotlib.pyplot as plt
import pickers_model.agent.agent_portrayal as ap
# import pickers_model.strawberry_field
from matplotlib.patches import Rectangle, Polygon

#========================================= 
# Receives MQTT messages containing the location of the human that requires the robot-runner
#   and sets those locations as goals for the robot.
class MqttCommandSender:

    ROBOT_ID = 'gofar' #os.getenv('ROBOT_ID') # ENVIRONMENT VARIABLE
    MQTT_BROKER_IP = 'mqtt.lcas.group'#'127.0.0.1' thats right
    # MQTT_BROKER_IP = '10.101.8.31'
    # MQTT_BROKER_IP = '10.101.12.68'
    MQTT_BROKER_PORT = 1883 #Thats right.
    CLIENT_ID = "cofruit_scheduler"
        
    def __init__(self, mesa_model, fig):  #setup_connections(self)

        self.mesa_model = mesa_model 
        self.figure = fig        
        self.connect_to_mqtt()

    #------
    
    def connect_to_mqtt(self):    
        self.mqtt_client = mqtt.Client( self.CLIENT_ID ) # client ID "mqtt-test"
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        #client.username_pw_set("myusername", "aeNg8aibai0oiloo7xiad1iaju1uch")
        self.mqtt_client.connect(self.MQTT_BROKER_IP, self.MQTT_BROKER_PORT, keepalive = 3000)
        self.mqtt_client.loop_forever()  
        
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
        
        # TODO: Write something better. 
        # print(f"Message received [{msg.topic}]: {msg.payload}")

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
            
            self.mesa_model.update_picker_gps( msg_content ) 
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

       
#------

def update_model( model, reading ): 
    
    picker = next(( x for x in model.pickers if x.picker_id == reading['user'] ), None)
    
    picker_long = reading[ 'LONGITUDE' ]
    picker_lat = reading[ 'LATITUDE' ] 
    date_and_time = reading[ 'UTC_DATE_TIME' ]
    
    if picker_long=='' or picker_lat=='':
        return
    
    picker.pos = model.field_map.find_xy_from_longlat( float(picker_long), float(picker_lat) ) 

def create_Riseholme_model(): 
    
    field_map = fm3.make_Riseholme_1(  ) 
    number_of_pickers = 5 
    number_of_robots = 0
    step_size = 3.0
    start_datetime = datetime.datetime(2023,7,3,10,00,00)
    
    #model = PickersModelTaskAssgner
    
    pickers = [ 'STD_v2_bcddc2cfcb68', 'STD_v2_246f284a6c94', 'STD_v2_e831cd35d0f4', 'STD_v2_70b8f606c710', 'STD_v2_0cb8158460c0' ]
    model = pmodelc.PickersModelTaskAssigner( field_map, pickers )
        
    model.add_n_robots( number_of_robots ) 
    model.set_start_datetime( start_datetime ) 

    model.pickers[0].picker_id = 'STD_v2_bcddc2cfcb68'
    model.pickers[0].picker_id_short = 'bcddc2cfcb68'
    model.pickers[0].picking_speed = 20
    model.pickers[0].fruit_in_basket = 0.0
    model.pickers[0].polytunnel_count = 0
    model.pickers[0].time_in_polytunnels = 150.0
    model.pickers[0].start_time_in_polytunnels = model.pickers[0].time_in_polytunnels
    model.pickers[0].fruit_basket_capacity = 18000
    model.pickers[1].picker_id = 'STD_v2_246f284a6c94'
    model.pickers[1].picker_id_short = '246f284a6c94'
    model.pickers[1].picking_speed = 20
    model.pickers[1].fruit_in_basket = 0.0
    model.pickers[1].polytunnel_count = 0
    model.pickers[1].time_in_polytunnels = 10.0
    model.pickers[1].start_time_in_polytunnels = model.pickers[1].time_in_polytunnels
    model.pickers[1].fruit_basket_capacity = 18000 
    model.pickers[2].picker_id = 'STD_v2_e831cd35d0f4'
    model.pickers[2].picker_id_short = 'e831cd35d0f4'
    model.pickers[2].picking_speed = 20
    model.pickers[2].fruit_in_basket = 0.0
    model.pickers[2].polytunnel_count = 0
    model.pickers[2].time_in_polytunnels = 130.0
    model.pickers[2].start_time_in_polytunnels = model.pickers[2].time_in_polytunnels
    model.pickers[2].fruit_basket_capacity = 18000 
    model.pickers[3].picker_id = 'STD_v2_70b8f606c710'
    model.pickers[3].picker_id_short = '70b8f606c710'
    model.pickers[3].picking_speed = 20
    model.pickers[3].fruit_in_basket = 0.0
    model.pickers[3].polytunnel_count = 0
    model.pickers[3].time_in_polytunnels = 120.0
    model.pickers[3].start_time_in_polytunnels = model.pickers[3].time_in_polytunnels
    model.pickers[3].fruit_basket_capacity = 18000 
    model.pickers[4].picker_id = 'STD_v2_0cb8158460c0'
    model.pickers[4].picker_id_short = '0cb8158460c0'
    model.pickers[4].picking_speed = 20
    model.pickers[4].fruit_in_basket = 0.0
    model.pickers[4].polytunnel_count = 0
    model.pickers[4].time_in_polytunnels = 0.0
    model.pickers[4].start_time_in_polytunnels = model.pickers[4].time_in_polytunnels
    model.pickers[4].fruit_basket_capacity = 18000 
    
    for p in model.field_map.polytunnel_list: 
        model.field_map.unpicked_rows_list += p.list_of_rows
    
    grams_per_row = 36000 
    for r in model.field_map.unpicked_rows_list:
        r.fruit_yield = grams_per_row

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
    
    return model,fig

#========================================= 
if __name__ == '__main__':

    # test_1() 

    mesa_model, fig = create_Riseholme_model()
    mqttCommandSender = MqttCommandSender(mesa_model, fig)    

 
#========================================= 
    
