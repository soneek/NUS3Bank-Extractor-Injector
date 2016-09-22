import sys
from util import *
import os
import string

class strg(object):
	name = ""
	size = 0
	offset = 0
	def __init__(self, id):
		self.id = id

class nus3bank(object):
	contents = []
	propOffset = 0
	binfOffset = 0
	grpOffset = 0
	dtonOffset = 0
	toneOffset = 0
	junkOffset = 0
	packOffset = 0
	def __init__(self, size):
		self.size = size

class tone(object):
	name = ""
	ext = ""
	packOffset = 0
	size = 0
	def __init__(self, offset, metaSize):
		self.offset = offset
		self.metaSize = metaSize

nus3 = open(sys.argv[1], 'rb')
if len(sys.argv) < 3:
	outfolder = string.replace(sys.argv[1], ".nus3bank", "")
else:
	outfolder = sys.argv[2]
if not os.path.exists(outfolder):
	os.mkdir(outfolder)
assert nus3.read(4) == "NUS3"
size = readu32le(nus3)

bank = nus3bank(size)
assert nus3.read(8) == "BANKTOC ", "Not a bank archive!"
tocSize = readu32le(nus3)
count = readu32le(nus3)
offset = 0x14 + tocSize
assert nus3.read(4) == "PROP"
propOffset = offset
propSize = readu32le(nus3)
assert nus3.read(4) == "BINF"
binfOffset = propOffset + propSize + 8
binfSize = readu32le(nus3)
assert nus3.read(4) == "GRP "
grpOffset = binfOffset + binfSize + 8
grpSize = readu32le(nus3)
assert nus3.read(4) == "DTON"
dtonOffset = grpOffset + grpSize + 8
dtonSize = readu32le(nus3)
assert nus3.read(4) == "TONE"
toneOffset = dtonOffset + dtonSize + 8
toneSize = readu32le(nus3)
assert nus3.read(4) == "JUNK"
junkOffset = toneOffset + toneSize + 8
junkSize = readu32le(nus3)
assert nus3.read(4) == "PACK"
packOffset = junkOffset + junkSize + 8
packSize = readu32le(nus3)




nus3.seek(toneOffset)
assert nus3.read(4) == "TONE"
assert readu32le(nus3) == toneSize
toneCount = readu32le(nus3)
tones = []
for i in range(toneCount):
	offset = readu32le(nus3) + toneOffset + 8
	metaSize = readu32le(nus3)
	tones.append(tone(offset, metaSize))
	
for i in range(toneCount):
	if tones[i].metaSize <= 0xc:
		continue
	nus3.seek(tones[i].offset+6)
	if readByte(nus3) > 9:
		nus3.seek(5, 1)
	else:
		nus3.seek(1,1)
	stringSize = readByte(nus3)
#	print hex(nus3.tell())
	tones[i].name = nus3.read(stringSize - 1)
	nus3.seek(1,1)
	print tones[i].name
	padding = (stringSize + 1) % 4
	if padding == 0:
		nus3.seek(4, 1)
	else:
		nus3.seek(abs(padding-4) + 4, 1)
	assert readu32le(nus3) == 8
	tones[i].packOffset = readu32le(nus3)
	tones[i].size = readu32le(nus3)
#	print hex(tones[i].packOffset) + " - " + hex(tones[i].size)
	nus3.seek(packOffset + 8 + tones[i].packOffset)
	fourcc = nus3.read(4)
	nus3.seek(-4,1)
	if fourcc == "IDSP":
		tones[i].ext = ".idsp"
	elif fourcc == "RIFF":
		tones[i].ext = ".at9"
	outfile = open(outfolder + "/" + tones[i].name + tones[i].ext, "wb")
	outfile.write(nus3.read(tones[i].size))
	outfile.close()
	
nus3.close()
