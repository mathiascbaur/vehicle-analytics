"""
Trace representation for relevance calculations on vehicle traces.

@since: 30.06.2010
@version: 15.02.2012
@status: final
@author: Mathias Baur
@contact: mathias@smartlane.de
"""

import TraceMatch
import GeoShapes
import C2XDENMessage
import math
import datetime
import time
import sys,traceback


class NotEnoughTracePointsException(Exception):
    
    """
    Exception that is raised if the number of currently available trace points is not sufficient
    """
    
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return repr(self.value)
    
    
class Trace(object):
    """
    vehicle trace class.
    A trace consists of 
    
    - a reference position that defines the starting position of each trace calculations (e.g. the event position).
    - a list of x trace points defining the course of the trace with x in (2,TRACE_N_MAX) for a valid trace
    
    and offers functionality as forwarding / relevance area calculation and matching between the trace and vehicle positions    
    
    """
    
    # # # # # --- CONSTANTS --- # # # # #
    
    TRACE_MIN_DIST = 10                             #: minimum driven distance between two trace points (in m)
    TRACE_MAX_DIST = 200                            #: maximum driven distance between two trace points (in m)
    TRACE_MAX_OFFSET = 10                           #: maximum deviation (in m) from motion vector of last trace point
    TRACE_MAX_HEDINGDELTA = math.radians(45)        #: maximum heading delta. Should be smaller than MATCH_MAX_HEADING_DELTA
    TRACE_N_MAX = 16                                #: maximum number of stored position points in one trace
    TRACE_LENGTH_MAX = 2500                         #: maximum trace length (in m)
    MATCH_MAX_DIST = 2500                           #: maximum distance from reference position
    MATCH_MAX_OFFSET = 20.0                         #: maximum offset for trace matching
    MATCH_MAX_HEADINGDELTA = math.radians(60)       #: maximum heading delta for trace matching. Should be greater than TRACE_MAX_HEADING_DELTA
    MATCH_DIST_SMOOTH = 20                          #: maximum smoothing distance for match quality
    MATCH_MIN_QUALITY = 0.8                         #: minimum quality that should be marked as match
    AREA_WIDTH_OVERFLOW = 30.0                      #: overflow on the left and right of a rectangular area
    QUALITY_DELTA = 0.01                            #: minimum delta in quality comparison for result "different"     
    MAX_VALUE = 9999                                #: constant for an arbitrary maximum value of a number
    MIN_EVALUATION_TRACE_LENGHT = 1000
    # # # # # --- VARIABLES --- # # # # #   
    
    __points = []                                   #: list of current points in trace 
    __odometer = 0                                  #: currently accumulated odometer (driven distance since last calculation)
    __relevanceArea = None                          #: the relevance area of the trace (usually a circle or a rectangle)    
    
    __ntptotal = 0                                  #: total number of trace points

    __alphamin = 0.0                                #: temporary value for direction calculation 
    __alphamax = 0.0                                #: temporary value for direction calculation
    
    __referencePosition = None                      #: the reference position of the trace    
    __currentPos = None                             #: the current vehicle position
    
    __initialTime = 0.0                             #: initial invocation time will be stored as creation time of the trace
    
    __vehID = 0                                     #: ID of the vehicle the trace belongs to

    __virtualEvaluationPoints = []

    def __init__(self, initialPosition, initialTime, initialV, initialVehId):
        '''
        Constructor
        '''
        
        self.__points = []
        self.__ntptotal = 0
        self.__currentPos = None
        self.__referencePosition = initialPosition
        self.__odometer = 0
        self.__alphamin = 0.0
        self.__alphamax = 0.0 # directions      
        self.__initialTime = initialTime   
        self.__vehID = initialVehId
        self.__addTracePoint(initialPosition.X,initialPosition.Y, initialTime, initialV)
        
        
    def getCreationTime(self):
        return self.__initialTime
    
    def overwriteMaxTraceLength(self,maxNrOfPoints=-1,maxLength=-1):
        """
        changes the initially defined maximum number of points for this trace and/or the maximum trace length in meters
        @param maxNrOfPoints: optional. the new maximum number of points for this trace. Default is initial setting
        @type maxNrOfPoints: int 
        @param maxLength: optional. the new maximum trace length in meters. Default is initial setting 
        @type maxLength: float 
        """      
        
        if (maxNrOfPoints and maxNrOfPoints>0):
            self.TRACE_N_MAX = maxNrOfPoints
                    
        if (maxLength and maxLength>0):
            self.TRACE_LENGTH_MAX = maxLength
        
        
    def __addTracePointByPosition(self,position,v):
        
        currenttime = datetime.datetime.now
        self.__addTracePoint(position.X,position.Y,currenttime,v)
    
    
    def __addTracePoint(self,x,y,currenttime,velocity):    
        """
        appends a new trace point to the point list
        @param x: the x coordinate of the point in the VISSIM coordinate system
        @type x: float 
        @param y: the y coordinate of the point in the VISSIM coordinate system
        @type y: float 
        @param datetime.datetime.now: the creation time of the point
        @type datetime.datetime.now: float  
        @param velocity: the speed of the vehicle at the point creation time and position
        @type velocity: float
        """  
        
        # if trace point list has reached maximum number of points, delete oldest point first
        if (len(self.__points) >= self.TRACE_N_MAX):
            if self.calcTraceLength() < self.MIN_EVALUATION_TRACE_LENGHT:
                self.__virtualEvaluationPoints.insert(0,(self.__points[-1]))
            del self.__points[-1]
            self.__ntptotal = self.__ntptotal - 1
            
        position = Vector(x,y)   
        
        # insert new trace point at the beginning of the list
        self.__points.insert(0,(position,currenttime,velocity,self.__vehID))
        
        self.__odometer = 0
        self.__alphamin = 0 #-2*math.pi
        self.__alphamax = 2*math.pi
        
        # increase point counter
        self.__ntptotal = self.__ntptotal + 1           
   
    
    def forcePointCreation(self,position,v):
        """
        creates a new trace point without considering the preconditions for regular point creation
        @param position: the position of the new point in the VISSIM coordinate system
        @type position: float 
        @param velocity: the speed of the vehicle at the point creation time and position
        @type velocity: float
        """          
        self.__addTracePointByPosition(position, v)
    
    
    def getPoints(self):
        """
        retrieves the list of points the trace consists of
        @return: the trace points
        @rtype: list
        """               
        return self.__points

    def getEvaluationPoints(self):
        """
        retrieves the list of points the trace consists of and potential additional points
        enlarging the trace to MIN_EVALUATION_TRACE_LENGTH
        @return: the trace points
        @rtype: list
        """               
        return self.__points.extend(self.__virtualEvaluationPoints) 
    
    def printPoints(self):        
        """
        prints information on all trace points in human readable output to the console
        """           
        index = 0
        for point in self.__points:
            print "vehicle: ",point[3]
            print "time: ",point[1]
            print "point nr. ",index,", X=",point[0].X, "Y=",point[0].Y
            index = index+1
        
        
    def getDirection(self, pos1, pos2):
        """
        calculates the geometric direction between two points
        @param pos1: the first position, defining the origin of the direction calculation
        @type pos1: float
        @param pos2: the second position, defining the destination of the direction calculation
        @type pos2: float                          
        @return: the direction from pos1 to pos2 in the VISSIM coordinate system [0,2*pi]
        @rtype: float
        """            
        
        # the vector of the y axis
        yVector = Vector(0.0,1.0)
        
        # coordinate distances
        x = pos2.X - pos1.X
        y = pos2.Y - pos1.Y
        scaledPosition = Vector(x,y)        
        
        # calculate angle
        directionAngle = yVector.getAngle(scaledPosition)
        
        # normalisation. angle > 180deg -> quadrant with pos x
        if (x > 0):
            directionAngle = 2*math.pi - directionAngle
        
        return directionAngle
    
    
    def calculateWideRectangularArea(self, length, offset):
        """
        calculates a rectangle with a given length starting at the offsetted traces reference position.
        The rectangle's width is calculated by the maximum trace point deviation
        @param length: the length of the rectangle
        @type length: float
        @param offset: the starting point offset from the trace's reference position
        @type offset: float                          
        @return: the rectangle with the given length along the trace starting at the offset position 
        @rtype: GeoShapes.Rectangle
        """             
        
        return self.calculateRectangularArea(-1.0,length,offset)
        

    def calculateRectangularArea(self, width, length, offset):
        """
        calculates a rectangle with a given length and width starting at the offsetted traces reference position.
        @param length: the length of the rectangle
        @type length: float
        @param width: the width of the rectangle
        @type width: float        
        @param offset: the starting point offset from the trace's reference position
        @type offset: float                          
        @return: the rectangle with the given length and width along the trace starting at the offset position 
        @rtype: GeoShapes.Rectangle
        """            
            
        try:
            rectArea = None                    
            
            # the starting point will be calculated by the reference position and the offset
            refPos = self.__referencePosition
                        
            if (len(self.__points) > 0):
                
                oldestTracePoint = self.__points[-1]
                            
                traceDist = refPos.getDistance(oldestTracePoint[0])
                
                # rectangle can not be longer than trace
                if (length > traceDist):
                    length = traceDist - offset                            
                
                # negative offset values move the rectangle into the approach direction
                d = length - offset
            
                # heading of rectangle is needed for rectangle point calculation
                rectHeading = self.calcHeadingForwardingArea(self.__points,refPos,d)
                
                # width can be calculated by trace point deviation if indicated by negative value for width
                if(width < 0):
                    maxoffset = 0.0
                    dev = 0.0
                    for point in self.__points:
                        if (not (oldestTracePoint[0].X == refPos.X and oldestTracePoint[0].Y == refPos.Y)):
                            dev = self.__calcEdgeDistance(refPos, oldestTracePoint[0], point[0]);
                            if(dev > maxoffset):
                                maxoffset = dev
                    width = 2.0 * (maxoffset + self.AREA_WIDTH_OVERFLOW);            
            
            # an empty trace can only calculate a vertical rectangle
            else:
                rectHeading = 0
                if (width <= 0):
                    width = length
                

            sinHeading = math.sin(rectHeading)
            cosHeading = math.cos(rectHeading)
            # TODO: Fall 0
            normAbs = math.fabs(sinHeading * cosHeading)
            if normAbs == 0:
                # sin = 0 or cos = 0
                signIndicator = sinHeading + cosHeading
            else:
                signIndicator = sinHeading * cosHeading / normAbs
            
            #signIndicator is 1 or -1
            signedWidth = signIndicator * width
            
            # geometric projections and rotations for the rectangle points                               
            projectedX1 = refPos.X + signedWidth / 2.0 * sinHeading
            projectedY1 = refPos.Y + signedWidth / 2.0 * cosHeading
                                        
            rotatedX1withOffset = projectedX1 - offset * sinHeading
            rotatedY1withOffset = projectedY1 + offset * cosHeading         
            
            rotatedX2withOffset = rotatedX1withOffset - length * sinHeading
            rotatedY2withOffset = rotatedY1withOffset + length * cosHeading              

            p1 = Vector(rotatedX1withOffset,rotatedY1withOffset)
            p2 = Vector(rotatedX2withOffset,rotatedY2withOffset)

            # generate a rectangle from 2 points and rectangle width
            rectArea = GeoShapes.Rectangle(p1,p2,width)      
            
            return rectArea
    
        except Exception, err:
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            traceback.print_tb(exceptionTraceback, limit=1, file=sys.stdout)
            traceback.print_exception(exceptionType, exceptionValue, exceptionTraceback,limit=2, file=sys.stdout)
            time.sleep(4)   
            return 1       
        
        
    def createCircularArea(self,radius,offset):
        """
        calculates a circle with a given radius starting at the offsetted traces reference position.
        @param radius: the radius of the circle
        @type radius: float     
        @param offset: the starting point offset from the trace's reference position
        @type offset: float                          
        @return: the circle with the given radius at the offset position 
        @rtype: GeoShapes.Circle
        """          
        
        try:
            refPos = self.__referencePosition
                        
            # negative offset values move the circle into the approach direction
            d = radius - offset
            
            refPosWithOffsetX = refPos.X
            refPosWithOffsetY = refPos.Y            
            
            if (not offset == 0): 
                circHeading = self.MAX_VALUE
                # if there is a approach, get moving direction 
                points = self.__points
                
                # heading of circle is needed for circle calculation
                circHeading = self.calcHeadingForwardingArea(points, refPos, d)
                
                # geometric projections and rotations for the circle center points
                if(not circHeading == self.MAX_VALUE): 
                    refPosWithOffsetX = refPos.X + offset * math.sin(circHeading) 
                    refPosWithOffsetY = refPos.Y + offset * math.cos(circHeading)
            
            center = Vector(refPosWithOffsetX,refPosWithOffsetY)
            # generate a circle from center point and radius
            return GeoShapes.Circle(center,radius)
        
        
        except Exception, err:
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            traceback.print_tb(exceptionTraceback, limit=1, file=sys.stdout)
            traceback.print_exception(exceptionType, exceptionValue, exceptionTraceback,limit=2, file=sys.stdout)
            time.sleep(4)   
            return 1              
                
        
    def calcHeadingForwardingArea(self,tracePoints,refPos,d):        
        """
        calculates the heading of the trace's forwarding area based on the current trace direction
        @param tracePoints: the points of the trace
        @type tracePoints: list     
        @param refPos: the trace's reference position
        @type refPos: float   
        @param d: distance from reference position to the end of the forwarding area
        @type d: float 
        @return: the direction from the reference position to the end of the forwarding area
        @rtype: float
        """          
        
        tPos = Vector(0,0)
  
        for tracePos in tracePoints:
            tPos = tracePos[0]
            curdist = tPos.getDistance(refPos); 
            if(curdist > d):
                #print "curdist: ",curdist
                break
        
        return self.getDirection(refPos,tPos)
    
    
    def calcCurrentTraceHeading(self):
        """
        calculates the current heading of the trace represented by the direction of the two most recent trace points
        @return: the current trace heading
        @rtype: float
        """          
        if (len(self.__points) > 1):
            return self.getDirection((self.__points[1])[0], (self.__points[0])[0])
        else:
            #print "NotEnoughTracePointsException"
            raise NotEnoughTracePointsException(str(len(self.__points)))
        
    
    
    def processNewPositionWithoutSpeed(self,newPos):
        self.processNewPosition(self,newPos, 0.0)  
    
    def processNewPosition(self,newPos, curSpeed):
        """
        checks if preconditions for trace point generation are complied with
        and if so generates a new trace point from the current vehicle position and speed 
        @param newPos: the current ego vehicle's position
        @type newPos: Vector
        @param curSpeed: the current ego vehicle's speed
        @type curSpeed: float       
        """          
        
        try:
        
            if self.__currentPos:
                
                # calculate the distance to the position from last calculation
                edgelength = self.__currentPos.getDistance(newPos)
                
                # temporary updated odometer
                newOdometer = self.__odometer + edgelength
                
                if(len(self.__points) <= 0):
                    # if no point in the buffer add current position as first point
                    self.__addTracePointByPosition(self.__currentPos,curSpeed)
                elif (self.__odometer >= self.TRACE_MIN_DIST):  # not newodometer !!
                    # otherwise if driven distance between last trace point and the possible
                    # new trace point (curpos) is bigger than MIN_DIST, check if the curpos 
                    # should be added to the trace
                    lasttp = (self.__points[0])[0] #last Element
                    # direction from last trace point to the new position
                    dir = self.getDirection(lasttp,newPos)
                    # direction between point from last calculation point to the new position
                    newPosHeading = self.getDirection(self.__currentPos,newPos)
                    if (newOdometer >= self.TRACE_MAX_DIST): 
                        # if driven distance between last trace point and newPos > TRACE_MAX_DIST, add trace point
                        self.__addTracePointByPosition(self.__currentPos,curSpeed)
                    elif(math.fabs(dir-newPosHeading) > self.TRACE_MAX_HEDINGDELTA):
                        # if delta between edge heading and driving heading is bigger than > TRACE_MAX_HEADINGDELTA, add a trace point
                        self.__addTracePointByPosition(self.__currentPos,curSpeed)
                    elif(dir < self.__alphamin or dir > self.__alphamax):
                        # if newPos is outside all possible tubes, add tracepoint
                        self.__addTracePointByPosition(self.__currentPos,curSpeed)
                        
                
                # recalculate trace point criteria
                # IMPORTANT: self.points.getFirst() and self.odometer might have changed
                # since the start of the method because a new trace point has been set
                self.__odometer = self.__odometer + edgelength
                lasttp = (self.__points[0])[0] # last trace point must exist 
                dist = lasttp.getDistance(newPos)
                dir = self.getDirection(lasttp,newPos)
                
                # if distance between last trace point and the new position is greater than MATCH_MAX_OFFSET, recalculate new angles
                if(dist > self.MATCH_MAX_OFFSET):  # otherwise beta would be NaN -> i. e. beta == 180
                    beta = math.asin (self.TRACE_MAX_OFFSET / dist)
                    betamin = dir-beta # might result in values < -180
                    betamax = dir+beta # might result in values > 180
                    if(betamin >= self.__alphamin and betamin <= self.__alphamax or betamax <= self.__alphamax and betamax <= self.__alphamin):
                        if (betamin > self.__alphamin):
                            self.__alphamin = betamin                  
                        if (betamax < self.__alphamax):
                            self.__alphamax = betamax
                        
            self.__currentPos = newPos
        
        except Exception, err:
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            traceback.print_tb(exceptionTraceback, limit=1, file=sys.stdout)
            traceback.print_exception(exceptionType, exceptionValue, exceptionTraceback,limit=2, file=sys.stdout)
            time.sleep(4)   
            return 1            

    

    def matchToPosition(self, position, heading, forwardingArea, oldTraceMatch):
        """
        calculates a percentage value in the range [0,1] indicating
        the match quality between the trace and a given position and its heading.
        Plus, a forwarding area must be given. If the position is not within 
        this forwarding area, the match quality is 0.
        Furthermore, the nearest match distance between the reference position and the given position is calculated 
        The forwarding area can have any shape, but it must implement the method "contains".
        @param position: the position to be matched with the trace
        @type position: Vector 
        @param heading: the heading to be matched with the trace heading
        @type heading: float
        @param forwardingArea: the forwarding area where the position must be placed in
        @type forwardingArea: GeoShapes.T
        @param oldTraceMatch: a TraceMatch object from a previous matching 
        @type oldTraceMatch: TraceMatch
        @return: a TraceMatch object containing the match quality and the nearest match distance 
        @rtype: TraceMatch
        """           
        
        # a new TraceMatch object
        traceMatch = TraceMatch.TraceMatch()
        
        matchQuality = 0.0
        try:        
            
            # No matching possible with less then 2 points
            if(len(self.__points) < 2):
                return traceMatch
            
        
            # forwarding area must be rectangle or circle or anything implementing "contains"
            if not (forwardingArea.contains(position.X,position.Y)):

                traceMatch.setMatchStatus(traceMatch.STATUS_NO_MATCH_RELEVANCE_AREA)
                return traceMatch
            
            directionToRefPos = self.getDirection(position, self.getReferencePosition())
            
            # rough preselection: if matching object's heading is completely different, no trace match is possible 
            if (directionToRefPos > self.calcCurrentTraceHeading() + math.pi/2.0 or directionToRefPos < self.calcCurrentTraceHeading() - math.pi/2.0):          
                traceMatch.setMatchStatus(traceMatch.STATUS_NO_MATCH_HEADING)
                return traceMatch
            
            rp1 = None
            rp2 = None
            
            # initialization of best match values
            bmquality = 0.0
            bmoffset = 9999       
            bmrawdist = 0
            bmtp = None            
            rawdist = 0
                        
            # loop all trace points and find closest combination of two neighboring points
            for point in self.__points:
                               
                if (not rp1):
                   
                    rp1 = point                    
                    continue
                
                rp2 = point
            
                # the offset is the shortest distance between the position and 
                # the edge rp1 - rp2
                offset = self.__calcEdgeDistance(rp1[0], rp2[0], position)
    
                currentTraceDirection = self.getDirection(rp2[0], rp1[0])
                
                # calculate difference between matching object's heading and trace heading
                hddelta = math.fabs(heading - currentTraceDirection)
                
                # direction angles between currently regarded two trace points and matching position
                directionAngle1 = self.__getDirectionAngle(rp2[0], position, rp1[0])
                directionAngle1before = directionAngle1
                if (directionAngle1 > math.pi):
                    directionAngle1 = 2*math.pi - directionAngle1                
                    
                directionAngle2 = self.__getDirectionAngle(rp1[0], position, rp2[0])
                directionAngle2before = directionAngle2
                if (directionAngle2 > math.pi):
                    directionAngle2 = 2*math.pi - directionAngle2
                
                oldMatchDistance = 9999
                oldMatchQuality = 0.0                            
                
                # exclude offsets and directions outside relevant area
                if(offset <= self.MATCH_MAX_OFFSET and hddelta <= self.MATCH_MAX_HEADINGDELTA): # and directionAngle1 <= math.pi/2.0 and directionAngle2 <= math.pi/2.0):s
                    
                    quality = 0
                    
                    # calculate match quality. use previously calculated match quality if available
                    if oldTraceMatch:
                        oldMatchDistance = oldTraceMatch.getMatchDistance()
                        oldMatchQuality = oldTraceMatch.getMatchQuality()
                        quality = self.__calcCombinedMatchQuality(offset, hddelta, oldMatchQuality, oldMatchDistance)
                    else:
                        quality = self.__calcMatchQuality(offset, hddelta)                                                            
                        
                    # if new quality is significantly higher than previous best quality, this is the new best quality        
                    if(quality > bmquality + self.QUALITY_DELTA):
                                                
                        bmquality = quality
                        bmoffset = offset
                        bmrawdist = rawdist    
                        bmtp = rp1[0]
                        
                # raw trace distance between trace points considered by now
                rawdist += rp1[0].getDistance(rp2[0])     
                
                rp1 = rp2
                        
            if(bmoffset < 9999):
            
                # if a new offset was calculated, store best match quality and nearest match distance in TraceMatch object
                
                matchrawdist = bmrawdist                
                matchtp = bmtp
                matchdist = position.getDistance(matchtp) + matchrawdist
                
                if oldMatchDistance < matchdist:
                    
                    matchdist = oldMatchDistance
                    matchQuality = oldMatchQuality
                else:
                    matchQuality = bmquality 
                
                traceMatch = TraceMatch.TraceMatch()         
                traceMatch.setMatchDistance(matchdist)
                traceMatch.setMatchQuality(matchQuality)
                traceMatch.setMatchStatus(traceMatch.STATUS_MATCH)
            else:
                traceMatch.setMatchStatus(traceMatch.STATUS_NO_MATCH_TRACE)
                        
            return traceMatch
            
        except Exception, err:
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            traceback.print_tb(exceptionTraceback, limit=1, file=sys.stdout)
            traceback.print_exception(exceptionType, exceptionValue, exceptionTraceback,limit=2, file=sys.stdout)
            time.sleep(4)   
            return 1      
    
    
    def __calcCombinedMatchQuality(self,offset, hddelta, oldquality, oldegodist):
        # single match quality
        smq = self.__calcMatchQuality(offset, hddelta)
        # smooth factor
        sf = max(0, 1 - (oldegodist / self.MATCH_DIST_SMOOTH))
        # combined match quality
        cmq = sf*oldquality + (1-sf)*smq
        
        return cmq
   
   
   
    def __matchToOtherTrace(self,trace,xoff,yoff):
        """
        calculates a percentage value in the range [0,1] indicating
        the match quality between two traces.
        @param trace: the other trace to be matched with this one
        @type trace: Trace
        @param xoff: the x coordinate of the offset which is used to adjust one trace starting point to the other's 
        @type xoff: float
        @param yoff: the y coordinate of the offset which is used to adjust one trace starting point to the other's 
        @type yoff: float
        @return: the match quality between the two traces [0,1] 
        @rtype: float
        """               
        
        try:

            # get points of both traces
            rps1 = self.getPoints()
            rps2 = trace.getPoints()
            
            totaloffsets = 0
            totalmatches = 0
            dist = 0
            
            tmprp = Vector(0,0)
            i2 = 0;
            rp1 = None
            
            # iterate points of both traces and compare all distances between points and edges
            for rp2 in rps1:
                
                if not rp1:
                    rp1 = rp2
                    continue
                
                while (i2 < len(rps2)):

                    tmprp = Vector(rps2[i2][0].X+xoff,rps2[i2][0].Y+yoff)
                    offset = self.__calcEdgeDistance(rp1[0],rp2[0],tmprp)
                    if(offset < self.MATCH_MAX_OFFSET): # rps2[i2] matched on rp1 -> rp2
                        totaloffsets = totaloffsets + offset
                        totalmatches = totalmatches + 1
                        if(i2 == 0):
                            dist = dist + rp1[0].getDistance(tmprp)
                        i2 = i2+1
                    else: # otherwise try to match with next edge
                        if(i2 == 0): 
                            dist = dist+rp1[0].getDistance(rp2[0])
                        break
                
                rp1 = rp2
            
            if(totalmatches > 0):
                avgoffset = totaloffsets / totalmatches
                # calculate match quality
                quality = totalmatches / len(rps2) * (1.0 - avgoffset / self.MATCH_MAX_OFFSET)
                return quality
            
            return 0
    
        except Exception, err:
            exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
            traceback.print_tb(exceptionTraceback, limit=1, file=sys.stdout)
            traceback.print_exception(exceptionType, exceptionValue, exceptionTraceback,limit=2, file=sys.stdout)
            time.sleep(4)   
            return 1       
    


    def matchToOtherTrace(self,atrace):
        """
        calculates a percentage value in the range [0,1] indicating
        the match quality between two traces. The trace's starting points are adjusted between each other.
        @param trace: the other trace to be matched with this one
        @type trace: Trace
        @return: the match quality between the two traces [0,1] 
        @rtype: float
        """             
              
        a2xoff = atrace.getReferencePosition().X - self.__referencePosition.X
        a2yoff = atrace.getReferencePosition().Y - self.__referencePosition.Y
        
        # try to match trace2 on trace1
        return self.__matchToOtherTrace(atrace, a2xoff, a2yoff)
 
    
    
    def __calcEdgeDistance(self,edgeP1,edgeP2,P):
        """
        calculates the minimal distance between a point and an edge defined by two points.
        @param edgeP1: the first point of the edge
        @type edgeP1: Vector
        @param edgeP2: the first point of the edge
        @type edgeP2: Vector
        @param P: the reference point of the calculation
        @type P: Vector  
        @return: the minimal distance between the edge and the point
        @rtype: float
        """           
        x = P.X 
        y = P.Y
        
        # distance calculation by Hesse normal form
        
        if (not edgeP2.X == edgeP1.X):
            
            
            yDiff = (edgeP2.Y-edgeP1.Y)
            xDiff = (edgeP2.X-edgeP1.X)                
            a = yDiff/xDiff
            b = 1.0

            c = - (edgeP1.Y - a*edgeP1.X)

            # calculate a straight line defining the normal vector
            normal = -a*x + b*y + c
            
            offset = math.fabs(normal / math.sqrt(a*a + b*b))
            
        elif (not edgeP2.Y == edgeP1.Y):
            # if y coordinate is the same, the points form a vertical line
            offset = math.fabs(x - edgeP1.X)
        
        else: # => edgeP1 == edgeP2
            raise NotEnoughTracePointsException(1)
        
        return offset
        
    
    def __positionInTraceRange(self,position,firstPointPos, secondPointPos):           
        """
        checks if a given position is within the relevant range of the trace
        @param position: the position to be checked
        @type position: Vector
        @param firstPointPos: the first trace position for the check
        @type firstPointPos: Vector
        @param secondPointPos: the second trace position for the check
        @type secondPointPos: Vector  
        @return: the result of the range check
        @rtype: boolean
        """              
        directionAngle = self.__getDirectionAngle(firstPointPos, position, secondPointPos)
        
        if (directionAngle > math.pi):
            directionAngle = 2*math.pi - directionAngle
                         
        positionInRange =  directionAngle <= math.pi/2
        return positionInRange
            
    
    def __getDirectionAngle(self,anglePoint,point1,point2):
        """
        calculates an angle between two vectors
        @param anglePoint: the origin of the angle calculation
        @type position: Vector
        @param firstPointPos: the point defining the direction of the first vector
        @type firstPointPos: Vector
        @param secondPointPos: the point defining the direction of the second vector
        @type secondPointPos: Vector  
        @return: the angle between the two vectors
        @rtype: float
        """          
        return math.fabs(self.getDirection(anglePoint, point1) - self.getDirection(anglePoint, point2))
 
                
    def __isMatchQualitySufficient(self,matchquality):
        """
        checks if a given match quality is sufficient with respect to the minimum match quality
        @param matchquality: the match quality to be hcekced against the minimum match quality
        @type matchquality: flaot
        @return: the result of the check
        @rtype: boolean
        """         
        return (matchquality >= self.MATCH_MIN_QUALITY) 
            
             
            
    def __calcMatchQuality(self,offset, hddelta):
        """
        calculates the quality of a trace match depending on the ofsset and the heading difference
        @param offset: the minimum offset between a matched position and the trace
        @type offset: float
        @param hddelta: the heading difference between a matched position and the trace
        @type hddelta: float        
        @return: the calculated match quality
        @rtype: float
        """            
        return 0.7 * (1 - (offset / self.MATCH_MAX_OFFSET)) + 0.3 * (1 - (hddelta / self.MATCH_MAX_HEADINGDELTA));
                
      
    def calcTraceLength(self):
        """
        calculates the length of the trace in meters       
        @return: the geometric length of the trace in meters
        @rtype: float
        """          
        
        oldPoint = None
        length = 0
        for point in self.__points:
            if (oldPoint):
                length = length + point[0].getDistance(oldPoint[0])            
            oldPoint = point
        
        return length
    
    def calcEvaluationTraceLength(self):
        
        oldPoint = None
        length = 0
        for point in self.__virtualEvaluationPoints:
            if (oldPoint):
                length = length + point[0].getDistance(oldPoint[0])            
            oldPoint = point
        
        return self.calcTraceLength() + length
        
    
    def calcNrOfPoints(self):
        return len(self.__points)  
    
    def calcNrOfEvaluationPoints(self):
        return (len(self.__points) + len(self.__virtualEvaluationPoints))
    
    def getCurrentReferencePosition(self):
        return self.__currentPos  
          
    def setReferencePosition(self,value):
        self.__referencePosition = value
        
    def getReferencePosition(self):
        return self.__referencePosition
    
    def setExtensionPosition(self,value):
        self.__extensionPosition = value
        
    def getExtensionPosition(self):
        return self.__extensionPosition       
    
    def setRelevanceArea(self,value):
        self.__relevanceArea = value
        
    def getRelevanceArea(self):
        return self.__relevanceArea    
            
            
            