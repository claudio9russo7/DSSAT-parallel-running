
working_directory = r"C:\DSSAT48\Sequence"
MODEL_EXE = r"C:\DSSAT48\DSCSM048.EXE"
BATCH_NAME = "DSSBatch.v48"
SQX_NAME = "UNIT2509.SQX"




batch_content = f"""
$BATCH(SEQUENCE)
!
! Directory    : {working_directory}
! Command Line : "{MODEL_EXE}" Q {BATCH_NAME}
! Crop         : Sequence
! Experiment   : {SQX_NAME}
! ExpNo        : 1
! Debug        : {MODEL_EXE} " Q {BATCH_NAME}"
!
@FILEX                                                                                        TRTNO     RP     SQ     OP     CO
{working_directory}\\{SQX_NAME}                                                                  1      1      1      1      0
{working_directory}\\{SQX_NAME}                                                                  1      1      2      1      0
{working_directory}\\{SQX_NAME}                                                                  1      1      3      1      0
{working_directory}\\{SQX_NAME}                                                                  1      1      4      1      0
"""

print(batch_content)