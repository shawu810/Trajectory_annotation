# -*- coding: utf-8 -*-
"""
Created on Tue Jan 09 11:01:35 2018

@author: fxw133-admin
"""

from utility import AnnotationUtility    
from collections import Counter
import numpy as np
import time
import pdb
# data model

class Point(object):
    
    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng
    
    
class GPSSample(object):
    
    def __init__(self, lat, lng, timestamp, speed):
        self.lat = lat
        self.lng = lng
        self.timestamp = timestamp 
        self.speed = speed
    
    def get_unix_time(self):
        return time.mktime(self.timestamp.timetuple())


class Trajectory(object):
    
    def __init__(self):
        self.point_list = list()
        
    def add_point(self, p):
        self.point_list.append(p)
        
    def get_gps_by_index(self, ind):
        return self.point_list[ind]
        
    def get_indexes(self):
        return range(len(self.point_list))
       
    def get_matrix(self):
        return np.array([(gpsp.get_unix_time(), gpsp.lat, gpsp.lng, gpsp.speed) for gpsp in self.point_list],
                  dtype=float)        
        
class Survey(object):

    def __init__(self):
        # question type query        
        self.item_dictionary = dict()
        
        
    def get_length(self):
        return len(self.item_dictionary)
        
    def get_item_types(self):
        return self.item_dictionary.keys()
    
    def get_item_bytype(self, qtype):
        return self.item_dictionary[qtype] if qtype in self.item_dictionary else None
        
    def add_item(self, key, survey_item):
        self.item_dictionary[key] = survey_item
        
    def geo_coding_withupdate(self, coded):
        for address in self.item_dictionary.values():
            address.geo_coding_withupdate(coded)
     
     
class SurveyItem(object):
    
    def __init__(self, item, name, address):
        self.address = None
        self.item = item
        self.name = name
        self.address = address
        self.query_address = self.address + ', Chicago, IL'
    
    def set_query_address(self, query_address):
        self.query_address = query_address
 
    def geo_coding_withupdate(self, coded):
        if self.query_address in coded:
            self.geo_code_raw = coded[self.query_address]
        else:
            self.geo_code_raw = AnnotationUtility().GoogGeoAPI(self.query_address)
            coded[self.query_address] = self.geo_code_raw
            print self.geo_code_raw 
    
    def get_location(self):
        return Point(self.geo_code_raw[1], self.geo_code_raw[2])
          

###############################################################################

class User(object):
    
    def __init__(self, uid):
        self.uid = uid
        self.traj = Trajectory()
        self.survey = Survey()
        self.label = None
        
    def _gridfy_survey(self):
        grid_survey = dict()
        for stype in self.survey.get_item_types():
            add_loc = self.survey.get_item_bytype(stype).get_location()
            if add_loc.lat is None:
                print self.survey.get_item_bytype(stype).geo_code_raw
                continue
            spatial_key = AnnotationUtility().make_spatial_grid_key(add_loc.lat, 
                                                                  add_loc.lng)
            if spatial_key not in grid_survey:
                grid_survey[spatial_key] = list()
            grid_survey[spatial_key].append(stype)
        return grid_survey
            
    def _gridfy_traj(self):
        grid_traj = dict()
        for traj_i in self.traj.get_indexes():
            gps = self.traj.get_gps_by_index(traj_i)
            spatial_key = AnnotationUtility().make_spatial_grid_key(gps.lat, gps.lng)
            
            if spatial_key not in grid_traj:
                grid_traj[spatial_key] = list()
            grid_traj[spatial_key].append(traj_i)
        return grid_traj
        
        
    ###############################################################################
    # prep       
           
    def generate_labels(self, SPEED_THRES=10, 
                        DIST_THRES=0.001): # ~~110 meters, speed km/h
        grid_survey = self._gridfy_survey()
        traj_ground = dict()
        for traj_i in self.traj.get_indexes():
            gps = self.traj.get_gps_by_index(traj_i)
            if gps.speed > SPEED_THRES:
                traj_ground[traj_i] = None
                continue
            key = AnnotationUtility().make_spatial_grid_key(gps.lat, gps.lng)
            kl = AnnotationUtility().get_nearby_spatial_key(key, gps, DIST_THRES, grid_size=0.01)
            for k in kl:
                if k in grid_survey:
                    items_keys = grid_survey[k]
                    for item_key in items_keys:
                        item = self.survey.get_item_bytype(item_key)
                        if AnnotationUtility().eudist(item.get_location(), gps) < DIST_THRES:
                            if traj_i in traj_ground:                            
                                traj_ground[traj_i] += ',' + item_key
                            else:
                                traj_ground[traj_i] = item_key
        self.label = traj_ground
        return self.label
        
        
    def print_label_stats(self, PRINT=False):
        labels = [x for x in self.label.values() if x is not None]
        speed = len([x for x in self.label.values() if x is None])
        double_labels = [x for x in labels if ',' in x] 
        label_ratio = float(len(labels)) / len(self.traj.get_indexes())
        double_label_ratio = float(len(double_labels)) / len(self.traj.get_indexes())
        cc = Counter(labels)
        if PRINT:
            print '{} out of {}, {} lablled'.format(len(labels), 
                                                    len(self.traj.get_indexes()), 
                                                    label_ratio)
            print '{} out of {}, {} double lablled'.format(len(double_labels), 
                                                    len(self.traj.get_indexes()), 
                                                    double_label_ratio)
            print cc
            
        return len(labels), len(double_labels), len(self.traj.get_indexes()), speed, cc
        
        
    def prepare_annotation(self, venueDB, GRID_SIZE, DIST_THRES):
        traj_annotation = dict()
        for traj_i in self.traj.get_indexes():
            gps = self.traj.get_gps_by_index(traj_i)
            key = AnnotationUtility().make_spatial_grid_key(gps.lat, gps.lng, grid_size=GRID_SIZE)
            kl = AnnotationUtility().get_nearby_spatial_key(key, gps, DIST_THRES, grid_size=GRID_SIZE)
            #pdb.set_trace()
            for k in kl:
                if k in venueDB:
                    for vid in range(len(venueDB[k])):
                        venue = venueDB[k][vid]
                        vp = Point(venue.location.lat, venue.location.lon)
                        #pdb.set_trace()
                        if AnnotationUtility().eudist(vp, gps) < DIST_THRES:
                            if traj_i not in traj_annotation:
                                traj_annotation[traj_i] = list()
                            traj_annotation[traj_i].append(venue) # append reference to the venue obj
                            #pdb.set_trace()
                            
        self.annotation_cand = traj_annotation
        return self.annotation_cand
    
    def print_annotation_stats(self):
        overcount = len(set(self.annotation_cand.keys()).intersection(set(self.label.keys())))
        lc = [len(self.annotation_cand[x]) for x in self.annotation_cand.keys()]
        hasnearby = len([x for x in lc if x >=1])
        hasnearby2 = len([x for x in lc if x >=2])
        hasnearby5 = len([x for x in lc if x >=5])

        return overcount, hasnearby, hasnearby2, hasnearby5, len(self.traj.get_indexes())
        
    ###########################################################################
    # annotation
        
    def dist2p(self, P, venue, sigma=0.03):
        d = AnnotationUtility().eudist(P, Point(venue.location.lat, venue.location.lon))
        return np.exp(-d/(2 * sigma**2))
        
    def pop(self,venue):
        if venue.extra_id == 'google':
            user_count = 1
        else:
            user_count = venue.user_count
        value = np.log10(10 + (user_count)/20.0)
        #pdb.set_trace()
        return value
        
    def dist_pop(self, P, venue, sigma=0.03):
        return self.dist2p(P, venue, sigma) * self.pop(venue) # was log10
        
    def annotate_by_measure(self, measure='dist'):
        #using self.annotation_cand
        self.annotation = dict()
        for traj_i in self.annotation_cand.keys():
            cand_list = self.annotation_cand[traj_i]
            gps = self.traj.get_gps_by_index(traj_i)
            if measure == 'dist':
                cand_dist_list = [(self.dist2p(gps, x), x) for x in cand_list]
            elif measure == 'dist+pop':
                cand_dist_list = [(self.dist_pop(gps, x), x) for x in cand_list]
            elif measure == 'pop':
                cand_dist_list = [(self.pop(x), x) for x in cand_list]
            
            cand_dist_list.sort(key = lambda x:x[0], reverse=True)
            self.annotation[traj_i] = [x[1] for x in cand_dist_list]
                
            

        
  