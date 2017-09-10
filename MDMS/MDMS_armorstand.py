# Essentials
import math
import random
import copy

# MDMS libraries - armorstand needs math and cinematics
from MDMS_sigVar import *
from MDMS_math import *

#------------------------------------------------
# ArmorStand Animations

class armorstand:

    basicOffset = {"body": vec3Cart(0, 0, 0), # 0, 1.5, 0 - Body is the center
                   "leftArm": vec3Cart(0.4, 0, 0), # 0.4, 1.5, 0.0
                   "rightArm": vec3Cart(-0.4, 0, 0), # -0.4, 1.5, 0.0
                   #"leftLeg": vec3Cart(0.15, -0.75, 0), # 0.15, 0.75, 0.0
                   #"rightLeg": vec3Cart(-0.15, -0.75, 0), # -0.15, 0.75, 0.0
                   "leg" : vec3Cart(0, -0.75, 0)
                   #"head": vec3Cart(0, 0, 0) # 0, 1.5, 0
                   ,"test": vec3Cart(2.5, -6.2, 1.3),
                   "test2": vec3Cart(1, 2, -1.5),
                   "test3": vec3Cart(-3, 7, -6),
                   "test4": vec3Cart(-1, -1, -1)
                   }

    def __init__(self, vec5 = None, pose = None, selector = "@e[type=armor_stand]"):

        if vec5 is None:
            vec2 = vec2Angle(0, 0)
            vec3 = vec3Cart(0, 0, 0)
            vec5 = vec5MC(vec3, vec2)
        self.v5 = vec5
        
        if pose is None:
            self.pose = {}
            for bodypart in armorstand.basicOffset:
                self.pose[bodypart] = vec3Cart(0, 0, 0)
        else:
            self.pose = pose

        self.selector = selector

    def changePos(self, v5):
        if type(v5) is vec5MC:
            self.v5 = v5
        else:
            raise TypeError("Invalid v5 type in changePos in class armorstand")

    def changePose(self, bodypart, v3):
        if (type(v3) is vec3Angle) and (bodypart in armorstand.basicOffset):
            self.pose[bodypart] = copy.deepcopy(v3)
        else:
            raise TypeError("Invalid input type in changePose in class armorstand")

    def getPose(self):
        pose = {}
        tempAngle = copy.deepcopy(self.v5.v2) #; tempAngle.rx = 0
        print("TempAngle = " + str(tempAngle) + "\n")
        for bodypart in armorstand.basicOffset:
            pose[bodypart] = armorstand.basicOffset[bodypart].rotated(self.pose['body'])
            pose[bodypart] -= armorstand.basicOffset[bodypart]
            print("Rotating " + bodypart + ": " + str(pose[bodypart]) + ", " + str(tempAngle))
            print("Transfered: " + str(pose[bodypart].convert_sph()))
            print("Retransfered: " + str(pose[bodypart].convert_sph().convert_cart()))
            pose[bodypart] = pose[bodypart].rotated(tempAngle)
            #print("Result = " + str(pose[bodypart] - pose[bodypart].convert_sph().convert_cart()))
            print("")
        return pose


#a = armorstand()
#a.changePose("body", vec3Angle(45,25,0))
#b = a.getPose()
#print(b["leg"])
