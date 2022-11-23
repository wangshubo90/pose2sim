import cv2
import glob
import os

outdir = r"C:\Users\wangs\dev\pose2sim\Pose2Sim\Empty_project\calib-2d"
for idx, i in enumerate(glob.glob(r"C:\Users\wangs\Documents\ZED\*HD2K*.png")):
    img = cv2.imread(i)
    l = img[:, :img.shape[1]//2]
    cv2.imwrite(os.path.join(outdir, "left", f"left_{idx:0>4d}.png"), l)
    r = img[:, img.shape[1]//2:]
    cv2.imwrite(os.path.join(outdir, "right", f"right_{idx:0>4d}.png"), r)
    