"""
MOVES CLASS
    This class aids when automating displacements in the Zaber X-series motors
    Specifies a move provided 3 parameters
    1. Device (motor index)
    2. Target Position/Displacement
    3. Speed with which to perform the motion
"""

from motor import Motor

class Move:
    # Constructor - a whole string provided as: "[device_id] [target_position] [speed]"
    def __init__(self, command):
        self.motor_id, self.position, self.speed = command.split()
        self.motor_id = int(self.motor_id)
        self.position = float(self.position)
        self.speed = float(self.speed)

    # Returns the device, target position, and speed of the stored move
    def get_move(self):
        return self.motor_id, self.position, self.speed

    # Prints the move
    def to_string(self, template = "Move{{ id:{}, pos:{}, speed:{} }}"):
        return template.format(self.motor_id, self.position, self.speed)

    

    def testing():
        # Read from a file a list of commands and execute them accordingly
        # Each command comes to fill the values of the Moves class
        # The Moves class contains: Motor ID, position, and speed

        # IMPORT COMMANDS FROM AN INPUT FILE

        myMotor = Motor(0, "COM11")
        myMotor.home()