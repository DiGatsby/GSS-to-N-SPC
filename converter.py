DEBUG = 0

songs = [
    ["start", 25956, 3353, "DAEF9"],
    ["story", 25888, 4300, "D9D9D"],
    ["normal scoreboard", 25938, 2005, "DC29D"],
    ["final scoreboard", 25980, 3379, "DCFC3"],
    ["dance", 25878, 4400, "D78A5"]
]

for i, song in enumerate(songs):
    print str(i) + ": " + song[0]

song = songs[int(raw_input("SONG>>"))]
adr_offset_raw = raw_input("DATA OFFSET (DEC)>>")
adr_offset = int(adr_offset_raw)
#nspc_ref_adr_raw = raw_input("NSPC START ADR (DEC)>>")
nspc_ref_adr = song[1] + adr_offset #int(nspc_ref_adr_raw) + adr_offset


read_adr = -1
write_adr = -1
data_to_read_raw = raw_input("GSS DATA>>")
data_to_read = []
for hx in data_to_read_raw.split():
    data_to_read.append(int(hx, 16))

#print "DATA TO READ: " + str(data_to_read)

converted_data = []
current_channel = -1

def firstPass():
    global data_to_read, read_adr, DEBUG

    newChannel()
    
    note_length = 0
    note_offset = 0
    long_delay_after_note = False
    while read_adr < len(data_to_read) - 1:
        b = readByte()     
        
        # Note
        if (b >= 149 and b <= 245):
            if (DEBUG):
                print "READ: " + str(b) + " Note"
            note = b
            # If keyoff.. else apply conversion and offset
            if (note == 245):
                note = 201 # C9
            else:
                note = b - 34 + note_offset + 12
                
            last_note_length = note_length
            note_length = readByte()
            if (note_length <= 127):
                if (last_note_length == note_length):
                    writeBytes([note])
                else:
                    writeBytes([note_length, 127, note])
            else:
                print "WARNING: After note there's byte " + str(note_length)
        # Set volume
        elif (b == 247):
            if (DEBUG):
                print "READ: " + str(b) + " Volume"
            vol = readByte()           
            vol = remap(vol, 1, 127, 76, 255) 
            writeBytes([237, vol])
        # Set instrument
        elif (b == 254):
            if (DEBUG):
                print "READ: " + str(b) + " Instrument"
            ins = readByte() - 8
            note_offset = getNoteOffset(ins)

            writeBytes([224, ins])
        # Small delay
        elif (b <= 127):
            if (DEBUG):
                print "READ: " + str(b) + " Delay"
            last_note_length = note_length
            note_length = b

            if (last_note_length == note_length):
                writeBytes([200])
            else:
                writeBytes([note_length, 127, 200])
        # Loop, treat as ch end
        elif (b == 255):
            if (DEBUG):
                print "READ: " + str(b) + " Loop"
            readByte() # Don't need the loop addresses
            readByte()
            writeBytes([0]) # Channel ends here
            # If not end of data, start writing new channel
            if (read_adr < len(data_to_read) - 1):
                last_note_length = 0
                note_length = 0
                newChannel()
        else:
            print "WARNING: Skipped byte " + str(b)

def newChannel():
    global converted_data
    global current_channel
    current_channel = current_channel + 1
    print "Writing to channel " + str(current_channel)
    converted_data.append([237, 255]) # [237, 255]

def readByte():
    global data_to_read
    global read_adr
    read_adr = read_adr + 1
    return data_to_read[read_adr]

def writeBytes(_b):
    global write_adr
    global converted_data
    global current_channel
    write_adr = write_adr + 1
    #print "Write: " + str(_b)
    converted_data[current_channel].extend(_b)

def getTwoByteValue(_b1, _b2):
    hx1 = hex(_b1)[2:]
    if (len(hx1) == 1):
        hx1 = "0" + hx1
    hx2 = hex(_b2)[2:]
    if (len(hx2) == 1):
        hx2 = "0" + hx2
    return int(hx2 + hx1, 16)

def getTwoHex(_dec):
    hx = hex(_dec)[2:]
    #print "hx: " + hx
    if (len(hx) != 4):
        print "You're doing something odd with getTwoHex function."
    hx = hx[2:4] + " " + hx[0:2]
    return hx

def getNoteOffset(_ins):
    _note_offset = "ERR"
    if (_ins >= 1 and _ins <= 3):
        _note_offset = -15
    elif (_ins >= 4 and _ins <= 6):
        _note_offset = -19
    elif (_ins >= 7 and _ins <= 8):
        _note_offset = -7
    elif (_ins >= 9 and _ins <= 12):
        _note_offset = -13
    elif (_ins >= 13 and _ins <= 14):
        _note_offset = -22
    elif (_ins >= 15 and _ins <= 18):
        _note_offset = -7
    elif (_ins >= 19 and _ins <= 22):
        _note_offset = -12
    elif (_ins >= 23 and _ins <= 24):
        _note_offset = -12
    elif (_ins >= 25 and _ins <= 27):
        _note_offset = -22 # 2
    elif (_ins >= 28 and _ins <= 31):
        _note_offset = -12
    elif (_ins >= 32 and _ins <= 36):
        _note_offset = 12
    elif (_ins >= 37 and _ins <= 39):
        _note_offset = -23
    elif (_ins >= 40 and _ins <= 43):
        _note_offset = 0
    elif (_ins >= 44 and _ins <= 48):
        _note_offset = -12
    elif (_ins >= 49 and _ins <= 52):
        _note_offset = -12
    elif (_ins >= 53 and _ins <= 56):
        _note_offset = -11
    elif (_ins >= 57 and _ins <= 60):
        _note_offset = -6 # 3
    elif (_ins >= 61 and _ins <= 61):
        _note_offset = -12
    elif (_ins >= 62 and _ins <= 65):
        _note_offset = -12
    elif (_ins >= 66 and _ins <= 67):
        _note_offset = -23
    elif (_ins >= 68 and _ins <= 68):
        _note_offset = -20
    elif (_ins >= 69 and _ins <= 73):
        _note_offset = -23
    elif (_ins >= 74 and _ins <= 77):
        _note_offset = -23
    else:
        print "ERROR: Not an instrument " + str(_ins)
    return _note_offset

def remap( x, oMin, oMax, nMin, nMax ):

    #range check
    if oMin == oMax:
        print "Warning: Zero input range"
        return None

    if nMin == nMax:
        print "Warning: Zero output range"
        return None

    #check reversed input range
    reverseInput = False
    oldMin = min( oMin, oMax )
    oldMax = max( oMin, oMax )
    if not oldMin == oMin:
        reverseInput = True

    #check reversed output range
    reverseOutput = False   
    newMin = min( nMin, nMax )
    newMax = max( nMin, nMax )
    if not newMin == nMin :
        reverseOutput = True

    portion = (x-oldMin)*(newMax-newMin)/(oldMax-oldMin)
    if reverseInput:
        portion = (oldMax-x)*(newMax-newMin)/(oldMax-oldMin)

    result = portion + newMin
    if reverseOutput:
        result = newMax - portion

    return result


# Compress rate could be higher but this was fine for the KDCGG project
compressed_data = []
add_to_beginning = ""
def compress():
    global converted_data, nspc_ref_adr, compressed_data, add_to_beginning

    compress_list = []
    
    ch_num = 0
    for ch in converted_data:
        ch_grouped = []
        _adr = 0
        while 1:
            # Channel end
            if (ch[_adr] == 0):
                ch_grouped.append([ch[_adr]])
                break
            # Note parameter, group next parameter and note
            elif (ch[_adr] <= 127):
                ch_grouped.append([ch[_adr], ch[_adr+1], ch[_adr+2]])
                _adr = _adr + 2 # 2 params
            # Notes without parameters are allowed
            elif (ch[_adr] >= 128 and ch[_adr] <= 201):
               ch_grouped.append([ch[_adr]])
            # Set volume and instrument, both take 1 parameter
            elif (ch[_adr] == 224 or ch[_adr] == 237):
                ch_grouped.append([ch[_adr], ch[_adr+1]])
                _adr = _adr + 1
            else:
                print "WARNING: Unexpected byte " + str(ch[_adr])
            _adr = _adr + 1
            #print "uck?" + str(_adr)


        ch_hex_str = getDataAsHexString(converted_data[ch_num])
        item_i = 0
        while item_i < len(ch_grouped):
            compare1 = getDataAsHexString(ch_grouped[item_i])
            
            # Command occurs in data more than once
            count = ch_hex_str.count(compare1)
            if (count > 1):
                stop = False
                # Calculate space save. Original size (length * count) - Jump sizes (4 * count) + length of 1 original
                original_size = len(compare1.split(" ")) * count
                compressed_size = len(compare1.split(" ")) + 4 * count

                percentage = compressed_size / float(original_size)

                longest_str = compare1
                tries = 0
                loops = 0
                while (stop == False):
                    loops = loops + 1
                    if (item_i + loops >= len(ch_grouped)):
                        #print "humm?"
                        item_i = item_i + loops
                        break
                    if (ch_grouped[item_i][0] == 0):
                        break
                    compare1 = compare1 + getDataAsHexString(ch_grouped[item_i + loops])
                    #print "comp: " + compare1
                    #print "compare1: " + compare1 + " > count: " + str(ch_hex_str.count(compare1))
                    count = ch_hex_str.count(compare1)
                    original_size = len(compare1.split(" ")) * count
                    compressed_size = len(compare1.split(" ")) + 4 * count
                    new_percentage = compressed_size / float(original_size)
                    if (new_percentage < percentage and new_percentage < 1): #(ch_hex_str.count(compare1) >= count or len(compare1) < 6 * 3):
                        longest_str = compare1
                        #print "This " + compare1 + " has size percent of " + str(new_percentage)
                        percentage = new_percentage
                        stop = False
                    else:
                        tries = tries + 1
                    if (tries > 6):
                        if (percentage > 1):
                            #print "FUCK"
                            item_i = item_i
                        break
                    
                if (percentage < 1):
                    item_i = item_i + loops

                    compress_list.append(longest_str)
                    
                    count = ch_hex_str.count(longest_str)
                    #print "longest: " + longest_str + " count: " + str(count)
            item_i = item_i + 1
        ch_num = ch_num + 1

    ch_num = 0
    for ch in converted_data:
        ch_hex_str = getDataAsHexString(converted_data[ch_num])
        for compress_str in compress_list:
            if (ch_hex_str.find(compress_str) != -1):
                ch_hex_str = ch_hex_str.replace(compress_str, "EF " + getTwoHex(nspc_ref_adr + len(add_to_beginning.split(" ")) - 1) + " 01 ")
                add_to_beginning = add_to_beginning + compress_str + "00 "
                
        compressed_data.append(ch_hex_str.strip().split())
        ch_num = ch_num + 1
    #compr = add_to_beginning + compr
    #print "beginning: " + add_to_beginning
    #print "compressed: " + str(compressed_data)
    #print "len: " + str(len(compr.split(" ")))

def getDataAsHexString(_data):
    _hex_str = ""
    for _dec in _data:
        _hx = hex(_dec)[2:]
        if (len(_hx) == 1):
            _hx = "0" + _hx
        _hex_str = _hex_str + _hx + " "
    return _hex_str
        
def init():
    firstPass()

init()
print ""
#print str(converted_data)
print ""
hex_str = "fa 42 e7 52 e5 af " # e5 af sounds fine but scoreboard uses e5 cd


#ch_adrs = [ch_data_start_adr]
no_compress = True
if (no_compress):
    ch_str = getTwoHex(nspc_ref_adr) + " "
    for ch in converted_data:
        for dec in ch:
            hx = hex(dec)[2:]
            if (len(hx) == 1):
                hx = "0" + hx
            hex_str = hex_str + hx + " "
        
        #hex_str = hex_str + "EF " + getTwoHex(ch_data_start_adr + len(hex_str.split()) + 4) + " FF C8 00 "
        #ch_adrs.append(ch_data_start_adr + len(hex_str.split()))
        ch_str = ch_str + getTwoHex(nspc_ref_adr + len(hex_str.split())) + " "
    #ch_adrs = ch_adrs[:-1]25

if (len(hex_str.split()) + adr_offset > song[2]):
    print "Data doesn't fit (" + str(len(hex_str.split()) + adr_offset) + "), compress"
    compress()
    hex_str = "fa 42 e7 52 e5 af "
    nspc_ref_adr = nspc_ref_adr + len(add_to_beginning.split(" ")) - 1
    ch_str = getTwoHex(nspc_ref_adr) + " "
    for ch in compressed_data: #converted_data
        for hx in ch:
            hex_str = hex_str + hx + " "
        
        #hex_str = hex_str + "EF " + getTwoHex(ch_data_start_adr + len(hex_str.split()) + 4) + " FF C8 00 "
        #ch_adrs.append(ch_data_start_adr + len(hex_str.split()))
        ch_str = ch_str + getTwoHex(nspc_ref_adr + len(hex_str.split())) + " "
    #ch_adrs = ch_adrs[:-1]
    hex_str = add_to_beginning + hex_str


#print str(ch_adrs)
print ch_str
print hex_str
print ""
print "Length of gss data: " + str(len(data_to_read))
print "Length of kdc data: " + str(len(hex_str.split()) + adr_offset) + " (Max: " + str(song[2]) + ")"
print "kdc address: " + song[3]
