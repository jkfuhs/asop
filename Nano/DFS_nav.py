import serial
import struct
import ctypes

# Replace with port name
port = "/dev/ttyUSB0"
baud_rate = 115200

# Create serial object
ser = serial.Serial(port, baud_rate, timeout=1)

# Define command structure
command_format = 'BHH'
reply_format = 'llH'



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

# Function to check if a complete reply is ready
def is_reply_ready():
    return ser.in_waiting >= struct.calcsize(reply_format)

