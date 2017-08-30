# Essentials
import math
import random
import copy

# Regular Expressions for compile
import re

# File operations
import os
import shutil

# MDMS libraries - event needs regex
from MDMS_sigVar import *
from MDMS_regex import *

#------------------------------------------------
# Variable support

class scoreVar:
    
    # [varID] : self
    # universalScoreVar = {}
    usingMemSize = 0
    maxMemoryLimit = 10000
    
    def USVlen():
        s = 0
        for mode in sigVar.supportedVariableTypes:
            s += len(sigVar.supportedVariableTypes[mode]["memSize"])
        return s

    # Int, Char : x
    # Float : x, y -> unit(x) * 10^y (1 <= abs(real x) < 10, Sccore is int(x * (10**8)))
    # Bool : x (0 False, Other True)
    # Long : x, y -> x * 2**32 + y (if x<0 -> real x = x + 2**32 / -2**31 <= x,y <= 2**31-1)

    # scoreboard objective : MDMS_varXXX
    def __init__(self, varName, parentEvent, valLens = [], varType = "int"):
        self.parentEvent = parentEvent

        self.dimension = len(valLens) # valLen[1][2][3][4]
        self.listLength = copy.deepcopy(valLens)
        self.totalArraySize = 1
        for length in self.listLength:
            if length <= 0:
                raise SyntaxError("Invalid "+ self.varName +" dimension length in __init__, class scoreVar")
            self.totalArraySize *= length
        
        self.varType = varType
        self.varName = varName
        #self.varID = parentEvent.nameID + "." + varName
        
        self.scoreObjectiveNum = scoreVar.usingMemSize # MDMS_varXXX
        if varType in sigVar.supportedVariableTypes: # Is that type valid?
            if self.varName not in self.parentEvent.variables: # First defined?
                self.parentEvent.variables[varName] = self
                scoreVar.usingMemSize += sigVar.supportedVariableTypes[self.varType]["memSize"] * self.totalArraySize
                if scoreVar.usingMemSize >= scoreVar.maxMemoryLimit:
                    raise MemoryError("Too many allocated memories in __init__ in class scoreVar")
            else:
                raise NameError("Already same variable defined in __init__ in class scoreVar")
        else:
            raise ValueError("Invalid mode input in __init__ in class scoreVar")

    def copyValueToOtherName(self, otherName, scoreObjective = "MDMS_tempCal", offsets = []):
        commands = []
        if len(offsets) != self.dimension:
            raise SyntaxError("Invalid memory access in ")
        totaloffset = 0
        for offset in offsets:
            totaloffset 

        if self.varType == "int":
            commands.append("scoreboard players operation " + otherName + "_int " + scoreObjective + " = @s MDMS_var" + str(self.scoreObjectiveNum + offset))             
        elif self.varType == "float":
            commands.append("scoreboard players operation " + otherName + "_float_factor " + scoreObjective + " = @s MDMS_var" + str(self.scoreObjectiveNum + offset*2))
            commands.append("scoreboard players operation " + otherName + "_float_offset " + scoreObjective + " = @s MDMS_var" + str(self.scoreObjectiveNum + offset*2 + 1))
        elif self.varType == "bool":
            commands.append("scoreboard players operation " + otherName + "_bool " + scoreObjective + " = @s MDMS_var" + str(self.scoreObjectiveNum + offset))
        return commands

#------------------------------------------------
# Marker

class marker:

    universalMarker = []
    
    def __init__(self, target):
        
        self.entityName = "MDMS_marker_" + str(id(self))
        
        self.target = target # Target should be the subBlock
        self.tags = ["MDMS_system", "MDMS_marker"]
        marker.universalMarker.append(self)

    def tempAECsummonCommand(CustomName, Tags):
        raise NotImplementedError("")

    def tagStr(self, additionalTags = []):
        totalstr = '['
        for tag in self.tags:
            totalstr += '"' + tag + '",'
        for tag in additionalTags:
            totalstr += '"' + tag + '",'
        totalstr = totalstr[:-1] + "]"
        return totalstr

    def basicNBTstr(self, additionalTags = []): # CustomName, Tags, Duration are only needed.
        return '{CustomName:"' + self.entityName + '", Tags:' + self.tagStr(additionalTags = additionalTags) + ', Duration:999999999}'

    def summonCommand(self, x="~", y="~", z="~"):
        return "summon area_effect_cloud " + str(x) + " " + str(y) + " " + str(z) + " " + self.basicNBTstr(additionalTags = ["MDMS_marker_beforeInit"])

    def initCommands(self, mode):

        # MDMS_prevStackID : the UUID of previous stack marker
        # MDMS_markerTarget: the next target block ID of marker
        
        tempSelector = "@e[type=area_effect_cloud,name="+ self.entityName +",tag=MDMS_marker_beforeInit,c=1]"
        result = []
        result.append("scoreboard players tag @e[type=area_effect_cloud,tag=MDMS_marker_beforeInit] remove MDMS_marker_beforeInit") # remove other beforeInit
        result.append(self.summonCommand()) # summon

        result.append("scoreboard players set "+ tempSelector + " MDMS_targetBlock " + str(subBlock.blockDestinationID[self.target])) # ID set

        result.append("scoreboard players add MDMS_markerTotalNum MDMS_UUID 1")
        result.append("scoreboard players operation " + tempSelector + " MDMS_UUID = MDMS_markerTotalNum MDMS_UUID")
        result.append("scoreboard players set "+ tempSelector + " MDMS_system -1") # Marker's MDMS_system = 1, Normal entities' MDMS_system = 0
        result.append("scoreboard players set "+ tempSelector + " MDMS_prevStackID -1")

        if mode == "eventCall": # stack
            result.append("scoreboard players operation "+ tempSelector + " MDMS_prevStackID = @s[type=area_effect_cloud,tag=MDMS_marker] MDMS_UUID")
        elif mode == "delay": # set the time
            raise ValueError("Delay mode is now unsupported since delay no more use new markers in initCommand in class marker")
        elif mode == "cinematic":
            #result.append("scoreboard players tag @e[type=area_effect_cloud,tag=MDMS_marker_beforeInit] add MDMS_cinematic_noWait")
            pass
        else:
            raise ValueError("Invalid mode in initCommand in class marker")

        #result.append("scoreboard players tag @e[type=area_effect_cloud,tag=MDMS_marker_beforeInit] remove MDMS_marker_beforeInit") # remove beforeInit
        return result            


#------------------------------------------------
# Functionfile: Manage the function file

class functionFile: # functionfile

    universalFiles = {}
    defaultNameSpace = "mdms"

    def __init__(self, subPath, fileName = None):
        
        if fileName is None:
            self.fileName = functionFile.defaultNameSpace + "_" + str(id(self)) + ".mcfunction"
        else:
            self.fileName = fileName + ".mcfunction"

        if subPath in ("", None):
            self.filePath = self.fileName
        else:
            self.filePath = subPath + "/" + self.fileName

        if self.filePath in functionFile.universalFiles:
            raise NameError("Already same filename exist in functionFile.universalFiles in __init__ in class functionFile")
        else:
            functionFile.universalFiles[self.filePath] = self # adding to universalFiles

        namespace = re.findall(reStr.variableName, self.filePath, re.M)[0]
        self.functionName = namespace + ":" + re.sub(r'.mcfunction', r'', self.filePath[len(namespace)+1:])

        if not os.path.isdir(subPath):
            os.makedirs(subPath)

        #print(subPath, self.filePath)
        self.file = open(self.filePath, 'w')
        #self.file.write("# McDic MapScripter - " + functionFile.defaultNameSpace.upper() + "\n"
        #                + "# Designed for Minecraft map making\n"
        #                + "# Made by McDic\n"
        #                + "# More info at blog.mcdic.com\n\n")

    def write(self, commands):
        for command in commands:
            self.file.write(command)
            self.file.write("\n")

#------------------------------------------------
# SubBlock: Each part of event

class subBlock:

    blockDestinationID = {None:-1} # block: id, None: -1 / (values: -1, 1, 2, 3, ... len-1)
    bDID_reverse = {-1:None}

    def __init__(self, parentEvent): #, previousBlock):

        self.parentEvent = parentEvent
        self.subBlockName = "__sub" + str(len(parentEvent.subBlockMap))
        parentEvent.subBlockMap.append(self)
        #if previousBlock is not None:
        #    previousBlock.nextSubBlocks.append(self)
        
        self.commands = []
        #self.nextSubBlocks = [] # (delay/if)
        self.pathList = copy.deepcopy(parentEvent.pathList)
        self.pathList.append(parentEvent.eventName)
        
        self.path = ""
        for i in range(0, len(self.pathList)):
            self.path += self.pathList[i] + "/"
        self.path = self.path[:-1]
        self.file = functionFile(self.path, fileName = self.subBlockName)

        self.commands.append("# SubBlock Information:")
        if (parentEvent is None) or parentEvent.blockIDset:
            subBlock.blockDestinationID[self] = len(subBlock.blockDestinationID)
            subBlock.bDID_reverse[subBlock.blockDestinationID[self]] = self
            self.commands.append("#   BlockDestination ID: " + str(subBlock.blockDestinationID[self]))
        else:
            self.commands.append("#   No BlockDestination ID for this subBlock")
        self.commands.append("#   Function Name: \"" + self.file.functionName + "\"\n")

        self.commands.append("# MDMS_system scoring.")
        self.commands.append("scoreboard players set @e[tag=!MDMS_system] MDMS_system 0\n")

        '''
        # tellraw debug
        if "mcdic_mapscripter.__system.__mainloop" in event.universalEvents and self.parentEvent is not event.universalEvents["mcdic_mapscripter.__system.__mainloop"]:
            self.commands.append("# Debugging. Add tag \"MDMS_debug\" to get debug messages.")
            debugStr  = 'tellraw @a[score_MDMS_debugMsg_min=1,score_MDMS_debugMsg=1] {"text":"", "color":"dark_red", "extra":[{"text":"DEBUG: Running ' + self.file.functionName
            debugStr += ' from UUID "}, {"score":{"objective":"MDMS_UUID", "name":"@s"}}, {"text":", markerID "},'            
            #debugStr  = 'tellraw @a[score_MDMS_debugMsg_min=1,score_MDMS_debugMsg=1] {"text":"", "color":"dark_red", "extra":[{"text":"DEBUG:\\n  Running ' + self.file.functionName
            #debugStr += '\\n  from UUID "}, {"score":{"objective":"MDMS_UUID", "name":"@s"}}, {"text":", markerID "},'
            debugStr += ' {"score":{"objective":"MDMS_targetBlock", "name":"@s"}}, {"text":", prevStack "},'
            debugStr += ' {"score":{"objective":"MDMS_prevStackID", "name":"@s"}}]}'
            self.commands.append(debugStr + "\n")
        '''

    def __repr__(self):
        totalstr  = "SubBlock " + self.file.functionName + " details:"
        totalstr += "\n\t\tParentEvent: " + str(self.parentEvent.eventName)
        totalstr += "\n\t\tPath: " + str(self.path)
        totalstr += "\n\t\tCommands:"
        for command in self.commands:
            totalstr += "\n\t\t\t" + str(command)
        return totalstr

    def makeBinarySearch(self, baseSelector, scoreObjective, valueList, left, right, BSdict, preExecute = "execute @s ~ ~ ~ "):

        if left > right:
            #raise ValueError("Warning, the min score is bigger than max score in makeBinarySearch in class subBlock. " + str(minScore) + " " + str(maxScore))
            return

        elif left == right:
            BSdict[left] = self
            return

        newBlockLeft = subBlock(self.parentEvent)
        newBlockRight = subBlock(self.parentEvent)

        mid = math.floor((left + right)/2)
        #print(minScore, midScore, maxScore)

        selectorLeft, selectorRight = "", ""
        if baseSelector[-1] == "]":
            selectorLeft = baseSelector[:-1] + ",score_" + scoreObjective + "_min=" + str(valueList[left]) + ",score_" + scoreObjective + "=" + str(valueList[mid]) + "]"
            selectorRight = baseSelector[:-1] + ",score_" + scoreObjective + "_min=" + str(valueList[mid+1]) + ",score_" + scoreObjective + "=" + str(valueList[right]) + "]"
        else:
            selectorLeft = baseSelector + "[score_" + scoreObjective + "_min=" + str(valueList[left]) + ",score_" + scoreObjective + "=" + str(valueList[mid]) + "]"
            selectorRight = baseSelector + "[score_" + scoreObjective + "_min=" + str(valueList[mid+1]) + ",score_" + scoreObjective + "=" + str(valueList[right]) + "]"

        commandLeft  = preExecute + "function " + newBlockLeft.file.functionName  + " if " + selectorLeft
        commandRight = preExecute + "function " + newBlockRight.file.functionName + " if " + selectorRight
        self.commands.append(commandLeft)
        self.commands.append(commandRight)

        newBlockLeft.makeBinarySearch(baseSelector, scoreObjective, valueList, left, mid, BSdict, preExecute = preExecute) # Left ~ leftMid
        newBlockRight.makeBinarySearch(baseSelector, scoreObjective, valueList, mid+1, right, BSdict, preExecute = preExecute) # rightMid ~ Right
        return

    def statementLinking(self, statement, trueBlock, falseBlock, modeStr = "If ", inputIndex = None):

        tempBranchIf = event.universalEvents["mcdic_mapscripter.__system.__branchtemp.__if"].firstBlock
        tempBranchElse = event.universalEvents["mcdic_mapscripter.__system.__branchtemp.__else"].firstBlock

        (statementCalCommands, statementType) = calculateStatement(compileStatement(statement), self.parentEvent, inputIndex = inputIndex)
        if statementType != "bool":
            raise TypeError("Invalid statement type in line " + str(inputIndex))

        self.commands += statementCalCommands
        self.commands.append("kill @e[type=area_effect_cloud,tag=MDMS_branchTemp]")
        self.commands.append("kill @e[type=area_effect_cloud,tag=MDMS_tempComparison]")
        self.commands.append('summon area_effect_cloud ~ ~ ~ {CustomName:"MDMS_branchTempComparison", Tags:["MDMS_system", "MDMS_tempComparison"]}')
        self.commands.append("scoreboard players operation @e[type=area_effect_cloud,tag=MDMS_tempComparison] MDMS_tempCal = MDMS_statementResult_bool MDMS_tempCal")
        self.commands.append("function " + tempBranchIf.file.functionName + " unless @e[type=area_effect_cloud,tag=MDMS_tempComparison,score_MDMS_tempCal_min=0,score_MDMS_tempCal=0]")
        self.commands.append("function " + tempBranchElse.file.functionName + " if @e[type=area_effect_cloud,tag=MDMS_tempComparison,score_MDMS_tempCal_min=0,score_MDMS_tempCal=0]")
        self.commands.append("kill @e[type=area_effect_cloud,tag=MDMS_tempComparison]")
   
        ifLinkCommand = "execute @s ~ ~ ~ function " + trueBlock.file.functionName + " if @e[type=area_effect_cloud,tag=MDMS_branchTemp_if]"
        elseLinkCommand = "execute @s ~ ~ ~ function " + falseBlock.file.functionName + " if @e[type=area_effect_cloud,tag=MDMS_branchTemp_else]"
        self.commands.append(ifLinkCommand)
        self.commands.append(elseLinkCommand)

#------------------------------------------------
# Class event

class event:

    universalEvents = {}
    userDefinedEvents = {}

    def __init__(self, eventName = "", parentEvent = None, userDefined = False, blockIDset = True, makeFirstBlock = True):

        self.eventName = eventName
        if eventName == "":
            self.eventName = "event_id" + str(id(self))

        self.blockIDset = blockIDset
        self.parentEvent = parentEvent
        self.subBlockMap = []
        self.subEvents = []
        if parentEvent is not None:
            parentEvent.subEvents.append(self)

        #self.actions = [] # [(actionType, actionDetail), ...]
        
        if parentEvent is None:
            self.pathList = []
        else:
            self.pathList = copy.deepcopy(parentEvent.pathList) + [parentEvent.eventName]

        self.nameID = ""
        if len(self.pathList) > 0:
            self.nameID = self.pathList[0] + "."
        for i in range(1, len(self.pathList)):
            self.nameID += self.pathList[i] + "."
        self.nameID += self.eventName

        # Add this event to universalEvents
        if self.nameID in event.universalEvents:
            raise NameError("Already same event exist in __init__ in class event")
        else:
            event.universalEvents[self.nameID] = self
            if userDefined:
                event.userDefinedEvents[self.nameID] = self

        self.path = ""
        for i in range(0, len(self.pathList)):
            self.path += self.pathList[i] + "/"
        self.path = self.path[:-1]

        if makeFirstBlock:
            self.firstBlock = subBlock(self)
        else:
            self.firstBlock = None
        self.endBlock = None
        
        self.variables = {}
        self.cinematics = []
        

    def __repr__(self):
        totalstr  = "Event " + self.eventName + " details:\n"
        if self.parentEvent is None:
            totalstr += "\tParentEvent = None"
        else:
            totalstr += "\tParentEvent = " + str(self.parentEvent.eventName)

        totalstr += "\n\tFirstBlock: " + str(self.firstBlock)
        if self.firstBlock is not self.endBlock:
            totalstr += "\n\tEndBlock: " + str(self.endBlock)
        else:
            totalstr += "\n\tEndBlock is same as FirstBlock"
        totalstr += "\n\tEvent ID: " + str(self.nameID)
        totalstr += "\n\tPath: " + str(self.path)
        return totalstr
