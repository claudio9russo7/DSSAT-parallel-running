import math
import time
import os
import shutil
import pandas as pd
import dssat_sequence_file_creator as dsf
import subprocess
import glob
from multiprocessing import Process

#Here we define path for DSSAT, for input file and the number_groups!
POINTS_CSV = r"C:\Users\Claudio\PycharmProjects\DSSAT_FileX_creator\run_example.csv"
SOIL_HORIZON_ADJUSTED = r"C:\Users\Claudio\PycharmProjects\DSSAT_FileX_creator\soil_initial_conditions.csv"
WORK_DIR = r"C:\DSSAT48\Sequence"
BATCH_NAME = "DSSBatch.v48"
MODEL_EXE = r"C:\DSSAT48\DSCSM048.EXE"
SKIPROWS_OSU = 3

#IMPORTANT MODIFY THIS NUMBER BASED ON THE NUMBER OF YOUR CORE-1
NUMBER_GROUPS = 9

TEMP_CSV_DIR = os.path.join(WORK_DIR, "temp_csv_osu")
os.makedirs(TEMP_CSV_DIR, exist_ok=True)
TEMP_CSV_DIR_OLC = os.path.join(WORK_DIR, "temp_csv_olc")
os.makedirs(TEMP_CSV_DIR_OLC, exist_ok=True)


MASTER_CSV = os.path.join(WORK_DIR, "all_point_results.csv")
if os.path.exists(MASTER_CSV):
    os.remove(MASTER_CSV)
OLC_MASTER_CSV = os.path.join(WORK_DIR, "all_point_results_olc.csv")
if os.path.exists(OLC_MASTER_CSV):
    os.remove(OLC_MASTER_CSV)

records = pd.read_csv(POINTS_CSV, sep=";").to_dict("records")
n_points = len(records)
chunk = math.ceil(n_points / NUMBER_GROUPS)
groups = {

    i+1: records[i*chunk: min((i+1)*chunk, n_points)]
    for i in range(NUMBER_GROUPS)
}




def init_group_dir(gid):
    gd = os.path.join(WORK_DIR, f"group_{gid}")
    if os.path.exists(gd):
        shutil.rmtree(gd)
    os.makedirs(gd)
    # Nome SQX e OSU specifici per questo gruppo
    sqx_name = f"UNIT250{gid}.SQX"
    osu_name = f"UNIT250{gid}.OSU"
    batch_content = (
        "$BATCH(SEQUENCE)\n"
        "!\n"
        f"! Directory    : {gd}\n"
        f"! Command Line : \"{MODEL_EXE}\" Q {BATCH_NAME}\n"
        "! Crop         : Sequence\n"
        f"! Experiment   : {sqx_name}\n"
        "! ExpNo        : 1\n"
        f"! Debug        : {MODEL_EXE} \" Q {BATCH_NAME}\"\n"
        "!\n"
        "@FILEX                                                                                        TRTNO     RP     SQ     OP     CO\n"
        f"{gd}\\{sqx_name}                                                          1      1      1      1      0\n"
        f"{gd}\\{sqx_name}                                                          1      1      2      1      0\n"
        f"{gd}\\{sqx_name}                                                          1      1      3      1      0\n"
        f"{gd}\\{sqx_name}                                                          1      1      4      1      0\n"
    )

    with open(os.path.join(gd, BATCH_NAME), "w") as f:
        f.write(batch_content)
    return gd, sqx_name


def run_group(gid):
    gd, sqx_name= init_group_dir(gid)
    for rec in groups[gid]:
        point_id = rec['code_nod']
        sqx_path = os.path.join(gd, sqx_name)
        txt = dsf.dssat_file_seq_creator(
            rec["code_nod"], sqx_name,
            rec["Soil_id"], rec["WS"], rec["Dem_class"],
            rec["Date_IC"], SOIL_HORIZON_ADJUSTED,
            rec["Planting_date_s"], rec["Planting_date_f"],
            rec["tillage_day_1"], rec["tillage_day_2"]
        )
        with open(sqx_path, "w") as f:
            f.write(txt)
        try:

        # 2) DSSAT RUN
            subprocess.run([MODEL_EXE, "Q", BATCH_NAME], cwd=gd, check=True)

        # 3) Collection .OSU file for point
            osu_path = os.path.join(gd, sqx_name.replace(".SQX", ".OSU"))
            df = pd.read_fwf(osu_path, skiprows=SKIPROWS_OSU)
            df.insert(0, "point_id", rec["code_nod"])
            out_csv = os.path.join(TEMP_CSV_DIR, f"{gid}_{rec['code_nod']}.csv")
            df.to_csv(out_csv, index=False)

        # 4) Collecting .OLC file for point
            olc_path = osu_path.replace(".OSU", ".OLC")
            df_olc = pd.read_fwf(olc_path, skiprows = 13, header = 0)
            df_olc.insert(0, "point_id", point_id)
            out_olc_csv = os.path.join(TEMP_CSV_DIR_OLC, f"{gid}_{point_id}_olc.csv")
            df_olc.to_csv(out_olc_csv, index=False)
            print(f"[Group {gid}] Punto {rec['code_nod']} completato.")

        except Exception as e:
            fail_log = os.path.join(WORK_DIR, "failed_points.csv")
            with open(fail_log, 'a') as logf:
                logf.write(f"{rec['code_nod']}, {gid}, {str(e).replace(',', '')}\n")
            print(f"[Group {gid}] Error point {rec['code_nod']} - Skipping. Error: {e}")


if __name__ == "__main__":
    start = time.perf_counter()
    procs = []
    for gid in groups:
        p = Process(target=run_group, args=(gid,))
        p.start()
        procs.append(p)
    for p in procs:
        p.join()

    osu_temp_files = glob.glob(os.path.join(TEMP_CSV_DIR, "*.csv"))
    master_df = pd.concat((pd.read_csv(f) for f in osu_temp_files), ignore_index=True)
    master_df.to_csv(MASTER_CSV, index=False)

    olc_temp_files = glob.glob(os.path.join(TEMP_CSV_DIR_OLC, "*.csv"))
    master_df = pd.concat((pd.read_csv(f) for f in olc_temp_files), ignore_index=True)
    master_df.to_csv(OLC_MASTER_CSV, index=False)

    end = time.perf_counter()
    total = end - start
    n_points = len(records)
    avg = total / n_points
    print(f"\nTempo totale: {total:.2f} s per {n_points} punti")
    print(f"Tempo medio: {avg:.2f} s/point")
    print(f"Tutti i punti salvati in: {MASTER_CSV}")
    print(f"Tutti i punti salvati in: {OLC_MASTER_CSV}")
