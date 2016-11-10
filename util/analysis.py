import pickle
import numpy as np

def calc_recall(results, gt, conf_thd):
    conf_results = []
    recall = 0
    for r in results:
        detected = False
        for t in r[1]:
            if t['conf'] > conf_thd:
                conf_results.append(r)
                detected = True
                break
        if detected and r[0] in gt:
            recall += 1
    return recall,len(conf_results)

if __name__ == '__main__':
    with open('../results/600_1000_100_call_results.pickle') as f:
        results = pickle.load(f)

    with open('callgt.txt') as f:
        gt = f.read().split()

    all_recall = []
    recall_txt = open('recall.txt', 'w')
    for i in np.arange(0.05, 0.6, 0.05):
        recall, detected = calc_recall(results, gt, i)
        recall_txt.write(str((i, recall, detected))+'\n')

    recall_txt.close()

