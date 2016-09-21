#!/usr/python
"""
The MIT License (MIT)

Copyright (c) 2015 Howard Chan
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
"""

# MSC Class in Python
# H.Chan
import binascii
import struct
import sys

# Configurable Parameters
MAX_NAME_LEN = 10
MIN_SPACING = 2
LINES_PER_PAGE = 5
LEADIN = 4
WIDTH  = 6

#TODO: Add DispWeb for https://www.websequencediagrams.com/

class DispTerm:
    ''' Class providing API to displaying ASCII formatted MSC symbols to stdout
    '''
    # These are the display tiles used to draw the MSC graphic symbols
    # The WIDTH can be configured and controls the center spacing
    TILES = {
        "CEN" : " " * WIDTH + " | " + " " * WIDTH,  # 0 CENTER: "   |   "
        "LFA" : " " * WIDTH + " |<" + "-" * WIDTH,  # 1 LF ARR: "   |<--"
        "LFE" : "-" * WIDTH + "-| " + " " * WIDTH,  # 2 LF END  "---|   "
        "RTA" : "-" * WIDTH + ">| " + " " * WIDTH,  # 3 RT ARR: "-->|   "
        "RTE" : " " * WIDTH + " |-" + "-" * WIDTH,  # 4 RT END: "   |---"
        "THR" : "-" * WIDTH + "---" + "-" * WIDTH,  # 5 THRU:   "-------"
        "SLF" : " " * WIDTH + " |}" + " " * WIDTH,  # 6 SELF    "   |}  "
        "STA" : " " * WIDTH + "[S]" + " " * WIDTH,  # 7 STATE:  "  [S]  "
        "EVT" : "_" * WIDTH + "\| " + " " * WIDTH,  # 8 ASYNC:  "__\|   "
        "DES" : " " * WIDTH + " X " + " " * WIDTH,  # 9 DESTROY:"   X   "
    }

    def __init__(self, linesPerPage=LINES_PER_PAGE, prefix="", stdout=None):
        ''' Initialize the display
        linesPerPage[in] - Sets the number of rows before printing a new banner
        prefix[in] - Prefix String or callable function to generate prefix string
        stdout[in] - Can be overwritten to a file or stdout
        '''
        self.lines = 0
        self.linesPerPage = linesPerPage
        self.prefix = prefix
        self.stdout = stdout if stdout is not None else sys.stdout
        self.banner = ""

    def _GetPrefix(self):
        ''' Private Function to return the prefix string
        '''
        if hasattr(self.prefix, '__call__'):
            # prefix is a function, call it to return the new prefix string
            return self.prefix()
        else:
            # return the static prefix string
            return self.prefix

    def SetObjList(self, objList):
        '''
        '''
        width = len(DispTerm.TILES["CEN"])
        # Step 1: Generate the object banner
        self.banner = ""
        for obj in objList:
            self.banner += ("[" + obj + "]").center(width)
        # Step 2: Print the banner to reflect changes
        self.Banner(True)

    def Banner(self, isRequired=False):
        ''' Displays the object banner after a number of lines or when the objList changes
        '''
        # Print the banner at each page
        if (self.lines % self.linesPerPage == 0) or isRequired:
            self.stdout.write(self._GetPrefix() + self.banner + "\n")
            self.lines = 0
        self.lines += 1

    def Message(self, objCnt, srcId, dstId, msgStr):
        ''' Displays a message line from the src to dst object's life line
        '''
        # Step 1: Check the message direction and distance between srcId and dstId
        dist = dstId - srcId
        start, end = (srcId, dstId) if dist > 0 else (dstId, srcId)
        # Step 2: Print optional prefix
        line = self._GetPrefix()
        # Step 3: Fill start with life lines
        line += DispTerm.TILES["CEN"] * start
        # Step 4: Build the message arrow
        if dist == 0:
            # Generate Self Message
            line += DispTerm.TILES["SLF"]
        elif dist > 0:
            # Generate ---> message
            line += DispTerm.TILES["RTE"]
            # Add lines that are long
            if dist > 1:
                line += DispTerm.TILES["THR"] * (dist - 1)
            line += DispTerm.TILES["RTA"]
        else:
            # Generate <--- message
            dist = -dist
            line += DispTerm.TILES["LFA"]
            if dist > 1:
                line += DispTerm.TILES["THR"] * (dist - 1)
            line += DispTerm.TILES["LFE"]
        # Step 5: Fill end
        line += DispTerm.TILES["CEN"] * (objCnt - 1 - end)
        self.stdout.write(line + " : " + msgStr + "\n")

    def Event(self, objCnt, objId, msgStr):
        ''' Displays a asynchronous event to an object's life line
        '''
        # Step 1: Print optional prefix
        line = self._GetPrefix()
        # Step 2: Build the event symbols
        for idx in range(objCnt):
            if idx == objId:
                line += DispTerm.TILES["EVT"]
            else:
                line += DispTerm.TILES["CEN"]
        self.stdout.write(line + " : " + msgStr + "\n")

    def State(self, objCnt, objId, stateStr):
        ''' Displays a state change in an object's life line
        '''
        # Step 1: Print optional prefix
        line = self._GetPrefix()
        # Step 2: Build the State symbols
        for idx in range(objCnt):
            if idx == objId:
                line += DispTerm.TILES["STA"]
            else:
                line += DispTerm.TILES["CEN"]
        self.stdout.write(line + " : " + stateStr + "\n")

    def Destroy(self, objCnt, objId):
        ''' Displays a destroy of an object's life line
        '''
        # Step 1: Print optional prefix
        line = self._GetPrefix()
        # Step 2: Build the Destroy symbols
        for idx in range(objCnt):
            if idx == objId:
                line += DispTerm.TILES["DES"]
            else:
                line += DispTerm.TILES["CEN"]
        self.stdout.write(line + "\n")

    def TestPt(self, objId, dst, msg):
        # Step 1: Print optional prefix
        line = self._GetPrefix()
        # Step 2: Build the test point symbols
        #TODO: Add testpoint generation
        self.stdout.write(line + "\n")


class MSC(object):
    '''
    The MSC class parses the MSC messages generated from a target device which are
    filtered and displayed

    The MSC format is as follows:
    typedef struct
    {
        uint8_t ucOpc : 5;      // Message Code (MSG:0, EVT:1, STA:2, TP:3, ACK:4)
        uint8_t ucMsk : 3;      // Priority (0x01 - Start of Sequence, 0x02 - Sequential, 0x04 - Alert)
        uint8_t ucLen;          // Length of message
    } MSC_HDR_t;

    typedef struct
    {
        MSC_HDR_t xHdr;
        uint8_t ucSrcMod;       // Source Module
        uint8_t ucSrcId;        // Source ID of Module Instance
        uint8_t ucDstMod;       // Destination Module
        uint8_t ucDstId;        // Destination ID of Module Instance
        uint16_t usMsgId;       // Message ID
    } MSC_MSG_t;

    typedef struct
    {
        MSC_HDR_t xHdr;
        uint8_t ucMod;          // Module
        uint8_t ucId;           // ID of Module Instance
        uint16_t usMsgId;       // TestPoint Data
    } MSC_EVT_t;

    typedef struct
    {
        MSC_HDR_t xHdr;
        uint8_t ucMod;          // Module
        uint8_t ucId;           // ID of Module Instance
        uint16_t usState;       // TestPoint Data
    } MSC_STA_t;

    typedef struct
    {
        MSC_HDR_t xHdr;
        uint8_t ucMod;          // Module
        uint8_t ucId;           // ID of Module Instance
        uint8_t aucData[0];     // TestPoint Data
    } MSC_TP_t;

    typedef struct
    {
        MSC_HDR_t xHdr;
        uint8_t ucMod;          // Module
        uint8_t ucId;           // ID of Module Instance
        uint16_t usMsgId;       // Message ID
    } MSC_ACK_t;

    [FlagsType=MSG(0)][Tag][SrcMod][SrcId][DstMod][DstId][Message]
    [Type=ACK(1)][Tag][SrcMod][SrcId][DstMod][DstId][Message]
    '''
    HDR_TYPE_MSG = 0
    HDR_TYPE_EVT = 1
    HDR_TYPE_STA = 2
    HDR_TYPE_TP  = 3
    HDR_TYPE_ACK = 4

    HDR_PRI_SOS = 1
    HDR_PRI_SEQ = 2
    HDR_PRI_ALT = 4

    HDR_OPC_SHF = 0
    HDR_OPC_LEN = 5
    HDR_OPC_MSK = (1 << HDR_OPC_LEN) - 1
    HDR_PRI_SHF = HDR_OPC_LEN
    HDR_PRI_LEN = 3
    HDR_PRI_MSK = (1 << HDR_PRI_LEN) - 1

    def __init__(self, disp):
        self.disp = disp
        self.msgDict = {}
        self.modDict = {}
        self.objDict = {}

    def RegisterMsg(self, usMsgId, strMsg):
        ''' Register the msgId with message string '''
        # Limit max length of string for formating
        self.msgDict[usMsgId] = strMsg[0:MAX_NAME_LEN]

    def RegisterMod(self, ucModId, strMod):
        ''' Register the module Id with module string '''
        # Limit max length of string for formating
        self.modDict[ucModId] = strMod[0:MAX_NAME_LEN]

    def AddFilter(self, key):
        #TODO: Add filter to Parse
        pass

    def DelFilter(self, key):
        #TODO: Add filter to Parse
        pass

    def BuildPkt(self, ucOpc, ucPri, msgId, srcMod, srcId, dstMod=0, dstId=0):
        '''
        Returns a message packet based on the message type (ucOpc)
        '''
        # Step 1: Build Header
        hdr = (MSC.HDR_OPC_MSK & ucOpc) << MSC.HDR_OPC_SHF | (MSC.HDR_PRI_MSK & ucPri) << MSC.HDR_PRI_SHF
        # Step 2: Format the body
        if ucOpc == MSC.HDR_TYPE_MSG:
            body = struct.pack("<BBBBH", srcMod, srcId, dstMod, dstId, msgId)
        elif ucOpc == MSC.HDR_TYPE_EVT:
            body = struct.pack("<BBH", srcMod, srcId, msgId)
        elif ucOpc == MSC.HDR_TYPE_TP:
            body = struct.pack("<BB", srcMod, srcId)
        elif ucOpc == MSC.HDR_TYPE_STA:
            body = struct.pack("<BBH", srcMod, srcId,msgId)
        # Step 3: Build Packet
        pkt = chr(hdr) + chr(len(body)) + body
        # print binascii.hexlify(pkt)
        return pkt

    def AddObj(self, keyList):
        ''' Adds object(s) to MSC
        '''
        isChanged = False
        for key in keyList:
            if key not in self.objDict:
                idx = len(self.objDict)
                self.objDict[key] = idx
                isChanged = True
        if isChanged:
            objList = []
            for key in self.objDict:
               objList.append("%x:%s" % (ord(key[1]), self.modDict[ord(key[0])]))
              #TODO: Fix dictionary order issue
            self.disp.SetObjList(objList)
        return isChanged

    def DelObj(self, key):
        ''' Removes the object from MSC
        '''
        #TODO: Add mechanism to delete object
        pass

    def Parse(self, pkt):
        ''' Parses the incoming MSC protocol packet then displays
        '''
        #TODO: Add Packet Filter Here

        # Print the packet type
        ucOpc = ord(pkt[0]) & MSC.HDR_OPC_MSK
        if ucOpc == MSC.HDR_TYPE_MSG:
            # Check if object needs to be added
            src = (pkt[2] ,pkt[3])
            dst = (pkt[4] ,pkt[5])
            self.AddObj([src, dst])
            # Display Banner (if required)
            self.disp.Banner()
            # Display Message
            self.disp.Message(len(self.objDict), self.objDict[src], self.objDict[dst], self.msgDict[2])
        elif ucOpc == MSC.HDR_TYPE_EVT:
            # Check if object needs to be added
            src = (pkt[2] ,pkt[3])
            self.AddObj([src])
            # Display Banner (if required)
            self.disp.Banner()
            # Display Event
            self.disp.Event(len(self.objDict), self.objDict[src], self.msgDict[2])
        elif ucOpc == MSC.HDR_TYPE_STA:
            # Check if object needs to be added
            src = (pkt[2] ,pkt[3])
            self.AddObj([src])
            # Display Banner (if required)
            self.disp.Banner()
            # Display State
            self.disp.State(len(self.objDict), self.objDict[src], self.msgDict[2])
        elif ucOpc == MSC.HDR_TYPE_TP:
            self.disp.TestPt(pkt[2], pkt[3], 0)


import datetime
def stamp():
    return str(datetime.datetime.now()) + " "

def main():
    print "----MSC Demo----"
    disp = DispTerm(20, stamp)

    # Test Display Features
    print "Display Test [Start]"
    disp.SetObjList([ "ModA", "ModB", "ModC", "ModD" ])
    disp.Message(4, 0, 1,    "MsgA")
    disp.Message(4, 1, 2, "MsgB")
    disp.Message(4, 2, 2, "MsgSelf")
    disp.Message(4, 0, 3, "MsgC")
    disp.Message(4, 3, 0, "MsgD")
    disp.Message(4, 2, 1, "MsgE")
    disp.Message(4, 1, 0, "MsgF")
    disp.Event(4, 0, "Async EvtA")
    disp.Event(4, 2, "Async EvtB")
    disp.Event(4, 3, "Async EvtC")
    disp.State(4, 1, "StateA")
    disp.State(4, 3, "StateB")
    disp.State(4, 2, "StateC")
    disp.Destroy(4, 1)
    print "Display Test [End]\n"

    msc = MSC(disp)
    # Step 1: Pull the Modules from the system
    msc.RegisterMod(0, "ModA")
    msc.RegisterMod(1, "ModB")
    msc.RegisterMod(2, "ModC")

    # Step 2: Pull the messages from the system
    msc.RegisterMsg(0, "MsgA")
    msc.RegisterMsg(1, "MsgB")
    msc.RegisterMsg(2, "MsgC")
    msc.RegisterMsg(3, "MsgD")
    msc.RegisterMsg(4, "MsgE")
    msc.RegisterMsg(5, "MsgF")

    # Step 3: Generate Messages and parse it
    print "Packet Parse Test [Start]"
    pkt = msc.BuildPkt(MSC.HDR_TYPE_MSG, 0, 0, 2, 8, 1, 10)
    msc.Parse(pkt)
    pkt = msc.BuildPkt(MSC.HDR_TYPE_MSG, 0, 1, 2, 9, 1, 11)
    msc.Parse(pkt)
    pkt = msc.BuildPkt(MSC.HDR_TYPE_MSG, 0, 2, 2, 9, 2, 9)
    msc.Parse(pkt)
    pkt = msc.BuildPkt(MSC.HDR_TYPE_MSG, 0, 3, 1, 11, 2, 8)
    msc.Parse(pkt)
    pkt = msc.BuildPkt(MSC.HDR_TYPE_MSG, 0, 4, 1, 10, 2, 9)
    msc.Parse(pkt)
    pkt = msc.BuildPkt(MSC.HDR_TYPE_MSG, 0, 0, 2, 8, 1, 10)
    msc.Parse(pkt)
    pkt = msc.BuildPkt(MSC.HDR_TYPE_STA, 0, 1, 1, 10)
    msc.Parse(pkt)
    pkt = msc.BuildPkt(MSC.HDR_TYPE_EVT, 0, 2, 1, 11)
    msc.Parse(pkt)
    pkt = msc.BuildPkt(MSC.HDR_TYPE_EVT, 0, 3, 2, 8)
    msc.Parse(pkt)
    print "Packet Parse Test [End]"

if __name__ == "__main__":
    main()
