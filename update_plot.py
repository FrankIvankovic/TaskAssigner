
import datetime
import matplotlib.pyplot as plt

import pickers_model.agent.agent_portrayal as ap

#without the plot
def simulation_step( i, model ):
    
    model.step()

#with the plot
def update_plot( i, model ): 
    
    model.step()

    for picker in model.pickers:
        x,y = picker.pos
        picker.scatterplot.set_offsets( (x,y) )
        picker.scatterplot.set_color( ap.agent_portrayal_pyplot( picker )["Color"] )

    for robot in model.robots:
        x,y = robot.pos
        robot.scatterplot.set_offsets( (x,y) )
        robot.scatterplot.set_color( "cyan" ) 
    
    plt.xlabel( str( model.start_time_datetime + datetime.timedelta( 0, i*model.step_size)  ) )

