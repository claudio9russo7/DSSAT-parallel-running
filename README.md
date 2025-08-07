# DSSAT Batch Processing Workflow

This script is designed to run DSSAT simulations on multiple points, each represented in the `POINTS_CSV` file. The workflow involves the following steps:

## 1. **Divide Points into Groups**
   The first step is to divide the points into groups based on the total number of points. The points are distributed equally among the groups defined by the `NUMBER_GROUPS` variable. Set this variable based on the core of your computer (core-1).

## 2. **Create Directories and Batch Files**
   For each group, a new directory is created. Additionally, a batch file (`BATCH_NAME`) is written containing the necessary information for running the DSSAT simulations. This batch file specifies the experiment, crop, and other parameters.

## 3. **Generate DSSAT Input Files for Each Point**
   For each point in a group, the function `dssat_file_seq_creator` generates an input file (`.SQX`) with the required data. This file is used by DSSAT to run the simulation.

## 4. **Run DSSAT**
   After generating the `.SQX` file, the DSSAT model is run using the following command:
   ```python
   subprocess.run([MODEL_EXE, "Q", BATCH_NAME], cwd=gd, check=True)