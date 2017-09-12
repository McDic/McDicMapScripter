# Operation float(bool)
# Result = If A is True then 1.0 else 0.0
kill @e[type=area_effect_cloud,tag=MDMS_op_temp]
summon area_effect_cloud ~ ~ ~ {Duration:999999999, Tags:["MDMS_system", "MDMS_tempCal", "MDMS_op", "MDMS_op_temp"]}
scoreboard players operation @e[type=area_effect_cloud,tag=MDMS_op_temp] MDMS_tempCal = MDMS_op_0_bool MDMS_tempCal
scoreboard players set MDMS_op_result_float_factor MDMS_tempCal 100000000
scoreboard players set MDMS_op_result_float_offset MDMS_tempCal 8
execute @e[type=area_effect_cloud,tag=MDMS_op_temp,score_MDMS_tempCal_min=0,score_MDMS_tempCal=0] ~ ~ ~ scoreboard players set MDMS_op_result_float_factor MDMS_tempCal 0