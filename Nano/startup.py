import serial
import struct
import time

# Replace with port name
port = "COM3"
baud_rate = 9600

# various variables
num_gps_tokens = 4

# Create serial object
ser = serial.Serial(port, baud_rate, timeout=1)

# Define command strucutre
command_format = 'BHH'

# Define the command values
command_data = {
    'FORWARD': 0,
    'REVERSE': 1,
    'LEFT': 2,
    'RIGHT': 3,
    'GETGPS': 4
}

# Function to create a command packet
def create_command_packet(command, value, unique_id):
    return struct.pack(command_format, command_data[command], value, unique_id)

# Function to verify validity of GPS packet
def validate_gps_data(gps_data):
    tokens = gps_data.split()
    print("len = " + str(len(tokens)))
    # check length requirement
    if len(tokens) != 4:
        return False
    if tokens[0] != 'G':
        return False
    
    return True

i = 1
ser.timeout = 10
ser.flushInput()
while 1:
    # Attempt to send a command
    command_packet = create_command_packet('GETGPS', 0, 0)    
    i = i+1
    ser.write(command_packet)
    
    # Wait unil reply is sent back
    if ser.in_waiting == 0:
        time.sleep(1)
        continue

    # Read from serial buffer
    gps_data = ser.read_until()

    # Trim serial metadata (b'...\r\n')
    gps_data = gps_data.decode()
    if validate_gps_data(gps_data):
        print(gps_data)

    time.sleep(2)



ser.close()