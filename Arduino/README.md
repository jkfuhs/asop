# ASOP Arduino
===============================================================================
## Communication protocol
* The Jetson Nano communicates with the following peripheral devices via the arduino board:
    - GPS
    - Motors
* The Arduino is interrupt driven so sending a command before the arduino has finished the
    previous command will cause it to abort.
* Once the Arduino has finished executing a command, it will return the 'DONE' signal.

## Control Packet Structure
* The following is the data structure of the commands to control the Arduino Uno from the Jetson Nano:
    - [uint8_t command] [uint16_t value]
* There are 5 executable commands: Forward=0, Reverse=1, Left=2, Right=3, and GetGPS=4.

* The value following a Foward or Reverse command is a distance in cm.
* The value following a Left or Right command is a direction in degrees.
* GetGPS doesn't care about the value field.

## Usage
* This code allows the Jetson nano to communicate with the Arduino Uno to control
    motors. 

## Remaining Work
* Calibrate the turn commands to whatever chasis they are connected to. That is, adjust
    the #define VALUE_TO_DISTANCE and #define VALUE_TO_TURN in main.cpp such that
    the move_forward() function moves the robot the correct distance and the turn_left()
    and turn_right() turns the correct amount. This will be mostly trial and error and
    depends on the chasis used.