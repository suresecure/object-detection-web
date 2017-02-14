prototxt = "/home/mythxcq/models/faster-rcnn-vgg16-27c-call-face/test_27c.pt"
caffemodel = "/home/mythxcq/models/faster-rcnn-vgg16-27c-call-face/vgg16_faster_rcnn_27c_1117_iter_100000.caffemodel"

CLASSES = ('__background__',
           'aeroplane', 'bicycle', 'bird', 'boat',
           'bottle', 'bus', 'car', 'cat', 'chair',
           'cow', 'diningtable', 'dog', 'horse',
           'motorbike', 'person', 'pottedplant',
           'sheep', 'sofa', 'train', 'tvmonitor',
           'call', 'sunglasses', 'mask', 'hat', 'helmet', 'glasses')
active_classes = ['call', 'sunglasses', 'hat', 'helmet', 'mask']
#for analog cameras
active_thds = {'call':0.1, 'sunglasses':0.45, 'hat': 0.3, 'mask':0.1, 'helmet': 0.35}
default_thd = 0.1
#for digital cameras
#active_thds = {'call':0.1, 'sunglasses':0.45, 'hat': 0.3, 'mask':0.1, 'helmet': 0.35}
#default_thd = 0.1

# Scales to use during testing (can list multiple scales)
# Each scale is the pixel size of an image's shortest side
TEST_SCALES = (300,)
## Number of top scoring boxes to keep before apply NMS to RPN proposals
TEST_RPN_PRE_NMS_TOP_N = 1000
## Number of top scoring boxes to keep after applying NMS to RPN proposals
TEST_RPN_POST_NMS_TOP_N = 100
