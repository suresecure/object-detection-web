import os
import optparse
import pickle
import numpy as np
import cv2
import shutil
import focus_thds


def calc_recall(results, gt, conf_thd):
    detected_result_sets = {}
    for g in gt:
        detected_result_sets[g] = set()
    for imgfile in results:
        for target in results[imgfile]:
            if target['conf'] > conf_thd:
                detected_result_sets[target['label']].add(imgfile)

    recall_results = {}
    for g in gt:
        recall_set = detected_result_sets[g] & set(gt[g])
        lost_set = set(gt[g]) - recall_set
        # recall(true_positive), lost(false_negtive), wrong(false_postive)
        recall_results[g] = (list(recall_set),
                             list(lost_set),
                             list(detected_result_sets[g] - recall_set))
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
    # img_dir = args[0]
    ground_truth_file = args[0]
    result_file = args[1]
    with open(result_file) as f:
        results = pickle.load(f)

    # with open(os.path.join(img_dir, 'gt.pickle')) as f:
    with open(ground_truth_file) as f:
        gt = pickle.load(f)

    origin_img_dir = os.path.dirname(ground_truth_file)
    result_dir = os.path.dirname(result_file)

    # conf_thd = 0.01
    recall_results_dict = {}
    thd_start = 0.1
    thd_stop = 0.9
    thd_step = 0.01
    for i in np.arange(thd_start, thd_stop, thd_step):
        recall_results = calc_recall(results, gt, i)
        # print i,':'
        for c, v in recall_results.iteritems():
            if c in recall_results_dict:
                recall_results_dict[c].append(v)
            else:
                recall_results_dict[c] = [v]
    for label in recall_results_dict:
        print label
        for idx, acc in enumerate(recal_results_dict[label]):
            print thd_start + thd_step * idx, len(acc[0]), len(acc[1]), len(acc[2])

    for label in focus_thds.FOCUS_THDS:
        thd = focus_thds.FOCUS_THDS[label]
        path_name = label + str(thd)
        focus_label_path = os.path.join(result_dir, path_name)
        if os.path.exists(focus_label_path):
            shutil.rmtree(focus_label_path)
        false_negtive_path = os.path.join(
            focus_label_path, 'false-negtive-lost')
        false_positive_path = os.path.join(
            focus_label_path, 'false-positive-wrong')

        os.makedirs(focus_label_path)
        os.makedirs(false_negtive_path)
        os.makedirs(false_positive_path)

        thd_idx = int((thd - thd_start) / thd_step)
        recall_result = recall_results_dict[label][thd_idx]
        for false_neg in recall_result[1]:
            shutil.copy(os.path.join(origin_img_dir, false_neg),
                        false_negtive_path)

        for false_pos in recall_result[2]:
            origin_img = cv2.imread(os.path.join(
                origin_img_dir, false_pos).rstrip())
            targets = results[false_pos]
            for t in targets:
                cv2.rectangle(origin_img, (t['x'], t['y']), (t['x'] + t['w'], t['y'] + t['h']),
                              (255, 0, 0), 3)
                cv2.putText(origin_img, t['label'] + ' ' + str(t['conf']),
                            (t['x'], t['y']), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)
            cv.imwrite(os.path.join(false_positive_path,
                                    false_pos).rstrip(), origin_img)
