#------------------------------------------------
# Constants, Important variables

class sigVar: # significant variables

    projectName = ""

    baseObjectives = {"dummy": ["MDMS_system", "MDMS_delay", "MDMS_targetBlock", "MDMS_afterDelay",
                                "MDMS_prevStackID", "MDMS_UUID", "MDMS_number", "MDMS_debugMsg",
                                "MDMS_tempCal", "MDMS_targetMem"]}
    # Variable objective: MDMS_varXXX
    
    systemInitCommands = []

    commands = ["advancement", "ban", "blockdata", "clear", "clone", "debug",
                "defaultgamemode", "deop", "difficulty", "effect", "enchant",
                "entitydata", "execute", "fill", "function", "gamemode", "gamerule",
                "give", "help", "kick", "kill", "list", "locate", "me", "op",
                "pardon", "particle", "playsound", "publish", "recipe", "reload",
                "replaceitem", "save", "say", "scoreboard", "seed", "setblock",
                "setidletimeout", "setmaxplayers", "setworldspawn", "spawnpoint",
                "spreadplayers", "stats", "stop", "stopsound", "summon", "teleport",
                "tell", "tellraw", "testfor", "testforblock", "testforblocks",
                "time", "title", "toggledownfall", "tp", "transferserver",
                "trigger", "weather", "whitelist", "worldborder", "wsserver", "xp"]
    
    supportedVariableTypes = {"int":    {"memSize":1, "childs":["int"]},
                              "float":  {"memSize":2, "childs":["float_factor", "float_offset"]},
                              "bool":   {"memSize":1, "childs":["bool"]}
                              }
