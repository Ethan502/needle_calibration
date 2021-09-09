from zaber_motion import Library
from zaber_motion.ascii import Connection

Library.enable_device_db_store()

with Connection.open_serial_port("/ttyUSB0") as connection:
    device_list = connection.detect_devices()
    print("Found {} devices".format(len(device_list)))