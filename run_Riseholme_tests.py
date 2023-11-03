
import sys
import os
import argparse
import enum
import mesa
import datetime
import field_maps.field_maps_1 as fm
import field_maps.field_maps_2 as fm2
import field_maps.field_maps_3 as fm3
import pickers_model.strawberry_field.strawberry_field as sf
import pickers_model.picker_routes as pr
import matplotlib.pyplot as plt
import pickers_model.agent.agent_portrayal as ap
from pickers_model.pickers_model import PickerType,PickersModel,Status
from pickers_model.agent.picking_agent import PickingAgent 
from update_plot import update_plot
from mesa_visual import run_with_mesa_visual
import matplotlib.animation as animation
from matplotlib.patches import Rectangle, Polygon
import numpy as np
import cv2
import matplotlib.animation as animation
import json

def example_json_1( ): 
    
    json_file = 'robot_schedule_example.json'
    f = open( json_file )
    data = json.load(f)

    return [ message for message in data['msg'] ] 

def test_1(): 
    
    #
    # Creating the model.  
    #    
    
    # Name of the robot schedule file. None is simply sys.stdout 
    # robot_schedule_filename = None
    robot_schedule_filename = 'robot_schedule.txt'
    
    # Saving the animation. 
    # save_animation = 'Field436_simulation_p12_r3.gif'
    save_animation = ''
    
    number_of_steps = 1200 * 1 # 1200 steps is 1 hour
    field_map = fm3.make_Riseholme_1( sf.SpaceType.CONTINUOUS2D ) 

    number_of_pickers = 1 
    number_of_robots = 1
    step_size = 3.0
    picker_type = PickerType.WAITING1
    start_datetime = datetime.datetime(2023,7,3,10,00,00)
    
    model = PickersModel( field_map, number_of_pickers, picker_type = picker_type, picker_data = None, step_size = step_size ) 
    model.add_n_robots( number_of_robots ) 
    model.set_start_datetime( start_datetime ) 
    
    #Picker 0 
    model.pickers[0].picker_id = '0cb8158460c0'
    model.pickers[0].picking_speed = 20
    model.pickers[0].fruit_in_basket = 0.0
    model.pickers[0].fruit_basket_capacity = 18000
    # picker[0].move_to_node( 'node_id' )
    
    #Robot 0
    model.robots[0].robot_id = 0
    model.robots[0].robot_id_name = 'gofar'
    # model.robots[0].move_to_node( 'node_id' )
    
    for p in model.field_map.polytunnel_list: 
        model.field_map.unpicked_rows_list += p.list_of_rows
    
    grams_per_row = 36000 
    for r in model.field_map.unpicked_rows_list:
        #r.fruit_yield = 3000
        r.fruit_yield = grams_per_row
    
    #
    # Visualisation. 
    #
    
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
        sc = ax.scatter( x,y, marker = 's' )
        robot.scatterplot = sc

    for picker in model.pickers:
        x,y = picker.pos
        sc = ax.scatter( x,y, marker = '.' )
        picker.scatterplot = sc

    xlim,ylim = field_map.image_dim
    ax.set_xlim( [ 0, xlim ] )
    ax.set_ylim( [ 0, ylim ] )

    plt.show()
    
    #
    # Running the simulation. 
    #
    
    if len( save_animation )>0:

        anim = animation.FuncAnimation( fig, update_plot, frames = range( number_of_steps -1 ), fargs = [ model ] )
        anim.save( save_animation )  
    
    else: 

        for i in range( number_of_steps ): 
            
            update_plot( i, model )
            fig.canvas.draw_idle()
            plt.pause(0.0000001) 
            
    #
    # Displaying the data. 
    #

    for p in model.pickers: 
        print( 'ID: ', p.picker_id )
        print( 'Payroll number: ', p.payroll_n )
        print( 'Total picked: ', p.total_fruit_picked )
        print( 'Total picking time: ', p.total_picking_time )
        print( 'Picking rate: ', p.total_fruit_picked / p.total_picking_time ) 
        
    return model.robot_schedule_messages_dicts(  )
    
if __name__ == '__main__' :
    
    messages = example_json_1( )
    for m in messages: 
        print(m)
        print(m['datetime'])
        print(m['ROBOT_ID'])
        print(m['picker_node_location'])
    # test_1()
