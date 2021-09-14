from zaber_motion import Library
from zaber_motion.ascii import Connection
from zaber_motion import Units
from zaber_motion.ascii import Axis
from zaber_motion.ascii import AxisSettings

MIN_GEAR = 0
MAX_GEAR = 2
GEARBOX = [0.2,1,4]

class Motor:
    #Constructor
    def __init__(self, device, max_speed, tray_length):
        self.homed = False # Boolean data member, allows for checking if device is homed at runtime
        self.script = [] # List of Move objects for automated execution
        self.scriptRecieved = False
        self.axis = device.get_axis(1) # Gets the axis of motion to perform displacements
        self.axis_settings = self.axis.settings #Gets the settings of the axis for manipulation
        self.tray_length = float(tray_length)