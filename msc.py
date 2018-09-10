#!/usr/bin/python
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
LINES_PER_PAGE = 10
LEADIN = 4
WIDTH  = 6

# Colors
MSC_COLOR_NONE = 0
MSC_COLOR_RED = 1
MSC_COLOR_GRN = 2
MSC_COLOR_YEL = 3
MSC_COLOR_BLU = 4
MSC_COLOR_MAG = 5
MSC_COLOR_CYN = 6
MSC_COLOR_WHT = 7


class DispPlantUML:
    ''' Class providing API for displaying in https://www.plantuml.com/
    '''
    # These are the terminal escape codes for color
    COLOR = [
        "",           #MSC_COLOR_NONE
        "[#red]",     #MSC_COLOR_RED
        "[#green]",   #MSC_COLOR_GRN
        "[#yellow]",  #MSC_COLOR_YEL
        "[#blue]",    #MSC_COLOR_BLU
        "[#magenta]", #MSC_COLOR_MAG
        "[#cyan]",    #MSC_COLOR_CYN
    ]

    def __init__(self, linesPerPage=LINES_PER_PAGE, prefix="", stdout=None):
        ''' Initialize the display
        linesPerPage[in] - Sets the number of rows before print(ng a new banner)
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
        self.stdout.write('"%s" -%s> "%s":%s\n' % (self.objList[srcId], DispPlantUML.COLOR[color], self.objList[dstId], msgStr))

    def Event(self, objId, msgStr, color=MSC_COLOR_NONE):
        ''' Displays a asynchronous event to an object's life line
        '''
        self.stdout.write('[-%s\\ "%s":%s\n' % (DispPlantUML.COLOR[color], self.objList[objId], msgStr))

    def State(self, objId, stateStr, color=MSC_COLOR_NONE):
        ''' Displays a state change in an object's life line
        '''
        self.stdout.write('hnote over "%s":%s\n' % (self.objList[objId], stateStr))

    def Create(self, srcId, dstId, msgStr, color=MSC_COLOR_NONE):
        ''' Displays a message line from the src to created object's life line
        '''
        self.stdout.write('create %s\n' % (self.objList[dstId]))
        self.stdout.write('"%s" -%s> "%s":%s\n' % (self.objList[srcId], DispPlantUML.COLOR[color], self.objList[dstId], msgStr))

    def Destroy(self, objId, color=MSC_COLOR_NONE):
        ''' Displays a destroy of an object's life line
        '''
        self.stdout.write('destroy "%s"\n' % self.objList[objId])

    def TestPt(self, objId, msgStr, color=MSC_COLOR_NONE):
        self.stdout.write('note over "%s":%s\n' % (self.objList[objId], msgStr))


class DispMscgen:
    ''' Class providing API for displaying in https://www.plantuml.com/
    '''
    # These are the terminal escape codes for color
    COLOR = [
        "#000000",    #MSC_COLOR_NONE
        "#ff0000",    #MSC_COLOR_RED
        "#00ff00",    #MSC_COLOR_GRN
        "#ffff00",    #MSC_COLOR_YEL
        "#0000ff",    #MSC_COLOR_BLU
        "#ff00ff",    #MSC_COLOR_MAG
        "#00ffff",    #MSC_COLOR_CYN
        "#ffffff",    #MSC_COLOR_WHT
    ]
    ASYNC = "Async"

    def __init__(self, linesPerPage=LINES_PER_PAGE, prefix="", stdout=None):
        ''' Initialize the display
        linesPerPage[in] - Sets the number of rows before print(ng a new banner)
        prefix[in] - Prefix String or callable function to generate prefix string
        stdout[in] - Can be overwritten to a file or stdout
        '''
        self.lines = 0
        self.linesPerPage = linesPerPage
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
        if (self.lines % self.linesPerPage == 0) or isRequired:
            #NOTE: There is no real async event support for mscgen, so add an async event proxy
            banner = '"%s"' % self.ASYNC
            # Add objects as listed
            for obj in self.objList:
                banner += ', "%s"' % obj
            self.stdout.write(banner + ";\n")
            self.lines = 0
        self.lines += 1

    def Message(self, srcId, dstId, msgStr, color=MSC_COLOR_NONE):
        ''' Displays a message line from the src to dst object's life line
        '''
        self.stdout.write('"%s"=>>"%s" [label="%s", linecolor="%s"];\n' % (self.objList[srcId], self.objList[dstId], msgStr, self.COLOR[color]))

    def Event(self, objId, msgStr, color=MSC_COLOR_NONE):
        ''' Displays a asynchronous event to an object's life line
        '''
        self.stdout.write('"Async"->"%s" [label="%s", linecolor="%s"];\n' % (self.objList[objId], msgStr, self.COLOR[color]))

    def State(self, objId, stateStr, color=MSC_COLOR_NONE):
        ''' Displays a state change in an object's life line
        '''
        color = color if (color != MSC_COLOR_NONE) else MSC_COLOR_WHT
        self.stdout.write('"%s" rbox "%s" [label="%s", textbgcolor="%s"];\n' % (self.objList[objId], self.objList[objId], stateStr, self.COLOR[color]))

    def Create(self, srcId, dstId, msgStr, color=MSC_COLOR_NONE):
        ''' Displays a message line from the src to created object's life line
        '''
        pass

    def Destroy(self, objId, color=MSC_COLOR_NONE):
        ''' Displays a destroy of an object's life line
        '''
        pass

    def TestPt(self, objId, msgStr, color=MSC_COLOR_NONE):
        color = color if (color != MSC_COLOR_NONE) else MSC_COLOR_WHT
        self.stdout.write('"%s" note "%s" [label="%s", textbgcolor="%s"];\n' % (self.objList[objId], self.objList[objId], msgStr, self.COLOR[color]))


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
        self.stdout.write('[-->"%s":%s\n' % (self.objList[objId], msgStr))

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
        self.stdout.write('note over "%s":%s\n' % (self.objList[objId], msgStr))


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
        "VAL" : " " * WIDTH     +  " +-" + "-" * WIDTH,  # B VALUE:  "   $  "
    }

    # These are the terminal escape codes for color
    COLOR = [
        ("", ""),                  #MSC_COLOR_NONE
        ("\033[1;31m", "\033[0m"), #MSC_COLOR_RED
        ("\033[1;32m", "\033[0m"), #MSC_COLOR_GRN
        ("\033[1;33m", "\033[0m"), #MSC_COLOR_YEL
        ("\033[1;34m", "\033[0m"), #MSC_COLOR_BLU
        ("\033[1;35m", "\033[0m"), #MSC_COLOR_MAG
        ("\033[1;36m", "\033[0m"), #MSC_COLOR_CYN
    ]

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
        line += DispTerm.COLOR[color][0]
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
        line += DispTerm.COLOR[color][1]
        # Step 5: Fill end
        line += DispTerm.TILES["CEN"] * (self.objCnt - 1 - end)
        self.stdout.write(line + " : %s%s%s\n" % (DispTerm.COLOR[color][0], msgStr, DispTerm.COLOR[color][1]))

    def Event(self, objId, msgStr, color=MSC_COLOR_NONE):
        ''' Displays a asynchronous event to an object's life line
        '''
        # Step 1: Print optional prefix
        line = self._GetPrefix()
        # Step 2: Build the event symbols
        for idx in range(self.objCnt):
            if idx == objId:
                # Add color start
                line += DispTerm.COLOR[color][0]
                line += DispTerm.TILES["EVT"]
                # Add color end
                line += DispTerm.COLOR[color][1]
            else:
                line += DispTerm.TILES["CEN"]
        self.stdout.write(line + " : %s%s%s\n" % (DispTerm.COLOR[color][0], msgStr, DispTerm.COLOR[color][1]))

    def State(self, objId, stateStr, color=MSC_COLOR_NONE):
        ''' Displays a state change in an object's life line
        '''
        # Step 1: Print optional prefix
        line = self._GetPrefix()
        # Step 2: Build the State symbols
        for idx in range(self.objCnt):
            if idx == objId:
                # Add color start
                line += DispTerm.COLOR[color][0]
                line += DispTerm.TILES["STA"]
                # Add color end
                line += DispTerm.COLOR[color][1]
            else:
                line += DispTerm.TILES["CEN"]
        self.stdout.write(line + " : %s%s%s\n" % (DispTerm.COLOR[color][0], stateStr, DispTerm.COLOR[color][1]))

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
        line += DispTerm.COLOR[color][0]
        line += DispTerm.TILES["RTE"]
        # Add lines that are long
        if dist > 1:
            line += DispTerm.TILES["THR"] * (dist - 1)
        line += DispTerm.TILES["CR8"]
        # Add color end
        line += DispTerm.COLOR[color][1]
        self.stdout.write(line + " : %s%s%s\n" % (DispTerm.COLOR[color][0], msgStr, DispTerm.COLOR[color][1]))

    def Destroy(self, objId, color=MSC_COLOR_NONE):
        ''' Displays a destroy of an object's life line
        '''
        # Step 1: Print optional prefix
        line = self._GetPrefix()
        # Step 2: Build the Destroy symbols
        for idx in range(self.objCnt):
            if idx == objId:
                # Add color start
                line += DispTerm.COLOR[color][0]
                line += DispTerm.TILES["DES"]
                # Add color end
                line += DispTerm.COLOR[color][1]
            else:
                line += DispTerm.TILES["CEN"]
        self.stdout.write(line + " Destroy %s%s%s\n" % (DispTerm.COLOR[color][0], self.objList[objId], DispTerm.COLOR[color][1]))

    def TestPt(self, objId, value, color=MSC_COLOR_NONE):
        # Step 1: Print optional prefix
        line = self._GetPrefix()
        # Step 2: Fill start with life lines
        line += DispTerm.TILES["CEN"] * objId
        # Step 3: Build the value note
        # Add color start
        line += DispTerm.COLOR[color][0]
        line += DispTerm.TILES["VAL"]
        # Add lines to the note
        line += DispTerm.TILES["THR"] * (self.objCnt - 1 - objId)
        # Add color end
        line += DispTerm.COLOR[color][1]
        self.stdout.write(line + "-[ %s0x%x%s ]\n" % (DispTerm.COLOR[color][0], value, DispTerm.COLOR[color][1]))


class MSC(object):
    '''
    The MSC class parses the MSC messages generated from a target device which are
    filtered and displayed

    The MSC format is as follows:
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
            uint8_t ucId;       // ID of Module Instance
            uint8_t ucMod;      // Module
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

    [FlagsType=MSG(0)][Tag][SrcObj(2)][DstObj(2)][Message(2)]
    [Type=ACK(1)][Tag][SrcObj(2)][DstObj(2)][Message(2)]
    '''
    HDR_TYPE_MSG = 0
    HDR_TYPE_EVT = 1
    HDR_TYPE_STA = 2
    HDR_TYPE_TP  = 3
    HDR_TYPE_DES = 4
    HDR_TYPE_ACK = 5

    HDR_PRI_SOS = 1
    HDR_PRI_SEQ = 2
    HDR_PRI_ALT = 4

    HDR_OPC_SHF = 0
    HDR_OPC_LEN = 5
    HDR_OPC_MSK = (1 << HDR_OPC_LEN) - 1
    HDR_PRI_SHF = HDR_OPC_LEN
    HDR_PRI_LEN = 3
    HDR_PRI_MSK = (1 << HDR_PRI_LEN) - 1

    DEFAULT_MESSAGE = "Unknown Message(0x%04x)"

    def __init__(self, disp):
        self.disp = disp
        self.msgDict = {}
        self.modDict = {}
        self.objDict = {}
        self.objList = []
        self.filterList = []

    def RegisterMsg(self, usMsgId, strMsg):
        ''' Register the msgId with message string '''
        self.msgDict[usMsgId] = strMsg

    def RegisterMod(self, ucModId, strMod):
        ''' Register the module Id with module string '''
        # Limit max length of string for formating
        self.modDict[ucModId] = strMod[0:MAX_NAME_LEN]

    def AddFilter(self, ucFilterType, ucPri, ucOpc, msgId, srcMod, srcId):
        filterObj = (ucFilterType, ucPri, ucOpc, msgId, srcMod, srcId)
        self.filterList += filterObj

    def DelFilter(self, FilterId=None):
        self.filterList = FilterId

    def BuildPkt(self, ucPri, ucOpc, msgId, srcMod, srcId, dstMod=0, dstId=0):
        '''
        Returns a message packet based on the message type (ucOpc)
        '''
        # Step 1: Build Header
        hdr = (MSC.HDR_OPC_MSK & ucOpc) << MSC.HDR_OPC_SHF | (MSC.HDR_PRI_MSK & ucPri) << MSC.HDR_PRI_SHF
        # Step 2: Format the body
        if ucOpc == MSC.HDR_TYPE_MSG:
            body = struct.pack("<BBBBH", srcId, srcMod, dstId, dstMod, msgId)
        elif ucOpc == MSC.HDR_TYPE_EVT:
            body = struct.pack("<BBH", srcId, srcMod, msgId)
        elif ucOpc == MSC.HDR_TYPE_STA:
            body = struct.pack("<BBH", srcId, srcMod, msgId)
        elif ucOpc == MSC.HDR_TYPE_TP:
            body = struct.pack("<BBL", srcId, srcMod, msgId)
        elif ucOpc == MSC.HDR_TYPE_DES:
            body = struct.pack("<BB", srcId, srcMod)
        # Step 3: Build Packet
        pkt = chr(hdr) + chr(len(body)) + str(body)
        # print binascii.hexlify(pkt)
        return pkt

    def AddObj(self, keyList):
        ''' Adds object(s) to MSC and assign it a position
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
               objList.append("%x:%s" % (ord(key[0]), self.modDict.get(ord(key[1]), "UNK(%d)" % ord(key[1]))))
            # Set display's object list
            self.disp.SetObjList(objList)
        return isChanged

    def DelObj(self, key):
        ''' Removes the object from MSC
        '''
        if key in self.objDict:
            self.objDict.pop(key, None)
            self.objList.remove(key)
            # Refresh dictionary
            for idx, key in enumerate(self.objList):
                self.objDict[key] = idx
            # Set display's object list
            objList = []
            for key in self.objList:
               objList.append("%x:%s" % (ord(key[0]), self.modDict.get(ord(key[1]), "UNK(%d)" % ord(key[1]))))
            self.disp.SetObjList(objList)

    def Parse(self, pkt):
        ''' Parses the incoming MSC protocol packet then displays
        '''
        hdr = ord(pkt[0])
        #ucLen = ord(pkt[1])
        #TODO: Add Packet Filter Here
        # Set color highlight
        ucPri = (hdr >> MSC.HDR_PRI_SHF) & MSC.HDR_PRI_MSK
        if ucPri == MSC.HDR_PRI_SOS:
            color = MSC_COLOR_CYN
        elif ucPri == MSC.HDR_PRI_SEQ:
            color = MSC_COLOR_BLU
        elif ucPri == MSC.HDR_PRI_ALT:
            color = MSC_COLOR_RED
        else:
            color = MSC_COLOR_NONE
        # Print the packet type
        ucOpc = hdr & MSC.HDR_OPC_MSK
        if ucOpc == MSC.HDR_TYPE_MSG:
            # [HDR(2)][SrcObj(2)][DstObj(2)][Message(2)]
            src = pkt[2:4]
            dst = pkt[4:6]
            msg = pkt[6:8]
            # Check if object needs to be added
            self.AddObj([src, dst])
            # Display Banner (if required)
            self.disp.Banner()
            # Display Message
            msg = struct.unpack("<H", msg)[0]
            self.disp.Message(self.objDict[src], self.objDict[dst], self.msgDict.get(msg, MSC.DEFAULT_MESSAGE % msg), color)
        elif ucOpc == MSC.HDR_TYPE_EVT:
            # [HDR(2)][SrcObj(2)][Message(2)]
            src = pkt[2:4]
            msg = pkt[4:6]
            # Check if object needs to be added
            self.AddObj([src])
            # Display Banner (if required)
            self.disp.Banner()
            # Display Event
            msg = struct.unpack("<H", msg)[0]
            self.disp.Event(self.objDict[src], self.msgDict.get(msg, MSC.DEFAULT_MESSAGE % msg), color)
        elif ucOpc == MSC.HDR_TYPE_STA:
            # [HDR(2)][SrcObj(2)][State(2)]
            src = pkt[2:4]
            msg = pkt[4:6]
            # Check if object needs to be added
            self.AddObj([src])
            # Display Banner (if required)
            self.disp.Banner()
            # Display State
            msg = struct.unpack("<H", msg)[0]
            self.disp.State(self.objDict[src], self.msgDict.get(msg, MSC.DEFAULT_MESSAGE % msg), color)
        elif ucOpc == MSC.HDR_TYPE_TP:
            # [HDR(2)][SrcObj(2)][Value(4)]
            src = pkt[2:4]
            value = pkt[4:]
            # Display Value
            if src in self.objDict:
                value = struct.unpack("<L", value)[0]
                self.disp.TestPt(self.objDict[src], value, color)
            else:
                print("unknown src:", src)
        elif ucOpc == MSC.HDR_TYPE_DES:
            # [HDR(2)][SrcObj(2)]
            src = pkt[2:4]
            if src in self.objDict:
                self.disp.Destroy(self.objDict[src], color)
                self.DelObj(src)
                # Display Banner (if required)
                self.disp.Banner()
            else:
                print("unknown src:", src)


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
    print("======== MSC Demo ========")
    print("Generate Raw Data")
    msc = MSC(DispTerm())
    pkts = []
    pkts.append(msc.BuildPkt(0,               MSC.HDR_TYPE_MSG, 0, 2, 8, 1, 10))
    pkts.append(msc.BuildPkt(0,               MSC.HDR_TYPE_MSG, 0, 1, 10, 2, 8))
    pkts.append(msc.BuildPkt(MSC.HDR_PRI_SOS, MSC.HDR_TYPE_MSG, 1, 2, 9, 1, 11))
    pkts.append(msc.BuildPkt(MSC.HDR_PRI_SEQ, MSC.HDR_TYPE_MSG, 2, 2, 9, 2, 9))
    pkts.append(msc.BuildPkt(MSC.HDR_PRI_SEQ, MSC.HDR_TYPE_MSG, 3, 1, 11, 2, 8))
    pkts.append(msc.BuildPkt(MSC.HDR_PRI_SEQ, MSC.HDR_TYPE_MSG, 4, 1, 10, 2, 9))
    pkts.append(msc.BuildPkt(0,               MSC.HDR_TYPE_MSG, 0, 2, 8, 1, 10))
    pkts.append(msc.BuildPkt(0,               MSC.HDR_TYPE_STA, 1, 1, 10))
    pkts.append(msc.BuildPkt(0,               MSC.HDR_TYPE_TP,  0x12345678, 1, 10))
    pkts.append(msc.BuildPkt(0,               MSC.HDR_TYPE_DES, 0, 1, 10))
    pkts.append(msc.BuildPkt(MSC.HDR_PRI_ALT, MSC.HDR_TYPE_EVT, 2, 1, 11))
    pkts.append(msc.BuildPkt(MSC.HDR_PRI_ALT, MSC.HDR_TYPE_EVT, 3, 2, 8))
    pkts.append(msc.BuildPkt(0,               MSC.HDR_TYPE_EVT, 0xDEAD, 2, 8))
    for pkt in pkts:
        print(binascii.hexlify(pkt))

    # Run through the demo using different Display types
    for disp in [DispTerm(20, stamp), DispWeb(), DispMscgen(), DispPlantUML()]:
        # Test Display Features
        print("----Display Test (%s) [Start]----" % disp.__class__.__name__)
        disp.SetObjList([ "ModA", "ModB", "ModC", "ModD", "ModE" ])
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
        disp.Create(2, 4, "New Obj")
        disp.State(1, "StateA", MSC_COLOR_MAG)
        disp.State(3, "StateB", MSC_COLOR_YEL)
        disp.State(2, "StateC")
        disp.TestPt(2, 0x12345678)
        disp.Destroy(1, MSC_COLOR_RED)
        print("----Display Test (%s) [End]----\n" % disp.__class__.__name__)

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
        print("----Packet Parse Test (%s) [Start]----" % disp.__class__.__name__)
        print("  No Filter")
        for pkt in pkts:
            msc.Parse(pkt)
        print("\n  Using Filter")
        for pkt in pkts:
            msc.Parse(pkt)
        print("----Packet Parse Test (%s) [End]----\n" % disp.__class__.__name__)

if __name__ == "__main__":
    main()
