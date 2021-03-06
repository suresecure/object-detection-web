prototxt = "/home/mythxcq/models/faster-rcnn-vgg16-22c-phonecall/test.pt"
# caffemodel = "/home/mythxcq/models/faster-rcnn-vgg16-22c-phonecall/vgg16_faster_rcnn_22c_iter_100000.caffemodel"
caffemodel = "/home/mythxcq/models/faster-rcnn-vgg16-22c-phonecall/vgg16_faster_rcnn_multi_22c_iter_100000.caffemodel"

CLASSES = ('__background__',
           'aeroplane', 'bicycle', 'bird', 'boat',
           'bottle', 'bus', 'car', 'cat', 'chair',
           'cow', 'diningtable', 'dog', 'horse',
           'motorbike', 'person', 'pottedplant',
           'sheep', 'sofa', 'train', 'tvmonitor', 'call')
active_classes = ['call']

# Scales to use during testing (can list multiple scales)
# Each scale is the pixel size of an image's shortest side
TEST_SCALES = (600,)
## Number of top scoring boxes to keep before apply NMS to RPN proposals
TEST_RPN_PRE_NMS_TOP_N = 1000
## Number of top scoring boxes to keep after applying NMS to RPN proposals
TEST_RPN_POST_NMS_TOP_N = 100
