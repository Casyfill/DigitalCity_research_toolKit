#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  два режима (сервер и локал) с подстановкой путей
mode = 'server' #'local' 

pathes = {'local':{'modulePath':"/Users/casy/Dropbox (RN&IA'N)/Projects/Kats/Afisha/4sqr_scrape/code/misc/",
					'resultPath':"/Users/casy/Dropbox (RN&IA'N)/Projects/Kats/Afisha/4sqr_scrape/data/"},
		  'server':{'modulePath':"/root/4sqr_scraper/code/misc",
					'resultPath':"/root/4sqr_scraper/data/"}}

modulePath, resultPath = pathes[mode]['modulePath'],pathes[mode]['resultPath']

# import requests,time,json
import sys, csv, time
sys.path.append(modulePath)

from frsqr_path import CLIENT_SECRET, CLIENT_ID
from matrix import matrix
from boundChecker import checkVsBound

import parseVenue, frsqrRequests
# from graphics import *
# win = GraphWin()



sleepTime = 10
place = 'Oklahoma1'
swBound = '33.329980, -103.567494'
neBound = '37.384914, -94.111012'
resultPath+=(place + '.csv')

headers=['genCategory',   # csv headers (params)
				'category',
				'name',
				'lon',
				'lat',
				'checkIns',
				'tips',
				'users',
				'createdAt',
				'tileID',
				'ID',
				'place',
				'time']


with open(resultPath, 'w') as csvfile:
	writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	writer.writerow(headers)

	newTileArray  = [{'sw':swBound, 'ne':neBound,'name':'0'}] #First list of requests
	catArrays = frsqrRequests.generateCatArray(CLIENT_SECRET, CLIENT_ID) #list of categories
	
	level = 0 #уровень детализации 
	spreads = 1 # количество необходимых запростов
	read = 0 # количество результативных запросов

	while len(newTileArray)>0:
		tileArray = newTileArray # рабочий список
		newTileArray = [] #обнуляем список для следующей итерации
		level+=1
		print 'level %d reached: %d requests ' %(level, len(tileArray))

		for tile in tileArray:
			time.sleep(sleepTime)
			
			
			ask = frsqrRequests.VenueSearch(tile['sw'],tile['ne'],CLIENT_ID,CLIENT_SECRET)

			p = []
			try:
				for venue in ask["response"]["venues"]:
					if checkVsBound(tile['sw'],tile['ne'],venue['location']['lat'], venue['location']['lng']):
						p.append(venue)
					else:
						pass
			except:
				pass

			if 'errorType' in ask['meta'].keys():
				if ask['meta']['errorType']=='geocode_too_big':
					# print ask['meta'].keys()
					newTileArray+=matrix(tile['sw'],tile['ne'],tile['name']) # добавляем детализированную матрицу к листу следующего уровня
					print tile['name'], ':', read, '/',spreads, ' too big, detailed!'
					spreads+=3 
			
			elif len(p)>=50:  #если запросов 50, то, скорее всего, включен лимит, нужна детализация
				newTileArray+=matrix(tile['sw'],tile['ne'],tile['name']) # добавляем детализированную матрицу к листу следующего уровня
				print tile['name'], ':', read, '/',spreads, ' detailed!'
				spreads+=3
				
			elif len(p)==0: #если ответ путой
				read+=1
				print tile['name'], ':', read, '/',spreads, 'zone empty'
			else: #если ответ не пустой
				read+=1
				print tile['name'], ':', read, '/',spreads, 'saved: %d venues' % (len(p))

				for venue in p:
					ID = venue['id']
					# Получаю полные данные по Venue
					full_venue = frsqrRequests.getCompleteDetails(ID,CLIENT_ID,CLIENT_SECRET)
					v = parseVenue.parseVenue(full_venue, catArrays, tile['name'], place)
					writer.writerow([v[key] for key in headers])
					# print '|'.join([str(v[key]) for key in headers])

print 'scraping %s done!' % (place)

