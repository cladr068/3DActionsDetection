
class annotationCounter: #this class permit to know which id belong the the person
	def __init__(self):
		self.BestAnnotationNumber = 0
		self.MostnumberOfArticulation = 0;

	def setNumberOfArticulation(self,num,annotation_number):
		if num > self.MostnumberOfArticulation:
			self.MostnumberOfArticulation = num
			self.BestAnnotationNumber = annotation_number;

def setJson(Json):
	global data
	data = Json

def FindIDOfThePerson(person,frame):
	annocounter = annotationCounter()
	for i in range(len(data[frame]['annotations'])): #check for each annotation of the image
		anno = data[frame]['annotations'][i]
		numberOfArticulation = 0
		for point in person.keyPoint:
			if not(person.keyPoint[point] is None):
				if pointIsInAnno(person.keyPoint[point],anno):#count how many point of the person is inside the annotation box
					numberOfArticulation+=1

		annocounter.setNumberOfArticulation(numberOfArticulation,i) #we check if there is more articulation in this bow than the pervious one.
	return data[frame]['annotations'][annocounter.BestAnnotationNumber]['id'] # when it's finish, the id correspond to the annotation which belong the more keypoint

		

def pointIsInAnno(point,anno): #true if the given point is in the given annotation box, else false
	try:
		if(point[0] > anno['x'] and point[0] < anno['x'] + anno['width'] and point[1] > anno['y'] and point[1] < anno['y'] + anno['height']):
			return True
		else:
			return False
	except:
		return False

