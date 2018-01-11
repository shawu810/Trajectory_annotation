# -*- coding: utf-8 -*-
"""
Created on Tue Jan 09 12:08:19 2018

@author: fxw133-admin
"""

from math import sin, cos, asin, radians, sqrt
import math
import urllib, json, time

class AnnotationUtility:   
    
    @classmethod
    def haversine(clf, P1, P2):
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees)
        """
        lon1 = P1.lng
        lon2 = P2.lng
        lat1 = P1.lat
        lat2 = P2.lat        
        
        # convert decimal degrees to radians 
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    
        # haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        r = 6371 # Radius of earth in kilometers. Use 3956 for miles
        return c * r * 1000 # in meters
    
    @classmethod    
    def GoogGeoAPI(clf, address,api="",delay=2):
        base = r"https://maps.googleapis.com/maps/api/geocode/json?"
        addP = "address=" + address.replace(" ","+")  
        GeoUrl = base + addP + "&key=" + api
        response = urllib.urlopen(GeoUrl)
        jsonRaw = response.read()
        jsonData = json.loads(jsonRaw)
        if jsonData['status'] == 'OK':
            resu = jsonData['results'][0]
            finList = [resu['formatted_address'],resu['geometry']['location']['lat'],resu['geometry']['location']['lng']]
        else:
            finList = [address,None,None]
        time.sleep(delay) #in seconds
        return finList 
        
    @classmethod    
    def eudist(clf, x1,x2 ):
        return math.sqrt( (x1.lat-x2.lat)**2 + (x1.lng-x2.lng)**2)

    ######################################################################################
    #make key stuff considering moving later
    ######################################################################################

    @classmethod
    def make_spatial_grid_key(clf, lat, lon, grid_size=0.01):
        def trunc(x, g):
            g = float(1.0)/g;
            return math.floor(x*g)/float(g)
        
        def map2grid_center(lat, lon,g):
            return (trunc(lat, g) + float(g)/2, 
                trunc(lon, g) + float(g)/2)
        ## all keys please follow lat, lon format
        grid_center = map2grid_center(lat, lon, grid_size)
        string_key  = '{},{}'.format(grid_center[0], grid_center[1])
        return string_key
        
    @classmethod
    def get_nearby_spatial_key(clf, key, point, DIST_THRES, grid_size=0.01):
        
        def decode_spatial_grid_key(one_grid):
            point = [float(x) for x in one_grid.rstrip('\n').split(',')]
            return (point[0],point[1])
        key_list = [key]    
        lat, lng = decode_spatial_grid_key(key)
        if math.sqrt((point.lat-lat)**2 + ( point.lng-lng) ** 2) < DIST_THRES:
            return key_list
        else:
            lat_min = lat - float(grid_size) / 2.0 + DIST_THRES
            lat_max = lat + float(grid_size) / 2.0 - DIST_THRES
            lng_min = lng - float(grid_size) / 2.0 + DIST_THRES
            lng_max = lng + float(grid_size) / 2.0 - DIST_THRES
            if point.lat <= lat_min:
                key_list.append(AnnotationUtility().make_spatial_grid_key(point.lat - DIST_THRES, point.lng))
            if point.lat >= lat_max:
                key_list.append(AnnotationUtility().make_spatial_grid_key(point.lat + DIST_THRES, point.lng))
            if point.lng <= lng_min:
                key_list.append(AnnotationUtility().make_spatial_grid_key(point.lat, point.lng - DIST_THRES))
            if point.lng >= lng_max:
                key_list.append(AnnotationUtility().make_spatial_grid_key(point.lat, point.lng + DIST_THRES))
            return key_list
            
    
       
    
    
        
