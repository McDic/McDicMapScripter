# Operation int(float)
# Result = A.factor * 10^(A.offset - 8)
execute @s[score_MDMS_tempCal_min=9] ~ ~ ~ scoreboard players operation MDMS_op_result_int MDMS_tempCal *= 10 MDMS_number
execute @s[score_MDMS_tempCal=7] ~ ~ ~ scoreboard players operation MDMS_op_result_int MDMS_tempCal /= 10 MDMS_number
scoreboard players remove @s[score_MDMS_tempCal_min=9] MDMS_tempCal 1
scoreboard players add @s[score_MDMS_tempCal=7] MDMS_tempCal 1
kill @s[score_MDMS_tempCal_min=8,score_MDMS_tempCal=8]
execute @s ~ ~ ~ function mcdic_mapscripter:__system/__operation/__typeconvert/__to_int/__from_float/__sub1