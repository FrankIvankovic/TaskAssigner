
import enum

class Status(enum.Enum):
    RUNNING = 1
    PICKING = 2
    BREAK = 3
    WAITING = 4
    WAITING_ASSIGNED = 5 
    DROPPINGOFF = 6 
    MOVING_ROWS = 7 
    GOING_BACK = 8
    FINISHED = 9
    
class RobotStatus(enum.Enum):
    WAITING = 1
    PICKINGUP = 2 
    DROPPINGOFF = 3
