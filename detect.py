import os
import optparse
import logging
import time
import pickle
import json
# import rfcn_person_detection_model_config as model_config
import phone_call_model_config as model_config
# import model_config as model_config

import _init_paths
from utils.timer import Timer
os.environ['GLOG_minloglevel'] = '2'
import numpy as np
import cv2
import caffe
from fast_rcnn.config import cfg
from fast_rcnn.test import im_detect
from fast_rcnn.nms_wrapper import nms

def init_net(index):
    prototxt = model_config.prototxt
    caffemodel = model_config.caffemodel

    cfg.TEST.HAS_RPN = True  # Use RPN for proposals
    cfg.TEST.BBOX_REG = False
    cfg.TEST.SCALES = model_config.TEST_SCALES
    cfg.TEST.RPN_PRE_NMS_TOP_N = model_config.TEST_RPN_PRE_NMS_TOP_N
    cfg.TEST.RPN_POST_NMS_TOP_N = model_config.TEST_RPN_POST_NMS_TOP_N

    caffe.set_mode_gpu()
    caffe.set_device(index)
    cfg.GPU_ID = index
    return caffe.Net(prototxt, caffemodel, caffe.TEST)

CLASSES = model_config.CLASSES

def detect_image(net, im):
    """Detect object classes in an image using pre-computed object proposals."""

    # Detect all object classes and regress object bounds
    timer = Timer()
    timer.tic()
    scores, boxes = im_detect(net, im)
    timer.toc()
    print('Detection took {:.3f}s for '
           '{:d} object proposals').format(timer.total_time, boxes.shape[0])

    # Visualize detections for each class
    # CONF_THRESH = 0.0

    CONF_THRESH = 0.01
    NMS_THRESH = 0.1

    targets = []
    for ac in model_config.active_classes:
        target_idx = CLASSES.index(ac)
        if len(boxes[1]) == 8:
            target_boxes = boxes[:, 4:8]
        elif len(boxes[1]) == len(CLASSES)*4:
            target_boxes = boxes[:, 4*target_idx:4*(target_idx + 1)]
        else:
            error
        target_scores = scores[:, target_idx]
        target_dets = np.hstack((target_boxes,
                      target_scores[:, np.newaxis])).astype(np.float32)
        target_keep = nms(target_dets, NMS_THRESH)
        target_dets = target_dets[target_keep, :]
        target_dets = target_dets[np.where(target_dets[:, -1] >= CONF_THRESH)]
        for r in target_dets:
            x = (int)(r[0].item())
            y = (int)(r[1].item())
            w = (int)(r[2].item())-x
            h = (int)(r[3].item())-y
            targets.append({'x':x,'y':y,'w':w,'h':h, 'class': ac, 'conf': r[4]})
    return targets

if __name__ == '__main__':
    person_detection_net = init_net(1)
    source_dir = '/home/mythxcq/july_new_person_events/7005/'
    # source_dir = '/home/mythxcq/july_new_person_events/call/'
    # source_dir = '/home/mythxcq/mycalltest'
    # source_dir = 'util/lost_call'
    # result_dir = 'my_results'
    # result_dir = 'lost_results'
    # result_dir = 'new_model_call_results'
    result_dir = '600_1000_100_call_results'
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    # result_dirs = {}
    # result_txts = {}
    # for ec in model_config.active_classes:
        # result_dirs[ec] = result_dir+'/'+ec
        # result_txts[ec] = open(result_dir+'/'+ec+'.txt', 'w')
    # result_txt = open(result_dir + '/'+'result.txt', 'w')

    # for k in result_dirs:
    # if not os.path.exists(result_dirs[k]):
        # os.makedirs(result_dirs[k])

    current_num = 0
    result_list = []
    for eachjpg in os.listdir(source_dir):
        if os.path.isfile(os.path.join(source_dir, eachjpg)) and eachjpg.endswith('.jpg'):
            # print eachjpg
            current_num+=1
            img = cv2.imread(os.path.join(source_dir, eachjpg))
            # cv2.imshow('origimg', img)
            # cv2.waitKey(0)
            targets = detect_image(person_detection_net, img)
            # status = {}
            # for ec in model_config.active_classes:
                # status[ec] = False

            # for et in targets:
                # cv2.rectangle(img, (et['x'], et['y']), (et['x']+et['w'], et['y']+et['h']),
                              # (255,0,0))
                # status[et['class']] = True
            # for k in status:
                # if status[k]:
                    # cv2.imwrite(os.path.join(result_dirs[k], eachjpg), img)
                    # result_txts[k].write(eachjpg + '\n')
            if(len(targets)>0):
                result_list.append((eachjpg, targets))
                # result_txt.write(eachjpg+':\n')
                # result_txt.write(targets)
            print 'current_num: ', current_num

    # close all txt files
    with open(result_dir+'/result.pickle', 'w') as f:
        pickle.dump(result_list, f)
    # with open(result_dir + '/'+'result.txt', 'w') as f:
    # for k in result_txts:
        # result_txts[k].close()

