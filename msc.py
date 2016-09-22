#!/usr/python
"""
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

# Colors
MSC_COLOR_RED = ("\033[1;31m", "\033[0m")
MSC_COLOR_GRN = ("\033[1;32m", "\033[0m")
MSC_COLOR_YEL = ("\033[1;33m", "\033[0m")
MSC_COLOR_BLU = ("\033[1;34m", "\033[0m")
MSC_COLOR_MAG = ("\033[1;35m", "\033[0m")
MSC_COLOR_CYN = ("\033[1;36m", "\033[0m")
MSC_COLOR_NONE = ("", "")

class DispWeb:
    ''' Class providing API for displaying in https://www.websequencediagrams.com/
    '''
    def __init__(self, linesPerPage=LINES_PER_PAGE, prefix="", stdout=None):
        ''' Initialize the display
        linesPerPage[in] - Sets the number of rows before printing a new banner
        prefix[in] - Prefix String or callable function to generate prefix string
        stdout[in] - Can be overwritten to a file or stdout
        '''
        self.stdout = stdout if stdout is not None else sys.stdout
        self.objList = []
        self.objCnt = len(self.objList)

    def SetObjList(self, objList):
        '''
        '''
        self.objList = objList
        self.objCnt = len(self.objList)

    def Banner(self, isRequired=False):
        ''' Displays the object banner after a number of lines or when the objList changes
        '''
        pass

    def Message(self, srcId, dstId, msgStr, color=MSC_COLOR_NONE):
        ''' Displays a message line from the src to dst object's life line
        '''
        self.stdout.write('"%s"->"%s":%s\n' % (self.objList[srcId], self.objList[dstId], msgStr))

    def Event(self, objId, msgStr, color=MSC_COLOR_NONE):
        ''' Displays a asynchronous event to an object's life line
        '''
        self.stdout.write('-->"%s":%s\n' % (self.objList[objId], msgStr))

    def State(self, objId, stateStr, color=MSC_COLOR_NONE):
        ''' Displays a state change in an object's life line
        '''
        self.stdout.write('state over "%s":%s\n' % (self.objList[objId], stateStr))

    def Create(self, srcId, dstId, msgStr, color=MSC_COLOR_NONE):
        ''' Displays a message line from the src to created object's life line
        '''
        self.stdout.write('"%s"->*"%s":%s\n' % (self.objList[srcId], self.objList[dstId], msgStr))

    def Destroy(self, objId, color=MSC_COLOR_NONE):
        ''' Displays a destroy of an object's life line
        '''
        self.stdout.write('destroy "%s"\n' % self.objList[objId])

    def TestPt(self, objId, msgStr, color=MSC_COLOR_NONE):
        self.stdout.write('note right of "%s":%s\n' % (self.objList[objId], msgStr))


class DispTerm:
    ''' Class providing API for displaying ASCII formatted MSC symbols to stdout
    '''
    # These are the display tiles used to draw the MSC graphic symbols
    # The WIDTH can be configured and controls the center spacing
    TILES = {
        "CEN" : " " * WIDTH     +  " | " + " " * WIDTH,  # 0 CENTER: "   |   "
        "LFA" : " " * WIDTH     +  " |<" + "-" * WIDTH,  # 1 LF ARR: "   |<--"
        "LFE" : "-" * WIDTH     +  "-| " + " " * WIDTH,  # 2 LF END  "---|   "
        "RTA" : "-" * WIDTH     +  ">| " + " " * WIDTH,  # 3 RT ARR: "-->|   "
        "RTE" : " " * WIDTH     +  " |-" + "-" * WIDTH,  # 4 RT END: "   |---"
        "THR" : "-" * WIDTH     +  "---" + "-" * WIDTH,  # 5 THRU:   "-------"
        "SLF" : " " * WIDTH     +  " |}" + " " * WIDTH,  # 6 SELF    "   |}  "
        "STA" : " " * WIDTH     +  "[S]" + " " * WIDTH,  # 7 STATE:  "  [S]  "
        "EVT" : "_" * WIDTH     +  "\| " + " " * WIDTH,  # 8 ASYNC:  "__\|   "
        "CR8" : "-" * (WIDTH-1) + ">[C]" + " " * WIDTH,  # 9 CREATE: "->[C]  "
        "DES" : " " * WIDTH     +  " X " + " " * WIDTH,  # A DESTROY:"   X   "
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
        self.objList = []
        self.objCnt = len(self.objList)

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
        ''' Set the object list for items to display
        #TODO: Add incremental mode in create and destroy
        '''
        self.objList = objList
        self.objCnt = len(self.objList)
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

    def Message(self, srcId, dstId, msgStr, color=MSC_COLOR_NONE):
        ''' Displays a message line from the src to dst object's life line
        '''
        # Step 1: Check the message direction and distance between srcId and dstId
        dist = dstId - srcId
        start, end = (srcId, dstId) if dist > 0 else (dstId, srcId)
        # Step 2: Print optional prefix
        line = self._GetPrefix()
        # Step 3: Fill start with life lines
        line += DispTerm.TILES["CEN"] * start
        # Add color start
        line += color[0]
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
        # Add color end
        line += color[1]
        # Step 5: Fill end
        line += DispTerm.TILES["CEN"] * (self.objCnt - 1 - end)
        self.stdout.write(line + " : %s%s%s\n" % (color[0], msgStr, color[1]))

    def Event(self, objId, msgStr, color=MSC_COLOR_NONE):
        ''' Displays a asynchronous event to an object's life line
        '''
        # Step 1: Print optional prefix
        line = self._GetPrefix()
        # Step 2: Build the event symbols
        for idx in range(self.objCnt):
            if idx == objId:
                # Add color start
                line += color[0]
                line += DispTerm.TILES["EVT"]
                # Add color end
                line += color[1]
            else:
                line += DispTerm.TILES["CEN"]
        self.stdout.write(line + " : %s%s%s\n" % (color[0], msgStr, color[1]))

    def State(self, objId, stateStr, color=MSC_COLOR_NONE):
        ''' Displays a state change in an object's life line
        '''
        # Step 1: Print optional prefix
        line = self._GetPrefix()
        # Step 2: Build the State symbols
        for idx in range(self.objCnt):
            if idx == objId:
                # Add color start
                line += color[0]
                line += DispTerm.TILES["STA"]
                # Add color end
                line += color[1]
            else:
                line += DispTerm.TILES["CEN"]
        self.stdout.write(line + " : %s%s%s\n" % (color[0], stateStr, color[1]))

    def Create(self, srcId, dstId, msgStr, color=MSC_COLOR_NONE):
        ''' Displays a message line from the src to created object's life line
            Assume direction is to the right
        '''
        # Step 1: Check the message direction and distance between srcId and dstId
        dist = dstId - srcId
        start, end = (srcId, dstId) if dist > 0 else (dstId, srcId)
        # Step 2: Print optional prefix
        line = self._GetPrefix()
        # Step 3: Fill start with life lines
        line += DispTerm.TILES["CEN"] * start
        # Step 4: Build the message arrow
        # Generate ---> message
        # Add color start
        line += color[0]
        line += DispTerm.TILES["RTE"]
        # Add lines that are long
        if dist > 1:
            line += DispTerm.TILES["THR"] * (dist - 1)
        line += DispTerm.TILES["CR8"]
        # Add color end
        line += color[1]
        self.stdout.write(line + " : %s%s%s\n" % (color[0], msgStr, color[1]))

    def Destroy(self, objId, color=MSC_COLOR_NONE):
        ''' Displays a destroy of an object's life line
        '''
        # Step 1: Print optional prefix
        line = self._GetPrefix()
        # Step 2: Build the Destroy symbols
        for idx in range(self.objCnt):
            if idx == objId:
                # Add color start
                line += color[0]
                line += DispTerm.TILES["DES"]
                # Add color end
                line += color[1]
            else:
                line += DispTerm.TILES["CEN"]
        self.stdout.write(line + " X %s%s%s\n" % (color[0], self.objList[objId], color[1]))

    def TestPt(self, objId, msgStr, color=MSC_COLOR_NONE):
        # Step 1: Print optional prefix
        line = self._GetPrefix()
        # Step 2: Build the test point symbols
        #TODO: Add testpoint generation
        self.stdout.write(line + " : %s%s%s\n" % (color[0], msgStr, color[1]))


class MSC(object):
    '''
    The MSC class parses the MSC messages generated from a target device which are
    filtered and displayed

    The MSC format is as follows:
    typedef struct
    {
        uint8_t ucOpc : 5;      // Message Code (MSG:0, EVT:1, STA:2, TP:3, ACK:4)
        uint8_t ucPri : 3;      // Priority (0x01 - Start of Sequence, 0x02 - Sequential, 0x04 - Alert)
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
        uint16_t usEvtId;       // Event Id
    } MSC_EVT_t;

    typedef struct
    {
        MSC_HDR_t xHdr;
        uint8_t ucMod;          // Module
        uint8_t ucId;           // ID of Module Instance
        uint16_t usState;       // State Id
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
        self.objList = []

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

    def BuildPkt(self, ucPri, ucOpc, msgId, srcMod, srcId, dstMod=0, dstId=0):
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
                idx = len(self.objList)
                self.objDict[key] = idx
                self.objList.append(key)
                isChanged = True
        if isChanged:
            objList = []
            for key in self.objList:
               objList.append("%x:%s" % (ord(key[1]), self.modDict[ord(key[0])]))
            # Set display's object list
            self.disp.SetObjList(objList)
        return isChanged

    def DelObj(self, key):
        ''' Removes the object from MSC
        '''
        if key in self.objDict:
            self.objDict[key]
            self.objList.remove(key)
            # Refresh dictionary
            for idx, key in enumerate(self.objList):
                self.objDict[key] = idx
            # Set display's object list
            objList = []
            for key in self.objList:
               objList.append("%x:%s" % (ord(key[1]), self.modDict[ord(key[0])]))
            self.disp.SetObjList(objList)

    def Parse(self, pkt):
        ''' Parses the incoming MSC protocol packet then displays
        '''
        #TODO: Add Packet Filter Here
        # Set color highlight
        ucPri = (ord(pkt[0]) >> MSC.HDR_PRI_SHF) & MSC.HDR_PRI_MSK
        if ucPri == MSC.HDR_PRI_SOS:
            color = MSC_COLOR_CYN
        elif ucPri == MSC.HDR_PRI_SEQ:
            color = MSC_COLOR_BLU
        elif ucPri == MSC.HDR_PRI_ALT:
            color = MSC_COLOR_RED
        else:
            color = MSC_COLOR_NONE
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
            self.disp.Message(self.objDict[src], self.objDict[dst], self.msgDict[2], color)
        elif ucOpc == MSC.HDR_TYPE_EVT:
            # Check if object needs to be added
            src = (pkt[2] ,pkt[3])
            self.AddObj([src])
            # Display Banner (if required)
            self.disp.Banner()
            # Display Event
            self.disp.Event(self.objDict[src], self.msgDict[2], color)
        elif ucOpc == MSC.HDR_TYPE_STA:
            # Check if object needs to be added
            src = (pkt[2] ,pkt[3])
            self.AddObj([src])
            # Display Banner (if required)
            self.disp.Banner()
            # Display State
            self.disp.State(self.objDict[src], self.msgDict[2], color)
        elif ucOpc == MSC.HDR_TYPE_TP:
            self.disp.TestPt(pkt[2], pkt[3], 0, color)


import datetime
def stamp():
    return str(datetime.datetime.now()) + " "

def main():
    ''' MSC Demo
    The following MSC demo shows the MSC protocol and display features
    Currently there is support for a Terminal base output and a Web UI
        DispTerm is designed for a live capture and post analysis
        DispWeb uses https://www.websequencediagrams.com/ which is for post analysis
    '''
    print "======== MSC Demo ========"
    print "Generate Raw Data"
    msc = MSC(DispTerm())
    pkts = []
    pkts.append(msc.BuildPkt(0,               MSC.HDR_TYPE_MSG, 0, 2, 8, 1, 10))
    pkts.append(msc.BuildPkt(MSC.HDR_PRI_SOS, MSC.HDR_TYPE_MSG, 1, 2, 9, 1, 11))
    pkts.append(msc.BuildPkt(MSC.HDR_PRI_SEQ, MSC.HDR_TYPE_MSG, 2, 2, 9, 2, 9))
    pkts.append(msc.BuildPkt(MSC.HDR_PRI_SEQ, MSC.HDR_TYPE_MSG, 3, 1, 11, 2, 8))
    pkts.append(msc.BuildPkt(MSC.HDR_PRI_SEQ, MSC.HDR_TYPE_MSG, 4, 1, 10, 2, 9))
    pkts.append(msc.BuildPkt(0,               MSC.HDR_TYPE_MSG, 0, 2, 8, 1, 10))
    pkts.append(msc.BuildPkt(0,               MSC.HDR_TYPE_STA, 1, 1, 10))
    pkts.append(msc.BuildPkt(MSC.HDR_PRI_ALT, MSC.HDR_TYPE_EVT, 2, 1, 11))
    pkts.append(msc.BuildPkt(MSC.HDR_PRI_ALT, MSC.HDR_TYPE_EVT, 3, 2, 8))
    for pkt in pkts:
        print binascii.hexlify(pkt)

    # Run through the demo using different Display types
    for disp in [DispTerm(20, stamp), DispWeb()]:
        # Test Display Features
        print "----Display Test [Start]----"
        disp.SetObjList([ "ModA", "ModB", "ModC", "ModD" ])
        disp.Message(0, 1, "MsgA")
        disp.Message(1, 2, "MsgB", MSC_COLOR_BLU)
        disp.Message(2, 2, "MsgSelf", MSC_COLOR_RED)
        disp.Message(0, 3, "MsgC")
        disp.Message(3, 0, "MsgD", MSC_COLOR_GRN)
        disp.Message(2, 1, "MsgE")
        disp.Message(1, 0, "MsgF")
        disp.Event(0, "Async EvtA")
        disp.Event(2, "Async EvtB")
        disp.Event(3, "Async EvtC")
        disp.State(1, "StateA", MSC_COLOR_MAG)
        disp.State(3, "StateB", MSC_COLOR_YEL)
        disp.State(2, "StateC")
        disp.Create(2, 3, "New Obj")
        disp.Destroy(1, MSC_COLOR_RED)
        print "----Display Test [End]----\n"

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
        print "----Packet Parse Test [Start]----"
        print "  No Filter"
        for pkt in pkts:
            msc.Parse(pkt)
        print "\n  Using Filter"
        for pkt in pkts:
            msc.Parse(pkt)
        print "----Packet Parse Test [End]----\n"

if __name__ == "__main__":
    main()
