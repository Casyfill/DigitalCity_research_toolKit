#!/usr/bin/env python
# -*- coding: utf-8 -*-

def checkVsBound(sw,ne, lat, lon):
	s,w =[float(x.strip()) for x in sw.split(',')]
	n,e =[float(x.strip()) for x in ne.split(',')]
	return (n>=lat >=s) and (e >= lon >=w)


