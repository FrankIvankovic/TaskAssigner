
from pickers_model.agent.status import Status

def agent_portrayal_mesa( agent ):
    
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "r": 25.0, portrayal["Layer"] : 1}
    
    if agent.status == Status.RUNNING:
        portrayal["Color"] = "blue"
    elif agent.status == Status.PICKING:
        portrayal["Color"] = "red"
    elif agent.status == Status.PICKING:
        portrayal["Color"] = "orange"
    else :
        portrayal["Color"] = "yellow"

    return portrayal

def agent_portrayal_pyplot( agent ):
    
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "r": 50.0}
    
    if agent.status in [ Status.RUNNING, Status.MOVING_ROWS ] :
        portrayal["Color"] = "blue"
    elif agent.status == Status.PICKING :
        portrayal["Color"] = "red"
    elif  agent.status == Status.WAITING :
        portrayal["Color"] = "orange"
    elif agent.status == Status.WAITING_ASSIGNED :
        portrayal["Color"] = "yellow"
    else:
        # BREAK
        portrayal["Color"] = "lime"

    return portrayal
