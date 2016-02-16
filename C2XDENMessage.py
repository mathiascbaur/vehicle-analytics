"""
Data object for a virtual V2X DEN message, e.g. for a traffic simulation.

@since: 01.07.2010
@version: 25.10.2011
@status: ready for final review
@author: Mathias Baur
@contact: mathias@smartlane.de
"""

class DENMessage(object):

    
    FORWARDING_TYPE_BROADCAST = 0
    FORWARDING_TYPE_UNICAST = 1
    FORWARDING_TYPE_GEOCAST_CIRCLE = 2
    FORWARDING_TYPE_GEOCAST_RECTANGLE = 3
    
    #: constants for different communication media
    MEDIUM_TYPE_PWLAN = 0
    MEDIUM_TYPE_CWLAN = 1
    MEDIUM_TYPE_UMTS = 2
    
    __sourceID = 0                  #: source of the message, reference to the sender
    __actionID = 0                  #: action ID of the message, identifies a message for a sending vehicle
    __forwardingType = 0            #: forwarding via broadcast, geocast or unicast. usually, only broadcast is used. message relevance is handled by forwarding area 
    __forwardingArea = None         #: forwarding area must be a Rectangle or a Circle type object, can be evaluated by the traces, must implement "contains"
    __time = 0.0                    #: sending time
    __validityTime = 0              #: time in seconds until message becomes invalid
    __referencePosition = None      #: reference position of the causing event
    __acceleration = 0.0            #: acceleration of the sender
    __speed = 0.0                   #: speed of the sender
    __trace = None                  #: trace of the sender, must be a Trace type object
    __causeCode = 0                 #: optional code for the cause of the message
    __subCause = 0                  #: optional sub code for the cause of the message
    __directCause = 0               #: optional cause code for the cause of the message
    __cancelation = False           #: Flag, indicating if message is a cancelation message
    __reliability = 0               #: reliability of the message
    __medium = 0                    #: used medium: p-WLAN, c-WLAN, UMTS. by now, only p-WLAN can be used
    __payloadData = ""              #: payload content of the message
    __priority = 0.0                #: priority of the message

    def __init__(self):
        '''
        Constructor
        '''

    def getSourceID(self):
        return self.__sourceID


    def setSourceID(self, value):
        self.__sourceID = value

        
    def setActionID(self, value):
        self.__actionID = value


    def getActionID(self):
        return self.__actionID        


    def getAcceleration(self):
        return self.__acceleration

    def setAcceleration(self, value):
        self.__acceleration = value
       
        
    def getSpeed(self):
        return self.__speed

    def setSpeed(self, value):
        self.__speed = value
        
    def getTime(self):
        return self.__time


    def setTime(self, value):
        self.__time = value        
        
                
    def getTrace(self):
        return self.__trace

    def setTrace(self, value):
        self.__trace = value
        

    def getMedium(self):
        return self.__medium


    def setMedium(self, value):
        self.__medium = value


    def delMedium(self):
        del self.__medium


    def getForwardingArea(self):
        return self.__forwardingArea


    def getValidityTime(self):
        return self.__validityTime


    def getReferencePosition(self):
        return self.__referencePosition


    def getCauseCode(self):
        return self.__causeCode


    def getSubCause(self):
        return self.__subCause


    def getDirectCause(self):
        return self.__directCause

    def setForwardingArea(self, value):
        self.__forwardingArea = value


    def setValidityTime(self, value):
        self.__validityTime = value


    def setReferencePosition(self, value):
        self.__referencePosition = value


    def setCauseCode(self, value):
        self.__causeCode = value


    def setSubCause(self, value):
        self.__subCause = value


    def setDirectCause(self, value):
        self.__directCause = value

    def delForwardingArea(self):
        del self.__forwardingArea


    def delValidityTime(self):
        del self.__validityTime


    def delReferencePosition(self):
        del self.__referencePosition


    def delCauseCode(self):
        del self.__causeCode


    def delSubCause(self):
        del self.__subCause


    def delDirectCause(self):
        del self.__directCause
        
    
    def getForwardingType(self):
        return self.__forwardingType


    def setForwardingType(self, value):
        self.__forwardingType = value


    def delForwardingType(self):
        del self.__forwardingType


    def isCancelation(self):
        return self.__cancelation


    def getReliability(self):
        return self.__reliability


    def setCancelation(self, value):
        self.__cancelation = value


    def setReliability(self, value):
        self.__reliability = value
        
    def getPriority(self):
        return self.__priority


    def setPriority(self, value):
        self.__priority = value
        
    def getPayloadData(self):
        return self.__payloadData


    def setPayloadData(self, value):
        self.__payloadData = value

        
    