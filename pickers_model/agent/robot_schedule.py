
# list of assignments. 

class RobotAssignment : 
    
    def __init__( self, dt, robot, picker, location ): 
        
        self.datetime = dt #datetime
        self.robot = robot 
        self.picker = picker 
        self.location = location 
        
    def assignment_string( self ): 
        
        s = '{"datetime": "' + self.datetime.strftime( "%Y-%m-%dT%H:%M:%S.%f" ) + '", "ROBOT_ID": "'+ str(self.robot.robot_id_name)+'", "PICKER": "'+str(self.picker.picker_id)+'", '+self.location.string_xy_json( ) +', "picker_node_location": '+self.location.node_id +'}'
        
        return s

    def assignment_dict( self ): 
        
        return { "datetime" : self.datetime.strftime( "%Y-%m-%dT%H:%M:%S.%f" ), "ROBOT_ID" : self.robot.robot_id_name, "PICKER" : self.picker.picker_id, "picker_node_location" : self.location.node_id }
        
