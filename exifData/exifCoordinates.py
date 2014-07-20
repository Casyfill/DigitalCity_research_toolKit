#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import exifread
import os

folder = "/Users/casy/Dropbox (RN&IA'N)/Camera Uploads/"


files = []
for file in os.listdir(folder):
    if file.endswith(".jpg"):
        files.append(folder+file)


# Open image file for reading (binary mode)
# path_name = "/Users/casy/Dropbox (RN&IA'N)/Camera Uploads/2014-06-26 19.54.17.jpg"

def floatFromAspect(v):
	return float(v.num / v.den)

def reCalcDegrees(l):
	return floatFromAspect(l[0]) + floatFromAspect(l[1])/60 + floatFromAspect(l[2])/3600
	# print clean(l[0]) ,'|', clean(l[1])/60 ,'|', clean(l[2])/3600

def grabMeta(path):
	f = open(path, 'rb')
	tags = exifread.process_file(f, details=False)
	# print file
	
	try: 
		lon= reCalcDegrees(tags['GPS GPSLongitude'].values)
	except:
		lon = None

	try:
		lat= reCalcDegrees(tags['GPS GPSLatitude'].values)
	except:
		lat= None

	try:
		direction=floatFromAspect(tags['GPS GPSImgDirection'].values[0])
	except:
		direction= None

	try:
		t = tags['EXIF LensModel'].values
	except:
		t=None

	try:
		timestamp = tags['EXIF DateTimeOriginal'].values
	except:
		timestamp = None


	return {'lon':lon, 'lat':lat, 'direction':direction, 'type':t, 'timestamp':timestamp}

def printMeta(path):
	import pprint
	f = open(path, 'rb')
	tags = exifread.process_file(f, details=False)
	pprint.pprint(tags)


# p = "/Users/casy/Dropbox (RN&IA'N)/Camera Uploads/2014-01-01 17.13.16.jpg"
# print printMeta(p)


# saving folder as array
data = []
for file in files:
	data.append(grabMeta(file))
	

# printing Folder out
print '|'.join(data[0].keys()) 
for info in data:
	print '|'.join([str(info[x]) for x in info])
