"""

Logger for vehicle traces.
Default logging is XML output
  
@since: 22.08.2011
@version: 07.11.2011
@status: final.
@author: Mathias Baur
@contact: mathias@smartlane.de
"""

import xml.etree
from xml.etree import ElementTree as ET

class XMLLogging():
    
      
    
    def xmlPrint(self,root,pretty=True):
        """
        prints a XML element tree into a string. Pretty printing (indentation) is optional 
        @param root: root element of the XML tree
        @type root: etree.Element
        @param pretty: activates pretty printing. default=True
        @type pretty: boolean  
        @return: XML tree as string representation
        @rtype: string
        """                     
        if pretty:
            self.__indent(root)
        return ET.tostring(root)        
        
        
    def __indent(self, elem, level=0):        
        """
        indentation for pretty printing of a XML structure. 
        @param elem: root element of the (partial) XML tree
        @type elem: etree.Element
        @param level: current indentation level. starting at default=0
        @type level: int         
        """            
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.__indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i        
                    
   
    def writeTrackingToFile(self,text,xmlFileName):
        """
        opens a file and writes a line of XML text
        @param text: line to be written
        @type text: String
        @param xmlFileName: the name of the XML file to be written into. If no absolute path is given, it is stored into the location of the TraceLogger class
        @type xmlFileName: String        
        """        
        statusFile = open(xmlFileName, "w")    
        #print text     
        statusFile.write(text) 
        statusFile.close()  
 


    def parseLinkTab(self,vissimFileName,linkTextSeperator="-- Mautberechnungsmodelle"):    
        """
        parses the given VISSIM network file and writes all link names and lengths into referring tables
        requirements to the VISSIM file:
        - First line (except blank lines) after all Links and Connectors starts with "-- Mautberechnungsmodelle".
        If not, a distinct seperator needs to be given as a parameter
        - The referring lines must start with "STRECKE", "LAENGE" or "VERBINDUNG"
        
        @param vissimFileName: the name of the VISSIM network file
        @type vissimFileName: String  
        @param linkTextSeperator: the next text line (except blank lines) after all link and connector definitions in network file
        @type linkTextSeperator: String  
        """              

        lineArray = []
        streckenDone = False
        streckenName = ""
        linkTab = {}

        netFile = open(vissimFileName, "r") 
        
        for line in netFile:                    
            
            # first element in VISSIM file after links and connectors is usually "Mautberechnungsmodelle".
            # This needs to be checked each time a new VISSIM file is to be parsed!
            if (line.lstrip().startswith(linkTextSeperator)):
                return
            
            if (line.lstrip().startswith("-- Verbinder")):
                streckenDone = True
            
            # read link name
            if (not streckenDone and line.lstrip().startswith("STRECKE")):            
                lineArray = line.split()
                if lineArray[1]:
                    streckenName = lineArray[1]            
            
            # read link length    
            if (line.lstrip().startswith("LAENGE")):            
                lineArray = line.split()
                streckenLength = lineArray[1]
                linkTab[streckenName] = streckenLength     
                            
            # connectors need to be handled as links. Since connectors don't provide a length, an assumption is made
            elif (line.lstrip().startswith("VERBINDUNG")):
                lineArray = line.split()
                if lineArray[1]:
                    streckenName = lineArray[1]
                    # connectors are assumed to be 2m long
                    linkTab[streckenName] = str(2.0) 
                    
        return linkTab
            
        
   
class CSVLogging():
    
    __filePath = "/"
        
    def __init__(self,filePath="/"):
        """
        Constructor of CSVLogging
        @param filePath: the path of the resulting csv file. If no path is given in the constructor, it is stored into the location of the TraceLogger class
        @type filePath: String
        """          
        
        self.__filePath = filePath    
    
    
    def writeEval(self, evalData):
        """
        Prepares the output of evaluation parameters for file writing
        """
        
        if evalData.getLeadingVehicleData():
            
            leadingVehiclePos = Vector(evalData.getLeadingVehicleData()[0],evalData.getLeadingVehicleData()[1])
            leadingVehicleLength = evalData.getLeadingVehicleData()[2]
            
            timeGap = evalData.getVehiclePosition().getDistance(leadingVehiclePos) - leadingVehicleLength
            
            if timeGap > 0 and timeGap <= 200:
                
                leadingVehicleSpeed = evalData.getLeadingVehicleData()[3]
                relativeSpeed = evalData.getVehicleSpeed() - evalData.getLeadingVehicleData()[3]
                
                
                if (relativeSpeed > 0.001):
                    ttc = timeGap / relativeSpeed  
                    #print "ttc calc: ",ttc                                                                    
                    if ttc > 50:
                        ttc = str(-1)
                                                                                         
                else:
                    ttc = str(-1)
            else:
                timeGap = str(-1)
                ttc = str(-1)    
        else:
            timeGap = str(-1)
            ttc = str(-1)  
            
#        if distanceToSender > 550:
#            print "distanceToSender: ",distanceToSender 
                                                                                         
        line = str(evalData.getCurrentSystemTime()) + "," + str(evalData.getVehicleID())+ "," + str(evalData.getVehicleType()) + "," + str(evalData.getVehiclePosition().X) + "," + str(evalData.getVehiclePosition().Y)
        line = line + "," + str(evalData.getVehicleSpeed()) + "," + str(evalData.getVehicleAcceleration())+ "," + str(timeGap) + "," + str(ttc)  + "," + str(evalData.getWarningDistance())+ ","
        line = line + str(evalData.getInfoDistance())+ "," + str(evalData.getReceptionDistance()) + "," + str(evalData.getCamJamDistance())                                                               
        
        self.__writeEvalToFile(line, evalData.getCurrentSystemTime())        
        
                      
                      
    def __writeEvalToFile(self,line,timestepID):
        """
        opens a file and writes current vehicle information into a csv file
        @param line: line to be written
        @type line: String
        @param timestepID: ID of the current timestep
        @type line: float 
        """
        
        timeIdentifier = '%06.1f' % timestepID
        
        statusFile = open(self.__filePath+"eval/record_" + timeIdentifier + ".csv", "a")         
        statusFile.write(line+"\n") 
        statusFile.close()    
        
        
class EvalData():

    
        __currentSystemTime = 0.0
        __vehicleID = 0
        __vehicleType = ""
        __vehicleSpeed = 0.0
        __vehicleAcceleration = 0.0
        __leadingVehicleData = []
        __vehiclePosition = None
        __warningDistance = 0.0
        __infoDistance = 0.0
        __receptionDistance = 0.0
        __camJamDistance  = 0.0
        
        
        def __init__(self, currentSystemTime, vehicleID, vehicleType, vehicleSpeed, vehicleAcceleration, leadingVehicleData, vehiclePosition, warningDistance, infoDistance, receptionDistance, camJamDistance):
            self.__currentSystemTime = currentSystemTime
            self.__vehicleID = vehicleID
            self.__vehicleType = vehicleType
            self.__vehicleSpeed = vehicleSpeed
            self.__vehicleAcceleration = vehicleAcceleration
            self.__leadingVehicleData = leadingVehicleData
            self.__vehiclePosition = vehiclePosition
            self.__warningDistance = warningDistance
            self.__infoDistance = infoDistance
            self.__receptionDistance = receptionDistance
            self.__camJamDistance = camJamDistance        

        def getCurrentSystemTime(self):
            return self.__currentSystemTime


        def getVehicleID(self):
            return self.__vehicleID


        def getVehicleType(self):
            return self.__vehicleType


        def getVehicleSpeed(self):
            return self.__vehicleSpeed


        def getVehicleAcceleration(self):
            return self.__vehicleAcceleration


        def getLeadingVehicleData(self):
            return self.__leadingVehicleData


        def getVehiclePosition(self):
            return self.__vehiclePosition


        def getWarningDistance(self):
            return self.__warningDistance


        def getInfoDistance(self):
            return self.__infoDistance


        def getReceptionDistance(self):
            return self.__receptionDistance


        def getCamJamDistance(self):
            return self.__camJamDistance


        def setCurrentSystemTime(self, value):
            self.__currentSystemTime = value


        def setVehicleID(self, value):
            self.__vehicleID = value


        def setVehicleType(self, value):
            self.__vehicleType = value


        def setVehicleSpeed(self, value):
            self.__vehicleSpeed = value


        def setVehicleAcceleration(self, value):
            self.__vehicleAcceleration = value


        def setLeadingVehicleData(self, value):
            self.__leadingVehicleData = value


        def setVehiclePosition(self, value):
            self.__vehiclePosition = value


        def setWarningDistance(self, value):
            self.__warningDistance = value


        def setInfoDistance(self, value):
            self.__infoDistance = value


        def setReceptionDistance(self, value):
            self.__receptionDistance = value


        def setCamJamDistance(self, value):
            self.__camJamDistance = value

        