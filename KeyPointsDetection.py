# From Python
# It requires OpenCV installed for Python
import sys
import cv2
import os
from sys import platform

# Import Openpose (Windows/Ubuntu/OSX)
dir_path = os.path.dirname(os.path.realpath(__file__))
try:
    # Windows Import
    if platform == "win32":
        # Change these variables to point to the correct folder (Release/x64 etc.) 
        sys.path.append(dir_path + '/asset_openpose/python/openpose/Release');
        os.environ['PATH']  = os.environ['PATH'] + ';' + dir_path + '/asset_openpose/x64/Release;' +  dir_path + '/asset_openpose/bin;'
        import pyopenpose as op
    else:
        # Change these variables to point to the correct folder (Release/x64 etc.) 
        sys.path.append('asset_openpose/python');
        # If you run `make install` (default path is `/usr/local/python` for Ubuntu), you can also access the OpenPose/python module from there. This will install OpenPose and the python library at your desired installation path. Ensure that this is in your python path in order to use it.
        # sys.path.append('/usr/local/python')
        from openpose import pyopenpose as op
except ImportError as e:
    print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
    raise e
    
global params
params = dict()
params["model_folder"] = "asset_openpose/models/"
# Starting OpenPose
global opWrapper
opWrapper = op.WrapperPython()
opWrapper.configure(params)
opWrapper.start()

class Person:
    def __init__(self,sholderL,sholderR,elbowL,elbowR,wristL,wristR):
        self.keyPoint = {}
        
        if sholderL[0] != 0 and sholderL[1] != 0:
            self.keyPoint['SholderL'] = sholderL
        else:
            self.keyPoint['SholderL'] = None
        if sholderR[0] != 0 and sholderR[1] != 0:
            self.keyPoint['SholderR'] = sholderR
        else:
            self.keyPoint['SholderR'] = None
        if elbowL[0] != 0 and elbowL[1] != 0:
            self.keyPoint['ElbowL'] = elbowL
        else:
            self.keyPoint['ElbowL'] = None
        if elbowR[0] != 0 and elbowR[1] != 0:
            self.keyPoint['ElbowR'] = elbowR
        else:
            self.keyPoint['ElbowR'] = None
        if wristL[0] != 0 and wristL[1] != 0:
            self.keyPoint['WristL'] = wristL
        else:
            self.keyPoint['WristL'] = None
        if wristR[0] != 0 and wristR[1] != 0:
            self.keyPoint['WristR'] = wristR
        else:
            self.keyPoint['WristR'] = None
            
    def getPixelAround(self,string_point): #get the pixel in a round with 'point' as center with the radius 'radius'
        tab = []
        radius = 5
        point = self.keyPoint[string_point]
        if point is None:
            return None
        else :
            for i in range(-radius,radius):
                for j in range(-radius,radius):
                    if (((i)**2 + (j)**2) <= radius**2):
                        if (point[0]+i > 0 and point[0]+i<640 and point[1]+j > 0 and point[1]+j<480):
                            tab.append([point[0]+i,point[1]+j])
        return tab    
    def FillInTheArmOverTheDeskInformation(self,dictionary): #set the dictrionary containing the information af the arms over the desk
        self.ArmsOverTheDesk = dictionary

    def setId(self,id):# set the id of the person
        self.id = id


def find_person_skeleton(imagepath,RGBPath,show) : #find the Key point for each person on the given images
	
	PersonArray = []
	imageToProcess = cv2.imread(RGBPath+'/'+imagepath)
	try:
	    # Process Image
		datum = op.Datum()
		datum.cvInputData = imageToProcess
		img = imageToProcess.copy()
		opWrapper.emplaceAndPop([datum])
		for i in range(len(datum.poseKeypoints)): #get the point foreach person on the images
			points = datum.poseKeypoints[i]

			sholderL = [int(points[5][0]),int(points[5][1])]
			sholderR = [int(points[2][0]),int(points[2][1])]
			elbowL = [int(points[6][0]),int(points[6][1])]
			elbowR = [int(points[3][0]),int(points[3][1])]
			wristL = [int(points[7][0]),int(points[7][1])]
			wristR = [int(points[4][0]),int(points[4][1])]

			PersonArray.append(Person(sholderL,sholderR,elbowL,elbowR,wristL,wristR))

		if show:
			for i in range(len(PersonArray)):

				if PersonArray[i].getPixelAround('SholderL',3) != None:
					for j in range(len(PersonArray[i].getPixelAround('SholderL',3))):
						cv2.circle(img,(PersonArray[i].getPixelAround('SholderL',3)[j][0],PersonArray[i].getPixelAround('SholderL',3)[j][1]),1,(0,0,255),-1)
				if PersonArray[i].getPixelAround('SholderR',3) != None:
					for j in range(len(PersonArray[i].getPixelAround('SholderR',3))):
						cv2.circle(img,(PersonArray[i].getPixelAround('SholderR',3)[j][0],PersonArray[i].getPixelAround('SholderR',3)[j][1]),1,(0,0,255),-1)

				if PersonArray[i].getPixelAround('ElbowL',3) != None:
					for j in range(len(PersonArray[i].getPixelAround('ElbowL',3))):
						cv2.circle(img,(PersonArray[i].getPixelAround('ElbowL',3)[j][0],PersonArray[i].getPixelAround('ElbowL',3)[j][1]),1,(0,255,0),-1)
				if PersonArray[i].getPixelAround('ElbowR',3) != None:
					for j in range(len(PersonArray[i].getPixelAround('ElbowR',3))):
						cv2.circle(img,(PersonArray[i].getPixelAround('ElbowR',3)[j][0],PersonArray[i].getPixelAround('ElbowR',3)[j][1]),1,(0,255,0),-1)

				if PersonArray[i].getPixelAround('WristL',3) != None:
					for j in range(len(PersonArray[i].getPixelAround('WristL',3))):
						cv2.circle(img,(PersonArray[i].getPixelAround('WristL',3)[j][0],PersonArray[i].getPixelAround('WristL',3)[j][1]),1,(255,0,0),-1)
				if PersonArray[i].getPixelAround('WristR',3) != None:
					for j in range(len(PersonArray[i].getPixelAround('WristR',3))):
						cv2.circle(img,(PersonArray[i].getPixelAround('WristR',3)[j][0],PersonArray[i].getPixelAround('WristR',3)[j][1]),1,(255,0,0),-1)

			cv2.imshow("KeyPoint",img)
			cv2.waitKey(0)
			cv2.destroyAllWindows()

		return PersonArray

	except:
		return PersonArray
