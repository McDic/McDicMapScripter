# Essentials
import math
import random
import copy

# MDMS libraries - systemEvents needs event
from MDMS_sigVar import *
from MDMS_event import *

#------------------------------------------------
# Making system init events

def makeSystemEvents(initEvent):

    # __system
    systemMain = event('__system', parentEvent = initEvent, userDefined = False, blockIDset = False, makeFirstBlock = False)

    # __eventbackcall, __eventpopstack: Call back the event
    EBC = event('__eventbackcall', parentEvent = systemMain, userDefined = False, blockIDset = False) # eventCallEvent - calling by markerID
    EBC.firstBlock.commands.append("# This event is for calling events using markerID.")

    EPS = event('__eventpopstack', parentEvent = EBC, userDefined = False, blockIDset = False) # eventCallEvent - popping stack
    EPS.firstBlock.commands.append("# This event is for popping entity stack.")
    EPS.firstBlock.commands.append("scoreboard players tag @e[type=area_effect_cloud,tag=MDMS_marker_tempTarget] remove MDMS_marker_tempTarget")
    EPS.firstBlock.commands.append("scoreboard players operation tempUUIDstore MDMS_UUID = @s MDMS_prevStackID")
    EPS.firstBlock.commands.append("scoreboard players operation @e[type=area_effect_cloud,tag=MDMS_marker] MDMS_UUID -= tempUUIDstore MDMS_UUID")
    EPS.firstBlock.commands.append("scoreboard players tag @e[type=area_effect_cloud,tag=MDMS_marker,score_MDMS_UUID_min=0,score_MDMS_UUID=0] add MDMS_marker_tempTarget")
    EPS.firstBlock.commands.append("scoreboard players operation @e[type=area_effect_cloud,tag=MDMS_marker] MDMS_UUID += tempUUIDstore MDMS_UUID")
    #EPS.firstBlock.commands.append("execute @e[type=area_effect_cloud,tag=MDMS_marker_tempTarget] ~ ~ ~ function " + EBC.firstBlock.file.functionName)
            
    # __mainloop: tick counting loop
    TML = event('__mainloop', parentEvent = systemMain, userDefined = False, blockIDset = False)
    TML.firstBlock.commands.append("# This event is for main looping.")
    TML.firstBlock.commands.append("tp @e[type=area_effect_cloud,tag=MDMS_marker] @r")
    TML.firstBlock.commands.append("scoreboard players remove @e[type=area_effect_cloud,tag=MDMS_marker,score_MDMS_delay_min=0] MDMS_delay 1")

    # __mainloop.__eventcall
    TML_EC = event('__eventcall', parentEvent = TML, userDefined = False, blockIDset = False)
    # 1+: counting, 0: execute, -1: process end
    TML.firstBlock.commands.append("execute @e[type=area_effect_cloud,tag=MDMS_marker,score_MDMS_delay_min=0,score_MDMS_delay=0,score_MDMS_afterDelay_min=1] ~ ~ ~ function " + TML_EC.firstBlock.file.functionName)

    # __branchTemp
    BT = event('__branchtemp', parentEvent = systemMain, userDefined = False, blockIDset = False, makeFirstBlock = False)
    BTif = event('__if', parentEvent = BT, userDefined = False, blockIDset = False)
    BTif.firstBlock.commands.append("\n# This function is for branching-if.")
    BTif.firstBlock.commands.append('execute @r ~ ~ ~ summon area_effect_cloud ~ ~ ~ {CustomName:"MDMS_branchTemp_if", Tags:["MDMS_system", "MDMS_branchTemp", "MDMS_branchTemp_if"]}')
    BTelse = event('__else', parentEvent = BT, userDefined = False, blockIDset = False)
    BTelse.firstBlock.commands.append("\n# This function is for branching-else.")
    BTelse.firstBlock.commands.append('execute @r ~ ~ ~ summon area_effect_cloud ~ ~ ~ {CustomName:"MDMS_branchTemp_else", Tags:["MDMS_system", "MDMS_branchTemp", "MDMS_branchTemp_else"]}')

    # __variableMemory
    VM = event('__variablememory', parentEvent = systemMain, userDefined = False, blockIDset = False, makeFirstBlock = False)
    VMW = event('__write', parentEvent = VM, userDefined = False, blockIDset = False)
    VMR = event('__read', parentEvent = VM, userDefined = False, blockIDset = False)

    '''
    # __errors: Errors
    EE = event('__errors', parentEvent = systemMain) # errorEvent
    EE_eventCall = subBlock(EE) # FunctionCalledWithoutSelectorError
    EE_eventCall.commands.append("\n# This error is occured when event function is executed without any selector.")
    EE_eventCall.commands.append("say FunctionCalledWithoutSelectorError: Function called without any selectors.")
    '''
    
    # __init
    launchEvent = event('__start', parentEvent = systemMain, userDefined = False)
    launchEvent.firstBlock.commands.append("\n# This event is for launching whole project.")
    
    sigVar.systemInitCommands = ["# System init commands - Automatically added",
                                 "say Welcome, @a. I am McDic's scriptor. Thanks for using MDMS. You can see more info about MDMS in blog.mcdic.com.",
                                 "say Initializing system...",
                                 "kill @e[type=area_effect_cloud,tag=MDMS_system]",
                                 "gamerule gameLoopFunction "+ TML.firstBlock.file.functionName, # gameLoopFunction
                                 "gamerule commandBlockOutput false",
                                 "gamerule logAdminCommands false"]

    for objectiveType in sigVar.baseObjectives: # scores
        for objectiveName in sigVar.baseObjectives[objectiveType]:
            sigVar.systemInitCommands.append("scoreboard objectives remove " + objectiveName) # objectives remove
            sigVar.systemInitCommands.append("scoreboard objectives add " + objectiveName + " " + objectiveType) # objectives add
    for i in range(-100, 101): # numbers: -100 ~ 100
        sigVar.systemInitCommands.append("scoreboard players set " + str(i) + " MDMS_number " + str(i))
    for initCommand in sigVar.systemInitCommands: # systemInitCommands
        launchEvent.firstBlock.commands.append(initCommand)

    launch2 = subBlock(launchEvent)
    launch2.commands.append("\n# This subBlock is just used for processing after main init.")
    launchEventCaller = marker(launch2)
    launchEvent.firstBlock.commands += launchEventCaller.initCommands(mode = "eventCall")
    command  = "execute @e[type=area_effect_cloud,tag=MDMS_marker_beforeInit,c=1,name="+ launchEventCaller.entityName +"] ~ ~ ~ "
    command += "function " + initEvent.firstBlock.file.functionName
    launchEvent.firstBlock.commands.append(command)
