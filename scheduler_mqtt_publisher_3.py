#!/usr/bin/env python3

import paho.mqtt.client as mqtt # pip3 install paho-mqtt
import os, json
import msgpack

import time 
import datetime
import random
import matplotlib.pyplot as plt

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
            
            if self.figure!=None:
            
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

        for p in self.mesa_model.pickers: 
            if p.picker_id_short==client_id: 
                p.made_at_least_one_call = True
