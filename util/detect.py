import os
import optparse
import logging
import time
import pickle
import json
import model_configs.rfcn_person_detection_model_config as model_config
# import phone_call_model_config as model_config
# import call_sunglass_23c_model_config as model_config
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

def detect_file(file_name, conf_thd, object_detection_net):
    img = cv2.imread(file_name)
    targets = detect_image(object_detection_net, img)
    print targets
    for t in targets:
        if t['conf'] > conf_thd:
            print 'draw'
            cv2.rectangle(img, (t['x'],t['y']), (t['x']+t['w'],t['y']+t['h']),
                          (255,0,0),3)
    cv2.imwrite('detect_file_result.jpg', img)
    cv2.imshow('img', img)
    cv2.waitKey(0)

def detect_dir(dir_name, result_dir, show_result, store_result, object_detection_net):
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    current_num = 0
    result_list = []
    for eachjpg in os.listdir(dir_name):
        if os.path.isfile(os.path.join(dir_name, eachjpg)) and eachjpg.endswith('.jpg'):
            # print eachjpg
            current_num+=1
            img = cv2.imread(os.path.join(dir_name, eachjpg))
            targets = detect_image(object_detection_net, img)

            if show_result:
                for et in targets:
                    cv2.rectangle(img, (et['x'], et['y']), (et['x']+et['w'], et['y']+et['h']),
                                  (255,0,0))
                    cv2.imshow('result', img)
                    cv2.waitKey(0)
            if store_result:
                for k in status:
                    cv2.imwrite(os.path.join(result_dirs, eachjpg), img)
            if(len(targets)>0):
                result_list.append((eachjpg, targets))
                print targets
                # result_txt.write(eachjpg+':\n')
                # result_txt.write(targets)
            print 'current_num: ', current_num

    # close all txt files
    file_name = '/{0}-{1}-{2}.pickle'.format(model_config.TEST_SCALES[0],
                                             model_config.TEST_RPN_PRE_NMS_TOP_N,
                                             model_config.TEST_RPN_POST_NMS_TOP_N)
    with open(result_dir+file_name, 'w') as f:
        pickle.dump(result_list, f)

if __name__ == '__main__':
    parser = optparse.OptionParser()

    parser.add_option("-c", "--conf",
                      dest="conf_thd", default=0.1, type='float',
                      help="confidence threshold")
    parser.add_option("-g", "--gpu",
                      dest="gpuid", default=0, type='int',
                      help="gpu id")
    parser.add_option("-s", "--show",
                      action="store_true", dest="show_result", default=False,
                      help="show result")
    parser.add_option("-t", "--store",
                      action="store_true", dest="store_result", default=False,
                      help="store result")
    # parser.add_option("-d", "--result_dir", dest="result_dir",
                      # help="result directory", metavar="DIR")
    (options, args) = parser.parse_args()

    object_detection_net = init_net(options.gpuid)
    input_name = args[0]
    result_dir = 'results'
    if len(args)>1:
        result_dir = args[1]
    if os.path.isfile(input_name):
        detect_file(input_name, options.conf_thd, object_detection_net)
    elif os.path.isdir(input_name):
        detect_dir(input_name, result_dir, options.show_result, options.store_result, object_detection_net)

