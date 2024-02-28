#ifndef PERIPHERALCOMH
#define PERIPHERALCOMH 

#define REPLY_DATA_SIZE 9

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
    uint16_t unique_id;
}__attribute__((__packed__));

struct reply_st
{
    uint8_t reply_type;
    uint8_t data[REPLY_DATA_SIZE];
}__attribute__((__packed__));

struct done_reply_st
{
    uint16_t unique_id;
}__attribute__((__packed__));

struct gps_reply_st
{
    int32_t latitude;
    int32_t longitude;
    uint8_t SIV;
}__attribute__((__packed__));


#endif