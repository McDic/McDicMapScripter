# SubBlock Information:
#   No BlockDestination ID for this subBlock

# MDMS_system scoring.
scoreboard players set @e[tag=!MDMS_system] MDMS_system 0

# Result = if A is True then 1 else 0
kill @e[type=area_effect_cloud,tag=MDMS_op_temp]
summon area_effect_cloud ~ ~ ~ {Duration:999999999, Tags:["MDMS_system", "MDMS_tempCal", "MDMS_op", "MDMS_op_temp"]}
scoreboard players operation @e[type=area_effect_cloud,tag=MDMS_op_temp] MDMS_tempCal = MDMS_op_0_bool MDMS_tempCal
scoreboard players set MDMS_op_result_int MDMS_tempCal 1
execute @e[type=area_effect_cloud,tag=MDMS_op_temp,score_MDMS_tempCal_min=0,score_MDMS_tempCal=0] ~ ~ ~ scoreboard players set MDMS_op_result_int MDMS_tempCal 0