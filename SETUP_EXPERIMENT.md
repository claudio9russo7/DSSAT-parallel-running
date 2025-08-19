# How to Set Up Your Own DSSAT Experiment

This guide will walk you through the process of setting up and running your own DSSAT experiment using the provided Python scripts.

## 1. Folder Structure

It is recommended to have a clear folder structure for your experiment. For example:

```
C:/Your_Experiment/
|-- dssat_scripts/
|   |-- batch_creator.py
|   |-- dssat_sequence_file_creator.py
|   |-- run_parallel_dssat.py
|   |-- soil_initial_conditions.xlsx
|   |-- run_example.csv
|-- dssat_workspace/
    |-- Sequence/
```

*   `dssat_scripts`: This folder will contain the Python scripts and input files.
*   `dssat_workspace`: This folder will be your main DSSAT working directory. The scripts will create subdirectories inside the `Sequence` folder.

## 2. Prepare Your Input CSV File

The main input file for the experiment is a CSV file that contains a list of points to be simulated. You can use `run_example.csv` as a template.

The CSV file must have the following columns:

*   `code_nod`: A unique identifier for each point.
*   `Soil_id`: The ID of the soil type for the point. This should match a soil profile in your DSSAT database.
*   `WS`: The weather station code (e.g., 'ABAA').
*   `Dem_class`: Elevation class.
*   `Date_IC`: The date of the initial conditions in Julian day format (e.g., `23125`).
*   `Planting_date_s`: The start date for planting in Julian day format.
*   `Planting_date_f`: The end date for planting in Julian day format.
*   `tillage_day_1`: The first tillage day in Julian day format.
*   `tillage_day_2`: The second tillage day in Julian day format.

**Important:** The separator for the CSV file must be a semicolon (`;`).

## 3. Prepare the Soil Initial Conditions File

The script `dssat_sequence_file_creator.py` reads soil initial conditions from a CSV file. The file `soil_initial_conditions.xlsx` is provided as an example, but you need to convert it to a CSV file named `soil_initial_conditions.csv`.

The CSV file must have the following columns:

*   `code_nod`: The point identifier, which must match the `code_nod` in your main input CSV.
*   `LimIn`: The depth of the soil layer.
*   `SH2O`: The initial soil water content.
*   `Ammonium`: The initial ammonium content.
*   `Nitrate`: The initial nitrate content.

**Important:** The separator for the CSV file must be a semicolon (`;`).

## 4. Configure the Scripts

Before running the experiment, you need to modify the hardcoded paths in the Python scripts.

### 4.1. `run_parallel_dssat.py`

Open `run_parallel_dssat.py` and modify the following variables:

*   `POINTS_CSV`: Set the full path to your input CSV file.
*   `SOIL_HORIZON_ADJUSTED`: Set the full path to your `soil_initial_conditions.csv` file.
*   `WORK_DIR`: Set the path to your DSSAT `Sequence` directory (e.g., `C:\DSSAT48\Sequence`).
*   `MODEL_EXE`: Set the full path to the DSSAT executable (`DSCSM048.EXE`).
*   `NUMBER_GROUPS`: Set this to the number of CPU cores you want to use, minus one.

### 4.2. `dssat_sequence_file_creator.py`

Open `dssat_sequence_file_creator.py` and check the following variables. Although `run_parallel_dssat.py` passes the `SOIL_HORIZON_ADJUSTED` path, it's good practice to ensure the paths here are correct in case you want to run this script independently.

*   `OUTPUT_DIRECTORY`: Set the path to your DSSAT `Sequence` directory.
*   `csv_initial_conditions`: Set the full path to your `soil_initial_conditions.csv` file.

## 5. Run the Experiment

Once you have prepared your input files and configured the scripts, you can run the experiment by executing the `run_parallel_dssat.py` script from your terminal:

```bash
python run_parallel_dssat.py
```

The script will create a series of `group_X` folders in your `WORK_DIR`, and you will see the progress of the simulations in the console.

## 6. Output Files

After the simulation is complete, the script will generate two main output files in your `WORK_DIR`:

*   `all_point_results.csv`: This file contains the concatenated results from the `.OSU` files for all the simulated points.
*   `all_point_results_olc.csv`: This file contains the concatenated results from the `.OLC` files for all the simulated points.

You will also find a `failed_points.csv` file if any of the simulations failed. This file will contain the `code_nod` of the failed points and the corresponding error message.
