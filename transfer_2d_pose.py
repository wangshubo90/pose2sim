import os
import glob
import shutil
import re

srcdir = r"C:\Users\wangs\dev\pose2sim\data\zed\project1\posejson" 
dstdir = r"C:\Users\wangs\dev\pose2sim\Pose2Sim\Empty_project\pose-2d"

cam1dir = os.path.join(dstdir, "cam1_json")
cam2dir = os.path.join(dstdir, "cam2_json")

os.makedirs(cam1dir, exist_ok=True)
os.makedirs(cam2dir, exist_ok=True)

camdict = {"left":cam1dir, "right":cam2dir}
camjsondict = {"left":"cam01", "right":"cam02"}

for i in glob.glob(srcdir+r"\*.json"):
    cam, frame, postfix = re.search(r"(left|right)(\d+).+(.json)", i).groups()
    shutil.copy2(i, os.path.join(camdict[cam], camjsondict[cam]+"."+frame[2:]+".json"))
    