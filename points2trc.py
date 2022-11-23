import pandas as pd
import numpy as np
import os
import glob
import re
import typing as tp
from Pose2Sim.filter_3d import *
import toml

POINTS_KEYS = {
    'Pelvis': 0,
    'LHip': 1,
    'RHip': 2,
    'Spine1': 3,
    'LKnee': 4,
    'RKnee': 5,
    'Spine2': 6,
    'LAnkle': 7,
    'RAnkle': 8,
    'Spine3': 9,
    'LFoot': 10,
    'RFoot': 11,
    'Neck': 12,
    'LCollar': 13,
    'RCollar': 14,
    'Nose': 15,
    'LShoulder': 16,
    'RShoulder': 17,
    'LElbow': 18,
    'RElbow': 19,
    'LWrist': 20,
    'RWrist': 21,
    'LHand': 22,
    'RHand': 23
}

def read_config_file(config):
    '''
    Read configation file.
    '''

    config_dict = toml.load(config)
    return config_dict

config={
    "project":{
        "project_dir":"",
        "frame_rate":""
    },
    "keypoints_names":[
        "LKnee", "RKnee", 
        "LAnkle", "RAnkle", 
        "LHip", "RHip",
        "LWrist", "RWrist",
        "LElbow", "RElbow",
        "LShoulder", "RShoulder",
        "LFoot", "RFoot", "Nose", "Neck", "Pelvis"
    ],
}

def zup2yup(Q):
    '''
    Turns Z-up system coordinates into Y-up coordinates

    INPUT:
    - Q: pandas dataframe
    N 3D points as columns, ie 3*N columns in Z-up system coordinates
    and frame number as rows

    OUTPUT:
    - Q: pandas dataframe with N 3D points in Y-up system coordinates
    '''
    
    # X->Y, Y->Z, Z->X
    cols = list(Q.columns)
    cols = np.array([[cols[i*3+1],cols[i*3+2],cols[i*3]] for i in range(int(len(cols)/3))]).flatten()
    Q = Q[cols]

    return Q

def plot_3d(file:str):
    from matplotlib import pyplot as plt
    from mpl_toolkits import mplot3d
    
    data = np.array(read_points(file)).reshape((-1, 3)).T
    x, y, z = data
    
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    ax.scatter(x, y, z)
    

def ydown2yup(Q):
    '''
    Turns Z-down system coordinates into Y-up coordinates

    INPUT:
    - Q: pandas dataframe
    N 3D points as columns, ie 3*N columns in Z-up system coordinates
    and frame number as rows

    OUTPUT:
    - Q: pandas dataframe with N 3D points in Y-up system coordinates
    '''
    
    # X-> -Z, Y-> -Y, Z-> -X
    cols = list(Q.columns)
    cols = np.array([[cols[i*3+2],cols[i*3+1],cols[i*3]] for i in range(int(len(cols)/3))]).flatten()
    flips = np.array([[-1, -1, 1] for _ in range(int(len(cols)/3))]).flatten()
    # Q = Q[cols]*-1
    Q=Q[cols]*flips*2

    return Q

def list_points_file(directory:str) -> tp.List[str]:
    
    file_list = sorted(glob.glob(os.path.join(directory, "*.txt")))
    
    return file_list

def read_points(filename:str) -> tp.List[float]:
    with open(filename, "r") as f:
        points = f.readlines()
    
    coordinates = []
    for row in points:
        coordinates.extend(row.strip("\n").split(" "))
        
    coordinates = [float(i) for i in coordinates]
    return coordinates
    

def read_points_video(directory:str)-> pd.DataFrame:
    
    file_list:tp.List[str] = list_points_file(directory)
    data = []
    for file in file_list:
        coords = read_points(file)
        data.append(coords)
    df = pd.DataFrame(data)
    
    return df

# def make_trc(config:tp.Dict, data:pd.DataFrame, keypoints_names:tp.List[str]):
#     data = zup2yup(data)

def points2tr(directory:str, trc_file:str, osim_markers:tp.List[str]):
    
    config = read_config_file(r"Pose2Sim\Demo\User\Config.toml")
    filter_type = config.get('3d-filtering').get('type')
    df = read_points_video(directory)
    df = ydown2yup(df)
    # make_trc(config, df, osim_markers)
    
    points_key_index = [POINTS_KEYS[k] for k in osim_markers]
    points_col_index = []
    for i in points_key_index:
        for j in range(3):
            points_col_index.append(i*3+j)
    
    fps = 30
    df = df.loc[:, points_col_index]
    df = df.apply(filter1d, axis=0, args = [config, filter_type])
    df.insert(0, "t", df.index / fps)
    
    
    DataRate = fps
    CameraRate = fps
    NumFrames = len(df)
    NumMarkers = len(osim_markers)
    unit="m"
    OrigDataRate = fps
    OrigDataStartFrame = 0
    OrigNumFrames = len(df)
    
    header_trc = ['PathFileType\t4\t(X/Y/Z)\t' + trc_file, 
        'DataRate\tCameraRate\tNumFrames\tNumMarkers\tUnits\tOrigDataRate\tOrigDataStartFrame\tOrigNumFrames', 
        '\t'.join(map(str,[DataRate, CameraRate, NumFrames, NumMarkers, unit, OrigDataRate, OrigDataStartFrame, OrigNumFrames])),
        'Frame#\tTime\t' + '\t\t\t'.join(osim_markers) + '\t\t',
        '\t\t'+'\t'.join([f'X{i+1}\tY{i+1}\tZ{i+1}' for i in range(len(osim_markers))])]
    
    print(f"Writting TRC to {trc_file}")
    with open(trc_file, "w") as trc_o:
        [trc_o.write(line+'\n') for line in header_trc]
        df.to_csv(trc_o, sep="\t", index=True, header=None, lineterminator="\n")
    # df.to_csv(trc_file+".csv", index=True)
    # print(df.shape)
    
if __name__=="__main__":
    
    for i in glob.glob(r"data\keypoints\*"):
        
        name = os.path.basename(i)
        output = i.replace("keypoints", "trcs")+".trc"
        points2tr(i, output, config["keypoints_names"])
