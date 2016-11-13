import os
import pickle
import numpy as np
import cv2

def calc_recall(results, gt, conf_thd):
    conf_results = []
    recall = []
    recall_img = []
    for r in results:
        detected = False
        for t in r[1]:
            if t['conf'] > conf_thd and t['class'] == 'sunglass':
                conf_results.append(r)
                detected = True
                break
        if detected and r[0] in gt:
            recall.append(r)
            recall_img.append(r[0])
    lost_imgs = list(set(gt)-set(recall_img))

    return recall, conf_results, lost_imgs

def get_roc():
    with open('../23c-call-sunglass-results/300-1000-100.pickle') as f:
        results = pickle.load(f)

    with open('sunglassgt.txt') as f:
        gt = f.read().split()

    all_recall = []
    recall_txt = open('23c-sunglass-recall.txt', 'w')
    for i in np.arange(0.01, 0.6, 0.01):
        recall, detected, lost_imgs = calc_recall(results, gt, i)
        recall_txt.write(str((i, len(recall), len(detected)))+'\n')
        print i,recall,detected

    recall_txt.close()

if __name__ == '__main__':
    img_dir = '/home/mythxcq/july_new_person_events/sun_glasses'
    with open('../23c-call-sunglass-results/300-1000-100.pickle') as f:
        results = pickle.load(f)

    with open('sunglassgt.txt') as f:
        gt = f.read().split()

    conf_thd = 0.01

    recall, detected, lost_imgs = calc_recall(results, gt, conf_thd)
    print len(recall), len(detected), len(lost_imgs)
    # for img in lost_imgs:
        # img = cv2.imread(os.path.join(img_dir, img).rstrip())
        # cv2.imshow('img', img)
        # cv2.waitKey(0)

    for r in recall:
        img = cv2.imread(os.path.join(img_dir, r[0]).rstrip())
        for t in r[1]:
            if t['class'] == 'sunglass' and t['conf']>conf_thd:
                cv2.rectangle(img, (t['x'],t['y']), (t['x']+t['w'],t['y']+t['h']),
                              (255,0,0),3)
        cv2.imshow('timg', img)
        cv2.waitKey(0)
    # shutil.copy(os.path.join(img_dir, ej).rstrip(), os.path.join(lost_dir, ej).rstrip())
    # img = cv2.imread(os.path.join(img_dir, ej).rstrip())
    # cv2.imshow('img', img)
    # cv2.waitKey(0)

