import cv2
import numpy as np
from pynput.keyboard import Key, Controller

global keyboard
keyboard = Controller()

def setIntrinsicParam(param):
	global intrinsic
	intrinsic = param 

def EventClikForSelectLine(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global mouseX,mouseY
        mouseX,mouseY =  x, y
        keyboard.press('a')
        
def EventClikForSelectFirstPoint(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        a,b = getEquationOfLine(choosenline)
        global FirstPoint
        FirstPoint = [int(x),int((x-b)/a)]
        keyboard.press('a')
                
def EventClikForSelectSecondPoint(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        a,b = getEquationOfLine(choosenline)
        global SecondPoint
        SecondPoint = [int(x),int((x-b)/a)]
        keyboard.press('a')
        
        
def getEquationOfLine(TwoDimCoordsLine):
    x1,y1,x2,y2 = TwoDimCoordsLine
    #x =ay + b
    a = (x2-x1)/(y2-y1)
    b = x1-a*y1
    return a,b
        
        

def FindWichLineNumberIsNearTheClik(lines):
    step = None
    bestline = None
    for i in range(len(lines)):
        a,b = getEquationOfLine(getLinePointsCoords(lines[i]))
        if (step == None or abs(a*mouseY+b - mouseX) <= step):
            step = abs(a*mouseY+b - mouseX)
            bestline = i
        if (step == None or abs((mouseX-b)/a - mouseY) <= step):
            step = abs((mouseX-b)/a - mouseY)
            bestline = i
    return bestline
      
def getLinePointsCoords(line):
    for rho,theta in line:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))
        a = (x2-x1)/(y2-y1)
        b = x1-a*y1
        if (x1<0 and int(-b/a) != int((intrinsic.width-b)/a)): #if the point are out of the images, put it inside
            x1= 0
            y1= int(x1-b/a)+3
            x2= (intrinsic.width)
            y2= int((x2-b)/a)+3
        else:
            x1 = 0
            x2 = (intrinsic.width)   
        return x1,y1,x2,y2
 
def GetROI(img):
    imgCounter = img.copy()
    cv2.putText(imgCounter,'Please select a part of a counter and press Enter',(1,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(255,255,255),2,cv2.LINE_AA)
    cv2.putText(imgCounter,'Press Esc when you finished',(1,40), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(255,255,255),2,cv2.LINE_AA)
    counter = cv2.selectROIs('Counter', imgCounter, False)
    cv2.destroyAllWindows()
    return counter


def showAllLinesAndWaitForTheUserClick(img):
    imglines = img.copy()
    gray = cv2.cvtColor(imglines,cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray,50,150,apertureSize = 3) #edge detection
    lines = cv2.HoughLines(edges,1,np.pi/180,200)
    for i in range(len(lines)):
        x1,y1,x2,y2 = getLinePointsCoords(lines[i])
        cv2.line(imglines,(x1,y1),(x2,y2),(0,255,0),2)
    cv2.putText(imglines,'Select the line of edge of the counter',(1,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(255,255,255),2,cv2.LINE_AA)      
    cv2.imshow('CounterLine',imglines);
    cv2.setMouseCallback('CounterLine',EventClikForSelectLine)
    cv2.waitKey(0);
    cv2.destroyAllWindows()
    keyboard.release('a')
    lineNumber = FindWichLineNumberIsNearTheClik(lines)
    return getLinePointsCoords(lines[lineNumber])

def SelectFistPoint(img,line):
    global choosenline
    choosenline = line
    imgSelectedLine = img.copy();
    x1,y1,x2,y2 = line
    cv2.line(imgSelectedLine,(x1,y1),(x2,y2),(0,255,0),2)
    cv2.putText(imgSelectedLine,'Select the point were the counter begin',(1,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(255,255,255),2,cv2.LINE_AA)      
    cv2.imshow('Select 1st point',imgSelectedLine);
    cv2.setMouseCallback('Select 1st point',EventClikForSelectFirstPoint)
    cv2.waitKey(0);
    cv2.destroyAllWindows()
    keyboard.release('a')

def SelectSecondPoint(img,line):
    imgSelectedLine = img.copy();
    x1,y1,x2,y2 = line
    cv2.line(imgSelectedLine,(x1,y1),(x2,y2),(0,255,0),2)
    cv2.circle(imgSelectedLine,(FirstPoint[0],FirstPoint[1]), 5, (255,0,255), -1)
    cv2.putText(imgSelectedLine,'Select the point were the counter end',(1,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(255,255,255),2,cv2.LINE_AA)      
    cv2.imshow('Select 2st point',imgSelectedLine);
    cv2.setMouseCallback('Select 2st point',EventClikForSelectSecondPoint)
    cv2.waitKey(0);
    cv2.destroyAllWindows()
    keyboard.release('a')

def GetBackPoint():
    return FirstPoint[0],FirstPoint[1],SecondPoint[0],SecondPoint[1]