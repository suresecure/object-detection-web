import os
import optparse
import pickle
import numpy as np
import cv2
import shutil

def calc_recall(results, gt, conf_thd):
    detected_result_sets = {}
    for g in gt:
        detected_result_sets[g] = set()
    for r in results:
        for t in r[1]:
            if t['conf'] > conf_thd:
                detected_result_sets[t['class']].add(r[0])

    recall_results = {}
    for g in gt:
        recall_set = detected_result_sets[g]&set(gt[g])
        lost_set = set(gt[g]) - recall_set
        recall_results[g] = (list(recall_set),
                             list(lost_set),
                             list(detected_result_sets[g]-recall_set))
        # if detected and r[0] in gt:
            # recall.append(r)
            # recall_img.append(r[0])
    # lost_imgs = list(set(gt)-set(recall_img))
    # return recall, conf_results, lost_imgs

    return recall_results

if __name__ == '__main__':
    parser = optparse.OptionParser()
    # parser.add_option("-d", "--result_dir", dest="result_dir",
                      # help="result directory", metavar="DIR")
    (options, args) = parser.parse_args()
    # img_dir = '/home/mythxcq/july_new_person_events/sun_glasses'
    img_dir = '/home/mythxcq/july_new_person_events/'
    result_file = '../23c-call-sunglass-results/300-1000-100.pickle'
    img_dir = args[0]
    result_file = args[1]
    with open(result_file) as f:
        results = pickle.load(f)

    with open(os.path.join(img_dir, 'gt.pickle')) as f:
        gt = pickle.load(f)

    # conf_thd = 0.01
    recall_results_dict = {}
    for i in np.arange(0.01, 0.6, 0.01):
        recall_results = calc_recall(results, gt, i)
        # print i,':'
        for c,v in recall_results.iteritems():
            if c in recall_results_dict:
                recall_results_dict[c].append((i, v[0], v[1], v[2]))
            else:
                recall_results_dict[c] = [(i, v[0], v[1], v[2])]
    for k,v in recall_results_dict.iteritems():
        print k
        for e in v:
            print e[0], len(e[1]), len(e[2]), len(e[3])

    # print len(recall), len(detected), len(lost_imgs)
    # for img in lost_imgs:
        # img = cv2.imread(os.path.join(img_dir, img).rstrip())
        # cv2.imshow('img', img)
        # cv2.waitKey(0)

    # for r in recall:
        # img = cv2.imread(os.path.join(img_dir, r[0]).rstrip())
        # for t in r[1]:
            # if t['class'] == 'sunglass' and t['conf']>conf_thd:
                # cv2.rectangle(img, (t['x'],t['y']), (t['x']+t['w'],t['y']+t['h']),
                              # (255,0,0),3)
        # cv2.imshow('timg', img)
        # cv2.waitKey(0)
    focus_imgs_dir = 'focus_imgs'
    if os.path.exists(focus_imgs_dir):
        shutil.rmtree(focus_imgs_dir)
    os.makedirs(focus_imgs_dir)

    focus_img_set = recall_results_dict['mask'][-20][2]
    for img in focus_img_set:
        shutil.copy(os.path.join(img_dir, '7005', img).rstrip(), os.path.join(focus_imgs_dir, img).rstrip())
    # img = cv2.imread(os.path.join(img_dir, ej).rstrip())
    # cv2.imshow('img', img)
    # cv2.waitKey(0)

