# SubBlock Information:
#   No BlockDestination ID for this subBlock

# MDMS_system scoring.
scoreboard players set @e[tag=!MDMS_system] MDMS_system 0

# Result = A.factor * 10^(A.offset - 8)
scoreboard players operation MDMS_op_result_int MDMS_tempCal = MDMS_op_A_float_factor MDMS_tempCal
kill @e[type=area_effect_cloud,tag=MDMS_op_temp]
summon area_effect_cloud ~ ~ ~ {Duration:999999999, Tags:["MDMS_system", "MDMS_tempCal", "MDMS_op", "MDMS_op_temp"]}
execute @e[type=area_effect_cloud,tag=MDMS_op_temp] ~ ~ ~ function $$:__system/__operation/__typeconvert/__to_int/__from_float/__sub1