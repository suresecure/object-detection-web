import os
import optparse
import pickle
import numpy as np
import cv2
import shutil
import json

if __name__ == '__main__':
    parser = optparse.OptionParser()
    # parser.add_option("-d", "--result_dir", dest="result_dir",
                      # help="result directory", metavar="DIR")
    (options, args) = parser.parse_args()
    # img_dir = '/home/mythxcq/july_new_person_events/sun_glasses'
    img_dir = '/root/caffe_upload'
    result_dir = '/root/caffe_upload_detected'
    output_dir = '/root/caffe_upload_draw'

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    for ef in os.listdir(img_dir):
        if os.path.isfile(os.path.join(dir_name, ef)):
            try:
                img_data = cv2.imread(os.path.join(img_dir, ef))
                with open(os.path.join(result_dir, ef), 'r'):
                    targets = pickle.load(f)
                for t in
                for t in targets:
                    cv2.rectangle(img_data, (t['x'],t['y']), (t['x']+t['w'],t['y']+t['h']),
                                      (255,0,0),3)
                cv2.imwrite(os.path.join(focus_imgs_dir, img).rstrip(), img_data)
            except:
                pass

