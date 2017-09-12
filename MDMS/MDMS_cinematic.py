# Essentials
import math
import random
import copy

# MDMS libraries - Cinematic needs math, subBlock, event
from MDMS_math import *
from MDMS_armorstand import *
from MDMS_event import *

#------------------------------------------------
# Cinematic maths

def cuts_linear_singleval(points, times, angleMode = None, angleDirections = None):

    pointnum = len(points)
    timenum = len(times)

    if pointnum < 2 or timenum < 2:
        raise IndexError("Not enough index length of points/times in cuts_linear_singleval")
    elif pointnum != timenum:
        raise IndexError("Different index lengths in cuts_linear_singleval")

    locations = []
    for i in range(pointnum-1):

        pointnow  = copy.deepcopy(points[i])
        pointnext = copy.deepcopy(points[i+1])
        if angleDirections is not None: # direction support
            while angleDirections[i+1] == "+" and pointnow > pointnext:
                pointnext += 360
            while angleDirections[i+1] == "-" and pointnow < pointnext:
                pointnext -= 360

        for tick in range(times[i], times[i+1]):
            loc = pointnow + (tick - times[i]) / (times[i+1] - times[i]) * (pointnext - pointnow)
            if angleMode == "ry":
                loc = updateAngleTypeRY(loc)
            elif angleMode == "rx":
                loc = updateAngleTypeRX(loc)
            locations.append(loc)

    locations.append(points[-1])
    return locations

def cuts_spline_spheric_singleval(points, times, angleMode = None, angleDirections = None, startV = 0, endV = 0):
    # angleMode: "ry" : -180 ~ 180, "rx" : -90 ~ 90

    def cuts_spline_spheric_subcal(tk, tkp1, xk, xkp1, sphk, sphkp1): #return poly
        # tk = t(k), tkp1 = t(k+1), xk = x(k), xkp1 = x(k+1), sphk = sph(k), sphkp1 = sph(k+1)

        u1 = (xkp1 - xk) / (tkp1 - tk)
        u2_k   = (u1 - sphk  ) / (tkp1 - tk)
        u2_kp1 = (u1 - sphkp1) / (tk - tkp1)

        a = (u2_kp1 - u2_k) / (tkp1 - tk)
        b = u2_k - (tkp1 + 2*tk) * a
        c = sphk - 2*tk*b - 3*(tk**2)*a
        d = xk - tk*c - (tk**2)*b - (tk**3)*a

        newpoly = poly([d, c, b, a])
        return newpoly

    def cross2lines(line1, line2): # (a, b, c) ax+by+c=0
        a1 = line1[0]; b1 = line1[1]; c1 = line1[2]
        a2 = line2[0]; b2 = line2[1]; c2 = line2[2]
        if a1*b2 - a2*b1 == 0:
            return None
        else:
            d = (b1*c2 - b2*c1) / (a1*b2 - a2*b1)
            if b1 != 0:
                return (d, -a1/b1*d - c1/b1)
            else:
                if a1 != 0:
                    x = -c1/a1
                    if b2 != 0:
                        y = - a2/b2*x - c2/b2
                        return (x, y)
                    else:
                        if a2 != 0:
                            if -c1/a1 != -c2/a2:
                                return None
                            else:
                                return None
                        else:
                            raise ValueError("Inappopriate given line2 equation in cross2lines, cuts_spline_spheric_singlevar")
                else:
                    raise ValueError("Inappopriate given line1 equation in cross2lines, cuts_spline_spheric_singlevar")

    def changelineform(point, deriv): # y = deriv(x-x0) + y0 -> ax+by+c=0
        return (deriv, -1, -point[0]*deriv + point[1])

    def derivline(point1, point2):
        if point2[0] == point1[0]:
            return "inf"
        return (point2[1]-point1[1]) / (point2[0]-point1[0])

    def middle(point1, point2):
        return ( (point1[0]+point2[0])/2, (point1[1]+point2[1])/2 )

    def distance(point1, point2):
        dx = point2[0] - point1[0]
        dy = point2[1] - point1[1]
        return math.sqrt(dx*dx + dy*dy)

    def trianglesum(point1, point2, point3):
        x1 = point1[0]; y1 = point1[1]
        x2 = point2[0]; y2 = point2[1]
        x3 = point3[0]; y3 = point3[1]
        return math.abs(x1*y2 + x2*y3 + x3*y1 - x2*y1 - x3*y2 - x1*y3)/2.0


    pointnum = len(points)
    timenum = len(times)

    if pointnum < 3:
        raise IndexError("Not enough amount of points in cuts_spline_spheric_singleval")
    elif pointnum != timenum:
        raise IndexError("Different index lengths in cuts_spline_spheric_singleval")

    sphderivlist = [startV] # sphere deriatives for each triangles
    for i in range(1, pointnum-1):

        pointprev = copy.deepcopy([times[i-1], points[i-1]])
        pointnow  = copy.deepcopy([times[i], points[i]])
        pointnext = copy.deepcopy([times[i+1], points[i+1]])
        if angleDirections is not None: # direction support
            while angleDirections[i] == "+" and pointprev[1] > pointnow[1]:
                pointnow[1] += 360
                pointnext[1] += 360
            while angleDirections[i] == "-" and pointprev[1] < pointnow[1]:
                pointnow[1] -= 360
                pointnext[1] -= 360
            while angleDirections[i+1] == "+" and pointnow[1] > pointnext[1]:
                pointnext[1] += 360
            while angleDirections[i+1] == "-" and pointnow[1] < pointnext[1]:
                pointnext[1] -= 360

        #len1 = distance(pointprev, pointnow)
        #len2 = distance(pointnow, pointnext)
        #len3 = distance(pointnext, pointprev)
        #S = trianglesum(pointprev, pointnow, pointnext)
        #R = len1*len2*len3 / (4*S)

        if derivline(pointprev, pointnow) == 0:
            Rline1 = (-1, 0, middle(pointprev, pointnow)[0])
        else:
            Rline1 = changelineform(middle(pointprev, pointnow), -1/derivline(pointprev, pointnow))
        if derivline(pointnow, pointnext) == 0:
            Rline2 = (-1, 0, middle(pointnow, pointnext)[0])
        else:
            Rline2 = changelineform(middle(pointnow, pointnext), -1/derivline(pointnow, pointnext))

        Rcoord = cross2lines(Rline1, Rline2)
        if Rcoord is None:
            goalvalue = derivline(pointprev, pointnext)
        else:
            now_to_Rcoord = derivline(Rcoord, pointnow)
            if now_to_Rcoord == "inf":
                goalvalue = 0.0
            else:
                goalvalue = -1/now_to_Rcoord

        sphderivlist.append(goalvalue)

    sphderivlist.append(endV)
    polylist = []
    for i in range(pointnum-1):

        pointnow  = copy.deepcopy([times[i], points[i]])
        pointnext = copy.deepcopy([times[i+1], points[i+1]])
        if angleDirections is not None: # direction support
            while angleDirections[i+1] == "+" and pointnow[1] > pointnext[1]:
                pointnext[1] += 360
            while angleDirections[i+1] == "-" and pointnow[1] < pointnext[1]:
                pointnext[1] -= 360

        temppoly = cuts_spline_spheric_subcal(times[i], times[i+1], pointnow[1], pointnext[1], sphderivlist[i], sphderivlist[i+1])
        polylist.append(temppoly)

    locations = []
    for i in range(timenum-1):
        for j in range(times[i], times[i+1]):
            temp = polylist[i].val(j)
            if angleMode == "ry":
                temp = updateAngleTypeRY(temp)
            elif angleMode == "rx":
                temp = updateAngleTypeRX(temp)
            locations.append(temp)

    locations.append(points[-1])
    return locations

#------------------------------------------------
# Cinematics

class cinematic:

    #universalCinematics = []

    def __init__(self, relative = False, wait = True, mode = "Spline",
                 dimension = "Undefined", selector = "@a", parentEvent = None):

        if mode in ("Point", "Spline", "Linear"):
            self.mode = mode
        else:
            raise ValueError("Invalid mode in __init__ in class cinematic")
        self.relative = relative
        self.wait = wait
        self.selector = selector
        self.dimension = "Undefined"

        # Time: (x, y, z, ry, rx, ryd, rxd) -- This is the result of cuts functions
        # (x, y, z) for 3 dimensions, (x, y, z, ry, rx, ryd, rxd) for 5 dimensions
        self.coords = {}

        #cinematic.universalCinematics.append(self)
        if parentEvent is None:
            raise Exception("Cinematic should have parentEvent in __init in class cinematic")
        
        parentEvent.cinematicNum += 1
        self.cinematicEvent = event(eventName = "__cinematic_" + str(parentEvent.cinematicNum), parentEvent = parentEvent,
                                    userDefined = False, blockIDset = True, makeFirstBlock = True)
        self.written = False

    def __repr__(self):

        totalstr = ""
        totalstr += "-"*30 + "\n"
        totalstr += "Cinematic ID " + str(id(self)) + ":"
        for time in self.coords:
            totalstr += "\n\tTick " + str(time) + ": " + str(self.coords[time])
        return totalstr

    def generateCoord(self):

        if self.dimension == "Undefined":
            raise UnboundLocalError("Dimension of cinematic is not defined yet in generateCoord in class cinematic")

        if self.mode == "Point":
            raise NotImplementedError("")

        else:

            times = sorted(list(self.coords.keys()))
            Xcoord = [self.coords[time]["x"] for time in times]
            Ycoord = [self.coords[time]["y"] for time in times]
            Zcoord = [self.coords[time]["z"] for time in times]
            if self.dimension == 5:
                RYcoord = [self.coords[time]["ry"] for time in times]
                RXcoord = [self.coords[time]["rx"] for time in times]
                RYDcoord = [self.coords[time]["ryd"] for time in times]
                RXDcoord = [self.coords[time]["rxd"] for time in times]
            self.coords = {} # reset
            
            if self.mode == "Linear":

                if len(times) < 2:
                    raise IndexError("Invalid index in generateCoord in class cinematic (At least 2 points needed)")
                Xcoord = cuts_linear_singleval(Xcoord, times)
                Ycoord = cuts_linear_singleval(Ycoord, times)
                Zcoord = cuts_linear_singleval(Zcoord, times)
                if self.dimension == 5:
                    RYcoord = cuts_linear_singleval(RYcoord, times, angleMode = "ry", angleDirections = RYDcoord)
                    RXcoord = cuts_linear_singleval(RXcoord, times, angleMode = "rx", angleDirections = RXDcoord)

            elif self.mode == "Spline":

                if len(times) < 3:
                    raise IndexError("Invalid index in generateCoord in class cinematic (At least 3 points needed)")
                Xcoord = cuts_spline_spheric_singleval(Xcoord, times)
                Ycoord = cuts_spline_spheric_singleval(Ycoord, times)
                Zcoord = cuts_spline_spheric_singleval(Zcoord, times)
                if self.dimension == 5:
                    RYcoord = cuts_spline_spheric_singleval(RYcoord, times, angleMode = "ry", angleDirections = RYDcoord)
                    RXcoord = cuts_spline_spheric_singleval(RXcoord, times, angleMode = "rx", angleDirections = RXDcoord)

            else:
                raise ValueError("Invalid cinematic mode in generateCoord in class cinematic")

            for i in range(len(Xcoord)):
                if i + times[0] not in self.coords:
                    self.coords[i + times[0]] = {}
                self.coords[i + times[0]]["x"] = Xcoord[i]
                self.coords[i + times[0]]["y"] = Ycoord[i]
                self.coords[i + times[0]]["z"] = Zcoord[i]
                if self.dimension == 5:
                    self.coords[i + times[0]]["ry"] = RYcoord[i]
                    self.coords[i + times[0]]["rx"] = RXcoord[i]

    def writeCoord(self, beforeCinBlock, afterCinBlock):

        if self.written:
            raise UnboundLocalError("Already written in writeCoord in class cinematic")
        
        self.generateCoord()
        timeList = sorted(list(self.coords.keys()))
        tpBlocks = {}
        for time in timeList:
            tpBlocks[time] = subBlock(self.cinematicEvent)

            tempCoordStr = ""
            if self.relative:
                raise NotImplementedError("")
            else:
                tempCoordStr = str(self.coords[time]["x"]) + " " + str(self.coords[time]["y"]) + " " + str(self.coords[time]["z"])
                if self.dimension == 5:
                    tempCoordStr += " " + str(self.coords[time]["ry"]) + " " + str(self.coords[time]["rx"])
                    
            tpBlocks[time].commands.append("tp " + self.selector + " " + tempCoordStr)

        for i in range(len(timeList) - 2):
            nowTime = timeList[i]
            nextTime = timeList[i+1]
            tpBlocks[nowTime].commands.append("\n# Delay " + str(nextTime - nowTime) + " ticks and go <" + tpBlocks[nextTime].file.functionName + ">")
            tpBlocks[nowTime].commands.append("scoreboard players set @s MDMS_delay " + str(nextTime - nowTime))
            tpBlocks[nowTime].commands.append("scoreboard players set @s MDMS_afterDelay " + str(subBlock.blockDestinationID[tpBlocks[nextTime]]))

        if 0 not in tpBlocks:
            tpBlocks[0] = subBlock(self.cinematicEvent)
            tpBlocks[0].commands.append("scoreboard players set @s MDMS_delay " + str(timeList[0]))
            tpBlocks[0].commands.append("scoreboard players set @s MDMS_afterDelay " + str(subBlock.blockDestinationID[tpBlocks[timeList[0]]]))

        self.cinematicEvent.firstBlock.commands.append("\n# This block is for pre-processing cinematic functions.")
        for time in timeList:
            tempCoordStr = str(round(self.coords[time]["x"], 4)) + "\t" + str(round(self.coords[time]["y"], 4)) + "\t" + str(round(self.coords[time]["z"], 4))
            if self.dimension == 5:
                tempCoordStr += "\t" + str(round(self.coords[time]["ry"], 4)) + "\t" + str(round(self.coords[time]["rx"], 4))
            self.cinematicEvent.firstBlock.commands.append("# Tick " + str(time) + ":\t\t" + tempCoordStr)
        self.cinematicEvent.firstBlock.commands.append("execute @s ~ ~ ~ function " + str(tpBlocks[0].file.functionName))

        if self.wait:
            beforeCinBlock.commands.append("\n# Starting cinematic with waiting mode")
            beforeCinBlock.commands.append("execute @s ~ ~ ~ function " + self.cinematicEvent.firstBlock.file.functionName)
            tpBlocks[timeList[-1]].commands.append("\n# Finished cinematic with waiting mode, go to the next part")
            tpBlocks[timeList[-1]].commands.append("execute @s ~ ~ ~ function " + afterCinBlock.file.functionName)

        else:
            beforeCinBlock.commands.append("\n# Starting cinematic without waiting mode")
            newCinematicCaller = marker(None)
            beforeCinBlock.commands += newEventCaller.initCommands(mode = "cinematic")
            command  = "execute @e[type=area_effect_cloud,tag=MDMS_marker_beforeInit,c=1,name="+ newCinematicCaller.entityName +"] ~ ~ ~ "
            command += "function " + self.cinematicEvent.firstBlock.file.functionName
            beforeCinBlock.commands.append(command)
            beforeCinBlock.commands.append("\n# And skipping to next step.")
            beforeCinBlock.commands.append("execute @s ~ ~ ~ function " + afterCinBlock.file.functionName)

        self.written = True
