# Operation float(int)
# Result: Int -> Float ( a = b * 10^(c-8) )
kill @s[score_MDMS_tempCal_min=0,score_MDMS_tempCal=0]
kill @s[score_MDMS_tempCal_min=100000000,score_MDMS_tempCal=999999999]
kill @s[score_MDMS_tempCal=-100000000,score_MDMS_tempCal=-999999999]

execute @s[score_MDMS_tempCal_min=1000000000] ~ ~ ~ scoreboard players add MDMS_op_result_float_offset 1
execute @s[score_MDMS_tempCal_min=1,score_MDMS_tempCal=99999999] ~ ~ ~ scoreboard players remove MDMS_op_result_float_offset 1
execute @s[score_MDMS_tempCal=-1000000000] ~ ~ ~ scoreboard players add MDMS_op_result_float_offset 1
execute @s[score_MDMS_tempCal=-1,score_MDMS_tempCal_min=-99999999] ~ ~ ~ scoreboard players remove MDMS_op_result_float_offset 1

execute @s[score_MDMS_tempCal_min=1000000000] ~ ~ ~ scoreboard players operation MDMS_op_result_float_factor MDMS_tempCal /= 10 MDMS_number
execute @s[score_MDMS_tempCal_min=1000000000] ~ ~ ~ scoreboard players operation @s MDMS_tempCal /= 10 MDMS_number
execute @s[score_MDMS_tempCal=-1000000000] ~ ~ ~ scoreboard players operation MDMS_op_result_float_factor MDMS_tempCal /= 10 MDMS_number
execute @s[score_MDMS_tempCal=-1000000000] ~ ~ ~ scoreboard players operation @s MDMS_tempCal /= 10 MDMS_number

execute @s[score_MDMS_tempCal_min=1,score_MDMS_tempCal=99999999] ~ ~ ~ scoreboard players operation MDMS_op_result_float_factor MDMS_tempCal *= 10 MDMS_number
execute @s[score_MDMS_tempCal_min=1,score_MDMS_tempCal=99999999] ~ ~ ~ scoreboard players operation @s MDMS_tempCal *= 10 MDMS_number
execute @s[score_MDMS_tempCal=-1,score_MDMS_tempCal_min=-99999999] ~ ~ ~ scoreboard players operation MDMS_op_result_float_factor MDMS_tempCal *= 10 MDMS_number
execute @s[score_MDMS_tempCal=-1,score_MDMS_tempCal_min=-99999999] ~ ~ ~ scoreboard players operation @s MDMS_tempCal *= 10 MDMS_number

execute @s ~ ~ ~ function mcdic_mapscripter:__system/__operation/__typeconvert/__to_float/__from_int/__sub1