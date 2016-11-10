import os
import cv2
import shutil

img_dir = '/home/mythxcq/july_new_person_events/call'
gttxt = 'callgt.txt'
resulttxt = '../call_results/call.txt'
lost_dir = '600_02_lost_call'
if not os.path.exists(lost_dir):
    os.makedirs(lost_dir)

with open(gttxt, 'r') as f:
    gtset = f.readlines()
with open(resulttxt, 'r') as f:
    result_set = f.readlines()

intersect = list(set(gtset) & set(result_set))

print len(result_set),len(intersect), len(gtset)

recall = float(len(intersect))/len(gtset)

# lost_target = list(set(gtset)-set(intersect))

print 'recall: '+str(recall)
# print 'wrong detection: '+str(len(result_set)-len(intersect))

lost_set = list(set(gtset)-set(result_set))
for ej in lost_set:
    shutil.copy(os.path.join(img_dir, ej).rstrip(), os.path.join(lost_dir, ej).rstrip())
    # img = cv2.imread(os.path.join(img_dir, ej).rstrip())
    # cv2.imshow('img', img)
    # cv2.waitKey(0)
# print lost_set[1:11]
