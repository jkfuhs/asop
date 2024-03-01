import serial
import struct
import time
import math

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

# Define grid values
grid_value = {
    'UNEXPLORED': 0,
    'EMPTY': 1,
    'WEEDS': 2
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

# Function to set up a square grid from gps coordinates using resolution 1m
def setup_grid(pointA, pointB):
    # compute size of field in meters
    meters_per_degree = 111111 * math.cos(pointA[0] * math.pi / 180)
    grid_height = int((pointB[0] - pointA[0]) * meters_per_degree)
    # grid_height = (pointA[0] - pointB[0]) * 111111

    grid_width = int((pointB[1] - pointA[1]) * meters_per_degree)
    # grid_width = (pointA[1] - pointB[1]) * 111111

    grid = [[0] * grid_width] * grid_height
    print("width = " + str(grid_width))
    print("height = " + str(grid_height))
    
    return grid

def get_gps():
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
            
            latitude = int(gps_tokens[1]) * 10**-7
            longitude = int(gps_tokens[2]) * 10**-7
            siv = int(gps_tokens[3])
        
    # print("Current Location:\n\t Lat: " + str(latitude) + " Lon: " + str(longitude) + " SIV: " + str(siv))
    return [latitude, longitude]

sw_corner = [35.30002, -120.662]
ne_corner = [35.30008, -120.661]
current_loc = get_gps()
grid = setup_grid(sw_corner, ne_corner)
grid_coord = [0, 0]
grid_coord[0] = int((current_loc[0] - sw_corner[0]) * 111111 * math.cos(sw_corner[0] * math.pi / 180))
grid_coord[1] = int((current_loc[1] - sw_corner[1]) * 111111 * math.cos(sw_corner[0] * math.pi / 180))
print(current_loc)
print(grid_coord)
if (grid_coord[0] < 0 or grid_coord[0] > len(grid[0]) or grid_coord[1] < 0 or grid_coord[1] > len(grid)):
    print("Robot out of bounds. Move closer to center of field")
else:
    print("Robot in bounds. Beginning DFS of field for weeds")

def DFS_step(grid, grid_coord, vertical_obstacles, horizontal_obstacles):

    # Check if we're at the top
    if grid_coord[1] != len(grid[0]):

        # Check north
        if grid[grid_coord[0]][grid_coord[1]-1] == 'UNEXPLORED':
            
            horizontal_obstacles[grid_coord[0]][grid_coord[1]] = check_obstacles()
            if (horizontal_obstacles[grid_coord[0]][grid_coord[1]] == False):
                move_north()
                grid_coord[1] = grid_coord[1] -1
