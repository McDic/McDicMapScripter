# Essentials
import math
import random
import copy

# Regular Expressions for compile
import re

# File operations
import os
import shutil

# MDMS libraries - Main needs all
from MDMS_sigVar import *
from MDMS_regex import *
from MDMS_math import *
from MDMS_cinematic import *
from MDMS_armorstand import *
from MDMS_event import *
from MDMS_normalStatement import *
from MDMS_systemEvents import *

#------------------------------------------------
# Compile events
                
def compileMCEvent(lines, startindex, endindex, eventName, tabLevel = 0,
                   parentEvent = None, mainInit = False, userDefined = False): # return thisEvent

    thisEvent = event(eventName, parentEvent = parentEvent, userDefined = userDefined)
    thisBlock = thisEvent.firstBlock
    index = startindex - 1
    mode = "Normal"

    if mainInit: # At first only used to create initializing commands
        makeSystemEvents(thisEvent)

    thisCinematic = None
    cinematicMode = ""
    cinematicRelative = False
    cinematicWait = True
    
    ifSubEventQueue = []
    while index < endindex-1:
        index += 1

        print("Compiling line " + str(index) + "...(tabLevel "+ str(tabLevel) +", "+ mode +" mode)")

        line = lines[index]
        line = re.sub(r'\n', "", line) # Removing \n
        line = re.sub(reStr.selector, reStr.makeCommandSelectorSafe, line) # Making selector safe

        lineMatch = re.findall(reStr.emptyLine, line, re.M) # Empty line - comment of real empty
        if lineMatch: # comment or empty line
            continue

        if mode == "Normal":

            '''
            lineMatch = re.findall(reStr.endLine(tabLevel), line, re.M) # End line
            if lineMatch:
                thisEvent.endBlock = thisBlock
                break
            '''
            
            lineMatch = re.findall(reStr.commandLine(tabLevel), line, re.M) # /command
            if lineMatch:
                command = re.sub(reStr.preCommand, r'', line)
                commandType = command.split(" ")[0]
                if commandType in sigVar.commands: # Filter the unknown commands
                    thisBlock.commands.append(command)
                    if "summon" in command:
                        thisBlock.commands.append("scoreboard players set @e[tag=!MDMS_system] MDMS_system 0")
                else:
                    raise NameError("Unknown command in line " + str(index))
                continue

            lineMatch = re.findall(reStr.delayLine(tabLevel), line, re.M) # Delay time
            if lineMatch:
                time = reStr.tickExchange(re.findall(reStr.time, line, re.M)[0])

                if time < 0.05 :
                    raise ValueError("Time value is too small in line " + str(index))
                
                nextBlock = subBlock(thisEvent)
                thisBlock.commands.append("\n# Delay " + str(time) + " ticks and go <" + nextBlock.file.functionName + ">")
                thisBlock.commands.append("scoreboard players set @s MDMS_delay " + str(time))
                thisBlock.commands.append("scoreboard players set @s MDMS_afterDelay " + str(subBlock.blockDestinationID[nextBlock]))
                thisBlock = nextBlock # jump to the next block
                continue

            lineMatch = re.findall(reStr.eventCallLine(tabLevel, "Recursive"), line, re.M) # Eventcall - Recursive
            if lineMatch:

                givenEventID = re.findall(reStr.eventID, line, re.M)[1]
                searchEvent = thisEvent
                while True:
                    eventID = searchEvent.nameID + "." + givenEventID
                    if eventID in event.universalEvents:
                        break
                    elif searchEvent.parentEvent is not None:
                        searchEvent = searchEvent.parentEvent
                    else:
                        eventID = None
                        break
                
                if eventID is not None:
                    targetEvent = event.universalEvents[eventID]
                    nextBlock = subBlock(thisEvent)
                    newEventCaller = marker(nextBlock)
                    thisBlock.commands.append("\n# EventCall(Recursive) " + eventID)
                    thisBlock.commands += newEventCaller.initCommands(mode = "eventCall")
                    # The reason why I use execute is to use @s later.
                    command  = "execute @e[type=area_effect_cloud,tag=MDMS_marker_beforeInit,c=1,name="+ newEventCaller.entityName +"] ~ ~ ~ "
                    command += "function " + targetEvent.firstBlock.file.functionName
                    thisBlock.commands.append(command)
                    thisBlock = nextBlock
                    continue
                else:
                    raise UnboundLocalError("UnboundLocalError in eventcalling " + eventName + " at line " + str(index))

            lineMatch = re.findall(reStr.eventCallLine(tabLevel, "Multi"), line, re.M) # Eventcall - MultiProcessing
            if lineMatch:

                givenEventID = re.findall(reStr.eventID, line, re.M)[1]
                searchEvent = thisEvent
                while True:
                    eventID = searchEvent.nameID + "." + givenEventID
                    if eventID in event.universalEvents:
                        break
                    elif searchEvent.parentEvent is not None:
                        searchEvent = searchEvent.parentEvent
                    else:
                        eventID = None
                        break
                
                if eventID is not None:
                    targetEvent = event.universalEvents[eventID]
                    newEventCaller = marker(None)
                    thisBlock.commands.append("\n# EventCall(MultiProcessing) " + eventID)
                    thisBlock.commands += newEventCaller.initCommands(mode = "eventCall")
                    # The reason why I use execute is to use @s later.
                    command  = "execute @e[type=area_effect_cloud,tag=MDMS_marker_beforeInit,c=1,name="+ newEventCaller.entityName +"] ~ ~ ~ "
                    command += "function " + targetEvent.firstBlock.file.functionName
                    thisBlock.commands.append(command)
                    thisBlock.commands.append("")
                    continue
                else:
                    raise UnboundLocalError("UnboundLocalError in eventcalling " + eventName + " at line " + str(index))

            lineMatch = re.findall(reStr.eventDefLine(tabLevel), line, re.M) # Event definition
            if lineMatch:
                newEventName = (re.findall(reStr.variableName, line, re.M)[1]).lower() # function should be lowercase
                (newSubEvent, index) = compileMCEvent(lines, index+1, endindex, newEventName,
                                                      tabLevel = tabLevel+1, parentEvent = thisEvent, userDefined = True)
                continue

            lineMatch = re.findall(reStr.whileLine(tabLevel), line, re.M) # While statement
            if lineMatch:
                (whileSubEvent, index) = compileMCEvent(lines, index+1, endindex, thisBlock.subBlockName + "_while",
                                                        tabLevel = tabLevel+1, parentEvent = thisEvent)
                ifSubEventQueue.append(whileSubEvent)
                afterWhileBlock = subBlock(thisEvent)
                normalStatement = re.sub(r'While', r'', line)
                normalStatement = re.sub(reStr.blank, r' ', normalStatement)
                
                whileSubEvent.endBlock.commands.append("\n# While: " + normalStatement)
                whileSubEvent.endBlock.statementLinking(normalStatement, whileSubEvent.firstBlock, afterWhileBlock, inputIndex = index)
                thisBlock.commands.append("\n# While " + normalStatement)
                thisBlock.statementLinking(normalStatement, whileSubEvent.firstBlock, afterWhileBlock, inputIndex = index)
                thisBlock = afterWhileBlock
                continue

            lineMatch = re.findall(reStr.ifLine(tabLevel), line, re.M) # If statement
            if lineMatch: # If

                # make new subEvent(for if) and subBlock(for elif, else)
                (ifSubEvent, index) = compileMCEvent(lines, index+1, endindex, thisBlock.subBlockName + "_if",
                                                     tabLevel = tabLevel+1, parentEvent = thisEvent)
                ifSubEventQueue.append(ifSubEvent)
                nextBlockElse = subBlock(thisEvent)
                normalStatement = re.sub(r'If', r'', line)
                normalStatement = re.sub(reStr.blank, r' ', normalStatement)

                thisBlock.commands.append("\n# If " + normalStatement)
                thisBlock.statementLinking(normalStatement, ifSubEvent.firstBlock, nextBlockElse, inputIndex = index)
                thisBlock = nextBlockElse
                mode = "Branch"
                continue

            lineMatch = re.findall(reStr.OR((reStr.cinematicLine(tabLevel, 'Linear'),
                                             reStr.cinematicLine(tabLevel, 'Spline'))), line, re.M) # Cinematic Linear/Spline
            if lineMatch:
                mode = "Cinematic"
                cinematicMode = re.findall(reStr.variableName, line, re.M)[1] # Point/Linear/Spline
                cinematicRelative = (re.findall(r'Relative', line, re.M) != []) # Absolute/Relative
                cinematicWait = (re.findall(r'Wait', line, re.M) != []) # Wait/NotWait
                cinematicSelector = re.findall(reStr.selector, line, re.M)[0]
                thisCinematic = cinematic(relative = cinematicRelative, wait = cinematicWait,
                                          mode = cinematicMode, parentEvent = thisEvent, selector = cinematicSelector)
                continue

            tempStatus = False
            for varType in sigVar.supportedVariableTypes:
                lineMatch = re.findall(reStr.varDefLine(tabLevel, varType), line, re.M) # Variable Definition / Int A[][][]
                if lineMatch:
                    tempStatus = True
                    varName = re.findall(reStr.variableName, line)[1]
                    memSizeMatch = re.findall(reStr.memAddressConst, line)
                    offsets = []
                    if memSizeMatch:
                        memSizeStr = re.findall(reStr.memAddressConst, line)[0]
                        memSizeStr = re.sub(r'\]\[', r' ', memSizeStr)
                        memSizeStr = re.sub(r'\]|\[', r'', memSizeStr)
                        offsets = memSizeStr.split(" ")
                        for i in range(len(offsets)):
                            offsets[i] = int(offsets[i])

                    # varScore: def __init__(self, varName, parentEvent, valLens = [], varType = "int"):
                    thisBlock.commands.append("\n# Variables defined: " + line)
                    if varName not in thisEvent.variables:
                        newVarScore = scoreVar(varName, thisEvent, offsets, varType = varType)
                        for i in range(sigVar.supportedVariableTypes[newVarScore.varType]["memSize"] * newVarScore.totalArraySize):
                            thisBlock.commands.append("scoreboard objectives add MDMS_var" + str(i + newVarScore.scoreObjectiveNum) + " dummy Variable " + varName + "(" + varType + ")")
                            thisBlock.commands.append("scoreboard players set @s MDMS_var" + str(i + newVarScore.scoreObjectiveNum) + " 0")
                    else:
                        raise NameError("You can't redefine variables with same name in line " + str(index))
            if tempStatus:
                continue
    
            lineMatch = re.findall(reStr.normalStatementLine(tabLevel), line, re.M) # Normal statements
            if lineMatch:
                normalState = re.sub(reStr.blank, r' ', line)
                thisBlock.commands.append("\n# Statement calculation: " + line)
                thisBlock.commands += calculateStatement(compileStatement(normalState), thisEvent, inputIndex = index)[0]
                continue

        elif mode == "Branch":
            
            lineMatch = re.findall(reStr.elifLine(tabLevel), line, re.M) # Elif statement
            if lineMatch:

                # make new subevent(for if) and subblock(for elif, else)
                (elifSubEvent, index) = compileMCEvent(lines, index+1, endindex, thisBlock.subBlockName + "_elif",
                                                     tabLevel = tabLevel+1, parentEvent = thisEvent)
                ifSubEventQueue.append(elifSubEvent)
                nextBlockElse = subBlock(thisEvent)
                normalStatement = re.sub(r'Elif', r'', line)
                normalStatement = re.sub(reStr.blank, r' ', normalStatement)

                thisBlock.commands.append("\n# Elif " + normalStatement)
                thisBlock.statementLinking(normalStatement, elifSubEvent.firstBlock, nextBlockElse, inputIndex = index)
                thisBlock = nextBlockElse
                continue

            lineMatch = re.findall(reStr.elseLine(tabLevel), line, re.M) # Else statement
            if lineMatch:
                (elseSubEvent, index) = compileMCEvent(lines, index+1, endindex, thisBlock.subBlockName + "_else",
                                                       tabLevel = tabLevel+1, parentEvent = thisEvent)
                ifSubEventQueue.append(elseSubEvent)
                ifLinkCommand = "execute @s ~ ~ ~ function " + elseSubEvent.firstBlock.file.functionName
                thisBlock.commands.append("\n# Else")
                thisBlock.commands.append(ifLinkCommand)
                continue
            
            # return to Normal Mode
            afterBranchBlock = subBlock(thisEvent)
                
            linkToABB = "execute @s ~ ~ ~ function " + afterBranchBlock.file.functionName
            for iEvent in ifSubEventQueue:
                iEvent.endBlock.commands.append("\n# Linking to back")
                iEvent.endBlock.commands.append(linkToABB)
            if lineMatch: # If there is no else
                thisBlock.commands.append(linkToABB)

            ifSubEventQueue = []
            thisBlock = afterBranchBlock
            mode = "Normal"
            index -= 1
            continue

        elif mode == "Cinematic":

            lineMatch = re.findall(reStr.cinematicCoordLine(tabLevel, cinematicMode), line, re.M) # Cinematic coordinates
            if lineMatch:
                
                if cinematicMode == "Point": # starttime, endtime, x, y, z, ry, rx
                    startTime = reStr.tickExchange(re.findall(reStr.time, line, re.M)[0])
                    endTime = reStr.tickExchange(re.findall(reStr.time, line, re.M)[1])
                    x, y, z, ry, rx = None, None, None, None, None
                    lineCoord5 = re.findall(reStr.coord5, line, re.M)
                    lineCoord3 = re.findall(reStr.coord3, line, re.M)
                    if lineCoord5:
                        x, y, z, ry, rx = re.split(reStr.blank, lineCoord5[0])
                    elif lineCoord3:
                        x, y, z = re.split(reStr.blank, lineCoord3[0])

                    mode = "Normal"
                    raise NotImplementedError("")

                elif cinematicMode in ("Linear", "Spline"):
                    time = reStr.tickExchange(re.findall(reStr.time, line, re.M)[0])
                    x, y, z, ry, rx, ryd, rxd = None, None, None, None, None, "*", "*"
                    lineCoord5Dir = re.findall(reStr.coord5Dir, line, re.M)
                    lineCoord5 = re.findall(reStr.coord5, line, re.M)
                    lineCoord3 = re.findall(reStr.coord3, line, re.M)

                    if lineCoord5Dir:
                        x, y, z, ry, rx, ryd, rxd = re.split(reStr.blank, lineCoord5Dir[0])
                        if thisCinematic.dimension == "Undefined":
                            thisCinematic.dimension = 5
                        elif thisCinematic.dimension == 3:
                            raise SyntaxError("Different dimension input in line " + str(index))
                    elif lineCoord5:
                        x, y, z, ry, rx = re.split(reStr.blank, lineCoord5[0])
                        if thisCinematic.dimension == "Undefined":
                            thisCinematic.dimension = 5
                        elif thisCinematic.dimension == 3:
                            raise SyntaxError("Different dimension input in line " + str(index))
                    elif lineCoord3:
                        x, y, z = re.split(reStr.blank, lineCoord3[0])
                        if thisCinematic.dimension == "Undefined":
                            thisCinematic.dimension = 3
                        elif thisCinematic.dimension == 5:
                            raise SyntaxError("Different dimension input in line " + str(index))

                    if time in thisCinematic.coords:
                        raise Exception("Same cinematic times appeared in line " + str(index))

                    thisCinematic.coords[time] = {}
                    thisCinematic.coords[time]["x"] = float(x)
                    thisCinematic.coords[time]["y"] = float(y)
                    thisCinematic.coords[time]["z"] = float(z)
                    if ry is not None and rx is not None:
                        thisCinematic.coords[time]["ry"] = float(ry)
                        thisCinematic.coords[time]["rx"] = float(rx)
                        thisCinematic.coords[time]["ryd"] = ryd
                        thisCinematic.coords[time]["rxd"] = rxd

                continue

            else:

                if cinematicMode == "Point":
                    raise SyntaxError("Invalid cinematicPoint syntax in line " + str(index))

                else:
                    nextBlock = subBlock(thisEvent)
                    if cinematicMode == "Linear" and len(thisCinematic.coords) < 2:
                        raise IndexError("Invalid index length(linear) in line " + str(index))
                    elif cinematicMode == "Spline" and len(thisCinematic.coords) < 3:
                        raise IndexError("Invalid index length(spline) in line " + str(index))

                    thisCinematic.writeCoord(thisBlock, nextBlock)
                    mode = "Normal"
                    index -= 1
                    thisBlock = nextBlock
                    continue
        
        elif mode == "Animation":
            raise NotImplementedError("")

        if tabLevel > 0:
            index -= 1
            break
        elif line == "$END":
            print("Reached end of line.")
            break
        else:
            raise SyntaxError("Compile Error at line " + str(index) + "\n" + line)

    thisEvent.endBlock = thisBlock
    return (thisEvent, index) # return index

#------------------------------------------------
# Get input and compile

print("Input the name of file. The files will be generated in mcdic_mapscripter folder.")
inputFileName = input()
inputFile = open(inputFileName, "r")
#"mcdic_mapscripter" = re.sub(r'\.txt', '', inputFileName) # Project name = file name
inputs = inputFile.readlines() + ["$END"] # inputs = [line, line, ...]
inputFile.close()

if os.path.exists("mcdic_mapscripter"):
    shutil.rmtree("mcdic_mapscripter") # delete MDMS Contents if exists

compileMCEvent(inputs, 0, len(inputs), eventName = "mcdic_mapscripter", userDefined = True, mainInit = True)

#------------------------------------------------
# Post processing

tempList = range(1, len(subBlock.blockDestinationID))

# __mainloop.__eventcall backprocessing
MLEC = event.universalEvents["mcdic_mapscripter.__system.__mainloop.__eventcall"]
MLEC_dict = {}
MLEC.firstBlock.makeBinarySearch("@s[type=area_effect_cloud,tag=MDMS_marker,score_MDMS_delay=0,score_MDMS_delay_min=0]",
                                 "MDMS_afterDelay", tempList, 0, len(tempList)-1, MLEC_dict)
for key in MLEC_dict:
    tempBlock = subBlock.bDID_reverse[tempList[key]]
    MLEC_dict[key].commands.append("\n# Event Calling from delay.")
    MLEC_dict[key].commands.append("scoreboard players set @s[type=effect_cloud,tag=MDMS_marker] MDMS_afterDelay -1")
    MLEC_dict[key].commands.append("execute @s[type=area_effect_cloud,tag=MDMS_marker] ~ ~ ~ function " + tempBlock.file.functionName)
    
# Event call backprocessing - popstack
# Already end during compile
# EPS = event.universalEvents["mcdic_mapscripter.__system.__eventpopstack"]

# Event call backprocessing - calling
ECB = event.universalEvents["mcdic_mapscripter.__system.__eventbackcall"]
ECBdict = {}
ECB.firstBlock.makeBinarySearch("@s[type=area_effect_cloud,tag=MDMS_marker]", "MDMS_targetBlock",
                                tempList, 0, len(tempList)-1, ECBdict)
for key in ECBdict:
    tempBlock = subBlock.bDID_reverse[tempList[key]]
    ECBdict[key].commands.append("\n# Event Calling from backprocessing.")
    ECBdict[key].commands.append("execute @s ~ ~ ~ function " + event.universalEvents["mcdic_mapscripter.__system.__eventbackcall.__eventpopstack"].firstBlock.file.functionName)
    ECBdict[key].commands.append("kill @s")
    ECBdict[key].commands.append("execute @e[type=area_effect_cloud,tag=MDMS_marker_tempTarget] ~ ~ ~ function " + tempBlock.file.functionName)
    
# Eventcall backprocessing - normal
for iEvent in event.userDefinedEvents:
    if event.universalEvents[iEvent].endBlock is not None:
        event.universalEvents[iEvent].endBlock.commands.append("\n# This is for EventCall backprocessing.")
        event.universalEvents[iEvent].endBlock.commands.append("execute @s ~ ~ ~ function " + event.universalEvents["mcdic_mapscripter.__system.__eventbackcall"].firstBlock.file.functionName + " if @s[type=area_effect_cloud,tag=MDMS_marker,score_MDMS_prevStackID_min=0]")
        event.universalEvents[iEvent].endBlock.commands.append("kill @s[type=area_effect_cloud,score_MDMS_prevStackID=-1]")

# Memory access method - writing
EVW = event.universalEvents["mcdic_mapscripter.__system.__variablememory.__write"]
EVWdict = {}
EVW.firstBlock.makeBinarySearch("@s[type=area_effect_cloud,tag=MDMS_marker]", "MDMS_targetMem",
                               list(range(scoreVar.usingMemSize)), 0, scoreVar.usingMemSize - 1, EVWdict)
for key in EVWdict:
    EVWdict[key].commands.append("\n# Memory writing access with MDMS_targetMem.")
    EVWdict[key].commands.append("scoreboard players operation @s MDMS_var" + str(key) + " = @s MDMS_tempCal")
    EVWdict[key].commands.append("scoreboard players set @s MDMS_targetMem -1")

# Memory access method - reading
EVR = event.universalEvents["mcdic_mapscripter.__system.__variablememory.__read"]
EVRdict = {}
EVR.firstBlock.makeBinarySearch("@s[type=area_effect_cloud,tag=MDMS_marker]", "MDMS_targetMem",
                               list(range(scoreVar.usingMemSize)), 0, scoreVar.usingMemSize - 1, EVRdict)
for key in EVRdict:
    EVRdict[key].commands.append("\n# Memory reading access with MDMS_targetMem.")
    EVRdict[key].commands.append("scoreboard players operation @s MDMS_tempCal = @s MDMS_var" + str(key))
    EVRdict[key].commands.append("scoreboard players set @s MDMS_targetMem -1")

# Write all commands entered
for iEvent in event.universalEvents:
    for iSubBlock in event.universalEvents[iEvent].subBlockMap:
        iSubBlock.file.write(iSubBlock.commands)

# Close all files
for key in functionFile.universalFiles:
    file = functionFile.universalFiles[key]
    file.file.close()

print("\n\nSuccessfully translated.")
print("Copy the '"+ "mcdic_mapscripter" +"' folder to your world and type '/function "+ event.universalEvents["mcdic_mapscripter.__system.__start"].firstBlock.file.functionName +"'.")
