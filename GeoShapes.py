"""
Geo Object classes for (but not restricted to) the use as an V2X event forwarding /relevance area

@since: 21.09.2010
@version: 15.02.2012
@status: ready for final review
@author: Mathias
@contact: mathias@smartlane.de
"""

import math

class Circle(object):
    """
    Geo Object representing a circle for (but not restricted to) the use as an V2X event forwarding /relevance area
    """

    __center = None
    __radius = 0.0


    def __init__(self,center,radius):
        '''
        Constructor
        '''
        self.__center = center
        self.__radius = radius


    def getCenter(self):
        return self.__center
    
    def setCenter(self, value):
        self.__center = value
            

    def getRadius(self):
        return self.__radius

    def setRadius(self, value):
        self.__radius = value
        

    def contains(self,x,y):
        """
        Determines if a point is inside a given circle or not
        @param x: x coordinate of the reference point
        @type x: float 
        @param y: x coordinate of the reference point
        @type y: float
        @return: result of check
        @rtype: boolean 
        """
                
        refPoint = Vector(x,y)
    
        return (refPoint.getDistance(self.__center) <= self.__radius)
    
    
    
#####################################################################################################################################



class Rectangle(object):
    """
    Geo Object representing a rectangle for (but not restricted to) the use as an V2X event forwarding /relevance area
    """

    __p1 = None
    __p2 = None
    __width = 0.0
    __heading = 0.0


    def __init__(self,p1,p2,width):
        '''
        Constructor
        '''
        self.__p1 = p1
        self.__p2 = p2
        self.__width = width


    def getP1(self):
        return self.__p1
    
    def setP1(self, value):
        self.__p1 = value
            

    def getP2(self):
        return self.__p2

    def setP2(self, value):
        self.__p2 = value
        
    def getWidth(self):
        return self.__width


    def getLength(self):
        return math.sqrt(math.pow(self.__p1.X - self.__p2.X,2) + math.pow(self.__p1.Y - self.__p2.Y,2))
        

    def setWidth(self, value):
        self.__width = value


    def setLength(self, value):
        self.__length = value
        
    def getP3(self):
        
        x3 = self.__p2.X - self.__width * math.cos(self.getHeading())
        y3 = self.__p2.Y - self.__width * math.sin(self.getHeading())
        
        p3 = Vector(x3,y3)
        
        return p3
    
    def getP4(self):
        
        x4 = self.__p1.X - self.__width * math.cos(self.getHeading())
        y4 = self.__p1.Y - self.__width * math.sin(self.getHeading())
        
        p4 = Vector(x4,y4)
        
        return p4    


    def getHeading(self):
        """
        Calculates the heading of the rectangle
        @return: the heading of the rectangle
        @rtype: float 
        """       
        
        origin = Vector(0.0,1.0)
        
        x = self.__p2.X - self.__p1.X        
        
        y = self.__p2.Y - self.__p1.Y
        scaledPosition = Vector(x,y)
        
        directionAngle = origin.getAngle(scaledPosition)

        return directionAngle
    
    
    
    def contains(self,x,y):
        """
        Determines if a point is inside a given rectangle or not by means of a ray tracing algorithm
        @param x: x coordinate of the reference point
        @type x: float 
        @param y: y coordinate of the reference point
        @type y: float
        @return: result of check
        @rtype: boolean 
        """        
        
        x1=self.__p1.X
        y1=self.__p1.Y
        
        x2=self.__p2.X
        y2=self.__p2.Y
        
        x3=self.getP3().X
        y3=self.getP3().Y
        
        x4=self.getP4().X
        y4=self.getP4().Y      

        poly = [(x1,y1),(x2,y2),(x3,y3),(x4,y4)] 
    
        n = len(poly)
        inside = False
    
        p1x,p1y = poly[0]
        for i in range(n+1):
            p2x,p2y = poly[i % n]
            if y > min(p1y,p2y):
                if y <= max(p1y,p2y):
                    if x <= max(p1x,p2x):
                        if p1y != p2y:
                            xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x,p1y = p2x,p2y
    
        return inside
    
        