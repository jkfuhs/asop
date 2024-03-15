#include <Arduino.h>
#include <Wire.h>

#include "SparkFun_u-blox_GNSS_Arduino_Library.h"
#include "peripheral_commands.h"

#define SERIAL_BAUD 9600
#define GNSS_UPDATE_TIME    1000    // send GNSS data every 1000 msec
#define VALUE_TO_DISTANCE   1       // TODO: do measurememts and get a precise number for this.
#define DONE_TIMER          1000
#define VALUE_TO_TURN       1
#define DEFAULT_ID          0

#define in1L        9
#define in2L        8
#define in3L        7
#define in4L        6

#define in1R        5
#define in2R        4
#define in3R        3
#define in4R        2


#define DONE_MSG    -1


SFE_UBLOX_GNSS myGNSS;
uint32_t lastTime = 0;
uint32_t moveTime = 0;
uint8_t led_value = HIGH;
uint16_t lastMove_id = 0;
uint16_t lastDone = 0;
uint16_t lastDoneMsgTime = 0;

void setup() 
{
    // setup LED
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, led_value);

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

    // initialize serial coms with jetson
    Serial.begin(SERIAL_BAUD);
    while (!Serial); // wait for Serial with Jetson to open
    Serial.flush();

    // Serial.println("ASOP Arduino main");

    // GNSS setup
    Wire.begin();

    while (myGNSS.begin() == false)
    {
        led_value = led_value ^ HIGH;
        digitalWrite(LED_BUILTIN, led_value);
        delay(100);
    }
    myGNSS.setI2COutput(COM_TYPE_UBX);
    myGNSS.saveConfigSelective(VAL_CFG_SUBSEC_IOPORT);
    led_value = LOW;
    digitalWrite(LED_BUILTIN, led_value);
}

void stop_motors(uint16_t unique_id)
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

    
    if (unique_id == 0)
    {
        return;
    }

    // send DONE message
    lastDone = unique_id;
    // Serial.print("DONE ");
    // Serial.println(unique_id);

    return;
}

void set_stop_timer(uint32_t drive_time, uint16_t unique_id)
{
    moveTime = drive_time;
    lastMove_id = unique_id;
    lastTime = millis();
    digitalWrite(LED_BUILTIN, LOW);
}

void move_forward(uint16_t value, uint16_t unique_id)
{
    uint32_t drive_time;
    
    // calculate how long to go forward from 'value'
    drive_time = VALUE_TO_DISTANCE * value; 

    // set motors forward
    digitalWrite(in1L, LOW);
    digitalWrite(in2L, HIGH);
    digitalWrite(in3L, LOW);
    digitalWrite(in4L, HIGH);
    
    digitalWrite(in1R, HIGH);
    digitalWrite(in2R, LOW);
    digitalWrite(in3R, HIGH);
    digitalWrite(in4R, LOW);

    digitalWrite(LED_BUILTIN, HIGH);

    set_stop_timer(drive_time, unique_id);
}

void move_reverse(uint16_t value, uint16_t unique_id)
{
    unsigned long drive_time;

    // calculate how long to go backward from 'value'
    drive_time = VALUE_TO_DISTANCE * value;

    // set motors reverse
    digitalWrite(in1L, HIGH);
    digitalWrite(in2L, LOW);
    digitalWrite(in3L, HIGH);
    digitalWrite(in4L, LOW);

    digitalWrite(in1R, LOW);
    digitalWrite(in2R, HIGH);
    digitalWrite(in3R, LOW);
    digitalWrite(in4R, HIGH);

    set_stop_timer(drive_time, unique_id);
}

void turn_left(uint16_t value, uint16_t unique_id)
{
    unsigned long drive_time;
    
    // calculate how long to turn left
    drive_time = VALUE_TO_TURN * value;

    digitalWrite(in1L, HIGH);
    digitalWrite(in2L, LOW);
    digitalWrite(in3L, HIGH);
    digitalWrite(in4L, LOW);

    digitalWrite(in1R, HIGH);
    digitalWrite(in2R, LOW);
    digitalWrite(in3R, HIGH);
    digitalWrite(in4R, LOW);

    set_stop_timer(drive_time, unique_id);
}

void turn_right(uint16_t value, uint16_t unique_id)
{
    unsigned long drive_time;

    // calculate how long to turn right
    drive_time = VALUE_TO_TURN * value;

    // set left side forward, right side reverse
    digitalWrite(in1L, LOW);
    digitalWrite(in2L, HIGH);
    digitalWrite(in3L, LOW);
    digitalWrite(in4L, HIGH);

    digitalWrite(in1R, LOW);
    digitalWrite(in2R, HIGH);
    digitalWrite(in3R, LOW);
    digitalWrite(in4R, HIGH);

    set_stop_timer(drive_time, unique_id);
}

void get_gps(uint16_t unique_id)
{
    int32_t latitude;
    int32_t longitude;
    uint16_t siv;

    latitude = myGNSS.getLatitude();
    longitude = myGNSS.getLongitude();
    siv = myGNSS.getSIV();

    Serial.print("G ");
    Serial.print(latitude);
    Serial.print(" ");
    Serial.print(longitude);
    Serial.print(" ");
    Serial.println(siv);
}

// polling function for serial inputs
void SerialEvent(void)
{
    com_p serial_command = NULL;
    size_t len = sizeof(command_st);

    if (!Serial.available())
    {
        return;
    }

    if (Serial.readBytes((uint8_t*) serial_command, len) != len)
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
            get_gps(serial_command->unique_id);
            break;

        default:
            
            break;
        
    }
}


void loop()
{

    if (moveTime > 0 && millis() - lastTime > moveTime)
    {
        stop_motors(lastMove_id);
        moveTime = 0;
    }

    
    SerialEvent();    
}