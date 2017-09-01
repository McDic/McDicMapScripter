# SubBlock Information:
#   No BlockDestination ID for this subBlock

# MDMS_system scoring.
scoreboard players set @e[tag=!MDMS_system] MDMS_system 0

# Result = A
scoreboard players operation MDMS_op_result_float_factor MDMS_tempCal = MDMS_op_0_float_factor MDMS_tempCal
scoreboard players operation MDMS_op_result_float_offset MDMS_tempCal = MDMS_op_0_float_offset MDMS_tempCal