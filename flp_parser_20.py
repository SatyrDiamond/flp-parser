import argparse
import varint
import struct
from io import BytesIO

parser = argparse.ArgumentParser()
parser.add_argument("input")
args = parser.parse_args()

outfile = open('output.flps', 'w')

with open('flp_eventname.txt') as f:
    lines = f.readlines()

eventtable = []
for line in lines:
    idname = line.rstrip().split()
    if len(idname) > 1:
        eventtable.append([idname[0], idname[1]])
    else:
        eventtable.append([idname[0], '_unknown'])


def readriffdata(riffbytebuffer, offset):
    if isinstance(riffbytebuffer, (bytes, bytearray)) == True:
        riffbytebuffer = bytearray2BytesIO(riffbytebuffer)
    riffobjects = []
    riffbytebuffer.seek(0,2)
    filesize = riffbytebuffer.tell()
    riffbytebuffer.seek(offset)
    while filesize > riffbytebuffer.tell():
        chunkname = riffbytebuffer.read(4)
        chunksize = int.from_bytes(riffbytebuffer.read(4), "little")
        chunkdata = riffbytebuffer.read(chunksize)
        riffobjects.append([chunkname, chunkdata])
    return riffobjects


def datablock(PatternNotes, bytesnumber):
    notelistdata = BytesIO()
    notelistdata.write(PatternNotes)
    notelistdata_filesize = notelistdata.tell()
    notelistdata.seek(0)
    while notelistdata.tell() < notelistdata_filesize:
        print('\t\t' + bytes(notelistdata.read(bytesnumber)).hex())

def parse_patternnotes(patternnotesbytes):
    notelistdata = BytesIO()
    notelistdata.write(patternnotesbytes)
    notelistdata.seek(0,2)
    notelistdata_filesize = notelistdata.tell()
    notelistdata.seek(0)
    notelist = []
    while notelistdata.tell() < notelistdata_filesize:
        print('\tNote:')
        print('\t\tPosition:',int.from_bytes(notelistdata.read(4), "little"))
        print('\t\tFlags:',int.from_bytes(notelistdata.read(2), "little"))
        print('\t\tRackChannel:',int.from_bytes(notelistdata.read(2), "little"))
        print('\t\tDuration:',int.from_bytes(notelistdata.read(4), "little"))
        print('\t\tKey:',int.from_bytes(notelistdata.read(4), "little"))
        print('\t\tFinePitch:',int.from_bytes(notelistdata.read(1), "little"))
        print('\t\tUnknown:',int.from_bytes(notelistdata.read(1), "little"))
        print('\t\tRelease:',int.from_bytes(notelistdata.read(1), "little"))
        print('\t\tMIDIChannel:',int.from_bytes(notelistdata.read(1), "little"))
        print('\t\tPan:',int.from_bytes(notelistdata.read(1), "little"))
        print('\t\tVelocity:',int.from_bytes(notelistdata.read(1), "little"))
        print('\t\tModX:',int.from_bytes(notelistdata.read(1), "little"))
        print('\t\tModY:',int.from_bytes(notelistdata.read(1), "little"))

def parse_FLTrack(trackdata):
    fltrackdata = BytesIO()
    fltrackdata.write(trackdata)
    fltrackdata.seek(0)
    print('\tID:',int.from_bytes(fltrackdata.read(4), "little"))
    print('\tColor:',fltrackdata.read(4).hex())
    print('\tIcon:',int.from_bytes(fltrackdata.read(4), "little"))
    print('\tEnabled:',int.from_bytes(fltrackdata.read(1), "little"))
    print('\tHeight:',struct.unpack('<f', fltrackdata.read(4))[0])
    print('\tLockedToContent:',int.from_bytes(fltrackdata.read(1), "little"))
    print('\tMotion:',int.from_bytes(fltrackdata.read(4), "little"))
    print('\tPress:',int.from_bytes(fltrackdata.read(4), "little"))
    print('\tTriggerSync:',int.from_bytes(fltrackdata.read(4), "little"))
    print('\tQueued:',int.from_bytes(fltrackdata.read(4), "little"))
    print('\tTolerant:',int.from_bytes(fltrackdata.read(4), "little"))
    print('\tPositionSync:',int.from_bytes(fltrackdata.read(4), "little"))
    print('\tGrouped:',int.from_bytes(fltrackdata.read(1), "little"))
    print('\tLocked:',int.from_bytes(fltrackdata.read(1), "little"))
    print('\tRest:',fltrackdata.read())

def parse_arr(arrdata):
    flarrdata = BytesIO()
    flarrdata.write(arrdata)
    flarrdata.seek(0,2)
    flarrdata_filesize = flarrdata.tell()
    flarrdata.seek(0)
    while flarrdata.tell() < flarrdata_filesize:
        print('\tItem:')
        print('\t\tPosition:',int.from_bytes(flarrdata.read(4), "little"))
        print('\t\tPatternBase:',int.from_bytes(flarrdata.read(2), "little"))
        print('\t\tItemIndex:',int.from_bytes(flarrdata.read(2), "little"))
        print('\t\tLength:',int.from_bytes(flarrdata.read(4), "little"))
        print('\t\tTrackIndex:',int.from_bytes(flarrdata.read(4), "little"))
        print('\t\tUnknown1:',int.from_bytes(flarrdata.read(2), "little"))
        print('\t\tFlags:',int.from_bytes(flarrdata.read(2), "little"))
        print('\t\tUnknown2:',int.from_bytes(flarrdata.read(4), "little"))
        print('\t\tStartOffset:',int.from_bytes(flarrdata.read(4), "little"))
        print('\t\tEndOffset:',int.from_bytes(flarrdata.read(4), "little"))

def parse_automation(autodatabytes):
    autodata = BytesIO()
    autodata.write(autodatabytes)
    autodata.seek(0,2)
    autodata_filesize = autodata.tell()
    autodata.seek(0)
    while autodata.tell() < autodata_filesize:
        print('\tPoint:')
        print('\t\tPosition:',int.from_bytes(autodata.read(4), "little"))
        print('\t\tRackChannel:',int.from_bytes(autodata.read(1), "little")+1)
        print('\t\tControl:',autodata.read(3))
        print('\t\tValue:',autodata.read(4))

def parse_fxrouting(fxroutingbytes):
    fxroutingdata = BytesIO()
    fxroutingdata.write(fxroutingbytes)
    fxroutingdata.seek(0,2)
    fxroutingdata_filesize = fxroutingdata.tell()
    fxroutingdata.seek(0)
    fxcount = 0
    print('\tRoutes: ',end='')
    while fxroutingdata.tell() < fxroutingdata_filesize:
        fxchannel = int.from_bytes(fxroutingdata.read(1), "little")
        if fxchannel == 1:
            print(fxcount,end=' ')
        fxcount += 1 
    print()


def parse_flp_Events(riffobj):
    eventdatasize = len(riffobj)
    eventdatastream = BytesIO()
    eventdatastream.write(riffobj)
    eventdatastream.seek(0)
    outputtable = []
    while eventdatastream.tell() < int(eventdatasize):
        event_id = int.from_bytes(eventdatastream.read(1), "little")
        if event_id <= 63 and event_id >= 0: # int8
            outputtable.append([event_id,int.from_bytes(eventdatastream.read(1), "little")])
        if event_id <= 127 and event_id >= 64 : # int16
            outputtable.append([event_id,int.from_bytes(eventdatastream.read(2), "little")])
        if event_id <= 191 and event_id >= 128 : # int32
            outputtable.append([event_id,int.from_bytes(eventdatastream.read(4), "little")])
        if event_id <= 224 and event_id >= 192 : # text
            eventpartdatasize = varint.decode_stream(eventdatastream)
            eventpart = eventdatastream.read(eventpartdatasize)
            outputtable.append([event_id,eventpart])
        if event_id <= 255 and event_id >= 225 : # data
            eventpartdatasize = varint.decode_stream(eventdatastream)
            eventpart = eventdatastream.read(eventpartdatasize)
            outputtable.append([event_id,eventpart])
    return outputtable

def linearbyte2percent(inputbyteio):
    intvalue = int.from_bytes(inputbyteio.read(4), "little")
    smalltime = ((intvalue-100)/65436)*6
    outputval = smalltime * smalltime
    return intvalue

def parse_envelope(envelopebytes):
    envelopedata = BytesIO()
    envelopedata.write(envelopebytes)
    envelopedata.seek(0)
    print('\tFlags:',envelopedata.read(4))
    print('\tEnabled:',envelopedata.read(4))
    print('\tASDR PreDelay:',linearbyte2percent(envelopedata))
    print('\tASDR Attack:',linearbyte2percent(envelopedata))
    print('\tASDR Hold:',linearbyte2percent(envelopedata))
    print('\tASDR Decay:',linearbyte2percent(envelopedata))
    print('\tASDR Suspend:',int.from_bytes(envelopedata.read(4), "little")/128)
    print('\tASDR Release:',linearbyte2percent(envelopedata))
    print('\tASDR Amount:',int.from_bytes(envelopedata.read(4), "little"))
    print('\tLFO Delay:',int.from_bytes(envelopedata.read(4), "little"))
    print('\tLFO Attack:',int.from_bytes(envelopedata.read(4), "little"))
    print('\tLFO Amount:',int.from_bytes(envelopedata.read(4), "little"))
    print('\tLFO Speed:',int.from_bytes(envelopedata.read(4), "little"))
    print('\tLFO Shape:',int.from_bytes(envelopedata.read(4), "little"))
    print('\tASDR AttackTension:',int.from_bytes(envelopedata.read(4), "little"))
    print('\tASDR DecayTension:',int.from_bytes(envelopedata.read(4), "little"))
    print('\tASDR ReleaseTension:',int.from_bytes(envelopedata.read(4), "little"))

def parse_InitCtrlRecChan(inbytes):
    notelistdata = BytesIO()
    notelistdata.write(inbytes)
    notelistdata_filesize = notelistdata.tell()
    notelistdata.seek(0)
    while notelistdata.tell() < notelistdata_filesize:
        icrc_dummy = notelistdata.read(4)
        icrc_control = notelistdata.read(2)[::-1]
        icrc_group = notelistdata.read(2)[::-1]
        icrc_value = notelistdata.read(4)
        print('\t\t', 
            bytes(icrc_group).hex(), 
            bytes(icrc_control).hex(), 
            bytes(icrc_value).hex(),
            str(int.from_bytes(icrc_value, "little", signed=True)).ljust(10),
            str(struct.unpack('<f', icrc_value)[0]),
            )


fileobject = open(args.input, 'rb')
headername = fileobject.read(4)
rifftable = readriffdata(fileobject, 0)
for riffobj in rifftable:
    #print(str(riffobj[0]) + str(len(riffobj[1])))
    if riffobj[0] == b'FLhd':
        #print(riffobj[1][4:5])
        ppq = int.from_bytes(riffobj[1][4:5], "big")
    if riffobj[0] == b'FLdt':
        flpevents = parse_flp_Events(riffobj[1])

for flpevent in flpevents:
    event_id = flpevent[0]
    event_data = flpevent[1]
    if event_id == 238:
        print(lines[event_id].strip())
        parse_FLTrack(flpevent[1])
    elif event_id == 224:
        print(lines[event_id].strip())
        parse_patternnotes(flpevent[1])
    elif event_id == 223:
        print(lines[event_id].strip())
        parse_automation(flpevent[1])
    elif event_id == 233:
        print(lines[event_id].strip())
        parse_arr(flpevent[1])
    elif event_id == 218:
        print(lines[event_id].strip())
        parse_envelope(flpevent[1])

    elif event_id == 216:
        print(lines[event_id].strip())
        parse_InitCtrlRecChan(flpevent[1])

    elif event_id == 225:
        print(lines[event_id].strip())
        parse_InitCtrlRecChan(flpevent[1])

    elif event_id == 235:
        print(lines[event_id].strip())
        parse_fxrouting(flpevent[1])
    elif event_id <= 255 and event_id >= 192 : # text
        print(lines[event_id].strip())
        print('\t'+str(event_data.hex()))
    else:
        print(lines[event_id].strip()+";"+str(flpevent[1]))
