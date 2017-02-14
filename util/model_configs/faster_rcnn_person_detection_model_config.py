prototxt = "/home/mythxcq/models/faster-rcnn-person-detection-model/test.prototxt"
caffemodel = "/home/mythxcq/models/faster-rcnn-person-detection-model/vgg16_faster_rcnn_20160425.caffemodel"

CLASSES = ('__background__',
           'aeroplane', 'bicycle', 'bird', 'boat',
           'bottle', 'bus', 'car', 'cat', 'chair',
           'cow', 'diningtable', 'dog', 'horse',
           'motorbike', 'person', 'pottedplant',
           'sheep', 'sofa', 'train', 'tvmonitor')
#haoyun or 180/360 degrees of hongshi
active_classes = ['person']
active_thds = ['person': 0.8]
default_thd = 0.1
#nms = 0.3

# Scales to use during testing (can list multiple scales)
# Each scale is the pixel size of an image's shortest side
TEST_SCALES = (600,)
## Number of top scoring boxes to keep before apply NMS to RPN proposals
TEST_RPN_PRE_NMS_TOP_N = 6000
## Number of top scoring boxes to keep after applying NMS to RPN proposals
TEST_RPN_POST_NMS_TOP_N = 300

# prototxt = "/home/mythxcq/models/faster-rcnn-person-detection-model/test.prototxt"
# caffemodel = "/home/mythxcq/models/faster-rcnn-person-detection-model/vgg16_faster_rcnn_21c_hs.caffemodel"

# CLASSES = ('__background__',
           # 'aeroplane', 'bicycle', 'bird', 'boat',
           # 'bottle', 'bus', 'car', 'cat', 'chair',
           # 'cow', 'diningtable', 'dog', 'horse',
           # 'motorbike', 'person', 'pottedplant',
           # 'sheep', 'sofa', 'train', 'tvmonitor')
# active_classes = ['person']

# # Scales to use during testing (can list multiple scales)
# # Each scale is the pixel size of an image's shortest side
# TEST_SCALES = (240,)
# ## Number of top scoring boxes to keep before apply NMS to RPN proposals
# TEST_RPN_PRE_NMS_TOP_N = 1000
# ## Number of top scoring boxes to keep after applying NMS to RPN proposals
# TEST_RPN_POST_NMS_TOP_N = 100
# # thd = 0.4
