#include <Arduino.h>

#include "peripheral_commands.h"
#include "arduino-timer.h"

#define SERIAL_BAUD 115200
#define VALUE_TO_DISTANCE   1     // TODO: do measurememts and get a precise number for this.
#define VALUE_TO_TURN       1

#define in1L 9
#define in2L 8
#define in3L 7
#define in4L 6

#define in1R 5
#define in2R 4
#define in3R 3
#define in4R 2

#define DONE_MSG    "DONE"


auto timer = timer_create_default();

void setup() 
{
    // initialize peripherals
        // Motors
    pinMode(in1L, OUTPUT);
    pinMode(in2L, OUTPUT);
    pinMode(in3L, OUTPUT);
    pinMode(in4L, OUTPUT);
    pinMode(in1R, OUTPUT);
    pinMode(in2R, OUTPUT);
    pinMode(in3R, OUTPUT);
    pinMode(in4R, OUTPUT);

    digitalWrite(in1L, LOW);
    digitalWrite(in2L, LOW);
    digitalWrite(in3L, LOW);
    digitalWrite(in4L, LOW);
    digitalWrite(in1R, LOW);
    digitalWrite(in2R, LOW);
    digitalWrite(in3R, LOW);
    digitalWrite(in4R, LOW);
        // GPS

    // initialize serial coms with jetson
    Serial.begin(SERIAL_BAUD);
}

void loop() 
{
    SerialEvent();
    timer.tick();
}

// polling function for serial inputs
void SerialEvent(void)
{
    com_p serial_command;
    size_t len = sizeof(command_st);


    if (Serial.readBytes((uint8_t*) serial_command, sizeof(command_st)) != sizeof(command_st))
    {
        return;
    }

    switch (serial_command->command)
    {
        case FORWARD:
            move_forward(serial_command->value, serial_command->unique_id);
            break;

        case REVERSE:
            move_reverse(serial_command->value, serial_command->unique_id);
            break;

        case LEFT:
            turn_left(serial_command->value, serial_command->unique_id);
            break;
        
        case RIGHT:
            turn_right(serial_command->value, serial_command->unique_id);
            break;

        case GETGPS:
            get_gps();
            break;

        default:
            
            break;
        
    }
}

bool stop_motors(void *m)
{
    // turn off motors
    digitalWrite(in1L, LOW);
    digitalWrite(in2L, LOW);
    digitalWrite(in3L, LOW);
    digitalWrite(in4L, LOW);
    digitalWrite(in1R, LOW);
    digitalWrite(in2R, LOW);
    digitalWrite(in3R, LOW);
    digitalWrite(in4R, LOW);

    // send DONE message
    Serial.print(DONE_MSG);
    Serial.println((uint32_t) m);

    return false;
}

void move_forward(uint16_t value, uint32_t unique_id)
{
    unsigned long drive_time;
    
    // calculate how long to go forward from 'value'
    drive_time = VALUE_TO_DISTANCE * value; 

    // set motors forward
    digitalWrite(in1L, HIGH);
    digitalWrite(in2L, LOW);
    digitalWrite(in3L, HIGH);
    digitalWrite(in4L, LOW);
    digitalWrite(in1R, HIGH);
    digitalWrite(in2R, LOW);
    digitalWrite(in3R, HIGH);
    digitalWrite(in4R, LOW);

    timer.in(drive_time, stop_motors, (void*) unique_id);
}

void move_reverse(uint16_t value, uint32_t unique_id)
{
    unsigned long drive_time;

    // calculate how long to go backward from 'value'
    drive_time = VALUE_TO_DISTANCE * value;

    // set motors reverse
    digitalWrite(in1L, LOW);
    digitalWrite(in2L, HIGH);
    digitalWrite(in3L, LOW);
    digitalWrite(in4L, HIGH);
    digitalWrite(in1R, LOW);
    digitalWrite(in2R, HIGH);
    digitalWrite(in3R, LOW);
    digitalWrite(in4R, HIGH);

    timer.in(drive_time, stop_motors, (void*) unique_id);
}

void turn_left(uint16_t value, uint32_t unique_id)
{
    unsigned long drive_time;
    
    // calculate how long to turn left
    drive_time = VALUE_TO_TURN * value;

    // set left side reverse, right side forward
    digitalWrite(in1L, LOW);
    digitalWrite(in2L, HIGH);
    digitalWrite(in3L, LOW);
    digitalWrite(in4L, HIGH);

    digitalWrite(in1R, HIGH);
    digitalWrite(in2R, LOW);
    digitalWrite(in3R, HIGH);
    digitalWrite(in4R, LOW);


    timer.in(drive_time, stop_motors, (void*) unique_id);
}

void turn_right(uint16_t value, uint32_t unique_id)
{
    unsigned long drive_time;

    // calculate how long to turn right
    drive_time = VALUE_TO_TURN * value;

    // set left side forward, right side reverse
    digitalWrite(in1L, HIGH);
    digitalWrite(in2L, LOW);
    digitalWrite(in3L, HIGH);
    digitalWrite(in4L, LOW);

    digitalWrite(in1R, LOW);
    digitalWrite(in2R, HIGH);
    digitalWrite(in3R, LOW);
    digitalWrite(in4R, HIGH);

    timer.in(drive_time, stop_motors, (void*) unique_id);
}

void get_gps(void)
{
    // get gps data
}