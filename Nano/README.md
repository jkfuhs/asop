## Usage:
Put the coordinates of the field into field_coordinates.txt to map out the field. 
The first coordinate should be the southwest most point and the second coordinate
should be the northeast most point. Anything south or west of the first coordinate
or north or east of the second coordinate is out of bounds. Place the relatively
central in the field to start. (At least 10m from the boundary).

For demo, run DFS_nav.py on a Jetson Nano within the Jetson inference docker.
The code from ../arduino must be installed on the Arduino Uno connected to the Jetson
by UART.


## Navigation Routine
* Currently running a Depth First Search Algorithm.
* The search runs in simulation. Next step is to get it to run on the physical robot.
* TODO's are marked in the source code "DFS_nav.py"
* Known edge-cases: If an obstacle moves behind the robot to block the way back, it will
    get stuck until the obstacle moves out of the way. There are solutions, all of which
    required too much time investment for our scope, so the current solution is to wait
    until the obstacle leaves.