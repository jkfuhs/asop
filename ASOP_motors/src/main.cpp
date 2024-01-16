#include <Arduino.h>
#include "peripheral_commands.h"

#define SERIAL_BAUD 115200

#define in1L 9
#define in2L 8
#define in3L 7
#define in4L 6

#define in1R 5
#define in2R 4
#define in3R 3
#define in4R 2

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
    // clear flags, enable interrupts on serial input
}

void loop() 
{
    SerialEvent();
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
            // set direction forward
            // set timer
            break;

        case REVERSE:
            // set direction reverse
            // set timer
            break;

        case LEFT:
            // set direction left
            // set timer
            break;
        
        case RIGHT:
            // set direction right
            // set timer
            break;

        case GETGPS:
            // get gps data
            break;

        default:
            
            break;
        
    }
}