# regexTest needs
from MDMS_sigVar import *
from MDMS_regex import *
from MDMS_normalStatement import compileStatement

index = 0
st = input()

while st != "":
    index += 1
    stack = compileStatement(st, inputIndex = index)
    #print(stack)
    st = input()
