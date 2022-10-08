# SPDX-FileCopyrightText: 2022 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import varint
import argparse
import struct
from io import BytesIO

parser = argparse.ArgumentParser()
parser.add_argument("input")
args = parser.parse_args()

def create_bytesio(data):
    bytesio = BytesIO()
    bytesio.write(data)
    bytesio.seek(0,2)
    bytesio_filesize = bytesio.tell()
    bytesio.seek(0)
    return [bytesio, bytesio_filesize]

def parse_arr(arrdata):
    flarrdata = create_bytesio(arrdata)
    output = []
    while flarrdata[0].tell() < flarrdata[1]:
        placement = {}
        placement['position'] = int.from_bytes(flarrdata[0].read(4), "little")
        placement['patternbase'] = int.from_bytes(flarrdata[0].read(2), "little")
        placement['itemindex'] = int.from_bytes(flarrdata[0].read(2), "little")
        placement['length'] = int.from_bytes(flarrdata[0].read(4), "little")
        placement['trackindex'] = int.from_bytes(flarrdata[0].read(4), "little")
        placement['unknown1'] = int.from_bytes(flarrdata[0].read(2), "little")
        placement['flags'] = int.from_bytes(flarrdata[0].read(2), "little")
        placement['unknown2'] = int.from_bytes(flarrdata[0].read(4), "little")
        placement['startoffset'] = int.from_bytes(flarrdata[0].read(4), "little")
        placement['endoffset'] = int.from_bytes(flarrdata[0].read(4), "little")
        output.append(placement)
    return output

def parse_FLTrack(trackdata):
    fltrackdata = create_bytesio(trackdata)[0]
    params = {}
    params['id'] = int.from_bytes(fltrackdata.read(4), "little")
    params['color'] = fltrackdata.read(4).hex()
    params['icon'] = int.from_bytes(fltrackdata.read(4), "little")
    params['enabled'] = int.from_bytes(fltrackdata.read(1), "little")
    params['height'] = struct.unpack('<f', fltrackdata.read(4))[0]
    params['lockedtocontent'] = int.from_bytes(fltrackdata.read(1), "little")
    params['motion'] = int.from_bytes(fltrackdata.read(4), "little")
    params['press'] = int.from_bytes(fltrackdata.read(4), "little")
    params['triggersync'] = int.from_bytes(fltrackdata.read(4), "little")
    params['queued'] = int.from_bytes(fltrackdata.read(4), "little")
    params['tolerant'] = int.from_bytes(fltrackdata.read(4), "little")
    params['positionSync'] = int.from_bytes(fltrackdata.read(4), "little")
    params['grouped'] = int.from_bytes(fltrackdata.read(1), "little")
    params['locked'] = int.from_bytes(fltrackdata.read(1), "little")
    return params

def parse_fxrouting(fxroutingbytes):
    fxroutingdata = create_bytesio(fxroutingbytes)
    fxcount = 0
    routes = []
    while fxroutingdata[0].tell() < fxroutingdata[1]:
        fxchannel = int.from_bytes(fxroutingdata[0].read(1), "little")
        if fxchannel == 1:
            routes.append(fxcount)
        fxcount += 1
    return routes

def add_to_id_list(seperated_object_table, listname, listvar, number):
    numberfound = 0
    listdata = {listname: listvar}
    if seperated_object_table == []:
        seperated_object_table.append([number,listdata])
    else:
        for numberobj in seperated_object_table:
            if numberobj[0] == number:
                numberfound = 1
                numberobj[1] = numberobj[1] | listdata
        if numberfound == 0:
            seperated_object_table.append([number,listdata])

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

def parse_event(datastream):
    event_id = int.from_bytes(datastream.read(1), "little")
    if event_id <= 63 and event_id >= 0: # int8
        event_data = int.from_bytes(eventdatastream.read(1), "little")
    if event_id <= 127 and event_id >= 64 : # int16
        event_data = int.from_bytes(eventdatastream.read(2), "little")
    if event_id <= 191 and event_id >= 128 : # int32
        event_data = int.from_bytes(eventdatastream.read(4), "little")
    if event_id <= 224 and event_id >= 192 : # text
        eventpartdatasize = varint.decode_stream(datastream)
        event_data = datastream.read(eventpartdatasize)
    if event_id <= 255 and event_id >= 225 : # data
        eventpartdatasize = varint.decode_stream(datastream)
        event_data = datastream.read(eventpartdatasize)
    return [event_id, event_data]


fileobject = open(args.input, 'rb')
headername = fileobject.read(4)
rifftable = readriffdata(fileobject, 0)
for riffobj in rifftable:
    print(str(riffobj[0]) + str(len(riffobj[1])))
    if riffobj[0] == b'FLhd':
        flp_ppq = int.from_bytes(riffobj[1][4:6], "little")
        print('[input-flp] PPQ: '+ str(flp_ppq))
    if riffobj[0] == b'FLdt':
        mainevents = riffobj[1]

        global eventdatastream
        eventdatasize = len(mainevents)
        eventdatastream = BytesIO()
        eventdatastream.write(mainevents)
        eventdatastream.seek(0)

        eventtable = []
        while eventdatastream.tell() < int(eventdatasize):
            event_id = int.from_bytes(eventdatastream.read(1), "little")
            if event_id <= 63 and event_id >= 0: # int8
                event_data = int.from_bytes(eventdatastream.read(1), "little")
            if event_id <= 127 and event_id >= 64 : # int16
                event_data = int.from_bytes(eventdatastream.read(2), "little")
            if event_id <= 191 and event_id >= 128 : # int32
                event_data = int.from_bytes(eventdatastream.read(4), "little")
            if event_id <= 224 and event_id >= 192 : # text
                eventpartdatasize = varint.decode_stream(eventdatastream)
                event_data = eventdatastream.read(eventpartdatasize)
            if event_id <= 255 and event_id >= 225 : # data
                eventpartdatasize = varint.decode_stream(eventdatastream)
                event_data = eventdatastream.read(eventpartdatasize)
            eventtable.append([event_id, event_data])

FL_Main = {}
FL_Channels = []
FL_Tracks = []
FL_Patterns = []
FL_Mixer = []
for _ in range(127):
    FL_Mixer.append({})
FL_TimeMarkers = []
FL_Arrangements = []
FL_FXCreationMode = 0
T_FL_FXNum = -1

for event in eventtable:
    event_id = event[0]
    event_data = event[1]
    if event_id == 199: FL_Main['Version'] = event_data.decode('utf-8').rstrip('\x00')
    if event_id == 156: FL_Main['Tempo'] = event_data/1000
    if event_id == 194: FL_Main['Title'] = event_data.decode('utf-16le').rstrip('\x00')
    if event_id == 206: FL_Main['Genre'] = event_data.decode('utf-16le').rstrip('\x00')
    if event_id == 207: FL_Main['Author'] = event_data.decode('utf-16le').rstrip('\x00')
    if event_id == 202: FL_Main['ProjectDataPath'] = event_data.decode('utf-16le').rstrip('\x00')
    if event_id == 195: FL_Main['Comment'] = event_data.decode('utf-16le').rstrip('\x00')
    if event_id == 237: FL_Main['ProjectTime'] = event_data
    if event_id == 231: T_FL_ChanGroupName = event_data.decode('utf-16le').rstrip('\x00')




    if event_id == 65: 
        T_FL_CurrentPattern = event_data
        print('Pattern:', event_data)
    if event_id == 223: #AutomationData
        print('\\__AutomationData')
        autodata = create_bytesio(event_data)
        autopoints = []
        while autodata[0].tell() < autodata[1]:
            pointdata = {}
            pointdata['pos'] = int.from_bytes(autodata[0].read(4), "little")
            pointdata['rack'] = int.from_bytes(autodata[0].read(1), "little")+1
            pointdata['control'] = autodata[0].read(3)
            pointdata['value'] = autodata[0].read(4)
            autopoints.append(pointdata)
        add_to_id_list(FL_Patterns, 'automation', autopoints, T_FL_CurrentPattern)
    if event_id == 224: #PatternNotes
        print('\\__PatternNotes')
        fl_notedata = create_bytesio(event_data)
        notelist = []
        while fl_notedata[0].tell() < fl_notedata[1]:
            notedata = {}
            notedata['pos'] = int.from_bytes(fl_notedata[0].read(4), "little")
            notedata['flags'] = int.from_bytes(fl_notedata[0].read(2), "little")
            notedata['rack'] = int.from_bytes(fl_notedata[0].read(2), "little")+1
            notedata['dur'] = int.from_bytes(fl_notedata[0].read(4), "little")
            notedata['key'] = int.from_bytes(fl_notedata[0].read(4), "little") - 60
            notedata['finep'] = int.from_bytes(fl_notedata[0].read(1), "little")
            notedata['u1'] = int.from_bytes(fl_notedata[0].read(1), "little")
            notedata['rel'] = int.from_bytes(fl_notedata[0].read(1), "little")
            notedata['midich'] = int.from_bytes(fl_notedata[0].read(1), "little")
            notedata['pan'] = (int.from_bytes(fl_notedata[0].read(1), "little")-64)/64
            notedata['velocity'] = int.from_bytes(fl_notedata[0].read(1), "little")/128
            notedata['mod_x'] = int.from_bytes(fl_notedata[0].read(1), "little")
            notedata['mod_y'] = int.from_bytes(fl_notedata[0].read(1), "little")
            notelist.append(notedata)
        add_to_id_list(FL_Patterns, 'notes', notelist, T_FL_CurrentPattern)



    if event_id == 150: 
        hexcolor = event_data.to_bytes(4, 'little')
        color = [hexcolor[0],hexcolor[1],hexcolor[2]]
        add_to_id_list(FL_Patterns, 'color', notelist, T_FL_CurrentPattern)



    if event_id == 238: #PLTrackInfo
        FL_Tracks.append(parse_FLTrack(event_data))




    if event_id == 99: 
        T_FL_CurrentArrangement = event_data
        print('NewArrangement:', event_data)
    if event_id == 241: 
        event_text = event_data.decode('utf-16le').rstrip('\x00')
        print('\\__ArrangementName:', event_text)
        add_to_id_list(FL_Arrangements, 'name', event_text, T_FL_CurrentArrangement)
    if event_id == 233: 
        playlistitems = parse_arr(event_data)
        add_to_id_list(FL_Arrangements, 'items', playlistitems, T_FL_CurrentArrangement)


    if event_id == 148: 
        T_FL_CurrentTimeMarker = event_data
        print('NewTimeMarker:', event_data)
    if event_id == 205: 
        event_text = event_data.decode('utf-16le').rstrip('\x00')
        print('\\__TimeMarkerName:', event_text)
        add_to_id_list(FL_TimeMarkers, 'name', event_text, T_FL_CurrentTimeMarker)
    if event_id == 33: 
        print('\\__TimeMarkerNumerator:', event_data)
        add_to_id_list(FL_TimeMarkers, 'numerator', event_data, T_FL_CurrentTimeMarker)
    if event_id == 34: 
        print('\\__TimeMarkerDenominator:', event_data)
        add_to_id_list(FL_TimeMarkers, 'denominator', event_data, T_FL_CurrentTimeMarker)


    if event_id == 64: 
        T_FL_CurrentChannel = event_data
        print('Channel:', event_data)
        add_to_id_list(FL_Channels, 'group', T_FL_ChanGroupName, T_FL_CurrentChannel)
    if event_id == 21: 
        print('\\__Type:', event_data)
        add_to_id_list(FL_Channels, 'type', event_data, T_FL_CurrentChannel)



    if event_id == 38: 
        FL_FXCreationMode = 1
        T_FL_FXColor = None
        T_FL_FXIcon = None
    if FL_FXCreationMode == 0:
        if event_id == 201: 
            event_text = event_data.decode('utf-16le').rstrip('\x00')
            print('\\__DefPluginName:', event_text)
            DefPluginName = event_text
        if event_id == 212: 
            print('\\__NewPlugin')
            add_to_id_list(FL_Channels, 'plugin', DefPluginName, T_FL_CurrentChannel)
            add_to_id_list(FL_Channels, 'chandata', event_data, T_FL_CurrentChannel)
        if event_id == 203: 
            event_text = event_data.decode('utf-16le').rstrip('\x00')
            print('\\__PluginName:', event_text)
            add_to_id_list(FL_Channels, 'name', event_text, T_FL_CurrentChannel)
        if event_id == 155: add_to_id_list(FL_Channels, 'icon', event_data, T_FL_CurrentChannel)
        if event_id == 128: 
            hexcolor = event_data.to_bytes(4, 'little')
            color = [hexcolor[0],hexcolor[1],hexcolor[2]]
            add_to_id_list(FL_Channels, 'color', color, T_FL_CurrentChannel)
        if event_id == 213: add_to_id_list(FL_Channels, 'c', event_data, T_FL_CurrentChannel)
        if event_id == 0: add_to_id_list(FL_Channels, 'enabled', event_data, T_FL_CurrentChannel)
        if event_id == 209: add_to_id_list(FL_Channels, 'delay', event_data, T_FL_CurrentChannel)
        if event_id == 138: add_to_id_list(FL_Channels, 'delayreso', event_data, T_FL_CurrentChannel)
        if event_id == 139: add_to_id_list(FL_Channels, 'reverb', event_data, T_FL_CurrentChannel)
        if event_id == 89: add_to_id_list(FL_Channels, 'shiftdelay', event_data, T_FL_CurrentChannel)
        if event_id == 69: add_to_id_list(FL_Channels, 'fx', event_data, T_FL_CurrentChannel)
        if event_id == 86: add_to_id_list(FL_Channels, 'fx3', event_data, T_FL_CurrentChannel)
        if event_id == 71: add_to_id_list(FL_Channels, 'cutoff', event_data, T_FL_CurrentChannel)
        if event_id == 83: add_to_id_list(FL_Channels, 'resonance', event_data, T_FL_CurrentChannel)
        if event_id == 74: add_to_id_list(FL_Channels, 'preamp', event_data, T_FL_CurrentChannel)
        if event_id == 75: add_to_id_list(FL_Channels, 'decay', event_data, T_FL_CurrentChannel)
        if event_id == 76: add_to_id_list(FL_Channels, 'attack', event_data, T_FL_CurrentChannel)
        if event_id == 85: add_to_id_list(FL_Channels, 'stdel', event_data, T_FL_CurrentChannel)
        if event_id == 131: add_to_id_list(FL_Channels, 'fxsine', event_data, T_FL_CurrentChannel)
        if event_id == 70: add_to_id_list(FL_Channels, 'fadestereo', event_data, T_FL_CurrentChannel)
        if event_id == 22: add_to_id_list(FL_Channels, 'mixslicenum', event_data, T_FL_CurrentChannel)
        if event_id == 219: add_to_id_list(FL_Channels, 'basicparams', event_data, T_FL_CurrentChannel)
        if event_id == 229: add_to_id_list(FL_Channels, 'ofslevels', event_data, T_FL_CurrentChannel)
        if event_id == 221: add_to_id_list(FL_Channels, 'poly', event_data, T_FL_CurrentChannel)
        if event_id == 215: add_to_id_list(FL_Channels, 'params', event_data, T_FL_CurrentChannel)
        if event_id == 132: add_to_id_list(FL_Channels, 'cutcutby', event_data, T_FL_CurrentChannel)
        if event_id == 144: add_to_id_list(FL_Channels, 'layerflags', event_data, T_FL_CurrentChannel)
        if event_id == 145: add_to_id_list(FL_Channels, 'filternum', event_data, T_FL_CurrentChannel)
        if event_id == 143: add_to_id_list(FL_Channels, 'sampleflags', event_data, T_FL_CurrentChannel)
        if event_id == 20: add_to_id_list(FL_Channels, 'looptype', event_data, T_FL_CurrentChannel)
        if event_id == 135: add_to_id_list(FL_Channels, 'middlenote', event_data, T_FL_CurrentChannel)
        if event_id == 196: add_to_id_list(FL_Channels, 'samplefilename', event_data.decode('utf-16le').rstrip('\x00'), T_FL_CurrentChannel)
    else:
        if event_id == 149: 
            hexcolor = event_data.to_bytes(4, 'little')
            T_FL_FXColor = [hexcolor[0],hexcolor[1],hexcolor[2]]
            print('FXColor:', T_FL_FXColor)
        if event_id == 95: 
            T_FL_FXIcon = event_data
            print('FXIcon:', T_FL_FXIcon)
        if event_id == 236: 
            T_FL_FXNum += 1
            print('FXParams, Num', T_FL_FXNum)
            FL_Mixer[T_FL_FXNum]['color'] = T_FL_FXColor
            FL_Mixer[T_FL_FXNum]['icon'] = T_FL_FXIcon
            FL_Mixer[T_FL_FXNum]['slots'] = {}
            FXSlots = [{},{},{},{},{},{},{},{},{},{}]
            FXPlugin = None
            T_FL_FXColor = None
            T_FL_FXIcon = None
        if event_id == 201: 
            event_text = event_data.decode('utf-16le').rstrip('\x00')
            print('\\__DefPluginName:', event_text)
            DefPluginName = event_text
        if event_id == 212: 
            print('\\__NewPlugin')
            FXPlugin = {}
            FXPlugin['plugin'] = DefPluginName
            FXPlugin['data'] = event_data
        if event_id == 155: FXPlugin['icon'] = event_data
        if event_id == 98: #FXToSlotNum
            FL_Mixer[T_FL_FXNum]['slots'][event_data] = FXPlugin
            FXPlugin = None
        if event_id == 213: FXPlugin['pluginparams'] = event_data
        if event_id == 235: FL_Mixer[T_FL_FXNum]['routing'] = parse_fxrouting(event_data)
        if event_id == 154: FL_Mixer[T_FL_FXNum]['inchannum'] = event_data
        if event_id == 147: FL_Mixer[T_FL_FXNum]['outchannum'] = event_data
        if event_id == 204: 
            event_text = event_data.decode('utf-16le').rstrip('\x00')
            print('\\__FXName:', event_text)
            FL_Mixer[T_FL_FXNum]['name'] = event_text

#228 Tracking
#    64000000000000000000000000000000
#228 Tracking
#    3c000000000000000000000000000000
#218 Envelope
#    000000000000000064000000204e0000204e00003075000032000000204e00000000000064000000204e000000000000b680000000000000000000000000000000000000
#218 Envelope
#    040000000000000064000000204e0000204e00003075000032000000204e00000000000064000000204e000000000000b68000000000000000000000000000009bffffff
#218 Envelope
#    000000000000000064000000204e0000204e00003075000032000000204e00000000000064000000204e000000000000b680000000000000000000000000000000000000
#218 Envelope
#    000000000000000064000000204e0000204e00003075000032000000204e00000000000064000000204e000000000000b680000000000000000000000000000000000000
#218 Envelope
#    000000000000000064000000204e0000204e00003075000032000000204e00000000000064000000204e000000000000b680000000000000000000000000000000000000

print(FL_Main)

print('--- Patterns:')
for FL_Pattern in FL_Patterns:
    print(FL_Pattern)

print('--- Channels:')
for FL_Channel in FL_Channels:
    print(FL_Channel)

print('--- Mixer:')
for FL_FX in FL_Mixer:
    print(FL_FX)

print('--- Arrangements:')
for FL_Arrangement in FL_Arrangements:
    print(FL_Arrangement)

print('--- Time Markers:')
for FL_TimeMarker in FL_TimeMarkers:
    print(FL_TimeMarker)