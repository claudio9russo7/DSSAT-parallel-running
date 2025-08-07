import os
import pandas as pd
from typing import Union, Dict, Any


OUTPUT_DIRECTORY = r"C:\DSSAT48\Sequence"
csv_initial_conditions = r"C:\Users\Claudio\PycharmProjects\DSSAT_FileX_creator\soil_horizons_adjusted.csv"
osu_file = r"C:\Users\Claudio\PycharmProjects\DSSAT_FileX_creator\UNIT2501.OSU"
prov = "UNIT2509.SQX"


def remove_0(val):
    return f"{val:6.3f}".replace("0.", ".")

def elab_elevation_format(val):
    if val < 10:
        return f"   {val}"
    elif 10 <= val <100:
        return f"  {val}"

    elif val >= 1000:
        return f"{val}"
    else:
        return f" {val}"



def elab_nitrogen_format(val):
    if val >= 1:
        return f"{val:6.1f}"
    elif val < 1:
        return str(f" {val:6.1f}".replace("0.", ".")).ljust(2)
    else:
        return str(f"{val}").ljust(3)


def elab_depth_format(val):
    if val < 10:
        return f"  {str(val).ljust(2)}"
    elif val < 100:
        return f" {str(val).ljust(3)}"
    else:
        return f"{str(val).ljust(4)}"


def elab_weather_date(val):
    if len(str(val)) < 5:
        return f"0{val}"


def dssat_take_initial_conditions(code_nod: Union[str, int],
                                  csv_file: str,
                                  depth_col: str = None,
                                  water_col: str = "SH2O",
                                  nitrogen_cols: Dict[str, str] = None
                                  ) -> Dict[str, Any]:
    if depth_col is None:
        depth_col = {'bottom': 'LimIn'}
    if nitrogen_cols is None:
        nitrogen_cols = {"SNH4": "Ammonium", "SNO3": "Nitrate"}

    df = pd.read_csv(csv_file, sep = ";")
    subset = df[df['code_nod'].astype(str) == str(code_nod)]
    if subset.empty:
        raise ValueError(f"No record found for code_nod: {code_nod}")

    layers =[]

    for _, row in subset.iterrows():
        layers.append({
            'bottom': int(row[depth_col['bottom']]),
            "water" : float(row[water_col]),
            "SNH4"  : float(row[nitrogen_cols["SNH4"]]),
            "SNO3"  : float(row[nitrogen_cols["SNO3"]])
        })

    return {'layers': layers}


def dssat_file_seq_creator(code,
                           file_name,
                           soil,
                           ws,
                           elev,
                           date_initial_conditions,
                           ic_conditions,
                           planting_date_s,
                           planting_date_f,
                           tillage_day_1,
                           tillage_day_2
                           ):
    code_number = code
    code_ident_sf = f"SU{code_number}".ljust(25)
    code_ident_fb = f"FB{code_number}".ljust(25)
    soil_id = soil.ljust(10)
    weather_station = ws.ljust(4)
    date_IC = date_initial_conditions
    ic = dssat_take_initial_conditions(code_number, ic_conditions)
    p = file_name.split(".")[0] + "SQ"
    ic_rows = []
    for idx, layer in enumerate(ic['layers'], start=1):
        ic_rows.append(
            f" 1   {elab_depth_format(layer['bottom'])}"
            f"{remove_0(layer['water'])}"
            f"{elab_nitrogen_format(layer['SNH4'])}"
            f"{elab_nitrogen_format(layer['SNO3'])}"
        )

    treatments = (
            f"*EXP.DETAILS: {p} PROV\n"
            f"\n"
            "*GENERAL\n"
            "@PEOPLE\n"
            f"{-99}\n"
            "@ADDRESS\n"
            f"{-99}\n"
            "@SITE\n"
            f"{-99}\n"
            "@ PAREA  PRNO  PLEN  PLDR  PLSP  PLAY HAREA  HRNO  HLEN  HARM.........\n"
            "    -99   -99   -99   -99   -99   -99   -99   -99   -99   -99\n"
            "*TREATMENTS                        -------------FACTOR LEVELS------------\n"
            "@N R O C TNAME.................... CU FL SA IC MP MI MF MR MC MT ME MH SM\n"
            f" 1 1 1 0 {code_ident_sf}  1  1  0  1  1  0  1  0  0  0  0  0  1\n"
            f" 1 2 1 0 Fallow                     3  1  0  0  0  0  0  0  0  1  0  1  3\n"
            f" 1 3 1 0 {code_ident_fb}  2  1  0  0  2  0  0  0  0  0  0  3  2\n"
            f" 1 4 1 0 Fallow                     3  1  0  0  0  0  0  0  0  2  0  2  3\n"
    )

    cultivars = (
            f"\n"
            f"*CULTIVARS \n"
            f"@C CR INGENO CNAME\n"
            f" 1 SU UN0001 Ricino\n"
            f" 2 FB 999991 MINIMA\n"
            f" 3 FA IB0001 FALLOW\n"
    )
    fields = (
            f"\n"
            f"*FIELDS \n"
            f"@L ID_FIELD WSTA....  FLSA  FLOB  FLDT  FLDD  FLDS  FLST SLTX  SLDP  ID_SOIL    FLNAME\n"
            f" 1 00000001 {weather_station}      -99    -99   -99   -99   -99   -99  -99   -99  {soil_id} UN1\n"
            f"@L ...........XCRD ...........YCRD .....ELEV .............AREA .SLEN .FLWR .SLAS FLHST FHDUR\n"
            f" 1             -99             -99      {elab_elevation_format(elev)}               -99   -99   -99   -99   -99   -99"
    )

    soil_analysis = (

    )

    initial_conditions = (
        f"\n\n"
        f"*INITIAL CONDITIONS \n"
        f"@C   PCR ICDAT  ICRT  ICND  ICRN  ICRE  ICWD ICRES ICREN ICREP ICRIP ICRID ICNAME\n"
        f" 1   -99 {date_IC}   -99   -99   -99   -99   -99   -99   -99   -99   -99   -99 New\n"
        f"@C  ICBL  SH2O  SNH4  SNO3\n" +
        f"\n".join(ic_rows)
    )

    planting_details = (
        f"\n\n"
        f"*PLANTING DETAILS\n"
        f"@P PDATE EDATE  PPOP  PPOE  PLME  PLDS  PLRS  PLRD  PLDP  PLWT  PAGE  PENV  PLPH  SPRL                        PLNAME\n"
        f" 1 {elab_weather_date(planting_date_s)}   -99     5   -99     S     R   110   -99     3   -99   -99   -99   -99   -99                        SF{code}\n"
        f" 2 {elab_weather_date(planting_date_f)}   -99     5   -99     S     R   110   -99     3   -99   -99   -99   -99   -99                        FB{code}\n"
    )
    irrigation_water_management = (
        f"\n"
        f"*IRRIGATION AND WATER MANAGEMENT\n"
        f"@I  EFIR  IDEP  ITHR  IEPT  IOFF  IAME  IAMT IRNAME\n"
        f" 1    .9    30    50   100 IB001 IB001    10 Irrigated\n"
        f"@I IDATE  IROP IRVAL\n"
        f" 1     0 IR004    24\n"
        f" 1    53 IR004    60\n"
        f" 1    77 IR004    60\n"
        f" 1    81 IR004    60\n"
        f" 1    89 IR004    60\n"
    )

    fertilizers = (
        f"\n"
        f"*FERTILIZERS (INORGANIC)\n"
        f"@F FDATE  FMCD  FACD  FDEP  FAMN  FAMP  FAMK  FAMC  FAMO  FOCD FERNAME\n"
        f" 1     0 FE001 AP003     0    40   -99   -99   -99   -99   -99 SU{code}\n"
        f" 1    50 FE001 AP003     0    40   -99   -99   -99   -99   -99 SU{code}\n"
    )

    residues_and_organic_fertilizer = (
    )

    tillage_and_rotations = (
        f"\n"
        f"*TILLAGE AND ROTATIONS\n"
        f"@T TDATE TIMPL  TDEP TNAME\n"
        f" 1 04109 TI003    20 Fallow_1\n"
        f" 1 {elab_weather_date(tillage_day_1)} TI007    10 Fallow_1\n"
        f" 2 04272 TI003    20 Fallow_2\n"
        f" 2 {elab_weather_date(tillage_day_2)} TI007    10 Fallow_2\n"
    )

    harvest_Details = (
        f"\n"
        f"*HARVEST DETAILS\n"
        f"@H HDATE  HSTG  HCOM HSIZE   HPC  HBPC HNAME\n"
        f" 1 04274 GS000   -99   -99   -99   -99 Fallow_1\n"
        f" 2 04105 GS000   -99   -99   -99   -99 Fallow_2\n"
        f" 3   110 GS000     H     A     0     0 Fallow_2\n"
    )

    simulation_controls = (
        f"\n"
        f"*SIMULATION CONTROLS\n"
        f"@N GENERAL     NYERS NREPS START SDATE RSEED SNAME.................... SMODEL\n"
        f" 1 GE             19     1     S 04001  0450 Safflower\n"
        f"@N OPTIONS     WATER NITRO SYMBI PHOSP POTAS DISES  CHEM  TILL   CO2\n"
        f" 1 OP              Y     Y     N     N     N     N     N     Y     D\n"
        f"@N METHODS     WTHER INCON LIGHT EVAPO INFIL PHOTO HYDRO NSWIT MESOM MESEV MESOL\n"
        f" 1 ME              M     M     E     R     S     L     R     1     P     R     2\n"
        f"@N MANAGEMENT  PLANT IRRIG FERTI RESID HARVS\n"
        f" 1 MA              R     D     D     R     M\n"
        f"@N OUTPUTS     FNAME OVVEW SUMRY FROPT GROUT CAOUT WAOUT NIOUT MIOUT DIOUT VBOSE CHOUT OPOUT FMOPT\n"
        f" 1 OU              Y     Y     Y    90     Y     Y     Y     Y     N     N     Y     N     Y     A\n"
        f"\n"
        f"@  AUTOMATIC MANAGEMENT\n"
        f"@N PLANTING    PFRST PLAST PH2OL PH2OU PH2OD PSTMX PSTMN\n"
        f" 1 PL          04114 04135    40   100    30    40    10\n"
        f"@N IRRIGATION  IMDEP ITHRL ITHRU IROFF IMETH IRAMT IREFF\n"
        f" 1 IR             30    50   100 IB001 IB001    10     1\n"
        f"@N NITROGEN    NMDEP NMTHR NAMNT NCODE NAOFF\n"
        f" 1 NI             30    50    25 IB001 IB001\n"
        f"@N RESIDUES    RIPCN RTIME RIDEP\n"
        f" 1 RE            100     1    20\n"
        f"@N HARVEST     HFRST HLAST HPCNP HPCNR\n"
        f" 1 HA              0 02001   100     0\n"
        f"\n"
        f"@N GENERAL     NYERS NREPS START SDATE RSEED SNAME.................... SMODEL\n"
        f" 2 GE             19     1     S 04001  2150 Fava_bean\n"
        f"@N OPTIONS     WATER NITRO SYMBI PHOSP POTAS DISES  CHEM  TILL   CO2\n"
        f" 2 OP              Y     Y     Y     N     N     N     N     Y     D\n"
        f"@N METHODS     WTHER INCON LIGHT EVAPO INFIL PHOTO HYDRO NSWIT MESOM MESEV MESOL\n"
        f" 2 ME              M     M     E     R     S     L     R     1     P     R     2\n"
        f"@N MANAGEMENT  PLANT IRRIG FERTI RESID HARVS\n"
        f" 2 MA              R     N     N     R     D\n"
        f"@N OUTPUTS     FNAME OVVEW SUMRY FROPT GROUT CAOUT WAOUT NIOUT MIOUT DIOUT VBOSE CHOUT OPOUT FMOPT\n"
        f" 2 OU              Y     Y     Y    90     Y     Y     Y     Y     N     N     Y     N     Y     A\n"
        f"\n"
        f"@  AUTOMATIC MANAGEMENT\n"
        f"@N PLANTING    PFRST PLAST PH2OL PH2OU PH2OD PSTMX PSTMN\n"
        f" 2 PL          04288 04319    40   100    30    40    5\n"
        f"@N IRRIGATION  IMDEP ITHRL ITHRU IROFF IMETH IRAMT IREFF\n"
        f" 2 IR             30    50   100 IB001 IB001    10     1\n"
        f"@N NITROGEN    NMDEP NMTHR NAMNT NCODE NAOFF\n"
        f" 2 NI             30    50    25 IB001 IB001\n"
        f"@N RESIDUES    RIPCN RTIME RIDEP\n"
        f" 2 RE            100     1    20\n"
        f"@N HARVEST     HFRST HLAST HPCNP HPCNR\n"
        f" 2 HA              0 02001     0     0\n"
        f"\n"
        f"@N GENERAL     NYERS NREPS START SDATE RSEED SNAME.................... SMODEL\n"
        f" 3 GE             19     1     S 04001  2150 Fallow\n"
        f"@N OPTIONS     WATER NITRO SYMBI PHOSP POTAS DISES  CHEM  TILL   CO2\n"
        f" 3 OP              Y     Y     Y     N     N     N     N     Y     D\n"
        f"@N METHODS     WTHER INCON LIGHT EVAPO INFIL PHOTO HYDRO NSWIT MESOM MESEV MESOL\n"
        f" 3 ME              M     M     E     R     S     L     R     1     P     R     2\n"
        f"@N MANAGEMENT  PLANT IRRIG FERTI RESID HARVS\n"
        f" 3 MA              R     R     R     R     R\n"
        f"@N OUTPUTS     FNAME OVVEW SUMRY FROPT GROUT CAOUT WAOUT NIOUT MIOUT DIOUT VBOSE CHOUT OPOUT FMOPT\n"
        f" 3 OU              Y     Y     Y    90     Y     Y     Y     Y     N     N     Y     N     Y     A\n"
        f"\n"
        f"@  AUTOMATIC MANAGEMENT\n"
        f"@N PLANTING    PFRST PLAST PH2OL PH2OU PH2OD PSTMX PSTMN\n"
        f" 3 PL          04001 04001    40   100    30    40    5\n"
        f"@N IRRIGATION  IMDEP ITHRL ITHRU IROFF IMETH IRAMT IREFF\n"
        f" 3 IR             30    50   100 IB001 IB001    10     1\n"
        f"@N NITROGEN    NMDEP NMTHR NAMNT NCODE NAOFF\n"
        f" 3 NI             30    50    25 IB001 IB001\n"
        f"@N RESIDUES    RIPCN RTIME RIDEP\n"
        f" 3 RE            100     1    20\n"
        f"@N HARVEST     HFRST HLAST HPCNP HPCNR\n"
        f" 3 HA              0 02001   100     0\n"
    )
    return treatments + \
        cultivars + \
        fields + \
        initial_conditions + \
        planting_details + \
        irrigation_water_management + \
        fertilizers + tillage_and_rotations + \
        harvest_Details + simulation_controls
