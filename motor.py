from zaber_motion import Library
from zaber_motion.ascii import Connection

Library.enable_device_db_store()

<<<<<<< HEAD
with Connection.open_serial_port("COM1") as connection:
=======
with Connection.open_serial_port("/ttyUSB0") as connection:
>>>>>>> 94774e3b83fa55d6827b685edda93175be0cfd02
    device_list = connection.detect_devices()
    print("Found {} devices".format(len(device_list)))