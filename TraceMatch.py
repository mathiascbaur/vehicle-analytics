"""
trace match object containing the matching result for matches between positions and traces.

@since: 03.08.2010
@version: 15.02.2012
@status: final
@author: Mathias Baur
@contact: mathias@smartlane.de
"""

    
class TraceMatch(object):
    
    STATUS_MATCH = 0
    STATUS_NO_MATCH_RELEVANCE_AREA = 1
    STATUS_NO_MATCH_HEADING = 2
    STATUS_NO_MATCH_TRACE = 3
    STATUS_NO_MATCH_UNDEFINED = 4
    
    __matchQuality = 0.0
    __matchDistance = 9999.0
    __matchStatus = STATUS_NO_MATCH_UNDEFINED
    
    def __init__(self):
        self.__matchQuality = 0.0
        self.__matchDistance = 9999.0
        self.__matchStatus = self.STATUS_NO_MATCH_UNDEFINED     
        

    def getMatchQuality(self):
        return self.__matchQuality


    def getMatchDistance(self):
        return self.__matchDistance


    def setMatchQuality(self, value):
        self.__matchQuality = value

    def setMatchDistance(self, value):
        self.__matchDistance = value
        
    def getMatchStatus(self):
        return self.__matchStatus

    def setMatchStatus(self, value):
        self.__matchStatus = value        
            
            