prototxt = "/home/srzn/models/frv-9c-call-face/frv-9c-call-face.pt"
caffemodel = "/home/srzn/models/frv-9c-call-face/frv-9c-call-face-20170429.caffemodel"

CLASSES = ('__background__',
		'person','callingphone','sunglasses', 'mask','hat', 		'safety_helmet','helmet','glasses')
active_classes = ['call', 'sunglasses', 'hat', 'safety_helmet', 'helmet', 'mask']
#for analog cameras
label_alias = {'safety_helmet':'helmet'}
active_thds = {}
default_thd = 0.7
#for digital cameras
#active_thds = {'call':0.1, 'sunglasses':0.45, 'hat': 0.3, 'mask':0.1, 'helmet': 0.35}
#default_thd = 0.1

# Scales to use during testing (can list multiple scales)
# Each scale is the pixel size of an image's shortest side
TEST_SCALES = (600,)
## Number of top scoring boxes to keep before apply NMS to RPN proposals
TEST_RPN_PRE_NMS_TOP_N = 6000
## Number of top scoring boxes to keep after applying NMS to RPN proposals
TEST_RPN_POST_NMS_TOP_N = 300
