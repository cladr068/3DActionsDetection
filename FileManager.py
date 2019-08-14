#from pyntcloud import PyntCloud
import numpy as np
import json

DetailsOfArms = []

def setJson(Json):
	global annotation_file
	annotation_file = Json


def GenerePLYFile(df,frame):
    df[['red','green','blue']] = df[['red','green','blue']].astype(np.uint)
    cloud = PyntCloud(df)
    cloud.to_file("3D_ply_out/3D_point_cloud_"+frame+".ply", also_save=["mesh","points"],as_text=True)

def writeJson(yourDict,yourFileName,folderName): #enter your dict your file name and the folder name
	with open(folderName+'/'+yourFileName+'.json', 'w') as f:
		f.write(json.dumps(yourDict, indent=4, sort_keys=True))

def CreateFieldArmsOverTheDesk():#add to the DetailsOfArms the informations of the arms entirely (not all the keypoints)
        for iBox in range(len(DetailsOfArms)):
            try:
                if(DetailsOfArms[iBox]["keyPoints_above_desk"]["ElbowL"]  or DetailsOfArms[iBox]["keyPoints_above_desk"]["WristL"]):
                    armL = True
                else:
                    armL = False
                if(DetailsOfArms[iBox]["keyPoints_above_desk"]["ElbowR"] or DetailsOfArms[iBox]["keyPoints_above_desk"]["WristR"]):
                    armR = True
                else:
                    armR = False
            except:
                False
            DetailsOfArms[iBox]["arm_over_desk"] = {'arm_right' : armR,'arm_left' : armL} 


def createAnnotationFileWithArmOverTheDeskDetector():
    CreateFieldArmsOverTheDesk()
    for iBox in range(len(DetailsOfArms)):#for every people in dict created by us get frame and id
        frame = DetailsOfArms[iBox]["frame"]
        idPersDict = DetailsOfArms[iBox]["id_pers"]
        for iId in range(len(annotation_file[frame]["annotations"])):#for every annotation of the frame in the real annotation file get the id
            idPersAnno = annotation_file[frame]["annotations"][iId]["id"]
            if(idPersDict == idPersAnno): # if ids are the same add a field 'arm over the desk' that contains a dict of arm right arm left
                annotation_file[frame]["annotations"][iId]["arm_over_the_desk"] = DetailsOfArms[iBox]["arm_over_desk"]
    writeJson(annotation_file,"AnnotationWithArmsOverTheDesk","json_out")#creat the json file



def Load(path):
    return json.load(open(path, 'r'))

def AddInfoInDetailFile(info):
	DetailsOfArms.append(info)

def writeDetailFile():
	writeJson(DetailsOfArms,"detail","json_out")
