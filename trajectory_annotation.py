# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 16:24:54 2018

@author: fxw133-admin
"""
import cPickle as pickle
import pdb
import glob
import numpy

from Evaluation import Evaluation
TOPK = 20

PROCESS_USER = False
PROPERGATE_LABEL = False
PREPARE_ANNOTATION = True


PATH_PREFIX = 'C:\\Users\\fxw133\\Desktop\\chicago-movement\\data\\'
PATH2_SURVEY_FILE = PATH_PREFIX + 'ActivitySurvey.csv'
PATH2_DEMO_FILE = PATH_PREFIX + 'demo.csv'
PATH2_TRAJECTORY_FILES = PATH_PREFIX + 'chicago_trajectories\\Original\\GPS_Time1\\*.csv'
    
## output
PATH2_PROCESSED = PATH_PREFIX + 'trajectory_annotation\\processed_user\\'
PATH2_CODEING = "C:\\Users\\fxw133\\Desktop\\chicago-movement\\data\\trajectory_annotation\\GEOCODE.pkle"

PATH2_VENUEDB = "C:\\Users\\fxw133\\Desktop\\chicago-movement\\data\\grid_indexed_venues.pkle"


user_files = [u for u in glob.glob(PATH2_PROCESSED + '*_ground_cand.pkle')] 

r_list = list()

for ufile in user_files:
    one_user = pickle.load(open(ufile, 'rb')) 
    one_user.annotate_by_measure(measure='dist+pop')
    correct, tot = Evaluation().topk_annotation_acc(one_user, 5)
    print one_user.uid, correct, tot
    r_list.append((correct, tot, correct/float(tot)))
    #pdb.set_trace()