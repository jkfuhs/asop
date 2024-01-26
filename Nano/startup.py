import serial
import struct

# Replace with port name
port = "/dev/ttyUSB0"
baud_rate = 115200

# Create serial object
ser = serial.Serial(port, baud_rate, timeout=1)

# Define command strucutre
command_format = 'BHH'
reply_format = 'llH'

# Define the command values
command_data = {
    'FORWARD': 0,
    'REVERSE': 1,
    'LEFT': 2,
    'RIGHT': 3,
    'GETGPTS': 4
}

# Function to create a command packet
def create_command_packet(command, value, unique_id):
    return struct.pack(command_format, command_data[command], value, unique_id)

# Function to check if a complete reply is ready
def is_reply_ready():
    return ser.in_waiting >= struct.calcsize(reply_format)

int i = 1
while 1:
    # Attempt to send a command
    command_packet = create_command_packet('FORWARD', 10, i)    
    i = i+1
    ser.write(command_packet)
    
    # Wait unil reply is sent back
    while not is_reply_ready():
        pass

    # Read and extract the reply packet
    received_data = ser.read(struct.calcsize(reply_format))
    latitude, longitude, unique_id = struct.unpack(reply_format, received_data)

    # Print unpacked data
    print(f"Latitude: {latitude}, Longitude: {longitude}, Unique ID: {unique_id}")

ser.close()
