# SubBlock Information:
#   No BlockDestination ID for this subBlock

# Result: Float -> Bool / If a != 0 then True else False
kill @e[type=area_effect_cloud,tag=MDMS_op_temp]
summon area_effect_cloud ~ ~ ~ {Duration:999999999, Tags:["MDMS_system", "MDMS_tempCal", "MDMS_op", "MDMS_op_temp"]}
scoreboard players operation @e[type=area_effect_cloud,tag=MDMS_op_temp] MDMS_tempCal = MDMS_op_0_float_factor MDMS_tempCal
scoreboard players set MDMS_op_result_bool MDMS_tempCal 1
execute @e[type=area_effect_cloud,tag=MDMS_op_temp,score_MDMS_tempCal_min=0,score_MDMS_tempCal=0] ~ ~ ~ scoreboard players set MDMS_op_result_bool MDMS_tempCal 0
kill @e[type=area_effect_cloud,tag=MDMS_op_temp]