# Operation float(int)
# Result: Int -> Float ( a = b * 10^(c-8) )
kill @e[type=area_effect_cloud,tag=MDMS_op_temp]
summon area_effect_cloud ~ ~ ~ {Duration:999999999, Tags:["MDMS_system", "MDMS_tempCal", "MDMS_op", "MDMS_op_temp"]}
scoreboard players operation @e[type=area_effect_cloud,tag=MDMS_op_temp] MDMS_tempCal = MDMS_op_0_int MDMS_tempCal
scoreboard players operation MDMS_op_result_float_factor MDMS_tempCal = MDMS_op_0_int MDMS_tempCal
scoreboard players set MDMS_op_result_float_offset MDMS_tempCal 8
execute @e[type=area_effect_cloud,tag=MDMS_op_temp] ~ ~ ~ function mcdic_mapscripter:__system/__operation/__typeconvert/__to_float/__from_int/__sub1