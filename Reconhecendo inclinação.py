import cv2
import numpy as np
import math

def writeAngle(img, value):
    '''
    this function writes in the image
    the angle calculed
    '''
    
    text = '{}'.format(value)

    font   = cv2.FONT_HERSHEY_SCRIPT_COMPLEX
    scale  = 2
    espess = 3
    
    size, _ = cv2.getTextSize(text, font, scale, espess)

    cv2.putText(img, text, (int(img.shape[1]/10 - size[0]/10),
                int(img.shape[0]/10 + size[1]/10)), font,
                scale, (0,255,0), espess)


def applyMask(frameHsv, interval):
    '''
    this function applies a mask in a HSV imagem
    and retorns a binary image
    '''

    mask = cv2.inRange(frameHsv, np.array(interval["LOW"]), 
                       np.array(interval["HIGH"]))
    
    return mask

def countBiggerCont(contorns):
    '''
    this function receive a group of contorns and determine
    who is bigger (area) 
    '''
    
    bigger = 0
    
    for i in range(len(contorns)):
        if cv2.contourArea(contorns[i]) > bigger:
            bigger  = cv2.contourArea(contorns[i])
            contorn = contorns[i]         

    return contorn


def drawAngle(img, points):    
    '''
    this function draws in the image passed 
    two straights and a circle that show the Angle calculed
    '''
    
    cv2.line(img, (points["HIGH"][0], points["HIGH"][1]),
            (points["LOW"][0], points["LOW"][1]), (0, 255, 0), 2)
    cv2.line(img, (points["LOW"][0] - 100, points["LOW"][1]),
            (points["LOW"][0] + 100, points["LOW"][1]), (0, 255, 0), 2)
    
    cv2.circle(img, (points["LOW"][0], points["LOW"][1]), 15,
              (255, 255, 0), 2)

def findPoints(listOfPoints):
    '''
    this function find the points that are necessary 
    to determine the tangent of the object in the image
    '''
    
    width   = 0  #    [x, y]          [x, y]      
    points  = {"LOW": [0, 0], "HIGH": [0, 0]}
    
    #values in 'bigger' and 'smaller' are inverted 'cause the program needs
    #necessarily add a value in the variables. So,
    #the condition have to be true in the first loop
    
    bigger  = 0
    smaller = 640
    
    for i in range(4):
        if listOfPoints[i][1] > bigger:
            bigger = listOfPoints[i][1]
            
            points["LOW"] = listOfPoints[i]
                
    for j in range(4):
        if listOfPoints[j][0] < smaller:
            smaller = listOfPoints[j][0]
            
            points["HIGH"]   = listOfPoints[j]   
    
    return points

def findAngle(h, w):
    '''
    this function calculates the tangent for 
    the values passed. ('for i in range(8)':
    that's necessary 'cause the binary search divides
    the current interval in two intervals smaller and
    will be necessary 7 loops for the interval to contain
    just two values (first and last).
    '''
    
    tan = h/w
    
    first = 0
    last  = 90
    
    for i in range(20):
        
        avg     = int((first+last)/2)
        tanReal = math.tan(math.pi/180*(avg))
        diff    = abs(tan - tanReal)
        
        print(avg)
        
        if diff <= 0.01:
            return avg
        
        elif tan > tanReal:
            first = avg
        else:
            last = avg
    
    return avg

cap = cv2.VideoCapture(1)

while True:
    
    conf, frame = cap.read()

    if conf:
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  
        
        interval = {'LOW':[91, 20, 115], 'HIGH':[134, 255, 170]}
        
        mask = applyMask(hsv, interval)

        _, thresh = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
        
        contorns, _ = cv2.findContours(thresh, cv2.RETR_TREE,
                                                cv2.CHAIN_APPROX_SIMPLE)
        
        if contorns is not None:
            
            contorn = countBiggerCont(contorns)
    
            area = cv2.contourArea(contorn)
            
            if cv2.contourArea(contorn) > 1800:
            
                rect = cv2.minAreaRect(contorn)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                    
                points = findPoints(box)

                height = abs(points['HIGH'][1] - points['LOW'][1])
                width  = abs(points['HIGH'][0] - points['LOW'][0])
                    
                if width != 0:
                    
                    writeAngle(frame, findAngle(height, width))
                    drawAngle(frame, points)
                    
        cv2.imshow('fgdfh', mask)
        cv2.imshow('imagem', frame)
        cv2.imshow('imagem mesma coisa', frame)
        
        k = cv2.waitKey(1) & 0xFF
        
        if k == 27:
            break
        
cap.release()
cv2.destroyAllWindows()