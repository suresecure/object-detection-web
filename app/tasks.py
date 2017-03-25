import os
import optparse
import settings
import celery
import logging
import time
import model_config
import hs_fisheye

the_celery = celery.Celery('tasks')
the_celery.config_from_object(settings)

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
    print prototxt

    cfg.TEST.HAS_RPN = True  # Use RPN for proposals
    cfg.TEST.BBOX_REG = False
    cfg.TEST.SCALES = model_config.TEST_SCALES
    cfg.TEST.RPN_PRE_NMS_TOP_N = model_config.TEST_RPN_PRE_NMS_TOP_N
    cfg.TEST.RPN_POST_NMS_TOP_N = model_config.TEST_RPN_POST_NMS_TOP_N
    print cfg

    caffe.set_mode_gpu()
    print index
    # index = 1
    print "device index:"+str(index)
    caffe.set_device(index)
    cfg.GPU_ID = index
    global person_detection_net
    person_detection_net = caffe.Net(prototxt, caffemodel, caffe.TEST)

from celery.signals import worker_process_init
from celery.signals import worker_init
from billiard import current_process
@worker_init.connect
def init_workers(sender=None, headers=None, body=None, **kwargs):
    print "init workers"
    # batch_size = 5
@worker_process_init.connect
def configure_workers(sender=None, headers=None, body=None, **kwargs):
    init_net(current_process().index)

CLASSES = model_config.CLASSES
# ('__background__',
           # 'aeroplane', 'bicycle', 'bird', 'boat',
           # 'bottle', 'bus', 'car', 'cat', 'chair',
           # 'cow', 'diningtable', 'dog', 'horse',
           # 'motorbike', 'person', 'pottedplant',
           # 'sheep', 'sofa', 'train', 'tvmonitor')

def intersection(a,b):
  x = max(a[0], b[0])
  y = max(a[1], b[1])
  w = min(a[0]+a[2], b[0]+b[2]) - x
  h = min(a[1]+a[3], b[1]+b[3]) - y
  if w<0 or h<0: return () # or (0,0,0,0) ?
  return (x, y, w, h)

def compare_img(img, last_img, inter_area):
    sad = np.sum(np.absolute(img[inter_area[1]:inter_area[1]+inter_area[3],
                           inter_area[0]:inter_area[0]+inter_area[2]] -
                       last_img[inter_area[1]:inter_area[1]+inter_area[3],
                           inter_area[0]:inter_area[0]+inter_area[2]]))
    if sad/(inter_area[2]*inter_area[3]) < 10:
        return True
    else:
        return False

def detect_image(net, im, fisheye_type, last_image_file, last_targets):
    """Detect object classes in an image using pre-computed object proposals."""

    # Detect all object classes and regress object bounds
    timer = Timer()
    timer.tic()
    undist_type = int(fisheye_type)
    if undist_type != -1:
        im = hs_fisheye.image_undistortion(im, undist_type)
    scores, boxes = im_detect(net, im)
    timer.toc()
    print(str(current_process().index)+' Detection took {:.3f}s for '
           '{:d} object proposals').format(timer.total_time, boxes.shape[0])

    # Visualize detections for each class
    # CONF_THRESH = 0.0

    CONF_THRESH = 0.4
    NMS_THRESH = 0.1
    active_thds = {}
    if hasattr(model_config, 'active_thds'):
        active_thds = model_config.active_thds
    if hasattr(model_config, 'default_thd'):
        CONF_THRESH = model_config.default_thd

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
        conf_thd = CONF_THRESH
        if ac in active_thds:
            conf_thd = active_thds[ac]
        target_dets = target_dets[np.where(target_dets[:, -1] >= conf_thd)]
        for r in target_dets:
            x = (int)(r[0].item())
            y = (int)(r[1].item())
            w = (int)(r[2].item())-x
            h = (int)(r[3].item())-y
            if undist_type != -1:
                (x,y,w,h) = hs_fisheye.point_projection(x,y,w,h, undist_type)
            targets.append({'x':x,'y':y,'w':w,'h':h, 'label': ac, 'conf': int(100.0*r[4])})

    if last_image_file is not None and last_targets is not None:
        #load last image file
        try:
            last_img = cv2.imread(last_image_file)
            if last_img.shape != im.shape:
                filtered_targets = targets
            else:
                filtered_targets = []
                for t in targets:
                    filtered = False
                    for lt in last_targets:
                        t_rect = (t['x'], t['y'], t['w'], t['h'])
                        lt_rect = (lt['x'], lt['y'], lt['w'], lt['h'])
                        inter_rect = intersection(t, lt)
                        inter_area = inter_rect[2]*inter_rect[3]
                        if (inter_area>(t_rect[2]*t_rect[3]*0.95) and
                            inter_area>(lt_rect[2]*lt_rect[3]*0.95)):
                            filtered = compare_img(im, last_img, inter_area)
                            # only one possible intersected target
                            break

                    if not filtered:
                        filtered_targets.append(t)

        except Exception, ex:
            print(ex)
            filtered_targets = targets
        finally:
            pass

    return targets, filtered_targets

@the_celery.task(name="tasks.object_detection_task", queue="important")
def object_detection_task(imgstream, secure_filename, fisheye_type, last_image_file, last_targets):
    img = cv2.imdecode(np.asarray(bytearray(imgstream), dtype=np.uint8), -1)
    return detect_image(person_detection_net, img, fisheye_type, last_image_file, last_targets)
