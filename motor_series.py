"""
MOTOR SERIES CLASS
    This class implements teh interface to work with a series of Motor objects and perform
    all the native functionalities in a coordinated manner
"""

from _typeshed import Self
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
        
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging_level)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        file_handler = logging.FileHandler(f'{log_file_name_head}_{__name__}_log.log', mode = "w")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

        

        
