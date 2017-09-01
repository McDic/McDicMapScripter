# Essentials
import math
import random
import copy

#------------------------------------------------
# SIN COS

pi = math.pi

def sin(angle, mode):
    if mode in ("180", 180):
        return math.sin(angle*pi/180)
    elif mode in ("pi", pi):
        return math.sin(angle)
    else:
        raise ValueError("Undefined mode in sin")

def cos(angle, mode):
    if mode in ("180", 180):
        return math.cos(angle*pi/180)
    elif mode in ("pi", pi):
        return math.cos(angle)
    else:
        raise ValueError("Undefined mode in cos")

#------------------------------------------------
# Type supporting

def floatUnit(a): # a = factor * 10^offset, don't forget to use: int(factor * (10**8))
    (factor, offset) = (a, 0)
    if a == 0.0:
        return (0, 0)
    while abs(factor) < 1.0:
        factor *= 10.0
        offset -= 1
    while abs(factor) >= 10.0:
        factor /= 10.0
        offset += 1
        
    return (round(factor * (10**8)), offset - 8)

#------------------------------------------------
# Vectors

leftstr = ("left", "L", "LEFT", "Left")
rightstr = ("right", "R", "RIGHT", "Right")
updir = ("up", "U", "UP", "Up")
downdir = ("down", "D", "DOWN", "Down")

def updateAngleTypeRY(angle):
    ans = angle % 360
    if ans > 180:
        ans -= 360
    return ans

def updateAngleTypeRX(angle):
    while angle > 90 or angle < -90:
        if angle > 90:
            angle = 180 - angle
        elif angle < -90:
            angle = -180 - angle
    return angle

def updateAngleRXY(ry, rx): # update angles
    '''
    while ry > 180:
        ry -= 360
    while ry < -180:
        ry += 360
    '''
    ry = updateAngleTypeRY(ry)
    while rx > 90 or rx < -90:
        if rx > 90:
            rx = 180 - rx
        elif rx < -90:
            rx = -180 - rx
    return (ry, rx)

class vec3Cart: # Cartesian Vector (X, Y, Z)
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    def __str__(self):
        totalstr  = ""
        #totalstr += "vec3Cart, ID: " + id(self) + "\n"
        totalstr += "< X: " + str(self.x) + ", Y: " + str(self.y) + ", Z: " + str(self.z) + " >"
        return totalstr

    def __add__(self, anothervec3):
        if type(anothervec3) is vec3Cart:
            newvec3 = vec3Cart(0,0,0)
            newvec3.x = self.x + anothervec3.x
            newvec3.y = self.y + anothervec3.y
            newvec3.z = self.z + anothervec3.z
        elif type(anothervec3) is vec3Sph:
            raise TypeError("Type exception in __add__ in vec3Cart")
            '''
            newvec3 = vec3Cart(0,0,0)
            tempvec3 = anothervec3.convert_cart()
            newvec3.x = self.x + tempvec3.x
            newvec3.y = self.y + tempvec3.y
            newvec3.z = self.z + tempvec3.z
            '''
        else:
            raise TypeError("Type exception in __add__ in vec3Cart")
        return newvec3
    def __sub__(self, anothervec3):
        if type(anothervec3) is vec3Cart:
            newvec3 = vec3Cart(0,0,0)
            newvec3.x = self.x - anothervec3.x
            newvec3.y = self.y - anothervec3.y
            newvec3.z = self.z - anothervec3.z
        elif type(anothervec3) is vec3Sph:
            raise TypeError("Type exception in __sub__ in vec3Cart")
            '''
            newvec3 = vec3Cart(0,0,0)
            tempvec3 = anothervec3.convert_cart()
            newvec3.x = self.x - tempvec3.x
            newvec3.y = self.y - tempvec3.y
            newvec3.z = self.z - tempvec3.z
            '''
        else:
            raise TypeError("Type exception in __sub__ in vec3Cart")
        return newvec3
    def __mul__(self, counter):
        if type(counter) in (int, float): # simple multiplication
            newvec3 = vec3Cart(self.x, self.y, self.z)
            newvec3.x *= counter
            newvec3.y *= counter
            newvec3.z *= counter
        elif type(counter) is vec3Cart: # inner product
            return self.x * counter.x + self.y * counter.y + self.z * counter.z
        else:
            raise TypeError("Type exception in __mul__ in vec3Cart")
        return newvec3

    def __abs__(self):
        return math.sqrt(self.x*self.x + self.y*self.y + self.z*self.z)
    def convert_sph(self):
        x = self.x
        y = self.y
        z = self.z
        r = math.sqrt(x*x + y*y + z*z)
        if r==0:
            rx=0
            ry=0
        else:
            rx = math.asin(-y/r) / pi * 180
            if z==0:
                if x>0:
                    ry = 270
                elif x<0:
                    ry = 90
                else: # x=z=0
                   ry = 0
            else:
                ry = math.atan(-x/z) / pi * 180
        newvec3 = vec3Sph(r, vec2Angle(ry, rx))
        return newvec3

    def rotated(self, angle):
        x, y, z = self.x, self.y, self.z
        if type(angle) is vec3Angle:
            # X axis rotation: Y, Z -> c -s / s c
            y, z = cos(angle.xangle,"180")*y - sin(angle.xangle,"180")*z, sin(angle.xangle,"180")*y + cos(angle.xangle,"180")*z
            # Y axis rotation: Z, X -> c(-a) -s(-a) / s(-a) c(-a) -> c s -s c
            z, x = cos(angle.yangle,"180")*z + sin(angle.yangle,"180")*x, -sin(angle.yangle,"180")*z + cos(angle.yangle,"180")*x
            # Z axis rotation: Y, X -> c -s / s c
            y, x = cos(angle.zangle,"180")*y - sin(angle.zangle,"180")*x, sin(angle.zangle,"180")*y + cos(angle.zangle,"180")*x
        elif type(angle) is vec2Angle:
            sphConverted = self.convert_sph() + angle
            reconverted = sphConverted.convert_cart()
            x = reconverted.x
            y = reconverted.y
            z = reconverted.z
        return vec3Cart(x, y, z)

class vec2Angle: # Angle Vector (RY, RX)
    def __init__(self, ry, rx, ryd = None, rxd = None):
        self.ry = ry
        self.rx = rx
        self.ryd = ryd # RY direction in cinematics
        self.rxd = rxd # RX direction in cinematics
        self.update()
    def __str__(self):
        totalstr  = ""
        #totalstr += "vec2Angle, ID: " + id(self) + "\n"
        totalstr += "< RY: " + str(self.ry) + ", RX: " + str(self.rx) + " >"
        return totalstr

    def update(self):
        (self.ry, self.rx) = updateAngleRXY(self.ry, self.rx)

    def __add__(self, anothervec2):
        if type(anothervec2) is vec2Angle:
            newvec2 = vec2Angle(0,0)
            newvec2.ry = self.ry + anothervec2.ry
            newvec2.rx = self.rx + anothervec2.rx
        else:
            raise TypeError("Type exception in __add__ in vec2Angle")
        newvec2.update()
        return newvec2
    def __sub__(self, anothervec2):
        if type(anothervec2) is vec2Angle:
            newvec2 = vec2Angle(0,0)
            newvec2.ry = self.ry - anothervec3.ry
            newvec2.rx = self.rx - anothervec3.rx
        else:
            raise TypeError("Type exception in __sub__ in vec2Angle")
        newvec2.update()
        return newvec2
    def __mul__(self, counter):
        if type(counter) in (int, float):
            newvec2 = vec2Angle(self.ry, self.rx)
            newvec2.ry *= counter
            newvec2.rx *= counter
        else:
            raise TypeError("Type exception in __mul__ in vec2Angle")
        newvec2.update()
        return newvec2


class vec3Sph: # Spherical Vector (R, ANGLE)
    def __init__(self, r, angle):
        self.r = r
        if type(angle) is vec2Angle:
            self.angle = angle
        else:
            raise TypeError("Invalid type for angle in __init__ in vec3Sph")
        self.update()
    def __str__(self):
        totalstr  = ""
        #totalstr += "vec3Sph, ID: " + id(self) + "\n"
        totalstr += "< R: " + str(self.r) + ", RY: " + str(self.angle.ry) + ", RX: " + str(self.angle.rx) + " >"
        return totalstr
    def update(self):
        if self.r < 0:
            self.r *= -1
            self.angle.ry += 180
            self.angle.rx *= -1
        self.angle.update()

    def convert_cart(self): # in Minecraft
        r = self.r; ry = self.angle.ry; rx = self.angle.rx
        x = - r*cos(rx, "180")*sin(ry, "180")
        y = - r*sin(rx, "180")
        z = + r*cos(rx, "180")*cos(ry, "180")
        newv3 = vec3Cart(x, y, z)
        return newv3

    def __add__(self, anothervec):
        if type(anothervec) is vec3Sph:
            newvec3 = vec3Sph(0, vec2Angle(0,0))
            newvec3.angle = self.angle + anothervec.angle
            newvec3.r = self.r
        elif type(anothervec) is vec2Angle:
            newvec3 = vec3Sph(0, vec2Angle(0,0))
            newvec3.angle = self.angle + anothervec
            newvec3.r = self.r
        else:
            raise Exception("Type exception in __add__ in vec3Sph")
        newvec3.update()
        return newvec3
    def __sub__(self, anothervec):
        if type(anothervec) is vec3Sph:
            newvec3 = vec3Sph(0, vec2Angle(0,0))
            newvec3.angle = self.angle - anothervec.angle
            newvec3.r = self.r
        elif type(anothervec) is vec2Angle:
            newvec3 = vec3Sph(0, vec2Angle(0,0))
            newvec3.angle = self.angle - anothervec
            newvec.r = self.r
        else:
            raise Exception("Type exception in __sub__ in vec3Sph")
        newvec3.update()
        return newvec3
    def __mul__(self, counter):
        if type(counter) in (int, float):
            newvec3 = vec3Sph(0, vec2Angle(0, 0))
            newvec3.r = self.r * counter
            newvec3.angle.ry = self.angle.ry
            newvec3.angle.rx = self.angle.rx
        else:
            raise Exception("Type exception in __mul__ in vec3Sph")
        newvec3.update()
        return newvec3

class vec3Angle: # used for ArmorStand angle
    def __init__(self, X, Y, Z):
        self.xangle = X
        self.yangle = Y
        self.zangle = Z
        self.update()
    def __str__(self):
        totalstr  = ""
        #totalstr += "vec3Cart, ID: " + id(self) + "\n"
        totalstr += "< angleX: " + str(self.xangle) + ", angleY: " + str(self.yangle) + ", angleZ: " + str(self.zangle) + " >"
        return totalstr
    def update(self):
        self.xangle = updateAngleTypeRY(self.xangle)
        self.yangle = updateAngleTypeRY(self.yangle)
        self.zangle = updateAngleTypeRY(self.zangle)

class vec5MC: # Minecraft Standard Coordinates (Location, Angle)
    def __init__(self, v3_loc, v2_angle):
        self.v3 = v3_loc
        self.v2 = v2_angle
        self.update()
    def __str__(self):
        totalstr = ""
        totalstr += str(self.v3)
        totalstr += str(self.v2)
        return totalstr
    def update(self):
        self.v2.update()
        if type(self.v3) is vec3Sph:
            self.v3.update()

    def convert_cart(self):
        temp = self.deepcopy()
        if type(self.v3) is vec3Sph:
            newv3 = self.v3.convert_cart()
            return vec5MC(newv3, copy.deepcopy(self.v2))
        elif type(self.v3) is vec3Cart:
            return copy.deepcopy(self)
        else:
            raise Exception("Invalid type detected in vec5MC.convert_cart()")
    def convert_sph(self):
        if type(self.v3) is vec3Cart:
            newv3 = self.v3.convert_sph()
            return vec5MC(newv3, copy.deepcopy(self.v2))
        elif type(self.v3) is vec3Sph:
            return copy.deepcopy(self)
        else:
            raise Exception("Invalid type detected in vec5MC.convert_sph()")

    def __add__(self, anothervec):
        if type(anothervec) is vec5MC:
            newvec5 = vec5MC(vec3Cart(0,0,0), vec2Angle(0,0))
            newvec5.v3 = self.v3 + anothervec.v3
            newvec5.v2 = self.v2 + anothervec.v2
        elif type(anothervec) in (vec3Cart, vec3Sph):
            newvec5 = vec5MC(vec3Cart(0,0,0), vec2Angle(0,0))
            newvec5.v3 = self.v3 + anothervec
            newvec5.v2 = self.v2 + newvec5.v2
        elif type(anothervec) is vec2Angle:
            newvec5 = vec5MC(vec3Cart(0,0,0), vec2Angle(0,0))
            newvec5.v3 = self.v3 + newvec5.v3
            newvec5.v3 = self.v3
        else:
            raise Exception("Type exception in __add__ in vec5MC")
        newvec5.update()
        return newvec5
    def __sub__(self, anothervec):
        if type(anothervec) is vec5MC:
            newvec5 = vec5MC(vec3Cart(0,0,0), vec2Angle(0,0))
            newvec5.v3 = self.v3 - anothervec.v3
            newvec5.v2 = self.v2 - anothervec.v2
        elif type(anothervec) in (vec3Cart, vec3Sph):
            newvec5 = vec5MC(vec3Cart(0,0,0), vec2Angle(0,0))
            newvec5.v3 = self.v3 - anothervec
            newvec5.v2 = self.v2 - newvec5.v2
        else:
            raise Exception("Type exception in __sub__ in vec5MC")
        newvec5.update()
        return newvec5

class poly: # Polynomial; coefficients : [lv 0, lv 1, lv 2, ...]
    def __init__(self, coefflist):
        self.coeff = copy.deepcopy(coefflist)
    def __str__(self):
        totalstr = str(self.coeff[0])
        coefflen = len(self.coeff)
        for i in range(1, coefflen):
            totalstr += " + " + str(self.coeff[i]) + "x^" + str(i)
        return totalstr

    def val(self, x):
        s = 0.0
        coefflen = len(self.coeff)
        for i in range(coefflen):
            s += (x ** i) * self.coeff[i]
        return s

    def deriv(self):
        coeff_deriv = []
        lv = len(self.coeff)
        for i in range(lv-1):
            coeff_deriv.append( (i+1)*self.coeff[i+1] )
        derived = poly(coeff_deriv)
        return derived

    def print(self):
        length = len(self.coeff)
        ans = "poly id "+str(id(self))+" = "
        for i in range(length):
            ans += str(self.coeff[length-i-1])
            if i < length-1:
                ans += "x^"+str(length-i-1)+" + "
        print(ans)
