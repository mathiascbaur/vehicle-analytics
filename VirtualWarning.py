"""
Warning class for V2X warning functions.

A warning object contains all necessary information in order to derive a referring driving behavior.  

@since: 02.12.2010
@version: 15.02.2012
@status: final 
@author: Mathias Baur
@contact: mathias@smartlane.de
"""

import Trace

class Warning(object):
    
    '''
    Event Class
    '''


    # # # # # --- GLOBAL PARAMETERS --- # # # # #

    # # # # # --- CONSTANTS --- # # # # #
    
    WARNING_LEVEL_INFORMATION = 0
    WARNING_LEVEL_WARNING = 1
    MAX_VALUE = 9999

    __timeStart = 0
    __timeEnd = 0
    __presentationType = WARNING_LEVEL_INFORMATION
    __currentPrioritisation = 0
    __distanceToEvent = MAX_VALUE
    __typeOfWarning = 0
    

    def __init__(self):
        '''
        Constructor
        '''

    def getTimeStart(self):
        return self.__timeStart


    def getTimeEnd(self):
        return self.__timeEnd


    def getPresentationType(self):
        return self.__presentationType


    def getCurrentPrioritisation(self):
        return self.__currentPrioritisation


    def getDistanceToEvent(self):
        return self.__distanceToEvent


    def getTypeOfWarning(self):
        return self.__typeOfWarning


    def setTimeStart(self, value):
        self.__timeStart = value


    def setTimeEnd(self, value):
        self.__timeEnd = value


    def setPresentationType(self, value):
        self.__presentationType = value


    def setCurrentPrioritisation(self, value):
        self.__currentPrioritisation = value


    def setDistanceToEvent(self, value):
        self.__distanceToEvent = value


    def setTypeOfWarning(self, value):
        self.__typeOfWarning = value     


