from os import listdir
from os.path import isfile, join
import glob

import csv
import datetime
import time
import matplotlib.pyplot as plt

import cPickle as pickle

from query import GPSSample
from query import User
from query import SurveyItem
from query import Survey

import numpy as np

def get_user_file_list(PATH2_TRAJECTORY_FILES):
    onlyfiles = glob.glob(PATH2_TRAJECTORY_FILES)
    user_ids = [traj_file[-18:-13] for traj_file in onlyfiles]
    return dict(zip(user_ids, onlyfiles)) 

def preprocessing(PATH2_TRAJECTORY_FILES, PATH2_SURVEY_DATA, 
                  PATH2_DEMO_DATA, PATH2_CODEING, PATH2_PDATA):
    uid_indexed_raw_data = dict()
    uid_path_map = get_user_file_list(PATH2_TRAJECTORY_FILES)
    preprocess_movement(uid_path_map, uid_indexed_raw_data)
    preprocess_survey(PATH2_SURVEY_DATA, uid_indexed_raw_data)
    preprocess_demo(PATH2_DEMO_DATA, uid_indexed_raw_data)
    
    
    coded_address = pickle.load(open(PATH2_CODEING, 'rb'))
    
    preporcess_geo_code(uid_indexed_raw_data, coded_address, 
                        PATH2_CODEING, PATH2_PDATA)

    return uid_indexed_raw_data



def preporcess_geo_code(uid_indexed_raw_data, coded_address, 
                        PATH2_CODEING, PATH2_PDATA):
    
    for uid in uid_indexed_raw_data:
        print 'geo coding', uid
        user = uid_indexed_raw_data[uid]
        user.survey.geo_coding_withupdate(coded_address)
        pickle.dump(coded_address, open(PATH2_CODEING, 'wb'))
        pickle.dump(user, open(PATH2_PDATA + uid + '.pkle', 'wb'))


def preprocess_movement(uid_path_map, uid_indexed_raw_data):
    
    for uid in uid_path_map:
        raw_user_data = User(uid)
        filename = uid_path_map[uid]
        with open(filename, 'rb') as csvfile:
            print filename
            csvreader = csv.DictReader(csvfile)
            for row in csvreader:
                local_time_string = row[' LOCAL DATE'] + row[' LOCAL TIME'] 
                local_time = datetime.datetime.strptime(local_time_string, 
                                               " %Y/%m/%d %H:%M:%S") # datetime object
                lat_sign = 1 if row[' N/S'] == ' N' else -1 
                lon_sign = 1 if row[' E/W'] == ' E' else -1
                lat = float(row[' LATITUDE']) * lat_sign
                lon = float(row[' LONGITUDE']) * lon_sign
                
                km_per_hour = float(row[' SPEED'].replace("km/h", ""))
                raw_user_data.traj.add_point(GPSSample(lat, lon, local_time, km_per_hour))
        uid_indexed_raw_data[uid] = raw_user_data


def preprocess_survey(PATH2_SURVEY_DATA, uid_indexed_raw_data):
    with open(PATH2_SURVEY_DATA, 'rb') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            if '\xef\xbb\xbfpart_id' in row:
                uid = row['\xef\xbb\xbfpart_id']
            else:
                uid = row['part_id']
            if uid not in uid_indexed_raw_data:
                print 'no user trajectory: ' + uid
                continue
            for key in row:
                if 'add' in key and row[key].strip() != "":
                    address = row[key] + ' Chicago, IL'
                    prefix = key.split("_")[0] 
                    if prefix + '_nm' in row:
                        name = row[prefix + '_nm']
                    else:
                        name = 'noname but has address'
                    item = SurveyItem(name, prefix, address)
                    uid_indexed_raw_data[uid].survey.add_item(prefix ,item)
                    
                    
def preprocess_demo(PATH2_DEMO_DATA, uid_indexed_raw_data):
    with open(PATH2_DEMO_DATA, 'rb') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            user_id = row['id']
            res1 = row['res1_d1']
            home = SurveyItem(user_id + '_home', 'home', res1)
            if user_id not in uid_indexed_raw_data:
                continue
            uid_indexed_raw_data[user_id].survey.add_item('home', home)



def generate_labels(PATH2_PROCESSED, DIST_THRES, SPEED_THRES):
    user_files = [u for u in glob.glob(PATH2_PROCESSED + '*.pkle')]
    label_r = list()
    dlabel_r = list()
    nhlabel_r = list()
        
    for ufile in user_files:
        print ufile   
        one_user = pickle.load(open(ufile, 'rb')) 
        one_user.generate_labels(SPEED_THRES=SPEED_THRES, DIST_THRES=DIST_THRES)    
        label, double_label, total, speed_filter, cc = one_user.print_label_stats()
        label_r.append(float(label) / float(total - speed_filter))
        dlabel_r.append(float(double_label) / float(total - speed_filter))

        hc = cc['home'] if 'home' in cc else 0

        nhlabel_r.append(float(label - hc) / float(total - speed_filter - hc))
        fname =  PATH2_PROCESSED + one_user.uid + '_ground.pkle'
        pickle.dump(one_user, open(fname, 'wb'))
        
    return label_r, dlabel_r, nhlabel_r
    
def generate_annotation_candidate(PAHT2_PROCESSED, ANNOTATION_DIST_THRES, VDB_GRID_SIZE):
    print 'loading poi'
    mapped_venue = pickle.load(open(PATH2_VENUEDB, 'rb'))
    print 'done loading'
    user_files = [u for u in glob.glob(PATH2_PROCESSED + '*_ground.pkle')]  
    has_r = list()
    has5_r = list()
    has2_r = list()
    over_r = list()
    for ufile in user_files:
        one_user = pickle.load(open(ufile, 'rb')) 
        one_user.prepare_annotation(mapped_venue, VDB_GRID_SIZE, ANNOTATION_DIST_THRES)
        overcount, hasnearby, hasnearby2, hasnearby5, tot = one_user.print_annotation_stats() 
        print one_user.uid, overcount, hasnearby, hasnearby2, hasnearby5, tot
        
        has5_r.append(float(hasnearby5) / float(tot))        
        has2_r.append(float(hasnearby2) / float(tot))        
        has_r.append(float(hasnearby) / float(tot))                  
        over_r.append(float(overcount) / float(hasnearby))
        
        fname =  PATH2_PROCESSED + one_user.uid + '_ground_cand.pkle'
        pickle.dump(one_user, open(fname, 'wb'))
    
    return np.array([over_r, has_r, has2_r, has5_r])



PROCESS_USER = False
PROPERGATE_LABEL = False
PREPARE_ANNOTATION = True


PATH_PREFIX = 'C:\\Users\\fxw133\\Desktop\\chicago-movement\\data\\'
PATH2_SURVEY_FILE = PATH_PREFIX + 'ActivitySurvey.csv'
PATH2_DEMO_FILE = PATH_PREFIX + 'demo.csv'
PATH2_TRAJECTORY_FILES = PATH_PREFIX + 'chicago_trajectories\\Original\\GPS_Time1\\*.csv'
    
## output
PATH2_PROCESSED = PATH_PREFIX + 'trajectory_annotation\\processed_user\\'
PATH2_CODEING = ".\\VenueDB\\\\GEOCODE.pkle"

PATH2_VENUEDB = ".\\VenueDB\\grid_indexed_venues.pkle"
if PROCESS_USER:  
    ## preprocessing              
    udata = preprocessing(PATH2_TRAJECTORY_FILES, 
                          PATH2_SURVEY_FILE, 
                          PATH2_DEMO_FILE, 
                          PATH2_CODEING, 
                          PATH2_PROCESSED)
    
if PROPERGATE_LABEL:
    #pickle.dump(udata, open(PATH2_PDATA + 'processed.pkle', 'wb')
    import numpy as np
    
    DIST_THRES = 0.001 * 2
    SPEED_THRES = 5 # KM/H
    label_r, dlabel_r, nhlabel_r = generate_labels(PATH2_PROCESSED, 
                                                   DIST_THRES, 
                                                   SPEED_THRES)
    np.savetxt('label_stats_D220_S5.csv', 
               np.array([label_r, dlabel_r, nhlabel_r]), 
               delimiter=',' ,fmt='%s')

if PREPARE_ANNOTATION:
    VENUEDB_GRID_SIZE = 0.005
    ANNOTATION_THRES = 0.001
    stat = generate_annotation_candidate(PATH2_PROCESSED, 
                                         ANNOTATION_THRES, 
                                         VENUEDB_GRID_SIZE)    
    np.savetxt('prepare_stats.csv', 
               stat, delimiter=',', 
               fmt='%s')

    
    







# r
      