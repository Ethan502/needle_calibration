from zaber_motion import Library
from zaber_motion.ascii import Connection
from zaber_motion import Units
from zaber_motion.ascii import Axis
from zaber_motion.ascii import AxisSettings
import time

MIN_GEAR = 0
MAX_GEAR = 2
GEARBOX = [0.2,1,4]

class Motor:
    # Constructor--------------------------------------------------------------------
    def __init__(self, device, max_speed, tray_length):
        self.homed = False # Boolean data member, allows for checking if device is homed at runtime
        self.script = [] # List of Move objects for automated execution
        self.scriptRecieved = False
        self.axis = device.get_axis(1) # Gets the axis of motion to perform displacements
        self.axis_settings = self.axis.settings #Gets the settings of the axis for manipulation
        self.tray_length = float(tray_length)

        self.max_speed = float(max_speed)
        self.base_speed = 0
        self.gear = MIN_GEAR
        self.gearbox = GEARBOX

        self.set_default_speed(self.max_speed)
        self.set_base_speed()

    # Getters-----------------------------------------------------------------------
    def get_id(self):
        return self.axis.identity.peripheral_id

    def get_position(self):
        return self.axis.get_position(unit = Units.LENGTH_MILLIMETRES)

    def get_speed(self):
        return self.axis_settings.get("maxspeed", unit = Units.VELOCITY_MILLIMETRES_PER_SECOND)

    def get_acceleration(self):
        return self.axis_settings.get("accel", unit = Units.ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED)
        
    def get_script_status(self):
        return self.scriptRecieved
    
    def get_gear(self):
        return self.gear + 1

    def get_gearbox(self):
        return self.gearbox

    def get_base_speed(self):
        return self.base_speed

    def get_max_speed(self):
        return self.max_speed

    # Checks if the motor has been homed
    def is_homed(self):
        return self.homed

    # SETTERS -----------------------------------------------------------------------
    def set_default_speed(self, speed):
        self.axis_settings.set("maxspeed", speed, unit = Units.VELOCITY_MILLIMETRES_PER_SECOND)

    def set_base_speed(self):
        self.base_speed = self.max_speed / self.gearbox[MAX_GEAR]

    def set_acceleration(self, accel):
        self.axis_settings.set("accel", accel, unit = Units.VELOCITY_MILLIMETRES_PER_SECOND)

    def set_gearbox(self, gear_list):
        self.gearbox = gear_list
        self.set_base_speed() #this needs to be reset, since the base speed depends on the gearbox config

    def reset_gear(self):
        self.gear = MIN_GEAR

    # Gear Functions -----------------------------------------------------------------
    def shift_gear_up(self):
        if (self.gear < MAX_GEAR):
            self.gear = self.gear + 1
            return True
        else:
            return False

    def shift_gear_down(self):
        if (self.gear > MIN_GEAR):
            self.gear = self.gear - 1
            return True
        else:
            return False

    # Moves --------------------------------------------------------------------------
    # Moves the stage to the 0 position and defines it as the reference point for future displacements
    def home(self):
        self.set_default_speed(self.max_speed)
        self.axis.home()
        self.homed = True

    # Performs an absolute displacement to the given position
    def move_to(self, position):
        self.axis.move_absolute(position, unit = Units.LENGTH_MILLIMETRES, wait_until_idle = True)

    # Performs a relative displacement with the provided of default (1mm) step value
    def move_step(self, step = 1):
        negative_step = step < 0
        c1 = ( (self.get_position() - abs(step) ) >= 0)
        c2 = ( (self.get_position() + abs(step)) <= self.tray_length)

        if ( (negative_step and c1) or (not(negative_step) and c2) ):
            self.axis.move_relative(step, unit = Units.LENGTH_MILLIMETRES, wait_until_idle = True)
        else:
            print("Step too big, if performed motor will go beyond boundary. Cannot perform step.")
    
    # Performs an indefinite displacement at a given speed (providing a trigger [0-1] measurement)
    def move_speed(self, trigger):
        speed = self.base_speed * self.gearbox[self.gear] * trigger
        self.axis.move_velocity(speed, unit = Units.VELOCITY_MILLIMETRES_PER_SECOND)

    # This is the digital equivalent to pressing the button on the motor
    # Erases the reference point, so the device will need to be homed again
    def stop(self):
        self.axis.stop(wait_until_idle = True)
        self.homed = False

        """
        This section is only for testing motors individually. The motorseries class will be running
        the master script that will run motors normally. 
        """

    # Recieves a script as a list of Move objects
    def load_script(self, script):
        self.script = script
        self.scriptRecieved = True

    def print_script(self):
        for command in range(len(self.script)):
            print(self.script[command].to_string())

    # Runs a sequence of commands specified in a list of Move objects
    # Returns a boolean signifying if the motor has a script to run or not
    # CATCH: scripts can only be run once, then they need to be reloaded
    def run_script(self):
        if(self.scriptRecieved):
            for command in self.script:
                self.set_speed(command.speed)
                self.move_to(command.position)
            self.scriptReceived = False #reset the script boolean (script only runs once)
            return True # Returns true to signify that the Motor has a loaded script and just run it
                        # Whoever calls this function can then print a status message with the same name
        else:
            return False # Returns False to signify that the Motor doesn't have a loaded script

    def testing():
        # Open serial communications through the COM port
        Library.enable_device_db_store()
        com_port = "COM11"
        connection = Connection.open_serial_port(com_port)
        print("{} port successfully opened".format(com_port))
        device_list = connection.detect_devices()
        device = device_list[0]
        # Initialize a motor
        myMotor1 = Motor(device)
        myMotor1.home()
        print("myMotor1 is homed: ", myMotor1.is_homed())
        myMotor1.move_to(10)

        print("Starting move_speed() test")
        for i in range(5):
            myMotor1.move_speed(5*i)
            time.sleep(.5)
        for i in range(5):
            myMotor1.move_speed(5*-i)
            time.sleep(.5)

    if __name__ == "__main__":
        testing()