# Essentials
import math
import random
import copy

# Regular Expressions for compile
import re

# MDMS libraries - Regex needs sigVar
from MDMS_sigVar import *

#------------------------------------------------
# Regex Strings

class reStr:
    
    def questMark(re_str):
        return r'(?:' + re_str + r')?'
    def OR(re_strList):
        totalstr = r'(?:'
        for re_str in re_strList:
            totalstr += r'(?:' + re_str + r')|'
        return totalstr[:-1] + r')'
    def star(re_str):
        return r'(?:' + re_str + r')*'
    def plus(re_str):
        return r'(?:' + re_str + r')+'
    
    controlCharacters = ["\+", "\?", "\.", "\*", "\^",
                         "\$", "\(", "\)", "\[", "\]",
                         "\{", "\}", "\|", "\\\\"]
                         
    def escapeControl(re_str):
        objStr = copy.deepcopy(re_str)
        #objStr = re.sub(r'\\', r'\\\\', objStr)    
        for controlChar in reStr.controlCharacters:
            #if controlChar != "\\\\":
                objStr = re.sub(controlChar, controlChar, objStr)
        return objStr

    def makeCleanOperator(re_strList):
        totalList = []
        for objStr in re_strList:
            totalList.append(reStr.escapeControl(objStr))
        return totalList

    start = r'^'
    blank = r'[ \t]+'
    comment = r'#.*'
    endOfLine = questMark(blank) + questMark(comment) + r'$' # end of line always detects the comment
    emptyLine = start + endOfLine

    variableName = r'[A-Za-z_][A-Za-z0-9_]*'

    intNumber = r'[\+-]?[0-9]+'
    floatNumber = r'[\+-]?[0-9]*\.?[0-9]+'
    hour = floatNumber + r'h'
    minute = floatNumber + r'm'
    second = floatNumber + r's'
    tick = intNumber + r't'
    time = OR((questMark(hour) + questMark(minute) + questMark(second) + tick,
               questMark(hour) + questMark(minute) + second,
               questMark(hour) + minute,
               hour))

    selector = r'@[apres](?:\[[a-zA-Z0-9_.+-=]+\])?'
    #selector = r'@[praes](\[[A-Za-z_0-9=,]*\])?'

    def preTab(tabLevel):
        return reStr.start + r'\t' * tabLevel

    end = r'End'
    def endLine(tabLevel):
        return reStr.preTab(tabLevel) + reStr.end + reStr.endOfLine

    englishValues = [r'True', r'False']
    englishOperators = [r'And', r'Not', r'Or', r'Exist']
    keywords = [r'Event', r'Delay', r'Cinematic', r'Spline', r'Linear', r'Point', r'Animation',
                r'EventCall', r'If', r'Elif', r'Else', r'While']

    operatorPriority = {'(':100, ')':100, '[':100, ']':100, '{':100, '}':100,
                        'Int':20, 'Bool':20, 'Float':20, # Type casting
                        'Exist':20, 'Print':20, 'ReadScore':20, # Built-in Functions
                        '^':9, '~':8, '+@':8, '-@':8, # +@, -@ : single plus and minus
                        '*':7, '/':7, '%':7, '+':6, '-':6, # Arithmetic
                        '>=':5, '>':5, '<':5, '<=':5, '==':4, '!=':4, # Value comparing
                        '=':3, '+=':3, '-=':3, '*=':3, '/=':3, '%=':3, '^=':3, # Assign
                        'And':2, 'Not':2, 'Or':2, # Logics
                        ',':1 # Tupling
                        }
    operatorArgumentsNum = {'(':None, ')':None, '[':None, ']':None, '{':None, '}':None,
                            'Exist':1, 'Print':1, 'ReadScore':2,
                            '^':2, '~':1, '+@':1, '-@':1,
                            '*':2, '/':2, '%':2, '+':2, '-':2,
                            '>=':2, '>':2, '<':2, '<=':2, '==':2, '!=':2,
                            '=':2, '+=':2, '-=':2, '*=':2, '/=':2, '%=':2, '^=':2,
                            'And':2, 'Not':1, 'Or':2, ',':2,
                            '[]':2}
    
    duplicatedOperatorNames = {"+": {"Default": "+", "Operator":"+@", None:"+@"},
                               "-": {"Default": "-", "Operator":"-@", None:"-@"}
                               }

    def tickExchange(re_str): # return the tick
        lineMatch = re.findall(reStr.start + reStr.time + r'$', re_str, re.M)
        if lineMatch:
            result = 0
            hour = re.findall(reStr.hour, lineMatch[0])
            if hour:
                result += float(hour[0][:-1]) * 3600 * 20
            minute = re.findall(reStr.minute, lineMatch[0])
            if minute:
                result += float(minute[0][:-1]) * 60 * 20
            second = re.findall(reStr.second, lineMatch[0])
            if second:
                result += float(second[0][:-1]) * 20
            tick = re.findall(reStr.tick, lineMatch[0])
            if tick:
                result += float(tick[0][:-1])
            #print(hour, minute, second)
            return int(result)
        else:
            raise SyntaxError("Invalid input string in tickExchange in class reStr")

    #projectLine = reStr.start + r'Project' + reStr.blank + reStr.variableName + reStr.end

    preCommand = start + questMark(blank) + r'/'
    command = r'/.*'
    def commandLine(tabLevel):
        return reStr.preTab(tabLevel) + reStr.command + reStr.endOfLine

    def delayLine(tabLevel):
        return reStr.preTab(tabLevel) + r'Delay ' + reStr.time + reStr.endOfLine

    cinematicMode = ['Point', 'Spline', 'Linear']
    def cinematicLine(tabLevel, mode):
        if mode in reStr.cinematicMode:
            totalStr = reStr.preTab(tabLevel) + r'Cinematic'
            if mode == "Point":
                raise NotImplementedError("")
            else:
                totalStr += r' ' + mode + r' ' + reStr.OR([r'Absolute', r'Relative']) + r' '
                totalStr += reStr.OR([r'Wait', r'NotWait']) + r' ' + reStr.selector + reStr.endOfLine
            return totalStr
        else:
            raise ValueError("Invalid input in cinematicLine in class reStr")

    coord3 = floatNumber + blank + floatNumber + blank + floatNumber # X Y Z
    coord2 = floatNumber + blank + floatNumber # RY RX
    coord5 = coord3 + blank + coord2 # X Y Z RY RX
    coordDir = OR((r'\+', r'-', r'\*')) + blank + OR((r'\+', r'-', r'\*'))
    coord5Dir = coord5 + blank + coordDir
    coordNormal = coord3 + questMark(blank + coord2 + questMark(blank + coordDir)) # X Y Z (RY RX)
    def cinematicCoordLine(tabLevel, mode):
        totalStr = reStr.preTab(tabLevel + 1)
        if mode == "Point":
            totalStr += reStr.time + r' ' + reStr.time + r' ' + reStr.coordNormal + reStr.endOfLine
        elif mode in reStr.cinematicMode:
            totalStr += reStr.time + r' ' + reStr.coordNormal + reStr.endOfLine
        else:
            raise ValueError("Invalid cinematic mode in cinematicCoordLine in class reStr")
        return totalStr

    def eventDefLine(tabLevel):
        return reStr.preTab(tabLevel) + r'Event ' + reStr.variableName + reStr.endOfLine

    eventID = variableName + star(r'\.' + variableName)
    def eventCallLine(tabLevel, mode):
        if mode in ("Recursive", "Multi"):
            return reStr.preTab(tabLevel) + mode + r'Call ' + reStr.eventID + reStr.endOfLine
        else:
            raise ValueError("Invalid eventCall mode in eventCallLine in class reStr")

    def normalStatementLine(tabLevel):
        return reStr.preTab(tabLevel) + reStr.normalStatement + reStr.endOfLine

    def ifLine(tabLevel):
        return reStr.preTab(tabLevel) + r'If ' + reStr.normalStatement + reStr.endOfLine
    def elifLine(tabLevel):
        return reStr.preTab(tabLevel) + r'Elif ' + reStr.normalStatement + reStr.endOfLine
    def elseLine(tabLevel):
        return reStr.preTab(tabLevel) + r'Else' + reStr.endOfLine
    def whileLine(tabLevel):
        return reStr.preTab(tabLevel) + r'While ' + reStr.normalStatement + reStr.endOfLine

    memAddressConst = plus(r'\[' + intNumber + r'\]')
    def varDefLine(tabLevel, mode): # Int A =
        modeDef = mode[0].upper() + mode[1:]
        if mode in sigVar.supportedVariableTypes:
            return reStr.preTab(tabLevel) + modeDef + reStr.blank + reStr.variableName + reStr.questMark(reStr.memAddressConst) + reStr.endOfLine
        else:
            raise TypeError("Invalid type definition in varDefLine in class reStr")

    def addNewOnSelector(selector, newArg):
        # newArg: [(obj, value), ...]
        #       example: (score_MM_min, 1)
        if not re.findall(reStr.selector, selector):
            raise SyntaxError("Invalid inputs as selector in addNewOnSelector in class reStr")
        totalstr = copy.deepcopy(selector)
        if selector[-1] == "]":
            totalstr = totalstr[:-1] + ","
        else:
            totalstr += "["
        for (obj, val) in newArg:
            totalstr += obj + "=" + str(val) + ","
        return totalstr[:-1] + "]"
    
    def makeCommandSelectorSafe(matchObj):
        return reStr.addNewOnSelector(matchObj.group(0), [("score_MDMS_system_min", 0), ("score_MDMS_system", 0)])
    
    #def dashrepl(matchobj):
    #...     if matchobj.group(0) == '-': return ' '
    #...     else: return '-'
    #>>> re.sub('-{1,2}', dashrepl, 'pro----gram-files') -> 'pro--gram files'

reStr.operator = reStr.OR(reStr.makeCleanOperator(list(reStr.operatorPriority.keys())))
reStr.normalStatement = reStr.plus(reStr.OR(reStr.makeCleanOperator(list(reStr.operatorPriority.keys())) + [reStr.variableName, reStr.floatNumber, reStr.blank, reStr.selector]))

