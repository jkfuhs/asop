import serial
import struct
import time
import math
import sys

from jetson_inference import detectNet
from jetson_utils import videoSource, videoOutput

net = detectNet("ssd-mobilenet-v2", threshold=0.5)
camera0 = videoSource("csi://0")      # '/dev/video0' for V4L2
camera1 = videoSource("csi://1")      # '/dev/video0' for V4L2

display0 = videoOutput("display://0") # 'my_video.mp4' for file
display1 = videoOutput("display://1") # 'my_video.mp4' for file

# Replace with port name
port = "/dev/ttyACM0"
baud_rate = 9600

# Start pos
start_pos = [0, 0]

# Create serial object
ser = serial.Serial(port, baud_rate, timeout=1)

unique_id = 1

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
    grid_height = int((pointB[1] - pointA[1]) * meters_per_degree)

    grid_width = int((pointB[0] - pointA[0]) * meters_per_degree)

    grid = [[0 for i in range(grid_height)] for j in range(grid_width)]
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
        
    print("Current Location:\n\t Lat: " + str(latitude) + " Lon: " + str(longitude) + " SIV: " + str(siv))
    return [longitude, latitude]


# Checks if there is an obstacle (person) in the 1m x 1m square in front of the robot
# TODO: Make this more broad. Currently only looks for people, should identify ANY obstacle using depth
#       sensor instead of image recognition
def check_obstacles():

    if (display0.isStreaming() == False):
        return True
    
    img0 = camera0.Capture()
    img1 = camera1.Capture()

    if img0 is None or img1 is None:
        return True
    
    detections0 = net.Detect(img0)
    detections1 = net.Detect(img1)

    # Checks for person
    for detection in detections0:
        if (detection.ClassID == 1):
            return True
    for detection in detections1:
        if (detection.ClassID == 1):
            return True
    
    return False

# Checks the camera for weeds. Returns True if weeds are detected, False if not.
# TODO: Needs dataset trained on target weed species. Should only identify weeds
#       within the 1m x 1 m square in front of the robot
def check_weeds():

    if (display0.isStreaming() == False):
        return True
    
    img0 = camera0.Capture()
    img1 = camera1.Capture()

    if img0 is None or img1 is None:
        return True
    
    detections0 = net.Detect(img0)
    detections1 = net.Detect(img1)

    # TODO: Replace "YELLOW STAR THISTLE" with target weed detection ID
    for detection in detections0:
        if (detection.ClassID == "YELLOW STAR THISTLE"):
            return True
    for detection in detections1:
        if (detection.ClassID == "Yellow Star Thistle"):
            return True
    
    return False


def demo_main():
    bounds_f = open("field_coordinates.txt", "r")
    string = bounds_f.readline()
    tokens = string.split(" ")
    sw_corner = [float(tokens[1]), float(tokens[0])]
    string = bounds_f.readline()
    tokens = string.split(" ")
    ne_corner = [float(tokens[1]), float(tokens[0])]
    current_loc = get_gps()
    grid = setup_grid(sw_corner, ne_corner)
    grid_coord = [0, 0]
    meters_per_degree = 111111 * math.cos(sw_corner[0] * math.pi / 180)
    grid_coord[0] = int((current_loc[0] - sw_corner[0]) * meters_per_degree)
    grid_coord[1] = int((current_loc[1] - sw_corner[1]) * meters_per_degree)
    if (grid_coord[0] < 0 or grid_coord[0] >= len(grid) or grid_coord[1] < 0 or grid_coord[1] >= len(grid[0])):
        print("Robot out of bounds Move closer to center of field")
        print(grid_coord)
    else:
        print("Robot in bounds. Beginning DFS of field for weeds")
        print(grid_coord)
        start_pos = grid_coord
        vert_obstacles = [[False for i in range(len(grid[0]))] for j in  range(len(grid))]
        horiz_obstacles = [[False for i in range(len(grid[0]))] for j in  range(len(grid))]
        DFS_step(grid, grid_coord, vert_obstacles, horiz_obstacles)




# TODO: Calibrate motor speeds: turning time and forward movement time.
# Should move forward exactly 1m
def move_forward():
    pass
    # packet = create_command_packet(command_data["FORWARD"], 1,unique_id)
    # ser.flushInput()
    # ser.write(packet)
    # done = False
    # while (done == False):
    #     if ser.in_waiting == 0:
    #         continue

    #     reply = ser.read_until()
    #     reply = reply.decode()
    #     if (reply[:4] == "DONE" and int(reply[5:]) == unique_id):
    #         return
# TODO: hould turn the robot so it faces west
def turn_west():
    pass

# TODO: Turn the robot so it faces east
def turn_east():
    pass

# TODO: Turn the robot so it faces south
def turn_south():
    pass

# TODO: Turn the robot so it faces north
def turn_north():
    pass


def print_maps(grid, grid_coord, v_obst, h_obst):
    # For each row, do:
    
    for y in range(len(grid[0])-1, -1, -1):
        for x in range(len(grid)):
            if (h_obst[x][y] == True):
                sys.stdout.write("| ")
            else:
                sys.stdout.write("  ")

            if (grid_coord[0] == x and grid_coord[1] == y):
                sys.stdout.write("R ")
            elif (grid[x][y] == 1):
                sys.stdout.write("O ")
            elif (grid[x][y] == 2):
                sys.stdout.write("X ")
            else:
                sys.stdout.write("  ")

        sys.stdout.write("\n")
        
        for x in range(len(grid)):
            if (v_obst[x][y] == True):
                sys.stdout.write(" __ ")
            else:
                sys.stdout.write("    ")
        sys.stdout.write("\n")
            

def DFS_step(grid, grid_coord, vertical_obstacles, horizontal_obstacles):
    
    # Check if we're at the west border
    if grid_coord[0] > 0:
        # Check west
        if grid[grid_coord[0]-1][grid_coord[1]] == 0:
            
            turn_west()

            # Update obstacle mapping
            print_maps(grid, grid_coord, vertical_obstacles, horizontal_obstacles)
            input("Current Loc: [" + str(grid_coord[0]) + ", " + str(grid_coord[1]) + "]\nPress Enter to continue")
            horizontal_obstacles[grid_coord[0]][grid_coord[1]] = check_obstacles()
            # horizontal_obstacles[grid_coord[0]][grid_coord[1]] = True

            # input("checking west")
            

            # Check obstacles
            if (horizontal_obstacles[grid_coord[0]][grid_coord[1]] == False):
                
                # Check for weeds
                if (check_weeds()):
                    grid[grid_coord[0]-1][grid_coord[1]] = 2
                else:
                    grid[grid_coord[0]-1][grid_coord[1]] = 1

                # Move
                move_forward()
                grid_coord[0] -= 1

                # Recurse
                DFS_step(grid, grid_coord, vertical_obstacles, horizontal_obstacles)

                # Return to where we were
                turn_east()
                print_maps(grid, grid_coord, vertical_obstacles, horizontal_obstacles)
                input("Current Loc: [" + str(grid_coord[0]) + ", " + str(grid_coord[1]) + "]\nPress Enter to continue")
                horizontal_obstacles[grid_coord[0]+1][grid_coord[1]] = check_obstacles()
                # horizontal_obstacles[grid_coord[0]+1][grid_coord[1]] = True

                # Edge case where something moved into your path behind you, so you cannot return to where you were by stacks
                while (horizontal_obstacles[grid_coord[0]+1][grid_coord[1]] == True):
                    # Current solution: wait until return path is clear
                    print_maps(grid, grid_coord, vertical_obstacles, horizontal_obstacles)
                    input("Current Loc: [" + str(grid_coord[0]) + ", " + str(grid_coord[1]) + "]\nPress Enter to continue")
                    horizontal_obstacles[grid_coord[0]+1][grid_coord[1]] = check_obstacles()
                    
                move_forward()
                grid_coord[0] += 1

    # Check if we're at the South border
    if grid_coord[1] > 0:
        if grid[grid_coord[0]][grid_coord[1]-1] == 0:

            turn_south()
            # Update obstacle mapping
            print_maps(grid, grid_coord, vertical_obstacles, horizontal_obstacles)
            input("Current Loc: [" + str(grid_coord[0]) + ", " + str(grid_coord[1]) + "]\nPress Enter to continue")
            vertical_obstacles[grid_coord[0]][grid_coord[1]] = check_obstacles()

            # Check obstacles
            if (vertical_obstacles[grid_coord[0]][grid_coord[1]] == False):

                if (check_weeds()):
                    grid[grid_coord[0]][grid_coord[1]-1] = 2
                else:
                    grid[grid_coord[0]][grid_coord[1]-1] = 1

                # Move
                move_forward()
                grid_coord[1] -= 1

                # Recurse
                DFS_step(grid, grid_coord, vertical_obstacles, horizontal_obstacles)

                # Return to where we were
                turn_north()
                print_maps(grid, grid_coord, vertical_obstacles, horizontal_obstacles)
                input("Current Loc: [" + str(grid_coord[0]) + ", " + str(grid_coord[1]) + "]\nPress Enter to continue")
                vertical_obstacles[grid_coord[0]][grid_coord[1]+1] = check_obstacles()

                # Edge case where something moved behind you
                if (vertical_obstacles[grid_coord[0]][grid_coord[1]+1] == True):
                    print_maps(grid, grid_coord, vertical_obstacles, horizontal_obstacles)
                    input("Current Loc: [" + str(grid_coord[0]) + ", " + str(grid_coord[1]) + "]\nPress Enter to continue")
                    vertical_obstacles[grid_coord[0]][grid_coord[1]+1] = check_obstacles()
            
                move_forward()
                grid_coord[1]  += 1

    # Check if we're at the north border
    if grid_coord[1] < len(grid[0])-1:
        if grid[grid_coord[0]][grid_coord[1]+1] == 0:

            turn_north()
            # Update obstacle mapping
            print_maps(grid, grid_coord, vertical_obstacles, horizontal_obstacles)
            input("Current Loc: [" + str(grid_coord[0]) + ", " + str(grid_coord[1]) + "]\nPress Enter to continue")
            vertical_obstacles[grid_coord[0]][grid_coord[1]+1] = check_obstacles()
            # input("checking north")

            

            if (vertical_obstacles[grid_coord[0]][grid_coord[1]+1] == False):
                if (check_weeds()):
                    grid[grid_coord[0]][grid_coord[1]+1] = 2
                else:
                    grid[grid_coord[0]][grid_coord[1]+1] = 1
                # Move
                move_forward()
                grid_coord[1] += 1

                # Recurse
                DFS_step(grid, grid_coord, vertical_obstacles, horizontal_obstacles)

                # Return to where we were
                turn_south()
                print_maps(grid, grid_coord, vertical_obstacles, horizontal_obstacles)
                input("Current Loc: [" + str(grid_coord[0]) + ", " + str(grid_coord[1]) + "]\nPress Enter to continue")
                vertical_obstacles[grid_coord[0]][grid_coord[1]] = check_obstacles()

                # Edge case where something moved behind you
                if (vertical_obstacles[grid_coord[0]][grid_coord[1]] == True):
                    print_maps(grid, grid_coord, vertical_obstacles, horizontal_obstacles)
                    input("Current Loc: [" + str(grid_coord[0]) + ", " + str(grid_coord[1]) + "]\nPress Enter to continue")
                    vertical_obstacles[grid_coord[0]][grid_coord[1]] = check_obstacles()

                move_forward()
                grid_coord[1] -= 1

    # Check if we're at the east border
    if grid_coord[0] < len(grid)-1:
        if grid[grid_coord[0]+1][grid_coord[1]] == 0:

            turn_east()
            # Update obstacle mapping
            print_maps(grid, grid_coord, vertical_obstacles, horizontal_obstacles)
            input("Current Loc: [" + str(grid_coord[0]) + ", " + str(grid_coord[1]) + "]\nPress Enter to continue")
            horizontal_obstacles[grid_coord[0]+1][grid_coord[1]] = check_obstacles()
            # input("checking east")

            # Update weeds mapping
            if (check_weeds()):
                grid[grid_coord[0]+1][grid_coord[1]] = 2
            else:
                grid[grid_coord[0]+1][grid_coord[1]] = 1

            if (horizontal_obstacles[grid_coord[0]+1][grid_coord[1]] == False):
                # Move
                move_forward()
                grid_coord[0] += 1

                # Recurse
                DFS_step(grid, grid_coord, vertical_obstacles, horizontal_obstacles)

                # Return to where we were
                turn_west()
                print_maps(grid, grid_coord, vertical_obstacles, horizontal_obstacles)
                input("Current Loc: [" + str(grid_coord[0]) + ", " + str(grid_coord[1]) + "]\nPress Enter to continue")
                horizontal_obstacles[grid_coord[0]][grid_coord[1]] = check_obstacles()

                # Edge case where something moved behind you
                if (horizontal_obstacles[grid_coord[0]][grid_coord[1]] == True):
                    print_maps(grid, grid_coord, vertical_obstacles, horizontal_obstacles)
                    input("Current Loc: [" + str(grid_coord[0]) + ", " + str(grid_coord[1]) + "]\nPress Enter to continue")
                    horizontal_obstacles[grid_coord[0]][grid_coord[1]] = check_obstacles()

                move_forward()
                grid_coord[0] -= 1

        # If we get here, we're either done or stuck, so stop
                

if __name__ == "__main__":
    demo_main()