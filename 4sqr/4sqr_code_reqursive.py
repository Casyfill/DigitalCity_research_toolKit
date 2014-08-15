#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests,pprint, json, time, csv

CLIENT_SECRET = "your_secret"
CLIENT_ID = "your_id"

path = "/Users/f.kac/Dropbox (RN&IA'N)/Projects/Kats/Afisha/2014_07_24_RedOctober/4sqr/4sqr3.json"

p = {
	'place': 'Norman+'
	'swBound ': '35.156410,-97.564869'
	'neBound' : '35.276998,-97.354584'
	}

sleepTime = 10

resultPath = "/Users/f.kac/Dropbox (RN&IA'N)/Projects/Kats/Afisha/4sqr_scrape/data/Norman.csv"


def generateCatArray(CLIENT_SECRET, CLIENT_ID):

	#  gets json hierarchy of cats from 4sqr API
	def requestsCats(CLIENT_SECRET, CLIENT_ID):

		pl = {'client_id':CLIENT_ID,
				'client_secret':CLIENT_SECRET,
				'v':'20140723'
		}
		completeUrl = 'https://api.foursquare.com/v2/venues/categories'
		j = requests.get(completeUrl, params=pl)
		# print j.url

		if json.loads(j.text)['meta']["code"] == 200:
			return json.loads(j.text)["response"]["categories"]
		else:
			print 'error requesting categories from Foursquare, error code: ',json.loads(j.text)['meta']["code"]

	data = requestsCats(CLIENT_SECRET, CLIENT_ID)
	
	cats = {}
	for x in data:
		cats[x['name']]=[x['name']]
		for y in x['categories']:
			cats[x['name']].append(y['name'])
			if 'categories' in y.keys() and len(y['categories'])>0:
				for z in y['categories']:
					cats[x['name']].append(z['name'])
	return cats
	# pprint.pprint(cats, indent=4)


def genCategory(cat, catArrays):
	if cat==None:
		return None
	else:
		for c in catArrays.keys():
			if cat in catArrays[c]:
				return c


def getCompleteDetails(id, CLIENT_ID,CLIENT_SECRET):
	pl = {'client_id':CLIENT_ID,
			'client_secret':CLIENT_SECRET,
			'v':'20140723'
	}
	completeUrl = "https://api.foursquare.com/v2/venues/" + str(id)
	j = requests.get(completeUrl, params=pl)
	if json.loads(j.text)['meta']["code"] == 200:
		return json.loads(j.text)["response"]["venue"]
	else:
		print j.text
	time.sleep(sleepTime)



def VenueSearch(sw,ne,CLIENT_ID,CLIENT_SECRET):

	baseUrl = "https://api.foursquare.com/v2/venues/search?sw=%s&ne=%s&client_id=%s&client_secret=%s&intent=browse" % (sw, ne, CLIENT_ID, CLIENT_SECRET)
	payload = {'sw':sw,
				'ne':ne,
				'client_id':CLIENT_ID,
				'client_secret':CLIENT_SECRET,
				'intent':'browse',
				'v':'20140723',
				'limit':50
				}

	r = requests.get(baseUrl, params=payload)
	
	if json.loads(r.text)['meta']["code"] == 200:
		return json.loads(r.text)["response"]["venues"]
	else:
		print r.text


def matrix(swBound,neBound, boundID): 
	vert, gor = 2,2
	swBound =[float(x) for x in swBound.split(',')]
	neBound =[float(x) for x in neBound.split(',')]

	
 	verDelta = (neBound[0]-swBound[0])/vert
	gorDelta = (neBound[1]-swBound[1])/gor

	for i in xrange(vert):
		for j in xrange(gor):
			s = str((swBound[0]+ i*verDelta))
			w = str((swBound[1]+ j*gorDelta)) 

			n=str((swBound[0]+ (i+1)*verDelta))
			e=str((swBound[1]+ (j+1)*gorDelta))

			sw = s + ',' + w
			ne = n + ',' + e
			tileID = boundID + '_' + str(i) + str(j)

			yield [sw, ne, tileID]



# STARTING!
tileArray = [[p['swBound'], p['neBound'],'0']]
catArrays = generateCatArray(CLIENT_SECRET, CLIENT_ID)

headers=['genCategory','category','name','lon','lat','checkIns','tips','users','createdAt','tileID', 'ID', p['place'], 'time']
# print '|'.join(headers)
# unique_keys = [ 'ID' ]
errorTiles = []
with open(resultPath, 'a') as csvfile:
	writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	writer.writerow(headers)
	# блок рекурсии
	spreads = 1
	read = 0
	while len(tileArray)>0:
		for tile in tileArray:
			print tile[2], ':', read, '/',spreads

			try:
				p = VenueSearch(tile[0],tile[1],CLIENT_ID,CLIENT_SECRET)
				if len(p)==50:
					tileArray=tileArray+list(matrix(tile[0],tile[1],tile[2]))
					# print tile[2], ' detailed!'
					spreads+=3
				else:
					read+=1
					for venue in p:
						ID = venue['id']
						venue = getCompleteDetails(ID,CLIENT_ID,CLIENT_SECRET)
						try:
							createdAt = time.gmtime(venue["createdAt"])
						except:
							createdAt = 0

						try:
							c= venue['categories'][0]['name']
						except:
							c = 'None'

						
					
							
						d = { 'genCategory': genCategory(c,catArrays),
							'category': c.encode('utf-8'),
							'name': venue['name'].encode('utf-8'),
						 	'lon': venue['location']['lng'],
						 	'lat': venue['location']['lat'],
						 	'checkIns': venue['stats']['checkinsCount'],
						 	'tips': venue['stats']['tipCount'],
						 	'users': venue['stats']['usersCount'],
						 	'createdAt': time.strftime("%Y.%m.%d ", createdAt),
						 	'tileID': tile[2],
						 	'ID':ID.encode('utf-8'),
						 	'place':place.encode('utf-8'),
						 	'time':time.strftime("%Y.%m.%d %H:%M:%S ")
							}

						writer.writerow([d[key] for key in headers])
			except:
				errorTiles.append(tile)


	    			
					# scraperwiki.sql.save(unique_keys, d)

					# print tile[2], ' scraped!'

					# print '|'.join([str(d[key]) for key in headers])
			time.sleep(sleepTime)
			tileArray.remove(tile)

			 
for tile in errorTiles:
	print ','.join(tile)


