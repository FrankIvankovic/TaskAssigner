#!/usr/bin/env python3

import datetime
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

import field_maps.field_maps_3 as fm3
import pickers_model.pickers_model_coordinated as pmodelc

from scheduler_mqtt_publisher_3 import MqttCommandSender

def create_Riseholme_model( visualise = True ): 
    
    #Mesa model.
    number_of_pickers = 5 
    number_of_robots = 0
    start_datetime = datetime.datetime(2023,7,3,10,00,00) 
    pickers = [ 'STD_v2_bcddc2cfcb68', 'STD_v2_246f284a6c94', 'STD_v2_e831cd35d0f4', 'STD_v2_70b8f606c710', 'STD_v2_0cb8158460c0' ]

    field_map = fm3.make_Riseholme_1(  ) 
    model = pmodelc.PickersModelTaskAssigner( field_map, pickers )        
    model.add_n_robots( number_of_robots ) 
    model.set_start_datetime( start_datetime ) 

    #Trackers and pickers.
    model.pickers[0].picker_id = 'STD_v2_bcddc2cfcb68'
    model.pickers[0].picker_id_short = 'bcddc2cfcb68'
    model.pickers[0].picking_speed = 20
    model.pickers[0].fruit_in_basket = 150.0 * 20.0 
    model.pickers[0].polytunnel_count = 0
    model.pickers[0].time_in_polytunnels = 150.0
    model.pickers[0].start_time_in_polytunnels = model.pickers[0].time_in_polytunnels
    model.pickers[0].fruit_basket_capacity = 18000
    model.pickers[1].picker_id = 'STD_v2_246f284a6c94'
    model.pickers[1].picker_id_short = '246f284a6c94'
    model.pickers[1].picking_speed = 20
    model.pickers[1].fruit_in_basket = 200.0
    model.pickers[1].polytunnel_count = 0
    model.pickers[1].time_in_polytunnels = 10.0
    model.pickers[1].start_time_in_polytunnels = model.pickers[1].time_in_polytunnels
    model.pickers[1].fruit_basket_capacity = 18000 
    model.pickers[2].picker_id = 'STD_v2_e831cd35d0f4'
    model.pickers[2].picker_id_short = 'e831cd35d0f4'
    model.pickers[2].picking_speed = 20
    model.pickers[2].fruit_in_basket = 20 * 130.0
    model.pickers[2].polytunnel_count = 0
    model.pickers[2].time_in_polytunnels = 130.0
    model.pickers[2].start_time_in_polytunnels = model.pickers[2].time_in_polytunnels
    model.pickers[2].fruit_basket_capacity = 18000 
    model.pickers[3].picker_id = 'STD_v2_70b8f606c710'
    model.pickers[3].picker_id_short = '70b8f606c710'
    model.pickers[3].picking_speed = 20
    model.pickers[3].polytunnel_count = 0
    model.pickers[3].time_in_polytunnels = 120.0
    model.pickers[3].fruit_in_basket = 120.0 * 20.0
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
    if not visualise: 
        return model, None
    
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

if __name__ == '__main__':

    mesa_model, fig = create_Riseholme_model( visualise = False )
    mqttCommandSender = MqttCommandSender(mesa_model, fig)    
