from MDMS_cinematic import cuts_spline_spheric_singleval as csss

print("Remember the syntax is 't x y z ry rx (ryd) (rxd)'")

selector = input('Input your target entity to move: ')
inputfilename = input("Input your file name without '.txt': ")
file = open(inputfilename + '.txt')
lines = file.read().split("\n")
file.close()

xlist = []
ylist = []
zlist = []
tlist = []
rylist = []
rxlist = []
rydlist = []
rxdlist = []

i = 0
for line in lines:
    i += 1
    coords = line.split(" ")
    if len(coords) >= 6:
        xlist.append(float(coords[1]))
        ylist.append(float(coords[2]))
        zlist.append(float(coords[3]))
        rylist.append(float(coords[4]))
        rxlist.append(float(coords[5]))
        tlist.append(int(coords[0]))
        if len(coords) == 8:
            if coords[6] not in ('+', '-') or coords[7] not in ('+', '-'):
                raise ValueError("Invalid value for ryd, rxd in line " + str(i))
            rydlist.append(coords[6])
            rxdlist.append(coords[7])
        elif len(coords) == 6:
            rydlist.append('*')
            rxdlist.append('*')
        else:
            raise SyntaxError("Invalid arguments in line " + str(i))
    else:
        raise SyntaxError("Invalid arguments in line " + str(i))

#print(xlist, ylist, zlist)
#print(rylist, rxlist)
#print(tlist)
#print(rydlist, rxdlist)

xlist = csss(xlist, tlist)
ylist = csss(ylist, tlist)
zlist = csss(zlist, tlist)
rylist = csss(rylist, tlist, angleMode = "ry", angleDirections = rydlist)
rxlist = csss(rxlist, tlist, angleMode = "rx", angleDirections = rxdlist)

for i in range(len(xlist)):
    file = open('SimpleCinematicResult/' + inputfilename + str(i+1) + '.txt', mode = 'w')
    file.write('tp ' + selector + ' ' + str(xlist[i]) + ' ')
    file.write(str(ylist[i]) + ' ' + str(zlist[i]) + ' ')
    file.write(str(rylist[i]) + ' ' + str(rxlist[i]) + '\n')
    file.close()
