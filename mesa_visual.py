
def run_with_mesa_visual( field_map , number_of_pickers, picker_type, picker_data ):

    field_length, field_width = field_map.dimensions
    print("Field length: "+ str(field_length) + " Field height " + str(field_width) )
    visual = mesa.visualization.CanvasGrid( ap.agent_portrayal_mesa, int(field_length), int(field_width), 1000, 1000 )
    #chart = mesa.visualization.ChartModule([{"Label": "Gini", "Color": "Black"}], data_collector_name='datacollector')
    server = mesa.visualization.ModularServer( PickersModel, [visual], "PickersModel", { "N": number_of_pickers, "field_map": field_map, "picker_type" : picker_type , "picker_data" : picker_data } )

    server.port = 8521  # The default
    server.launch()
