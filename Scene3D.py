import numpy as np
from PIL import Image
from PIL import ImageFilter
import pandas as pd
import pandas
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import Geometry



def setIntrinsicParam(param):#give the instrinsic parametre of the camera to this python file
	global intrinsic
	intrinsic = param

def GetFiltredArray(depthImg):
    dst  = depthImg.filter(ImageFilter.MaxFilter(3)) #apply max filter X3 to remove the grind
    depthArray= np.array(dst.getdata())
    #remove the peaks
    std = np.std(depthArray)
    moy = np.mean(depthArray)
    for i in range (0,depthArray.size):
        if depthArray[i]>moy+std:
            depthArray[i]=depthArray[i]-moy+std
    return depthArray

def CreateDataFrameFor(file,RGBPath,DepthPath):
    df = createDataFrameFromImage(Image.open(RGBPath+'/'+file))
    #Open the depth-map as a greyscale image. Convert it into an array of depths.
    depthArray = GetFiltredArray(Image.open(DepthPath+'/'+file))
    
    #Create xyz points
    df = insertDepthInDataFrame(depthArray,df)
    df = transformTo3D(df,depthArray)
    df = Geometry.inverseZscene(df)
    #df = correctZAxes(df,30) #permit to rotate the scene around the y axis
    return df

def deproject_pixel_to_point(intrinsic, depth_coordsx, depth_coordsy, depth): #transpose the rgb image in to a 3D scene using parametres of the camera
        width = intrinsic.width #get the width of the image
        height= intrinsic.height #get the height of the image
        _x, _y  = depth_coordsx, depth_coordsy
        x     = (_x - intrinsic.ppx) / intrinsic.fx
        y     = (_y - intrinsic.ppy) / intrinsic.fy
        if  intrinsic.model == "distortion.brown_conrady":
            coeffs = intrinsic.coeffs
            r2 = x*x  + y*y
            f  = 1 + coeffs[0]*r2 + coeffs[1]*r2*r2 + coeffs[4]*r2*r2*r2
            ux = x*f + 2*coeffs[2]*x*y + coeffs[3]*(r2 + 2*x*x)
            uy = y*f + 2*coeffs[3]*x*y + coeffs[2]*(r2 + 2*y*y)
            x  = ux 
            y  = uy 
        dl     = (depth.reshape((width * height)) * intrinsic.depth_scale)
        xyz1   = np.ones((4, width * height))
        xyz1[0]= dl * x
        xyz1[1]= dl * y
        xyz1[2]= dl 
        return xyz1

def createDataFrameFromImage(img): #create dataframe from RGB image
	colourImg    = img.copy()
	colourPixels = colourImg.convert("RGB")

	#Add the RGB values to the DataFrame
	colourArray  = np.array(colourPixels.getdata()).reshape((colourImg.height, colourImg.width) + (3,))
	indicesArray = np.moveaxis(np.indices((colourImg.height, colourImg.width)), 0, 2)
	imageArray   = np.dstack((indicesArray, colourArray)).reshape((-1,5))
	return pd.DataFrame(imageArray, columns=["x", "y","red","green","blue"])

def insertDepthInDataFrame(depthArray,df): #add depth into the previous dataframe
	df.insert(loc=2, column='z', value=depthArray)
	df[['x','y','z']] = df[['x','y','z']].astype(float) #307200,0
	return df

def transformTo3D(df,depthArray): #transpose the dataframe by using the transposition methode
	xyz1 = deproject_pixel_to_point(intrinsic, df['x'], df['y'], depthArray)
	df['x'] = xyz1[0]
	df['y'] = xyz1[1]
	df['z'] = xyz1[2]
	return df

def addTodf(nb_points,df,dotline): #add an points inside the dataframe : it permit to add line for example
    for i in range(0,nb_points):
        df = pd.DataFrame(np.array([dotline[i]]), \
                      columns=["x", "y", "z","red", "green", "blue"]).append(df, ignore_index=True)
    return df

def isThePersonBehindtheLine(people,df,Line3D): #check if the givien person got this arms behind the counter line
    aroundWristL_list = people.getPixelAround('WristL')
    aroundWristR_list = people.getPixelAround('WristR')
    aroundElbowL_list = people.getPixelAround('ElbowL')
    aroundElbowR_list = people.getPixelAround('ElbowR')
    if(aroundWristL_list == None and aroundWristR_list == None and aroundElbowL_list == None and aroundElbowR_list == None):
        return False
    else:
        WristL = False
        WristR = False
        ElbowL = False
        ElbowR = False
        if (aroundWristL_list != None and isApointBehindTheLine(df,aroundWristL_list,Line3D)):
            WristL = True
        if(aroundWristR_list != None and isApointBehindTheLine(df,aroundWristR_list,Line3D)):
            WristR = True
        if(aroundElbowL_list != None and isApointBehindTheLine(df,aroundElbowL_list,Line3D)):
            ElbowL = True
        if(aroundElbowR_list != None and isApointBehindTheLine(df,aroundElbowR_list,Line3D)):
            ElbowR = True
        return {'WristL': WristL,'WristR': WristR,'ElbowL': ElbowL,'ElbowR': ElbowR}

def isApointBehindTheLine(df,aroundWristL_list,Line3D): #check if the given point is behind the given line
    x,y,z = Geometry.meanXYZPoint(aroundWristL_list,df)
    zline = Line3D['point2'][2] #get the z information of the line
    if (z < zline) :
        return False
    else:
        return True

def AddCounterLineInPointIfCloud(show,nb_points,line,df,Rois):
    if (show):
        dotline  = Geometry.creatDotLine(line,df,nb_points,Rois)
        df = addTodf(nb_points,df,dotline)
    return df

def correctZAxes(df,teta):#teta must be in degree
    teta = teta * math.pi / 180
    P = np.array([[np.cos(teta),-np.sin(teta),0],[np.sin(teta),np.cos(teta),0],[0,0,1]])
    df['x'],df['z'],df['y'] = P.dot(np.array([df['x'],df['z'],df['y']]))
    return df

def PrintScene(df):
	fig = plt.figure()
	ax = fig.add_subplot(111, projection = '3d')
	df[['red','green','blue']] = df[['red','green','blue']].astype(np.uint)/255
	ax.scatter(df[['x']], df[['y']], df[['z']], color=df[['red','green','blue']].values)
	plt.show()

