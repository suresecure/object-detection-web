import os

source_dir = '/home/mythxcq/july_new_person_events/sun_glasses_back'
target_file = 'sunglassgt.txt'
with open(target_file, 'w') as targetf:
    for ef in os.listdir(source_dir):
        if os.path.isfile(os.path.join(source_dir, ef)):
            targetf.write(ef+'\n')

