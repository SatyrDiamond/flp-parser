import argparse
import func_riff
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

def parse_patternnotes(patternnotesbytes):
    notelistdata = BytesIO()
    notelistdata.write(patternnotesbytes)
    notelistdata.seek(0,2)
    notelistdata_filesize = notelistdata.tell()
    notelistdata.seek(0)
    notelist = []
    while notelistdata.tell() < notelistdata_filesize:
        print('\t Note:')
        print('\t\t', end='')
        print('pos:',int.from_bytes(notelistdata.read(4), "little"), end=', ')
        print('flags:',int.from_bytes(notelistdata.read(2), "little"), end=', ')
        print('rackch:',int.from_bytes(notelistdata.read(2), "little"), end=', ')
        print('dur:',int.from_bytes(notelistdata.read(4), "little"), end=', ')
        print('key:',int.from_bytes(notelistdata.read(4), "little"), end=', ')
        print('finep:',int.from_bytes(notelistdata.read(1), "little"), end=', ')
        print('u1:',int.from_bytes(notelistdata.read(1), "little"), end=', ')
        print('rel:',int.from_bytes(notelistdata.read(1), "little"), end=', ')
        print('midich:',int.from_bytes(notelistdata.read(1), "little"), end=', ')
        print('pan:',int.from_bytes(notelistdata.read(1), "little"), end=', ')
        print('velocity:',int.from_bytes(notelistdata.read(1), "little"), end=', ')
        print('mod_x:',int.from_bytes(notelistdata.read(1), "little"), end=', ')
        print('mod_y:',int.from_bytes(notelistdata.read(1), "little"))

def parse_FLTrack(trackdata):
	fltrackdata = BytesIO()
	fltrackdata.write(trackdata)
	fltrackdata.seek(0)
	print('\t ID:',int.from_bytes(fltrackdata.read(4), "little"))
	print('\t Color:',fltrackdata.read(4).hex())
	print('\t Icon:',int.from_bytes(fltrackdata.read(4), "little"))
	print('\t Enabled:',int.from_bytes(fltrackdata.read(1), "little"))
	print('\t Height:',struct.unpack('<f', fltrackdata.read(4))[0])
	print('\t LockedToContent:',int.from_bytes(fltrackdata.read(1), "little"))
	print('\t Motion:',int.from_bytes(fltrackdata.read(4), "little"))
	print('\t Press:',int.from_bytes(fltrackdata.read(4), "little"))
	print('\t TriggerSync:',int.from_bytes(fltrackdata.read(4), "little"))
	print('\t Queued:',int.from_bytes(fltrackdata.read(4), "little"))
	print('\t Tolerant:',int.from_bytes(fltrackdata.read(4), "little"))
	print('\t PositionSync:',int.from_bytes(fltrackdata.read(4), "little"))
	print('\t Grouped:',int.from_bytes(fltrackdata.read(1), "little"))
	print('\t Locked:',int.from_bytes(fltrackdata.read(1), "little"))

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

fileobject = open(args.input, 'rb')
headername = fileobject.read(4)
rifftable = func_riff.readriffdata(fileobject, 0)
for riffobj in rifftable:
	#print(str(riffobj[0]) + str(len(riffobj[1])))
	if riffobj[0] == b'FLhd':
		#print(riffobj[1][4:5])
		ppq = int.from_bytes(riffobj[1][4:5], "big")
	if riffobj[0] == b'FLdt':
		flpevents = parse_flp_Events(riffobj[1])



for flpevent in flpevents:
	event_id = flpevent[0]
	if event_id == 238:
		print(lines[flpevent[0]].strip())
		parse_FLTrack(flpevent[1])
	elif event_id == 224:
		print(lines[flpevent[0]].strip())
		parse_patternnotes(flpevent[1])
	elif event_id == 238:
		print(lines[flpevent[0]].strip())
		parse_FLTrack(flpevent[1])
	elif event_id == 241:
		print(lines[flpevent[0]].strip())
		print('\t'+flpevent[1].decode('utf-16le').rstrip('\0'))
	elif event_id <= 255 and event_id >= 192 : # text
		print(lines[flpevent[0]].strip())
		print('\t'+str(flpevent[1].hex()))
	else:
		print(lines[flpevent[0]].strip()+";"+str(flpevent[1]))
