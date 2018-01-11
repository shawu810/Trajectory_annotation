# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 10:09:55 2018

@author: fxw133-admin
"""

from query import SurveyItem
import difflib
import pdb
class Evaluation(object):
    @classmethod
    def ismatch(clf, annotations, item, topk=5):
        for i in range(min(topk, len(annotations))):
            if difflib.SequenceMatcher(None, item.item, annotations[i].name).ratio() > 0.5:
                return True
        return False    
    
    
    
    @classmethod
    def topk_annotation_acc(clf, user, topk):
        # user.annotation and user.label
        correct = 0
        tot = 0
        for traj_i in user.label:
            if traj_i not in user.annotation:
                continue
            if user.label[traj_i] is None :
                continue
            if user.label[traj_i] == 'home':
                continue
            ground_truth = user.label[traj_i]
            #pdb.set_trace()
            if ',' in ground_truth:
                ground_truth = ground_truth.split(',')
            else:
                ground_truth = [ground_truth]
            item_list = [user.survey.get_item_bytype(x) for x in ground_truth]
            for item in item_list:
                if item.item == 'noname but has address':
                    continue
                if Evaluation.ismatch(user.annotation[traj_i], item, topk):
                    correct += 1
                    break
            tot += 1
        return correct, tot