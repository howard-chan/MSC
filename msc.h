/*
The MIT License (MIT)

Copyright (c) 2016 Howard Chan
https://github.com/howard-chan/MSC

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/
#ifndef __MSC_H__
#define __MSC_H__

#ifdef __cplusplus
extern "C" {
#endif

/* Add platform specific types here */
#include <stdint.h>

//----Type Definitions----
#define MSC_OPC_MSG         0
#define MSC_OPC_EVT         1
#define MSC_OPC_STA         2
#define MSC_OPC_TP          3
#define MSC_OPC_DES         4
#define MSC_OPC_ACK         5

#define MSC_PRI_SOS         1
#define MSC_PRI_SEQ         2
#define MSC_PRI_ALT         4

//----Macros----
#define MSC_SETOBJ(mod, id)     ((uint16_t)(((uint8_t)mod << 8) | (uint8_t)id))

//----Structure declaration----
typedef struct
{
    uint8_t ucOpc : 5;      // Message Code (MSG:0, EVT:1, STA:2, TP:3, DES:4 ACK:5)
    uint8_t ucPri : 3;      // Priority (0x01 - Start of Sequence, 0x02 - Sequential, 0x04 - Alert)
    uint8_t ucLen;          // Length of message
} MSC_HDR_t;

// Helper structure
typedef union
{
    struct
    {
        uint8_t ucMod;      // Module
        uint8_t ucId;       // ID of Module Instance
    };
    uint16_t usValue;       // Object Id
} MSC_OBJ_t;

typedef struct
{
    MSC_HDR_t xHdr;
    MSC_OBJ_t xSrc;         // Source Object
    MSC_OBJ_t xDst;         // Destination Object
    uint16_t usMsgId;       // Message ID
} MSC_MSG_t;

typedef struct
{
    MSC_HDR_t xHdr;
    MSC_OBJ_t xObj;         // Object
    uint16_t usEvtId;       // Event Id
} MSC_EVT_t;

typedef struct
{
    MSC_HDR_t xHdr;
    MSC_OBJ_t xObj;         // Object
    uint16_t usState;       // State Id
} MSC_STA_t;

typedef struct
{
    MSC_HDR_t xHdr;
    MSC_OBJ_t xObj;         // Object
    uint32_t ulData;        // TestPoint Data
} MSC_TP_t;

typedef struct
{
    MSC_HDR_t xHdr;
    MSC_OBJ_t xObj;         // Object
} MSC_DES_t;

typedef struct
{
    MSC_HDR_t xHdr;
    MSC_OBJ_t xObj;         // Object
    uint16_t usMsgId;       // Message ID
} MSC_ACK_t;

// Convenience typedef
typedef union
{
    MSC_MSG_t xMsg;
    MSC_EVT_t xEvt;
    MSC_STA_t xSta;
    MSC_TP_t  xTp;
    MSC_DES_t xDes;
    MSC_ACK_t xAck;
} MSC_t;

#ifdef __cplusplus
}
#endif

#endif // __MSC_H__
