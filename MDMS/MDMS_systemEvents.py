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

    # __operations: using MDMS_opCal_(A/B/... + result)_(int/float/..)
    OP = event('__operation', parentEvent = systemMain, userDefined = False, blockIDset = False, makeFirstBlock = False)

    '''
    operatorPriority = {'(':100, ')':100, '[':100, ']':100, '{':100, '}':100,
                        'Exist':20, 'Print':20, 'ReadScore':20, # Built-in Functions
                        '^':9, '~':8, '+@':8, '-@':8, # +@, -@ : single plus and minus
                        '*':7, '/':7, '%':7, '+':6, '-':6,
                        '>=':5, '>':5, '<':5, '<=':5, '==':4, '!=':4,
                        '=':3, '+=':3, '-=':3, '*=':3, '/=':3, '%=':3, '^=':3,
                        'And':2, 'Not':2, 'Or':2, ',':1}
    '''

    # type convert
    OP_typeconvert = event('__typeconvert', parentEvent = OP, userDefined = False, blockIDset = False, makeFirstBlock = False) # Type converting
    # int()
    OP_typeconvert_int = event('__to_int', parentEvent = OP_typeconvert, userDefined = False, blockIDset = False, makeFirstBlock = False)
    # int(int)
    OP_typeconvert_int_int = event('__from_int', parentEvent = OP_typeconvert_int, userDefined = False, blockIDset = False, makeFirstBlock = True)
    OP_typeconvert_int_int.firstBlock.commands.append("scoreboard players operation MDMS_opCal_result_int MDMS_tempCal = MDMS_opCal_A_int MDMS_tempCal")
    # int(float), float = factor * 10^(offset-8)
    OP_typeconvert_int_float = event('__from_float', parentEvent = OP_typeconvert_int, userDefined = False, blockIDset = False, makeFirstBlock = True)
    OP_typeconvert_int_float.firstBlock.commands.append("scoreboard players operation MDMS_opCal_result_int MDMS_tempCal = MDMS_opCal_A_float_factor MDMS_tempCal")
    OP_typeconvert_int_float.firstBlock.commands.append("kill @e[type=area_effect_cloud,tag=MDMS_opCal_TC_ff_loop]")
    OP_typeconvert_int_float.firstBlock.commands.append('summon area_effect_cloud ~ ~ ~ {CustomName:"MDMS_opCal_TC_ff_loop", Tags:["MDMS_system", "MDMS_opCal_TC_ff_loop"]}')
    OP_typeconvert_int_float.firstBlock.commands.append("scoreboard players operation @e[type=area_effect_cloud,tag=MDMS_opCal_TC_ff_loop] MDMS_tempCal = MDMS_opCal_A_float_offset MDMS_tempCal")
    OP_typeconvert_int_float.firstBlock.commands.append("scoreboard players remove @e[type=area_effect_cloud,tag=MDMS_opCal_TC_ff_loop] MDMS_tempCal 8")
    OPt_ff_loop = subBlock(OP_typeconvert_int_float) # temp loop for int(float)
    OP_typeconvert_int_float.firstBlock.commands.append("execute @e[type=area_effect_cloud,tag=MDMS_opCal_TC_ff_loop] ~ ~ ~ function " + OPt_ff_loop.file.functionName)
    OPt_ff_loop.commands.append("execute @s[score_MDMS_tempCal_min=1] ~ ~ ~ scoreboard players operation MDMS_opCal_result_int MDMS_tempCal *= 10 MDMS_number")
    OPt_ff_loop.commands.append("execute @s[score_MDMS_tempCal=-1] ~ ~ ~ scoreboard players operation MDMS_opCal_result_int MDMS_tempCal /= 10 MDMS_number")
    OPt_ff_loop.commands.append("scoreboard players remove @s[score_MDMS_tempCal_min=1] MDMS_tempCal 1")
    OPt_ff_loop.commands.append("scoreboard players remove @s[score_MDMS_tempCal=-1] MDMS_tempCal 1")
    OPt_ff_loop.commands.append("kill @s[score_MDMS_tempCal_min=0,score_MDMS_tempCal=0]")
    OPt_ff_loop.commands.append("execute @s ~ ~ ~ function " + OPt_ff_loop.file.functionName)
    # int(bool), True -> 1, False -> 0
    OP_typeconvert_int_bool = event('__from_bool', parentEvent = OP_typeconvert_int, userDefined = False, blockIDset = False)
    OP_typeconvert_int_bool.firstBlock.commands.append("scoreboard players operation MDMS_opCal_result_int MDMS_tempCal = MDMS_opCal_A_bool MDMS_tempCal")
    # float(int)
    #OP_typeconvert[]

    '''
    # Arithmetic
    OP['+'] = {}; OP['-'] = {}; OP['*'] = {}; OP['/'] = {}; OP['%'] = {}; OP['^'] = {}
    OP['+']['main'] = event('__add', parentEvent = OP, userDefined = False, blockIDset = False, makeFirstBlock = False)  
    OP['-']['main'] = event('__sub', parentEvent = OP, userDefined = False, blockIDset = False, makeFirstBlock = False)
    OP['*']['main'] = event('__mul', parentEvent = OP, userDefined = False, blockIDset = False, makeFirstBlock = False)
    OP['/']['main'] = event('__div', parentEvent = OP, userDefined = False, blockIDset = False, makeFirstBlock = False)
    '''

