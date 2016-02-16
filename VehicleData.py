"""
A container for extended information for a vehicle
    
@version: 15.02.2012
@status: final
@author: Mathias Baur
@contact: mathias@smartlane.de
"""


class C2XVehicleData ():
    
    """
    Vehicle Data Object: A container for extended information for a V2X vehicle
    """
    
    STATUS_NONE = 0
    STATUS_WARNED = 1
    STATUS_BROKEN_DOWN = 2
    STATUS_IN_JAM = 3
    STATUS_CAM_JAM_RECOGNITION = 4
    STATUS_APPROACH = 5
    STATUS_IN_CONSTRUCTIONSITE = 6
    STATUS_RESET = 7
    
    __desiredSpeed = -1
    __desiredLane = 0
    __oldPosition = None
    __currentPosition = None
    __storedMsg = None
    __trace = None
    __fcdList  = None
    __status = STATUS_NONE
    __receivedDENMessages = []
    __msgRelevanceHandler = None
    __currentMsgAggregat = None
    __displayValidityTime = 0.0
    __currentDisplayContent = None
    __driveability = 0.0

    def __init__ (self,desSpeed,trace,driveability=0):
        """Constructor"""
        self.__desiredSpeed = desSpeed
        self.__trace = trace
        self.__driveability = driveability

    def setDesiredSpeed(self,desSpeed):
        self.__desiredSpeed = desSpeed
        
    def getDesiredSpeed(self):
        return self.__desiredSpeed

    def setDesiredLane(self,desLane):
        self.__desiredLane = desLane
        
    def getDesiredLane(self):
        return self.__desiredLane
    
    def getCurrentPosition(self):
        return self.__currentPosition
    
    def setCurrentPosition(self, position):
        self.__currentPosition = position    
    
    def getOldPosition(self):
        return self.__oldPosition    
    
    def setOldPosition(self, position):
        self.__oldPosition = position    
    
    def setTrace(self,trace):
        self.__trace = trace
        
    def getTrace(self):
        return self.__trace  
    
    def setFcdList(self,fcdList):
        self.__fcdList = fcdList
        
    def getFcdList(self):
        return self.__fcdList  
    
    def getStatus(self):
        return self.__status    
    
    def setStatus(self, status):
        self.__status = status    
    
    def setDriveability(self,driveability):
        self.__driveability = driveability
        
    def getDriveability(self):
        return self.__driveability  
    
    def setStoredMsg(self,storedMsg):
        self.__storedMsg = storedMsg
        
    def getStoredMsg(self):
        return self.__storedMsg
    
    def getReceivedDENMessages(self):
        return self.__receivedDENMessages
    
    def clearReceivedDENMessages(self):
        self.__receivedDENMessages = []    
    
    def getMsgRelevanceHandler(self):
        return self.__msgRelevanceHandler
    
    def setMsgRelevanceHandler(self, msgRelevanceHandler):
        self.__msgRelevanceHandler = msgRelevanceHandler
        
    def getCurrentMsgAggregat(self):
        return self.__currentMsgAggregat
    
    def setCurrentMsgAggregat(self, currentMsgAggregat):
        self.__currentMsgAggregat = currentMsgAggregat
        
    def getDisplayValidityTime(self):
        return self.__displayValidityTime
    
    def setDisplayValidityTime(self, displayValidityTime):
        self.__displayValidityTime = displayValidityTime   
        
    def getCurrentDisplayContent(self):
        return self.__currentDisplayContent
    
    def setCurrentDisplayContent(self, currentDisplayContent):
        self.__currentDisplayContent = currentDisplayContent
