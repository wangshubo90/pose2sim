import sys
import os
from Pose2Sim import Pose2Sim
# Pose2Sim.calibrateCams()

args = sys.argv

if len(args) != 2:
    print("provide project root dir: python run.py path_to_project")
else:
    os.chdir(args[1])

Pose2Sim.track2D()
Pose2Sim.triangulate3D()
Pose2Sim.filter3D()