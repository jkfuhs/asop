#ifndef PERIPHERALCOMH
#define PERIPHERALCOMH

#define MOTORCOMMAND_Pos 

typedef enum
{
    FORWARD,
    REVERSE,
    LEFT,
    RIGHT,
    GETGPS
} command_t;

typedef struct command_st *com_p;
struct command_st
{
    uint8_t command;
    uint16_t value;
    uint32_t unique_id;
}__attribute__((__packed__));

#endif