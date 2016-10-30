import os
import optparse
import settings
import logging
import time
import model_config

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
    return person_detection_net = caffe.Net(prototxt, caffemodel, caffe.TEST)

CLASSES = model_config.CLASSES

def detect_image(net, im):
    """Detect object classes in an image using pre-computed object proposals."""

    # Detect all object classes and regress object bounds
    timer = Timer()
    timer.tic()
    scores, boxes = im_detect(net, im)
    timer.toc()
    print(str(current_process().index)+' Detection took {:.3f}s for '
           '{:d} object proposals').format(timer.total_time, boxes.shape[0])

    # Visualize detections for each class
    # CONF_THRESH = 0.0

    CONF_THRESH = 0.4
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
            targets.append({'x':x,'y':y,'w':w,'h':h, 'class': ac})
    return targets

    # targets = []
    img = cv2.imdecode(np.asarray(bytearray(imgstream), dtype=np.uint8), -1)
    return detect_image(person_detection_net, img)
    # result = detect_image(person_detection_net, img)

    # for r in result:
        # x = (int)(r[0].item())
        # y = (int)(r[1].item())
        # w = (int)(r[2].item())-x
        # h = (int)(r[3].item())-y
        # targets.append({'x':x,'y':y,'w':w,'h':h})

    # return result
if __name__ == 'main':

