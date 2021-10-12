"""
MOTOR SERIES CLASS
    This class implements teh interface to work with a series of Motor objects and perform
    all the native functionalities in a coordinated manner
"""

from zaber_motion import Library, MotionLibException
from zaber_motion.ascii import Connection
from motor import Motor
from moves import Move
import threading
import inspect
import json
import logging
import time
from zaber_motion import Library, LogOutputMode

STEP_SPEED = 1
STEP_SIZE = 0.1
UNKNOWN_VALUE = "UNKNOWN"

class MotorSeries:

    # The constructor receives a string that specifies the COM port as: "COMX"
    def __init__(self, com_port, config_file, log_file_name_head, logging_level=logging.DEBUG):
        
        # Zaber factory logs ---------------------------------------------
            file_name_tail = "_zaber_log.log"
            log_file_path = log_file_name_head + file_name_tail
            Library.set_log_output(LogOutputMode.FILE, log_file_path)
        #-----------------------------------------------------------------

