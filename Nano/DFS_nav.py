import serial
import struct
import time

# Replace with port name
port = "COM3"
baud_rate = 9600

# Create serial object
ser = serial.Serial(port, baud_rate, timeout=1)

# Define command structure
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
def validate_gps_data(tokens):
    # check length requirement
    if len(tokens) != 4:
        return False
    if tokens[0] != "G":
        return False
    
    return True

#Request GPS data, and wait until SIV > 3
siv = 0
command_packet = create_command_packet('GETGPS', 0, 0)
ser.flushInput()
while siv <= 3:
    ser.write(command_packet)

    # if no reply is received, wait and re-send
    if ser.in_waiting == 0:
        time.sleep(1)
        continue

    # Read one line of input
    gps_data = ser.read_until()
    gps_data = gps_data.decode()
    gps_tokens = gps_data.split()

    if validate_gps_data(gps_tokens):
        
        latitude = int(gps_tokens[1])
        longitude = int(gps_tokens[2])
        siv = int(gps_tokens[3])
    
    print("Current Location:\n\t Lat: " + str(latitude) + " Lon: " + str(longitude) + " SIV: " + str(siv))

