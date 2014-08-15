import flickrapi
import xml.etree.ElementTree as ET
import math, time

api_key='your_key'
api_secret ='your_secret'

p = { 'name': 'redOctober',
	'lat' : "55.740836",
	'lon' : "37.609925",
	'radius' : "0.3"
	}



def photoSerialiser(photoEl):
	d= {"farm":photoEl.get('farm').encode('utf-8'),
	"server":photoEl.get('server').encode('utf-8'),
	"secret":photoEl.get('secret').encode('utf-8'),
	"owner" : photoEl.get('owner').encode('utf-8'),
	"ID" : photoEl.get('id').encode('utf-8'),
	"title" : photoEl.get('title').encode('utf-8')}
	d['url']= "https://farm%s.staticflickr.com/%s/%s_%s_m.jpg" % (d['farm'], d['server'], d['ID'], d['secret'])
	return d

def detailsSerialiser(detailsEl):
	try:
		taken = detailsEl.find('dates').get('taken').encode('utf-8')
	except:
		try:
			taken = detailsEl.find('dates').get('posted').encode('utf-8')
		except:
			taken = 'n/a'
	try:
		ownerLoc = detailsEl.find('owner').get('location').encode('utf-8')
	except:
		ownerLoc = 'unknown'

	try:
		lon = detailsEl.find('location').get('longitude')
		lat = detailsEl.find('location').get('latitude')
	except:
		lon = '0'
		lat = '0'

	try:
		views = detailsEl.get('views').encode('utf-8')
	except:
		views = '-1'

	details = {'ownerLoc':ownerLoc,
				'taken': taken,
				'lon': lon,
				'lat': lat,
				'views': views}
	return details



data = []

flickr = flickrapi.FlickrAPI(api_key,secret=api_secret)
r = flickr.photos_search(lon=p['lon'], lat=p['lat'], radius=p['radius'], has_geo="1", per_page='500')


# define total pages (requests)
total = r[0].get('total')
pages= int(math.ceil(float(total)/250.0))
print pages

for photo in r[0].findall('photo'):
	data.append(photoSerialiser(photo))

for i in xrange(1,pages):
	print i+1, "/", pages
	r = flickr.photos_search(lon=lon, lat=lat, radius=radius, per_page='500', page=str(i+1))
	for photo in r[0].findall('photo'):
		data.append(photoSerialiser(photo))
# 	time.sleep(2)


print len(data)

# collecting additional data
headers = ['title','lat','lon','ownerLoc','owner','taken','views','url','ID','farm','server','secret']
print '|'.join(headers)

for d in data:
	request = flickr.photos_getinfo(secret=d['secret'],photo_id=d['ID'],api_key=api_key)
	for photo in request.find('photo'):
		details = detailsSerialiser(photo)
		d.update(details)
		time.sleep(0.2)
	print '|'.join([str(d[key]) for key in headers])


# headers = ['lat','lon','ownerLoc', 'taken','views']
# request = flickr.photos_getinfo(secret='5f5f012d6b',photo_id='8926261264',api_key=api_key)
# # ET.dump(request)
# X= detailsSerialiser(request.find('photo'))
# print '|'.join([str(X[key]) for key in headers])