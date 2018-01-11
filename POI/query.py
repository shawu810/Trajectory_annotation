# -*- coding: utf-8 -*-
"""
Created on Fri Jun  5 14:44:49 2015

@author: feiwu
"""

#import MySQLdb
import numpy as np
table_name = 'raw_tweets'

class Point:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon
    def make_key(self):
        return '{},{}'.format(self.lat,self.lon)

class POI:
    def __init__(self, name, pid, lat, lon, cat, checkin_count, user_count, source='fsq'):
        self.name = name
        self.pid = pid
        self.location = Point(lat,lon)
        self.cat = cat
        self.checkin_count = checkin_count
        self.user_count = user_count
        self.extra_id = '' # for debuging purposes
        self.popularity = dict()
        self.extra = ''
        self.source = source
        
    def add_extra_id(self, extra_id):
        self.extra_id = extra_id
        
    def add_extra(self, extra):
        self.extra = extra
        
    def add_density(self, key, den):
        self.popularity[key] = den
        
    
class Checkin:
    def __init__(self,timestamp,user_id,lat,lon,content='', annotated_list =list(), label = -1, entry_id = -1, result = -1):
        self.timestamp = timeString(timestamp)
        self.user_id = user_id
        self.lat = float(lat)
        self.lon = float(lon)
        self.content = content
        self.annotated = annotated_list
        self.ground_label = label
        self.extra_id = entry_id
        self.result = result
		
    def add_label(self,label):
        self.ground_label = label
		
    def add_list(self,annotated):
        self.annotated = annotated
		
    def add_predict(self,predicted):
        self.predicted = predicted
		
    def add_extraid(self,extra):
        self.extra_id = extra
		
    def add_result(self,result):
        self.result = result
		
    def obj2string(self):
        return self.timestamp.obj2string(), self.user_id, self.lat, self.lon, self.content
    

class timeString:
    def __init__(self,timestamp):
        timestamp = str(timestamp)
        self.raw_timestamp = timestamp
        self.year = int(timestamp[0:4])
        self.month= int(timestamp[4:6])
        self.day  = int(timestamp[6:8])
        self.hour = int(timestamp[8:10])
        self.mins = int(timestamp[10:12])
        self.sec  = int(timestamp[12:14])
        
    def obj2string_raw(self):
        return self.raw_timestamp
    def obj2string(self):
        return self.year,self.month,self.day,self.hour,self.mins,self.sec
        
        
def draw_guassian_noise(mu,sigma):
    if sigma != 0:
        s = np.random.normal(mu,sigma)
    else:
        s =(0,0)
    return s
    
def read_in_user_list(filename):
    user_dict = dict()
    with open(filename,'r') as f:
        user_list = [ [int(x) for x in one_line.rstrip('\n').split('\t')] for one_line in f.readlines()]
    for one in user_list:
        user_dict[one[0]] = one[1] 
    return user_dict #return {user_id: # of check-ins}
    
def query_user_checkins_by_id(user_id, db_connection):
    cursor = db_connection.cursor()
    # on nyc data lat and lon are flipped
    query  = 'SELECT tweet_id, timestamp, lat, lon, content FROM {} WHERE user_id = {} AND content LIKE "%I m at %" AND content LIKE "%http%"; '.format(table_name,user_id)
    try:
        cursor.execute(query)
    except Exception as e:
        print e
    result = cursor.fetchall()
    user_checkins = list()
    extra_location= list()
    for one_entry in result:
        tid   = one_entry[0]
        times = one_entry[1]
        lon   = one_entry[2]
        lat   = one_entry[3]
        content= one_entry[4]
        one_checkin = Checkin(times,user_id,lat,lon,content,[],-1,tid)
        user_checkins.append(one_checkin)
        extra_location.append((lat,lon))
    return user_checkins,extra_location
    
def query_tweets_by_id(tweet_id, db_connection):
    cursor = db_connection.cursor()
    query  = 'SELECT * FROM {} WHERE tweet_id = {};'.format(table_name,tweet_id)
    try:
        cursor.execute(query)
    except Exception as e:
        print e
    result = cursor.fetchall()
    tweet_id = result[0][0]
    timestamp= result[0][1]
    userid   = result[0][2]
    #profile_location = result[0][3]
    lon      = result[0][4] # NYC setting
    lat      = result[0][5] #
    content  = result[0][6]
    return Checkin(timestamp,userid,lat,lon,content)
