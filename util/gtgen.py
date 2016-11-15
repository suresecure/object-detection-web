import os
import optparse
import pickle

def get_dir_list(dir_name):
    files = []
    for ef in os.listdir(dir_name):
        if os.path.isfile(os.path.join(dir_name, ef)):
            files.append(ef)
    return files

if __name__ == '__main__':
    parser = optparse.OptionParser()
    (options, args) = parser.parse_args()
    img_dir = args[0]

    gt = {}
    for ed in os.listdir(img_dir):
        if(os.path.isdir(os.path.join(img_dir, ed)) and ed != '7005' and
           ed != 'bad'):
            files = get_dir_list(os.path.join(img_dir, ed))
            gt[ed] = files

    with open(os.path.join(img_dir, 'gt.pickle'), 'w') as f:
        pickle.dump(gt, f)

