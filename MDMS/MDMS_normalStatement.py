# Essentials
import math
import random
import copy

# Regular Expressions for compile
import re

# MDMS libraries - NormalStatement needs regex and event
from MDMS_sigVar import *
from MDMS_regex import *
from MDMS_event import *

#------------------------------------------------
# Calculate normal statements

def calculateStatement(stateStack_, parentEvent, inputIndex = None):

    commands = []
    tempValueStore = 0

    # stateStack : {value, type, tempCalMem, variable(T/F), extra}
    stateStack = copy.deepcopy(stateStack_)
    index = 0
    for info in stateStack: # preprocess
        
        info["tempCalMem"] = index
        
        if info["variable"]:
            varName = info["value"]
            target = None
            tempEvent = parentEvent
            while tempEvent is not None:
                if varName in tempEvent.variables:
                    target = tempEvent.variables[varName]
                    break
                else:
                    tempEvent = tempEvent.parentEvent
            if target is None:
                raise NameError("No variable called '" + varName + "' in " + parentEvent.eventName + ", line " + str(inputIndex))
            else:
                info["value"] = target
                info["type"] = target.varType
                info["dimension"] = target.dimension
                info["offset"] = [] # consist of tempCalMem

                # Canceled this method
                #if info["dimension"] == 0: # ready to load
                #    if info["value"].varType == "int":
                #        commands.append("scoreboard players operation MDMS_tempCal" + str(info["tempCalMem"]) + "_int MDMS_tempCal = @s MDMS_var" + str(info["value"].scoreObjectiveNum))   

        # non-variable, should set the temp value for each elements
        elif info["type"] == "int":
            commands.append("scoreboard players set MDMS_tempCal" + str(info["tempCalMem"]) + "_int MDMS_tempCal " + str(info["value"]))

        elif info["type"] == "float":
            (factor, offset) = floatUnit(info["value"])
            commands.append("scoreboard players set MDMS_tempCal" + str(info["tempCalMem"]) + "_float_factor MDMS_tempCal " + str(factor))
            commands.append("scoreboard players set MDMS_tempCal" + str(info["tempCalMem"]) + "_float_offset MDMS_tempCal " + str(offset))

        elif info["type"] == "bool":
            if info["value"]:
                commands.append("scoreboard players set MDMS_tempCal" + str(info["tempCalMem"]) + "_bool MDMS_tempCal 1")
            else:
                commands.append("scoreboard players set MDMS_tempCal" + str(info["tempCalMem"]) + "_bool MDMS_tempCal 0")
        
        index += 1

    memReadCommand = "execute @s ~ ~ ~ function " + event.universalEvents["mcdic_mapscripter" + ".__system.__variablememory.__read"].firstBlock.file.functionName
    memWriteCommand = "execute @s ~ ~ ~ function " + event.universalEvents["mcdic_mapscripter" + ".__system.__variablememory.__write"].firstBlock.file.functionName

    def makeReadForDim0(index):
        if stateStack[index]["variable"] and stateStack[index]["dimension"] == 0:
            commands.append("# Memory Access: ")
            commands.append("scoreboard players set @s MDMS_targetMem 0")
            for i in range(len(stateStack[index]["offset"])):
                offset = stateStack[index]["offset"][i]
                dimlen = stateStack[index]["value"].listLength[i]
                commands.append("scoreboard players set " + str(dimlen) + " MDMS_number " + str(dimlen))
                commands.append("scoreboard players set " + str(offset) + " MDMS_number " + str(offset))
                commands.append("scoreboard players operation @s MDMS_targetMem *= " + str(dimlen) + " MDMS_number")
                commands.append("scoreboard players operation @s MDMS_targetMem += MDMS_tempCal" + str(offset) + "_int MDMS_tempCal")
                commands.append("scoreboard players add @s MDMS_targetMem " + str(stateStack[index]["value"].scoreObjectiveNum))
            if stateStack[index]["type"] == "int": # Int access
                commands.append(memReadCommand)
                commands.append("scoreboard players operation MDMS_tempCal" + str(stateStack[index]["tempCalMem"]) + "_int MDMS_tempCal = @s MDMS_tempCal")
            elif stateStack[index]["type"] == "float": # Float access
                commands.append(memReadCommand)
                commands.append("scoreboard players operation MDMS_tempCal" + str(stateStack[index]["tempCalMem"]) + "_float_factor MDMS_tempCal = @s MDMS_tempCal")
                commands.append("scoreboard players add @s MDMS_targetMem 1")
                commands.append(memReadCommand)
                commands.append("scoreboard players operation MDMS_tempCal" + str(stateStack[index]["tempCalMem"]) + "_float_offset MDMS_tempCal = @s MDMS_tempCal")
            elif stateStack[index]["type"] == "bool": # Bool access
                commands.append(memReadCommand)
                commands.append("scoreboard players operation MDMS_tempCal" + str(stateStack[index]["tempCalMem"]) + "_bool MDMS_tempCal = @s MDMS_tempCal")
        else:
            raise IndexError("Dimension of this variable is not 0 in makeReadForDim0 in calculateStatement")

    def tempWrite(stateIndex, tempNumIndex):
        if stateStack[stateIndex]["type"] == "int":
            commands.append("scoreboard players operation MDMS_op_" + str(tempNumIndex) + "_int MDMS_tempCal = MDMS_tempCal" + str(stateStack[stateIndex]["tempCalMem"]) + "_int MDMS_tempCal")
        elif stateStack[stateIndex]["type"] == "float":
            commands.append("scoreboard players operation MDMS_op_" + str(tempNumIndex) + "_float_factor MDMS_tempCal = MDMS_tempCal" + str(stateStack[stateIndex]["tempCalMem"]) + "_float_factor MDMS_tempCal")
            commands.append("scoreboard players operation MDMS_op_" + str(tempNumIndex) + "_float_offset MDMS_tempCal = MDMS_tempCal" + str(stateStack[stateIndex]["tempCalMem"]) + "_float_offset MDMS_tempCal")
        elif stateStack[stateIndex]["type"] == "bool":
            commands.append("scoreboard players operation MDMS_op_" + str(tempNumIndex) + "_bool MDMS_tempCal = MDMS_tempCal" + str(stateStack[stateIndex]["tempCalMem"]) + "_bool MDMS_tempCal")
        else:
            raise TypeError("Invalid fromType in tempWrite in calculateStatement")

    def readTempResult(stateIndex, resultType):
        if resultType == "int":
            commands.append("scoreboard players operation MDMS_tempCal" + str(stateStack[stateIndex]["tempCalMem"]) + "_int MDMS_tempCal = MDMS_op_result_int MDMS_tempCal")
        elif resultType == "float":
            commands.append("scoreboard players operation MDMS_tempCal" + str(stateStack[stateIndex]["tempCalMem"]) + "_float_factor MDMS_tempCal = MDMS_op_result_float_factor MDMS_tempCal")
            commands.append("scoreboard players operation MDMS_tempCal" + str(stateStack[stateIndex]["tempCalMem"]) + "_float_offset MDMS_tempCal = MDMS_op_result_float_offset MDMS_tempCal")
        elif resultType == "bool":
            commands.append("scoreboard players operation MDMS_tempCal" + str(stateStack[stateIndex]["tempCalMem"]) + "_bool MDMS_tempCal = MDMS_op_result_bool MDMS_tempCal")
    
    index = 0
    while index < len(stateStack):

        #print("\nPrinting stateStack at "+ str(index) +":")
        #for state in stateStack:
        #    print(state)

        print("\nLooking for index " + str(index) + ": " + str(stateStack[index]))

        if stateStack[index]["variable"] and stateStack[index]["dimension"] == 0:
            makeReadForDim0(index)
            
        elif stateStack[index]["type"] == "operator": # only pop the stack if the element is operator

            print("Operator", stateStack[index]["value"])

            if index >= reStr.operatorArgumentsNum[stateStack[index]["value"]]: # enough index?

                if stateStack[index]["value"] == "[]": # A[B]
                    if stateStack[index-2]["variable"]:
                        if stateStack[index-1]["type"] == "int":
                            if stateStack[index-2]["dimension"] > 0:
                                stateStack[index-2]["dimension"] -= 1
                                stateStack[index-2]["offset"].append(stateStack[index-1]["tempCalMem"])
                                if stateStack[index-2]["dimension"] == 0:
                                    makeReadForDim0(index-2)
                            else:
                                raise TypeError("Invalid type for dimensioning in line " + str(inputIndex))
                        else:
                            raise IndexError("Overdimensioned in line " + str(inputIndex))
                    else:
                        raise SyntaxError("Invalid indexing in line " + str(inputIndex))

                else: # Arithmetic, Assign, Arithmetic Logic
                    for i in range(1, reStr.operatorArgumentsNum[stateStack[index]["value"]]+1):
                        if stateStack[index-i]["variable"] and stateStack[index-i]["dimension"] > 0:
                            raise ValueError("Invalid variable dimension access in line " + str(inputIndex))

                    print(stateStack[index]["value"])
                    if stateStack[index]["value"] in ("+", "-", "*", "/", "^", "%"): # Arithmetic  
                        if stateStack[index]["value"] == "+": # A+B
                            if stateStack[index-2]["type"] == "int" and stateStack[index-1]["type"] == "int": # int + int
                                tempWrite(index-2, 0); tempWrite(index-1, 1)
                                commands.append("function mcdic_mapscripter:__system/__operation/__arithmetic/__add/__int_int_0")
                                readTempResult(index-2, "int")
                            else:
                                raise TypeError("Invalid types for + operation in line " + str(inputIndex))

                        elif stateStack[index]["value"] == "-": # A-B
                            if stateStack[index-2]["type"] == "int" and stateStack[index-1]["type"] == "int": # int + int
                                tempWrite(index-2, 0); tempWrite(index-1, 1)
                                commands.append("function mcdic_mapscripter:__system/__operation/__arithmetic/__sub/__int_int_0")
                                readTempResult(index-2, "int")
                            else: # A-B different type
                                raise TypeError("Invalid types for - operation in line " + str(inputIndex))

                        elif stateStack[index]["value"] == "*": # A*B
                            if stateStack[index-2]["type"] == "int" and stateStack[index-1]["type"] == "int": # int * int
                                tempWrite(index-2, 0); tempWrite(index-1, 1)
                                commands.append("function mcdic_mapscripter:__system/__operation/__arithmetic/__mul/__int_int_0")
                                readTempResult(index-2, "int")
                            else: # A-B different type
                                raise TypeError("Invalid types for * operation in line " + str(inputIndex))

                        elif stateStack[index]["value"] == "/": # A/B
                            if stateStack[index-2]["type"] == "int" and stateStack[index-1]["type"] == "int": # int / int
                                tempWrite(index-2, 0); tempWrite(index-1, 1)
                                commands.append("function mcdic_mapscripter:__system/__operation/__arithmetic/__div/__int_int_0")
                                readTempResult(index-2, "int")
                            else: # A-B different type
                                raise TypeError("Invalid types for / operation in line " + str(inputIndex))

                        elif stateStack[index]["value"] == "%": # A%B
                            if stateStack[index-2]["type"] == "int" and stateStack[index-1]["type"] == "int": # int % int
                                tempWrite(index-2, 0); tempWrite(index-1, 1)
                                commands.append("function mcdic_mapscripter:__system/__operation/__arithmetic/__mod/__int_int_0")
                                readTempResult(index-2, "int")
                            else: # A-B different type
                                raise TypeError("Invalid types for % operation in line " + str(inputIndex))

                        else:
                            raise NotImplementedError()

                        stateStack[index-2]["variable"] = False
                        stateStack[index-2]["unclear"] = True

                    elif stateStack[index]["value"] in ("=", "+=", "-=", "*=", "/=", "^=", "%="): # Assign

                        if not stateStack[index-2]["variable"]: # not variable
                            raise SyntaxError("Non-variable comes infront of '=' in line " + str(inputIndex))

                        memNum = stateStack[index-2]["value"].scoreObjectiveNum
                        commands.append("scoreboard players set @s MDMS_targetMem 0")
                        for i in range(len(stateStack[index-2]["offset"])):
                            offset = stateStack[index-2]["offset"][i]
                            dimlen = stateStack[index-2]["value"].listLength[i]
                            commands.append("scoreboard players set " + str(dimlen) + " MDMS_number " + str(dimlen))
                            commands.append("scoreboard players set " + str(offset) + " MDMS_number " + str(offset))
                            commands.append("scoreboard players operation @s MDMS_targetMem *= " + str(dimlen) + " MDMS_number")
                            commands.append("scoreboard players operation @s MDMS_targetMem += MDMS_tempCal" + str(offset) + "_int MDMS_tempCal")
                        commands.append("scoreboard players add @s MDMS_targetMem " + str(stateStack[index-2]["value"].scoreObjectiveNum))
                        
                        if stateStack[index]["value"] == "=": # A=B
                            print("dd")
                            if stateStack[index-2]["type"] == stateStack[index-1]["type"]: # same type operation
                                if stateStack[index-2]["type"] == "int": # int = int
                                    commands.append("scoreboard players operation @s MDMS_tempCal = MDMS_tempCal" + str(stateStack[index-1]["tempCalMem"]) + "_int MDMS_tempCal")
                                    commands.append(memWriteCommand)
                                elif stateStack[index-2]["type"] == "float": # float = float
                                    commands.append("scoreboard players operation @s MDMS_tempCal = MDMS_tempCal" + str(stateStack[index-1]["tempCalMem"]) + "_float_factor MDMS_tempCal")
                                    commands.append(memWriteCommand)
                                    commands.append("scoreboard players add @s MDMS_targetMem 1")
                                    commands.append("scoreboard players operation @s MDMS_tempCal = MDMS_tempCal" + str(stateStack[index-1]["tempCalMem"]) + "_float_offset MDMS_tempCal")
                                    commands.append(memWriteCommand)
                                elif stateStack[index-2]["type"] == "bool": # bool = bool
                                    commands.append("scoreboard players operation @s MDMS_tempCal = MDMS_tempCal" + str(stateStack[index-1]["tempCalMem"]) + "_bool MDMS_tempCal")
                                    commands.append(memWriteCommand)
                                else:
                                    raise TypeError("Invalid type for operation '=' in line " + str(inputIndex))
                            else:
                                raise NotImplementedError()
                            
                        elif stateStack[index]["value"] == "+=": # A+=B
                            if stateStack[index-2]["type"] == stateStack[index-1]["type"]: # same type operation
                                if stateStack[index-2]["type"] == "int": # int += int
                                    commands.append(memReadCommand)
                                    commands.append("scoreboard players operation @s MDMS_tempCal += MDMS_tempCal" + str(stateStack[index-1]["tempCalMem"]) + "_int MDMS_tempCal")
                                    commands.append(memWriteCommand)
                                elif stateStack[index-2]["type"] == "float": # float += float
                                    raise NotImplementedError()
                                #elif stateStack[index-2]["type"] == "bool": # bool += bool
                                #    raise TypeError("+= operation don't support Bool type in line " + str(inputIndex))
                                else:
                                    raise TypeError("Invalid type for operation '+=' in line " + str(inputIndex))
                            else:
                                raise NotImplementedError()

                        elif stateStack[index]["value"] == "-=": # A-=B
                            if stateStack[index-2]["type"] == stateStack[index-1]["type"]: # same type operation
                                if stateStack[index-2]["type"] == "int": # int -= int
                                    commands.append(memReadCommand)
                                    commands.append("scoreboard players operation @s MDMS_tempCal -= MDMS_tempCal" + str(stateStack[index-1]["tempCalMem"]) + "_int MDMS_tempCal")
                                    commands.append(memWriteCommand)
                                elif stateStack[index-2]["type"] == "float": # float -= float
                                    raise NotImplementedError()
                                #elif stateStack[index-2]["type"] == "bool": # bool -= bool
                                #    raise TypeError("-= operation don't support Bool type in line " + str(inputIndex))
                                else:
                                    raise TypeError("Invalid type for operation '-=' in line " + str(inputIndex))
                            else:
                                raise NotImplementedError()

                        elif stateStack[index]["value"] == "*=": # A*=B
                            if stateStack[index-2]["type"] == stateStack[index-1]["type"]: # same type operation
                                if stateStack[index-2]["type"] == "int": # int *= int
                                    commands.append(memReadCommand)
                                    commands.append("scoreboard players operation @s MDMS_tempCal *= MDMS_tempCal" + str(stateStack[index-1]["tempCalMem"]) + "_int MDMS_tempCal")
                                    commands.append(memWriteCommand)
                                elif stateStack[index-2]["type"] == "float": # float *= float
                                    raise NotImplementedError()
                                #elif stateStack[index-2]["type"] == "bool": # bool *= bool
                                #    raise TypeError("*= operation don't support Bool type in line " + str(inputIndex))
                                else:
                                    raise TypeError("Invalid type for operation '*=' in line " + str(inputIndex))
                            else:
                                raise NotImplementedError()

                        elif stateStack[index]["value"] == "/=": # A/=B
                            if stateStack[index-2]["type"] == stateStack[index-1]["type"]: # same type operation
                                if stateStack[index-2]["type"] == "int": # int /= int
                                    commands.append(memReadCommand)
                                    commands.append("scoreboard players operation @s MDMS_tempCal /= MDMS_tempCal" + str(stateStack[index-1]["tempCalMem"]) + "_int MDMS_tempCal")
                                    commands.append(memWriteCommand)
                                elif stateStack[index-2]["type"] == "float": # float /= float
                                    raise NotImplementedError()
                                #elif stateStack[index-2]["type"] == "bool": # bool /= bool
                                #    raise TypeError("/= operation don't support Bool type in line " + str(inputIndex))
                                else:
                                    raise TypeError("Invalid type for operation '/=' in line " + str(inputIndex))
                            else:
                                raise NotImplementedError()
                        
                        else:
                            raise NotImplementedError()

                    elif stateStack[index]["value"] in ("+@", "-@"): # Arithmetic Singular
                        
                        if stateStack[index]["value"] == "+@": # +A
                            if stateStack[index-1]["type"] in ("int", "float"):
                                pass
                            else:
                                raise TypeError("Invalid type for operation '+@' in line " + str(inputIndex))

                        elif stateStack[index]["value"] == "-@": # -A
                            if stateStack[index-1]["type"] == "int":
                                commands.append("scoreboard players operation MDMS_tempCal"+ str(stateStack[index]["tempCalMem"]) +"_int MDMS_tempCal *= -1 MDMS_number")
                            elif stateStack[index-1]["type"] == "float":
                                commands.append("scoreboard players operation MDMS_tempCal"+ str(stateStack[index]["tempCalMem"]) +"_float_factor MDMS_tempCal *= -1 MDMS_number")
                            else:
                                raise TypeError("Invalid type for operation '-@' in line " + str(inputIndex))

                        stateStack[index-1]["unclear"] = True
                        stateStack[index-1]["variable"] = False

                    elif stateStack[index]["value"] in ("==", ">", "<", "!=", ">=", "<="): # Arithmetic Logic

                        commands.append("kill @e[type=area_effect_cloud,tag=MDMS_tempComparison]")

                        if stateStack[index]["value"] == "==": # A == B
                            commands.append("scoreboard players set MDMS_tempBool MDMS_tempCal 0")
                            if stateStack[index-2]["type"] == stateStack[index-1]["type"]:
                                if stateStack[index-2]["type"] == "int":
                                    commands.append('summon area_effect_cloud ~ ~ ~ {CustomName:"MDMS_tempComparison_int", Tags:["MDMS_system", "MDMS_tempComparison"]}')
                                    commands.append("scoreboard players set @e[type=area_effect_cloud,tag=MDMS_tempComparison,name=MDMS_tempComparison_int] MDMS_tempCal 0")
                                    commands.append("scoreboard players operation @e[type=area_effect_cloud,tag=MDMS_tempComparison,name=MDMS_tempComparison_int] MDMS_tempCal += MDMS_tempCal" + str(stateStack[index-2]["tempCalMem"]) + "_int MDMS_tempCal")
                                    commands.append("scoreboard players operation @e[type=area_effect_cloud,tag=MDMS_tempComparison,name=MDMS_tempComparison_int] MDMS_tempCal -= MDMS_tempCal" + str(stateStack[index-1]["tempCalMem"]) + "_int MDMS_tempCal")
                                    commands.append("execute @e[type=area_effect_cloud,tag=MDMS_tempComparison,name=MDMS_tempComparison_int,score_MDMS_tempCal_min=0,score_MDMS_tempCal=0] ~ ~ ~ scoreboard players set MDMS_tempBool MDMS_tempCal 1")
                                elif stateStack[index-2]["type"] == "float":
                                    raise NotImplementedError()
                                elif stateStack[index-2]["type"] == "bool":
                                    commands.append('summon area_effect_cloud ~ ~ ~ {CustomName:"MDMS_tempComparison_bool", Tags:["MDMS_system", "MDMS_tempComparison"]}')
                                    commands.append("scoreboard players set @e[type=area_effect_cloud,tag=MDMS_tempComparison,name=MDMS_tempComparison_bool] MDMS_tempCal 0")
                                    commands.append("scoreboard players operation @e[type=area_effect_cloud,tag=MDMS_tempComparison,name=MDMS_tempComparison_bool] MDMS_tempCal += MDMS_tempCal" + str(stateStack[index-2]["tempCalMem"]) + "_int MDMS_tempCal")
                                    commands.append("scoreboard players operation @e[type=area_effect_cloud,tag=MDMS_tempComparison,name=MDMS_tempComparison_bool] MDMS_tempCal -= MDMS_tempCal" + str(stateStack[index-1]["tempCalMem"]) + "_int MDMS_tempCal")
                                    commands.append("execute @e[type=area_effect_cloud,tag=MDMS_tempComparison,name=MDMS_tempComparison_bool,score_MDMS_tempCal_min=0,score_MDMS_tempCal=0] ~ ~ ~ scoreboard players set MDMS_tempBool MDMS_tempCal 1")
                                else:
                                    raise TypeError("Invalid type for operation '==' in line " + str(inputIndex))
                            else:
                                raise NotImplementedError()

                        elif stateStack[index]["value"] == "!=": # A != B
                            commands.append("scoreboard players set MDMS_tempBool MDMS_tempCal 1")
                            if stateStack[index-2]["type"] == stateStack[index-1]["type"]:
                                if stateStack[index-2]["type"] == "int":
                                    commands.append('summon area_effect_cloud ~ ~ ~ {CustomName:"MDMS_tempComparison_int", Tags:["MDMS_system", "MDMS_tempComparison"]}')
                                    commands.append("scoreboard players set @e[type=area_effect_cloud,tag=MDMS_tempComparison,name=MDMS_tempComparison_int] MDMS_tempCal 0")
                                    commands.append("scoreboard players operation @e[type=area_effect_cloud,tag=MDMS_tempComparison,name=MDMS_tempComparison_int] MDMS_tempCal += MDMS_tempCal" + str(stateStack[index-2]["tempCalMem"]) + "_int MDMS_tempCal")
                                    commands.append("scoreboard players operation @e[type=area_effect_cloud,tag=MDMS_tempComparison,name=MDMS_tempComparison_int] MDMS_tempCal -= MDMS_tempCal" + str(stateStack[index-1]["tempCalMem"]) + "_int MDMS_tempCal")
                                    commands.append("execute @e[type=area_effect_cloud,tag=MDMS_tempComparison,name=MDMS_tempComparison_int,score_MDMS_tempCal_min=0,score_MDMS_tempCal=0] ~ ~ ~ scoreboard players set MDMS_tempBool MDMS_tempCal 0")
                                elif stateStack[index-2]["type"] == "float":
                                    raise NotImplementedError()
                                elif stateStack[index-2]["type"] == "bool":
                                    commands.append('summon area_effect_cloud ~ ~ ~ {CustomName:"MDMS_tempComparison_bool", Tags:["MDMS_system", "MDMS_tempComparison"]}')
                                    commands.append("scoreboard players set @e[type=area_effect_cloud,tag=MDMS_tempComparison,name=MDMS_tempComparison_bool] MDMS_tempCal 0")
                                    commands.append("scoreboard players operation @e[type=area_effect_cloud,tag=MDMS_tempComparison,name=MDMS_tempComparison_bool] MDMS_tempCal += MDMS_tempCal" + str(stateStack[index-2]["tempCalMem"]) + "_int MDMS_tempCal")
                                    commands.append("scoreboard players operation @e[type=area_effect_cloud,tag=MDMS_tempComparison,name=MDMS_tempComparison_bool] MDMS_tempCal -= MDMS_tempCal" + str(stateStack[index-1]["tempCalMem"]) + "_int MDMS_tempCal")
                                    commands.append("execute @e[type=area_effect_cloud,tag=MDMS_tempComparison,name=MDMS_tempComparison_bool,score_MDMS_tempCal_min=0,score_MDMS_tempCal=0] ~ ~ ~ scoreboard players set MDMS_tempBool MDMS_tempCal 0")
                                else:
                                    raise TypeError("Invalid type for operation '==' in line " + str(inputIndex))
                            else:
                                raise NotImplementedError()

                        elif stateStack[index]["value"] == ">": # A > B
                            commands.append("scoreboard players set MDMS_tempBool MDMS_tempCal 0")
                            if stateStack[index-2]["type"] == stateStack[index-1]["type"]:
                                if stateStack[index-2]["type"] == "int":
                                    commands.append('summon area_effect_cloud ~ ~ ~ {CustomName:"MDMS_tempComparison_int", Tags:["MDMS_system", "MDMS_tempComparison"]}')
                                    commands.append("scoreboard players set @e[type=area_effect_cloud,tag=MDMS_tempComparison,name=MDMS_tempComparison_int] MDMS_tempCal 0")
                                    commands.append("scoreboard players operation @e[type=area_effect_cloud,tag=MDMS_tempComparison,name=MDMS_tempComparison_int] MDMS_tempCal += MDMS_tempCal" + str(stateStack[index-2]["tempCalMem"]) + "_int MDMS_tempCal")
                                    commands.append("scoreboard players operation @e[type=area_effect_cloud,tag=MDMS_tempComparison,name=MDMS_tempComparison_int] MDMS_tempCal -= MDMS_tempCal" + str(stateStack[index-1]["tempCalMem"]) + "_int MDMS_tempCal")
                                    commands.append("execute @e[type=area_effect_cloud,tag=MDMS_tempComparison,name=MDMS_tempComparison_int,score_MDMS_tempCal_min=1] ~ ~ ~ scoreboard players set MDMS_tempBool MDMS_tempCal 1")
                                elif stateStack[index-2]["type"] == "float":
                                    raise NotImplementedError()
                                else: # Include bool
                                    raise TypeError("Invalid type for operation '>' in line " + str(inputIndex))
                            else:
                                raise NotImplementedError()

                        elif stateStack[index]["value"] == "<": # A < B
                            commands.append("scoreboard players set MDMS_tempBool MDMS_tempCal 0")
                            if stateStack[index-2]["type"] == stateStack[index-1]["type"]:
                                if stateStack[index-2]["type"] == "int":
                                    commands.append('summon area_effect_cloud ~ ~ ~ {CustomName:"MDMS_tempComparison_int", Tags:["MDMS_system", "MDMS_tempComparison"]}')
                                    commands.append("scoreboard players set @e[type=area_effect_cloud,tag=MDMS_tempComparison,name=MDMS_tempComparison_int] MDMS_tempCal 0")
                                    commands.append("scoreboard players operation @e[type=area_effect_cloud,tag=MDMS_tempComparison,name=MDMS_tempComparison_int] MDMS_tempCal += MDMS_tempCal" + str(stateStack[index-2]["tempCalMem"]) + "_int MDMS_tempCal")
                                    commands.append("scoreboard players operation @e[type=area_effect_cloud,tag=MDMS_tempComparison,name=MDMS_tempComparison_int] MDMS_tempCal -= MDMS_tempCal" + str(stateStack[index-1]["tempCalMem"]) + "_int MDMS_tempCal")
                                    commands.append("execute @e[type=area_effect_cloud,tag=MDMS_tempComparison,name=MDMS_tempComparison_int,score_MDMS_tempCal=-1] ~ ~ ~ scoreboard players set MDMS_tempBool MDMS_tempCal 1")
                                elif stateStack[index-2]["type"] == "float":
                                    raise NotImplementedError()
                                else: # Include bool
                                    raise TypeError("Invalid type for operation '<' in line " + str(inputIndex))
                            else:
                                raise NotImplementedError()

                        elif stateStack[index]["value"] == ">=": # A >= B
                            commands.append("scoreboard players set MDMS_tempBool MDMS_tempCal 0")
                            if stateStack[index-2]["type"] == stateStack[index-1]["type"]:
                                if stateStack[index-2]["type"] == "int":
                                    commands.append('summon area_effect_cloud ~ ~ ~ {CustomName:"MDMS_tempComparison_int", Tags:["MDMS_system", "MDMS_tempComparison"]}')
                                    commands.append("scoreboard players set @e[type=area_effect_cloud,tag=MDMS_tempComparison,name=MDMS_tempComparison_int] MDMS_tempCal 0")
                                    commands.append("scoreboard players operation @e[type=area_effect_cloud,tag=MDMS_tempComparison,name=MDMS_tempComparison_int] MDMS_tempCal += MDMS_tempCal" + str(stateStack[index-2]["tempCalMem"]) + "_int MDMS_tempCal")
                                    commands.append("scoreboard players operation @e[type=area_effect_cloud,tag=MDMS_tempComparison,name=MDMS_tempComparison_int] MDMS_tempCal -= MDMS_tempCal" + str(stateStack[index-1]["tempCalMem"]) + "_int MDMS_tempCal")
                                    commands.append("execute @e[type=area_effect_cloud,tag=MDMS_tempComparison,name=MDMS_tempComparison_int,score_MDMS_tempCal_min=0] ~ ~ ~ scoreboard players set MDMS_tempBool MDMS_tempCal 1")
                                elif stateStack[index-2]["type"] == "float":
                                    raise NotImplementedError()
                                else: # Include bool
                                    raise TypeError("Invalid type for operation '>=' in line " + str(inputIndex))
                            else:
                                raise NotImplementedError()

                        elif stateStack[index]["value"] == "<=": # A <= B
                            commands.append("scoreboard players set MDMS_tempBool MDMS_tempCal 0")
                            if stateStack[index-2]["type"] == stateStack[index-1]["type"]:
                                if stateStack[index-2]["type"] == "int":
                                    commands.append('summon area_effect_cloud ~ ~ ~ {CustomName:"MDMS_tempComparison_int", Tags:["MDMS_system", "MDMS_tempComparison"]}')
                                    commands.append("scoreboard players set @e[type=area_effect_cloud,tag=MDMS_tempComparison,name=MDMS_tempComparison_int] MDMS_tempCal 0")
                                    commands.append("scoreboard players operation @e[type=area_effect_cloud,tag=MDMS_tempComparison,name=MDMS_tempComparison_int] MDMS_tempCal += MDMS_tempCal" + str(stateStack[index-2]["tempCalMem"]) + "_int MDMS_tempCal")
                                    commands.append("scoreboard players operation @e[type=area_effect_cloud,tag=MDMS_tempComparison,name=MDMS_tempComparison_int] MDMS_tempCal -= MDMS_tempCal" + str(stateStack[index-1]["tempCalMem"]) + "_int MDMS_tempCal")
                                    commands.append("execute @e[type=area_effect_cloud,tag=MDMS_tempComparison,name=MDMS_tempComparison_int,score_MDMS_tempCal=0] ~ ~ ~ scoreboard players set MDMS_tempBool MDMS_tempCal 1")
                                elif stateStack[index-2]["type"] == "float":
                                    raise NotImplementedError()
                                else: # Include bool
                                    raise TypeError("Invalid type for operation '<=' in line " + str(inputIndex))
                            else:
                                raise NotImplementedError()

                        else:
                            raise NotImplementedError()

                        commands.append("scoreboard players operation MDMS_tempCal" + str(stateStack[index-2]["tempCalMem"]) + "_bool MDMS_tempCal = MDMS_tempBool MDMS_tempCal")
                        commands.append("kill @e[type=area_effect_cloud,tag=MDMS_tempComparison]")
                        stateStack[index-2]["type"] = "bool"
                        stateStack[index-2]["unclear"] = True
                        stateStack[index-2]["variable"] = False

                    elif stateStack[index]["value"] in ("And", "Or", "Not"): # Normal logic

                        if stateStack[index]["value"] == "And": # A and B
                            if stateStack[index-2]["type"] == stateStack[index-2]["type"]:
                                if stateStack[index-2]["type"] == "bool":
                                    commands.append("scoreboard players operation MDMS_tempCal" + str(stateStack[index-2]["tempCalMem"]) + "_bool MDMS_tempCal *= MDMS_tempCal" + str(stateStack[index-1]["tempCalMem"]) + "_bool MDMS_tempCal")
                                else:
                                    raise TypeError("Invalid type for operation 'And' in line " + str(inputIndex))
                            else:
                                raise NotImplementedError()
                            stateStack[index-2]["type"] = "bool"
                            stateStack[index-2]["unclear"] = True
                            stateStack[index-2]["variable"] = False

                        elif stateStack[index]["value"] == "Or": # A or B
                            if stateStack[index-2]["type"] == stateStack[index-2]["type"]:
                                if stateStack[index-2]["type"] == "bool":
                                    commands.append("scoreboard players operation MDMS_tempCal" + str(stateStack[index-2]["tempCalMem"]) + "_bool MDMS_tempCal += MDMS_tempCal" + str(stateStack[index-1]["tempCalMem"]) + "_bool MDMS_tempCal")
                                    commands.append("scoreboard players add MDMS_tempCal" + str(stateStack[index-2]["tempCalMem"]) + "_bool MDMS_tempCal 1")
                                    commands.append("scoreboard players operation MDMS_tempCal" + str(stateStack[index-2]["tempCalMem"]) + "_bool MDMS_tempCal /= 2 MDMS_number") # 0 1 2 -> 0 1 1
                                else:
                                    raise TypeError("Invalid type for operation 'Or' in line " + str(inputIndex))
                            else:
                                raise NotImplementedError()
                            stateStack[index-2]["type"] = "bool"
                            stateStack[index-2]["unclear"] = True
                            stateStack[index-2]["variable"] = False

                        elif stateStack[index]["value"] == "Not": # Not A
                            if stateStack[index-1]["type"] == "bool":
                                commands.append("scoreboard players add MDMS_tempCal" + str(stateStack[index-1]["tempCalMem"]) + "_bool MDMS_tempCal 1")
                                commands.append("scoreboard players operation MDMS_tempCal" + str(stateStack[index-2]["tempCalMem"]) + "_bool MDMS_tempCal %= 2 MDMS_number") # 0 1 -> 1 0
                            else:
                                raise TypeError("Invalid type for operation 'Not' in line " + str(inputIndex))
                            stateStack[index-1]["type"] = "bool"
                            stateStack[index-1]["unclear"] = True
                            stateStack[index-1]["variable"] = False

                    elif stateStack[index]["value"] in ("Exist", "Print"): # BuiltIn Function

                        if stateStack[index]["value"] == "Exist":
                            if stateStack[index-1]["type"] == "selector":
                                commands.append("scoreboard players set MDMS_tempCal" + str(stateStack[index-1]["tempCalMem"]) + "_bool MDMS_tempCal 0")
                                commands.append("execute " + stateStack[index-1]["value"] + " ~ ~ ~ scoreboard players set MDMS_tempCal" + str(stateStack[index-1]["tempCalMem"]) + "_bool MDMS_tempCal 1")
                            else:
                                raise TypeError("Invalid type for operation 'Exist' in line " + str(inputIndex))
                            stateStack[index-1]["type"] == "bool"
                            stateStack[index-1]["unclear"] = True
                            stateStack[index-1]["variable"] = False

                        elif stateStack[index]["value"] == "Print":
                            if stateStack[index-1]["type"] == "selector":
                                commands.append('tellraw @a {"selector":"'+ stateStack[index-1]["value"] +'"}')
                            else:
                                raise TypeError("Invalid type for operation 'Print' in line " + str(inputIndex))

                        else:
                            raise NotImplementedError()
                    
                    else: # Not implemented operator
                        raise NotImplementedError()

                for i in range(reStr.operatorArgumentsNum[stateStack[index]["value"]]):
                    del stateStack[index-i]
                index -= i + 1
                print("Now index=", index, "Whole length=", len(stateStack))

            else: # Not enough index
                raise IndexError("Invalid number of operator arguments in line " + str(inputIndex))

        index += 1

    if len(stateStack) > 1:
        for state in stateStack:
            print(state)
        raise IndexError("Result has deep depth of stack in line " + str(inputIndex))

    if stateStack[0]["type"] == "int":
        commands.append("scoreboard players operation MDMS_statementResult_int MDMS_tempCal = MDMS_tempCal0_int MDMS_tempCal")
    elif stateStack[0]["type"] == "float":
        commands.append("scoreboard players operation MDMS_statementResult_float_factor MDMS_tempCal = MDMS_tempCal0_float_factor MDMS_tempCal")
        commands.append("scoreboard players operation MDMS_statementResult_float_offset MDMS_tempCal = MDMS_tempCal0_float_offset MDMS_tempCal")
    elif stateStack[0]["type"] == "bool":
        commands.append("scoreboard players operation MDMS_statementResult_bool MDMS_tempCal = MDMS_tempCal0_bool MDMS_tempCal")
    elif stateStack[0]["type"] == "selector":
        pass
    else:
        raise NotImplementedError()

    return (commands, stateStack[0]["type"])

#------------------------------------------------
# Compile normal statements

def compileStatement(inputLine, inputIndex = None):

    line = copy.deepcopy(inputLine)
    line = re.sub(r'[ \t]+', r' ', line)
    
    totalStack = [] # [{}]
    operatorStack = [] # [operator, ...]
    bracketStack = [] # [bracket, ...]
    
    lastCatched = None
    while len(line) > 0:

        if line[0] in (" ", "\t"):
            line = line[1:]
            continue
        elif "#" == line[0]: # if comment then stop
            break

        print("-" * 40)
        print("Line:", line)
        #print("Total", totalStack)
        #print("Operator", operatorStack)
        #print("Bracket", bracketStack)
        
        if line[0] in ("(", "{", "["): # LeftBracket
            lastCatched = "Bracket"
            print("Catched " + line[0])
            operatorStack.append(line[0])
            bracketStack.append(line[0])
            line = line[1:]
            continue

        elif line[0] in (")", "]", "}"): # RightBracket
            lastCatched = "Bracket"
            leftB = ""
            if line[0] == ")":
                print("Catched )")
                leftB = "("
            elif line[0] == "]":
                print("Catched ]")
                leftB = "["
            if len(bracketStack) == 0 or bracketStack[-1] != leftB:
                raise SyntaxError("Invalid '"+ leftB +"' in line "+ str(inputIndex))
            while operatorStack[-1] != leftB:
                topOper = operatorStack.pop()
                totalStack.append({"value": topOper, "type": "operator", "variable": False, "unclear": False})
            operatorStack.pop()
            bracketStack.pop()
            if line[0] == "]":
                totalStack.append({"value": "[]", "type": "operator", "variable": False, "unclear": False})
            line = line[1:]

        elif re.match(reStr.selector, line, re.M): # Selector
            lastCatched = "Selector"
            selector = re.match(reStr.selector, line, re.M).group()
            print("Selector Catched", selector)
            totalStack.append({"value": selector, "type": "selector", "variable": False, "unclear": False})
            line = line[len(selector):]

        elif re.match(reStr.operator, line, re.M): # Operator
            oper = re.match(reStr.operator, line, re.M).group()
            for operator in reStr.operatorPriority:
                #print(operator, "VS", line[:len(operator)])
                if operator in line:
                    if operator[:len(oper)] == oper and len(operator) > len(oper):
                        oper = operator
                    
            if oper in reStr.duplicatedOperatorNames:
                if lastCatched in reStr.duplicatedOperatorNames[oper]:
                    oper = reStr.duplicatedOperatorNames[oper][lastCatched]
                else:
                    oper = reStr.duplicatedOperatorNames[oper]["Default"]
            while True:
                if len(operatorStack) == 0:
                    break
                elif operatorStack[-1] in ("(", "{", "["):
                    break
                elif reStr.operatorPriority[operatorStack[-1]] < reStr.operatorPriority[oper]:
                    break
                topOper = operatorStack.pop()
                totalStack.append({"value": topOper, "type": "operator", "variable": False, "unclear": False})
            print("Operator Catched", oper)
            lastCatched = "Operator"
            operatorStack.append(oper)
            if oper[-1] == "@":
                line = line[len(oper)-1:]
            else:
                line = line[len(oper):]

        elif re.match(reStr.variableName, line, re.M): # Variable
            lastCatched = "Variable"
            var = re.match(reStr.variableName, line, re.M).group()
            if var in reStr.keywords:
                raise NameError("Tried to set keyword as variable name in line " + str(inputIndex))
            elif var in reStr.englishValues:
                if var == "True":
                    totalStack.append({"value": True, "type": "bool", "variable": False, "unclear": False})
                    print("Value Catched True")
                elif var == "False":
                    totalStack.append({"value": False, "type": "bool", "variable": False, "unclear": False})
                    print("Value Catched False")
                else:
                    raise NotImplementedError()
                line = line[len(var):]
            else:
                totalStack.append({"value": var, "type": "unknown", "variable": True, "unclear": True})
                line = line[len(var):]
                print("Variable Catched", var)
                '''
                if len(line) > 0 and line[0] == "[":
                    operatorStack.append(line[0])
                    bracketStack.append(line[0])
                    line = line[1:]
                else:
                    totalStack.append({"value": 0, "type": "int", "variable": False}) # MemoryAccess offset should be int
                    totalStack.append({"value": "[]", "type": "operator", "variable": False, "unclear": False})
                '''

        elif re.match(reStr.floatNumber, line, re.M): # Number
            lastCatched = "Number"
            num = re.match(reStr.floatNumber, line, re.M).group()
            print("Number Catched", num)
            numlen = len(num)
            num = float(num)
            if int(num) != float(num):
                totalStack.append({"value": float(num), "type": "float", "variable": False, "unclear": False})
            else:
                totalStack.append({"value": int(num), "type": "int", "variable": False, "unclear": False})
            line = line[numlen:]

        else: # Compile Error
            raise SyntaxError("General Statement Compile Error in line " + str(inputIndex))

    while len(operatorStack) > 0:
        topOper = operatorStack.pop()
        totalStack.append({"value": topOper, "type": "operator", "variable": False, "unclear": False})

    print("-"*40)
    for tot in totalStack:
        print(tot)
    
    return totalStack
