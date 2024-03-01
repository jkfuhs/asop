import serial
import struct
import time


# various variables
NUM_GPS_TOKENS = 4

# Replace with PORT name
PORT = "COM3"
BAUD_RATE = 9600

# Define command strucutre
COMMAND_FORMAT = 'BHH'

# Define the command values
COMMAND_DATA = {
    'FORWARD': 0,
    'REVERSE': 1,
    'LEFT': 2,
    'RIGHT': 3,
    'GETGPS': 4
}


def create_command_packet(command, value, unique_id):
    """
    Create a Command Packet\n
    Args:
        command (str): The command to send.
        value (int): The value associated with the command.
        unique_id (int): The unique ID for the command packet.

    Returns:
        binary: The packet representing the command.
    """
    return struct.pack(COMMAND_FORMAT, COMMAND_DATA[command], value, unique_id)


def validate_gps_data(gps_data):
    """
    Validate GPS data.\n
    Args:
        gps_data (str): The GPS data string to validate.

    Returns:
        bool: True if the data is valid, False otherwise.
    """
    tokens = gps_data.split()
    print("len = " + str(len(tokens)))
    # check length requirement
    if len(tokens) != NUM_GPS_TOKENS:
        return False
    if tokens[0] != 'G':
        return False
    
    return True


def main():
    # Create serial object
    ser = serial.Serial(PORT, BAUD_RATE, timeout=1)

    i = 1   ###############unused?

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

if __name__ == "__main__":
    main()