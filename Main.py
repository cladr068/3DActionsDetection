
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 13:55:02 2019

@author: cladr068 & cbazi069
"""

import numpy as np
import cv2
import os
import tqdm



#personal import
import Counter_select
import Geometry
import Scene3D
import KeyPointsDetection
import InfoFromAnnotation
import FileManager



#class________________________________________________________________________
class objetintrinsic:
    def __init__(self, JSON):
        self.width = JSON['width']
        self.height = JSON['height']
        self.fx = JSON['fx']
        self.fy = JSON['fy']
        self.ppx =  JSON['ppx']
        self.ppy = JSON['ppy']
        self.model = JSON['model']
        self.coeffs = JSON['coeffs']
        self.depth_scale = JSON['depth_scale']
#end_class____________________________________________________________________
#functions_____________________________________________________________________

def loadJsoninGlobalVariable():
    global intrinsic
    intrinsic = objetintrinsic(FileManager.Load("json_in/intrinsics.json"))
    Counter_select.setIntrinsicParam(intrinsic)
    Geometry.setIntrinsicParam(intrinsic)
    Scene3D.setIntrinsicParam(intrinsic)
    global annotation_file
    annotation_file = FileManager.Load("json_in/annotations.json")
    InfoFromAnnotation.setJson(annotation_file)
    FileManager.setJson(annotation_file)
#end_functions__________________________________________________________________



RGBPath = 'images/RGB'
DepthPath = 'images/Depth'
RGB_files = os.listdir(RGBPath)
Depth_files = os.listdir(DepthPath)


#load the param of the camera.
loadJsoninGlobalVariable()

#read the color image.
img = cv2.imread(RGBPath+'/'+RGB_files[0])

#_________________________________Select_the_counter___________________________________________________


# Select ROIs of the counter. It permit to know how high is the counter using the depthmap
Rois = Counter_select.GetROI(img)

#select line of the counter. It permit to know where the counter is finished.
line = Counter_select.showAllLinesAndWaitForTheUserClick(img) #also return the line selected by the user

#show the selected line and ask the user to select two points that belong to the counter
Counter_select.SelectFistPoint(img,line)
Counter_select.SelectSecondPoint(img,line)
line = Counter_select.GetBackPoint()

#Creation of the 3D Scene in a dataframe for the first frame. that permit to know what is the line coords in 3D
df = Scene3D.CreateDataFrameFor(RGB_files[0],RGBPath,DepthPath)

LineOfTheCounterIn3D = Geometry.getLineCoord3D(line,df,Rois)

pbar = tqdm.tqdm(total=100)
#___________________________________Creation_of_the_3D_scene___________________________________________
for file in RGB_files : #for each frame in the image
    
    if(len(annotation_file[file]['annotations']) != 0): #if there is no annotation in the annotation file, we don't need to execute the process
        #try:  
    	#creation of the 3DScene for each images          
        df = Scene3D.CreateDataFrameFor(file,RGBPath,DepthPath)

        #Humain Detection            
        People_On_Image = KeyPointsDetection.find_person_skeleton(file,RGBPath,False) #Param = images name,Path of the image, boolean to show the keypoint in the image.
        for p in range(len(People_On_Image)):
            People_On_Image[p].FillInTheArmOverTheDeskInformation(Scene3D.isThePersonBehindtheLine(People_On_Image[p],df,LineOfTheCounterIn3D))
            People_On_Image[p].setId(InfoFromAnnotation.FindIDOfThePerson(People_On_Image[p],file))
    
            FileManager.AddInfoInDetailFile({'frame' : file, 'id_pers' : People_On_Image[p].id,'keyPoints_above_desk' : People_On_Image[p].ArmsOverTheDesk})
    
        #Add the desk limit line in red
        #Scene3D.PrintScene(df)
        #df = Scene3D.AddCounterLineInPointIfCloud(True,100,line,df,Rois)
        #Convert it to a Point Cloud and save it if last argument is True:
        #FileManager.GenerePLYFile(df,file)
        #except:
            #print("An Error became")
    pbar.update(round(100/float(len(RGB_files)),3))

pbar.close()
FileManager.writeDetailFile()
FileManager.createAnnotationFileWithArmOverTheDeskDetector()
