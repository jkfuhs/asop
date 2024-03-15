from jetson_inference import detectNet
from jetson_utils import videoSource, videoOutput
import serial
import struct
import time
import math

port = '/dev/ttyACM0'
baud_rate = 9600
ser = serial.Serial(port, baud_rate, timeout=1)
command_format = 'BHH'

command_data = {
    'FORWARD': 0,
    'REVERSE': 1,
    'LEFT': 2,
    'RIGHT': 3,
    'GETGPS': 4
}

def create_command_packet(command, value, unique_id):
    return struct.pack(command_format, command_data[command], value, unique_id)



net = detectNet("ssd-mobilenet-v2", threshold=0.5)
camera0 = videoSource("csi://0")      # '/dev/video0' for V4L2
camera1 = videoSource("csi://1")      # '/dev/video0' for V4L2

display0 = videoOutput("display://0") # 'my_video.mp4' for file
display1 = videoOutput("display://1") # 'my_video.mp4' for file

def main():
    cmdID = 1
    while display0.IsStreaming():
        stopFlag = 0

        img0 = camera0.Capture()
        img1 = camera1.Capture()

        if img0 is None: # capture timeout
            continue
        if img1 is None: # capture timeout
            continue

        detections0 = net.Detect(img0)
        detections1 = net.Detect(img1)

        for detection in detections0:
            if(detection.ClassID == 1):
                print("Camera 0 - Class:", detection.ClassID, "Confidence:", detection.Confidence)
                stopFlag = 1
                break
        if not stopFlag:           
            for detection in detections1:
                if(detection.ClassID == "Person"):
                    print("Camera 1 - Class:", detection.ClassID, "Confidence:", detection.Confidence)
                    stopFlag = 1
                    break

        display0.Render(img0)
        display0.SetStatus("Object Detection | Network {:.0f} FPS".format(net.GetNetworkFPS()))

        display1.Render(img1)
        display1.SetStatus("Object Detection | Network {:.0f} FPS".format(net.GetNetworkFPS()))

        if not stopFlag:
            print("Sending Forward")
            command_packet = create_command_packet('FORWARD', 1, cmdID)
            if cmdID % 7 == 0:
                ser.write(command_packet)
                ser.flush()
            cmdID += 1

# Checks if there is an obstacle (person) in front of robot. Returns True if there is, False if there isn't
def check_obstacles():

    if (display0.isStreaming() == False):
        return True
    
    img0 = camera0.Capture()
    img1 = camera1.Capture()

    if img0 is None or img1 is None:
        return True
    
    detections0 = net.Detect(img0)
    detections1 = net.Detect(img1)

    for detection in detections0:
        if (detection.ClassID == 1):
            return True
    for detection in detections1:
        if (detection.ClassID == 1):
            return True
    
    return False

def check_weeds():

    if (display0.isStreaming() == False):
        return True
    
    img0 = camera0.Capture()
    img1 = camera1.Capture()

    if img0 is None or img1 is None:
        return True
    
    detections0 = net.Detect(img0)
    detections1 = net.Detect(img1)

    for detection in detections0:
        if (detection.ClassID == "Yellow Star Thistle"):
            return True
    for detection in detections1:
        if (detection.ClassID == "Yellow Star Thistle"):
            return True
    
    return False


if __name__ == "__main__":
    main()
