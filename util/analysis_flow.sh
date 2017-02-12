# 1 generate ground truth file
#structure of img_dir
#img_dir:
  #jpg
  #jpg
  #all_jpgs
  #label1:
    #jpg
    #jpg
  #lable2:
    #jpg
    #jpg
#the following command will generate gt.pickle under the img dir
python gtgen.py <img_dir>

# 2 detect and store all targets
# the result will be store under result dir as result.pickle
python detect.py <img_idr> <result_dir>

# 3 analysis and store focus image set
#config focus thds in focus_thds.py
#the corresponding image set will be store in result dir
python analysis.py <gt.pickle> <result.pickle>


