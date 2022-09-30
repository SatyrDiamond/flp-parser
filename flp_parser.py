import argparse
import varint

from io import BytesIO

parser = argparse.ArgumentParser()
parser.add_argument("input")
args = parser.parse_args()

with open('flp_eventname.txt') as f:
    lines = f.readlines()

outfile = open('output.flps', 'w')

eventtable = []
for line in lines:
	idname = line.rstrip().split()
	if len(idname) > 1:
		eventtable.append([idname[0], idname[1]])
	else:
		eventtable.append([idname[0], '_unknown'])

def datablock(PatternNotes, bytesnumber):
	notelistdata = BytesIO()
	notelistdata.write(PatternNotes)
	notelistdata_filesize = notelistdata.tell()
	notelistdata.seek(0)
	while notelistdata.tell() < notelistdata_filesize:
		outfile.write('\t\t' + bytes(notelistdata.read(bytesnumber)).hex() + '\n')

def writestring(eventpart):
	outfile.write('\t\t' + eventpart.split(b'\x00')[0].decode("utf-8") + '\n')

def parse_flp_Events(riffobj):
	eventdatasize = len(riffobj)
	eventdatastream = BytesIO()
	eventdatastream.write(riffobj)
	eventdatastream.seek(0)
	while eventdatastream.tell() < int(eventdatasize):
		event_id = int.from_bytes(eventdatastream.read(1), "little")
		if event_id <= 63 and event_id >= 0: # int8
			outfile.write(str(event_id) + ' ' + eventtable[event_id][1] + ', ' + str(int.from_bytes(eventdatastream.read(1), "little")) + '\n')
		if event_id <= 127 and event_id >= 64 : # int16
			outfile.write(str(event_id) + ' ' + eventtable[event_id][1] + ', ' + str(int.from_bytes(eventdatastream.read(2), "little")) + '\n')
		if event_id <= 191 and event_id >= 128 : # int32
			outfile.write(str(event_id) + ' ' + eventtable[event_id][1] + ', ' + str(int.from_bytes(eventdatastream.read(4), "little")) + '\n')
		if event_id <= 224 and event_id >= 192 : # text
			eventpartdatasize = varint.decode_stream(eventdatastream)
			eventpart = eventdatastream.read(eventpartdatasize)
			if event_id == 224:
				outfile.write(str(event_id) + ' ' + eventtable[event_id][1] + '\n')
				datablock(eventpart, 20)
			elif event_id == 223:
				outfile.write(str(event_id) + ' ' + eventtable[event_id][1] + '\n')
				datablock(eventpart, 12)
			elif event_id in [192, 196, 201, 193]:
				outfile.write(str(event_id) + ' ' + eventtable[event_id][1] + '\n')
				writestring(eventpart)
			else:
				outfile.write(str(event_id) + ' ' + eventtable[event_id][1] + ', ' + eventpart.hex() + '\n')
		if event_id <= 255 and event_id >= 225 : # data
			eventpartdatasize = varint.decode_stream(eventdatastream)
			eventpart = eventdatastream.read(eventpartdatasize)
			outfile.write(str(event_id) + ' ' + eventtable[event_id][1] + ', ' + eventpart.hex() + '\n')

fileobject = open(args.input, 'rb')
headername = fileobject.read(4)
rifftable = func_riff.readriffdata(fileobject, 0)
for riffobj in rifftable:
	print(str(riffobj[0]) + str(len(riffobj[1])))
	if riffobj[0] == b'FLdt':
		parse_flp_Events(riffobj[1])
