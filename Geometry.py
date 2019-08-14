import numpy as np
import statistics
import math

class Point:
    def __init__(self,x,y,z):
        self.x=x
        self.y=y
        self.z=z
    def vector(self,point): #Build the [Self,point] vector
        vec_x = point.x-self.x
        vec_y = point.y-self.y
        vec_z = point.z-self.z
        vector = [vec_x,vec_y,vec_z]
        return vector
    def getPointArray(self): #convert the Point object in an array
        return [self.x,self.y,self.z]
# end_class__________________________________________________________

#correct the Z in our images
def inverseZscene(df):
    df['z'] = df['z']*-1
    return df

def setIntrinsicParam(param):
    global intrinsic
    intrinsic = param

#get coordonates from 1 point
def getCoord(x,y,df):
    num_index = y*(intrinsic.width)+x
    x = df['x'][num_index]
    y = df['y'][num_index]
    z = df['z'][num_index]
    return [x,y,z]

#method to have the mean of the coefficients of a 2D 3D 4D...nD vector
def mean_array(Tab):
    coord =[]
    nb_arguments = np.shape(Tab)[1] #can work for a 2D 3D 4D...nD vector
    nb_vectors = np.shape(Tab)[0] 
    for i in range(0,nb_arguments):
        coord.append(0.0)
    for i in range(0,nb_vectors):
        for j in range(0,nb_arguments):
            coord[j] = coord[j] + Tab[i][j]
    for i in range(0,np.shape(coord)[0]):
        coord[i] = coord[i]/(nb_vectors+1)
    return coord #return a tab of the mean coef ex : meanX,meanY,meanZ

    
def getMeanZByRois(Rois,df):
    tab_z = []
    for i in range(0,np.shape(Rois)[0]) :
        for a in range(Rois[i][0],Rois[i][0]+Rois[i][2]) :
            for b in range(Rois[i][1],Rois[i][1]+Rois[i][3]):
                x = a
                y = b
                z = getCoord(x,y,df)[2]
                tab_z.append(z)
    meanZ = statistics.mean(tab_z)
    return meanZ

def getNormalVector(points):

    Vec_array = []
    if len(points)<3:
        print("To have a 3D plan, you must give at least 3 points")
        return;
    for i in range(len(points)) :
        x1,y1,z1 = points[i] #getCoord(points[i][0],points[i][1],df)
        point1 = Point(x1,y1,z1)
        for j in range(i+1,len(points)):
            x2,y2,z2 = points[j] #getCoord(points[j][0],points[j][1],df)
            point2 = Point(x2,y2,z2)
            vec = point1.vector(point2)
            Vec_array.append(vec)
    norm_array = []
    for i in range(len(Vec_array)):
        for j in range(i+1,len(Vec_array)):
            norm_array.append(np.cross(Vec_array[i],Vec_array[j]))
    vec_mean = mean_array(norm_array)
    return vec_mean

#get the coefficients of the plan equation from a normal vector and a point of the plan
def getPlanEquation(normalVec,point): 
    a = normalVec[0]
    b = normalVec[1]
    c = normalVec[2]
    d = a*point[0]+b*point[1]+c*point[2]
    return [a,b,c,-d]

def getLineCoord3D(line,df,Rois): #line is (x1,y1,x2,y2) / Rois is an array [[x,y,box.width,box.height]...]
    x1 = line[0]
    y1 = line[1]
    x1,y1,z1 = getCoord(x1,y1,df)
    z1 = getMeanZByRois(Rois,df) # retrun mean Z coord from the Rois you selected 
    point1 = Point(x1,y1,z1)
    x2 = line[2]
    y2 = line[3]
    x2,y2,z2 = getCoord(x2,y2,df)
    z2 = z1
    point2 = Point(x2,y2,z2)
    vec = point2.vector(point1)
    return {'point1':[x1,y1,z1],'point2':[x2,y2,z2],'vector':vec }
    
def creatDotLine(line,df,nb_point,Rois): #create the points of the line of the desk. 
    line3D = getLineCoord3D(line,df,Rois) #return [point1(Point class),point2(Point class),
#                                          vector created frome the 2points]
    vec = line3D['vector']
    dotA = line3D['point1'] #class method which returns [x,y,z] from a Point
    points_of_line = []
    for t in range (-nb_point,nb_point): #parametric equation of the line of the desk
        x = dotA[0] + 1/nb_point*t*vec[0]
        y = dotA[1] + 1/nb_point*t*vec[1]
        z = dotA[2] + 1/nb_point*t*vec[2]
        r = 255
        g = 0
        b = 0
        points_of_line.append([x,y,z,r,g,b])
    return points_of_line

#from a list of 2D points give the mean xyz point
def meanXYZPoint(listOf2DPoints,df): #.shape give lines columns
    tabOfX = []
    tabOfY = []
    tabOfZ = []
    for line in range(0,np.shape(listOf2DPoints)[0]):
        x = listOf2DPoints[line][0]
        tabOfX.append(x)
        y = listOf2DPoints[line][1]
        tabOfY.append(y)
        z = getCoord(x,y,df)[2]
        tabOfZ.append(z)
    meanX = statistics.mean(tabOfX)
    meanY = statistics.mean(tabOfY)
    meanZ = statistics.mean(tabOfZ)
    return meanX,meanY,meanZ


def getDistanceBetweenPlaneAndPoint(plane,point):
    xa,ya,za = point
    a,b,c,d = plane
    return abs(a*xa+b*ya+c*za+d)/math.sqrt(a**2+b**2+c**2)

def ConvertKeyPoint(exact_point,around_point,df):
    x,y,z = getCoord(exact_point[0],exact_point[1],df)
    z = meanXYZPoint(around_point,df)[2]
    return [x,y,z]
