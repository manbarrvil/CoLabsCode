import time
import pickle
import logging
import pyodbc
import pandas as pd
import numpy as np
import os
import json
from pandas import read_excel
import datetime as dt
import random
import c104

#from get_dynamic_measurements import get_dynamic_measurements
from State_Estimation_generic_function_rt import State_Estimation_generic_function
from process_measurements_rt_new import process_measurements
#from process_measurements_temp import process_measurements_temp
#from Information_extraction_function_clean_rt import extract_info

# Load grid data. Assuming that the topology of the grid will not change in the framework of the WP3 tests, we do not need to extract the grid info
# each time using Pandapower. It can happen once, and then the information to be stored in an appropriate file (e.g., of pickle format). 
with open("extracted_grid_info.pkl", "rb") as f:
    (num_buses, slack_bus, der_positions_ratings, hashmap_names, hashmap_reduction,
     zero_injection_buses, hashmap_reduction2, hashmap_names2, H_v_full, H_p_full, H_q_full, 
     slack_bus_row_P, slack_bus_row_Q, injection_buses, adjacency_matrix_buses, 
     adjacency_matrix_branches, parent_child_adjacency, R, X, Bshunt, Gshunt, S_n) = pickle.load(f)

##The lines below to be activated if we want to re-extract the grid information 
#data_filepath = "C:\\Users\\stdim\\EC_Network_reduced_merged_final.xlsx"
   
#num_buses, slack_bus, der_positions_ratings, hashmap_names, hashmap_reduction, zero_injection_buses, hashmap_reduction2, hashmap_names2, H_v_full, H_p_full, #H_q_full, slack_bus_row_P, slack_bus_row_Q, injection_buses, adjacency_matrix_buses,  adjacency_matrix_branches, parent_child_adjacency, R, X, Bshunt, Gshunt, S_n = extract_info (data_filepath)  


# Initialize measurement arrays
Pmes = np.ones(num_buses, dtype=float)
Qmes = np.ones(num_buses, dtype=float)
Vmes = np.ones(num_buses, dtype=float)
Pflow_mes = np.zeros(num_buses, dtype=float)
Qflow_mes = np.zeros(num_buses, dtype=float)


pseudo_measurement_filepath = "C:\\workspace\\CoLabsCode\\EC_HEDNO\\FDII Code_AUTH_real_time v1\\Pseudomeasurements.xlsx"

pseudo_measurement_sheet_name = 'Pseudomeasurements'

tag_correspondence_filepath = "C:\\workspace\\CoLabsCode\\EC_HEDNO\\FDII Code_AUTH_real_time v1\\Tag correspondence.xlsx"
tag_correspondence_sheet_name = 'Correspondence'

###Measurement filepaths to bypass the use of database measurements, since they are still incomplete
measurement_filepath = "C:\\workspace\\CoLabsCode\\EC_HEDNO\\FDII Code_AUTH_real_time v1\\Input measurements_final.xlsx"
measurement_sheet_name = 'Measurements'

'''
===============================================================
NOTE: The following code segment placed in comments is no longer needed, since the USE code 
for measurement extraction from the database will be used. 
===============================================================
'''

# # Configure logging
# import logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # -----------------------------
# # Setup SQL Connection
# # -----------------------------
# import pyodbc

# server = 'localhost\\SQLEXPRESS'
# database = 'MSG-PV'
# conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=True;'

# try:
#     connection = pyodbc.connect(conn_str)
#     cursor = connection.cursor()
#     logging.info("Connected to SQL Server.")
# except Exception as e:
#     logging.error("Error connecting to SQL Server: %s", e)
#     exit()

# # -----------------------------
# # Load Measurement Configuration
# # -----------------------------
# import os
# import pandas as pd

# filepath_iec_tags = 'C:\\Users\\stdim\\IEC104_Tags.xlsx'
# meas_config = pd.read_excel(filepath_iec_tags, sheet_name='T13')

# PV_names = ['PV1', 'PV2', 'PV3', 'PV4', 'PV5', 'TRIAD']
# pattern = '|'.join(PV_names)
# PV_meas_config = meas_config[meas_config['T13 ((Measured Value), short floating point number)']
#                             .str.contains(pattern, na=False)]
# PV_meas_config.loc[:, 'SDG_ODBC'] = PV_meas_config['SDG_ODBC'].str.replace('W', '', regex=False)

# # CSV file with extended header including TRIAD measured variables (for raw measurements)
# measurement_file = 'extracted_measurements.csv'
# csv_columns = ['Device', 'Installed Power', 'Category', 'Frequency', 'Vout (V)', 
#                'Pout (kW)', 'Qout (kVAr)', 'Power Factor', 'Timestamp',
#                'I1', 'I2', 'I3', 'V12', 'V23', 'V31', 'PTOT', 'QTOT']

# if not os.path.exists(measurement_file):
#     pd.DataFrame(columns=csv_columns).to_csv(measurement_file, index=False)

# # -----------------------------
# # State Estimation Configuration
# # -----------------------------
# monitoring_sleep = 5  # seconds

# # Initialize accumulators for PV measurements (if needed)
# vb_dict = {pv: [] for pv in ['PV1', 'PV2', 'PV3', 'PV4', 'PV5']}
# prt_dict = {pv: [] for pv in ['PV1', 'PV2', 'PV3', 'PV4', 'PV5']}
# qrt_dict = {pv: [] for pv in ['PV1', 'PV2', 'PV3', 'PV4', 'PV5']}
# ib_dict = {pv: [] for pv in ['PV1', 'PV2', 'PV3', 'PV4', 'PV5']}

# # Initialize accumulators for TRIAD (feeder) measurements
# feeder_vb_list = []
# feeder_ib_list = []
# feeder_prt_list = []
# feeder_qrt_list = [] 


# ------------------------------------------------------------------
# Set up a state estimation accumulator dictionary.
# Keys are the state estimation parameters and values are lists
# containing the value from each cycle.
# ------------------------------------------------------------------
se_keys = ["max_residual_measurement_type", "max_residual_bus_index", "max_residual_index",
           "max_residual_val", "Vest_array", "Pest_array", "Qest_array", "Vmesp_array",
           "Pmesp_array", "Qmesp_array", "residuals_df_P", "residuals_df_Q", "residuals_df_V",
           "removed_residuals"]
se_accum = {key: [] for key in se_keys}

# Define the state estimation results CSV file.
# We will write the entire accumulator in a transposed format.
state_estimation_results_file = "state_estimation_results.csv"

def write_state_estimation_csv(accum_dict):
    """
    Write the state estimation accumulator as a CSV file.
    The output CSV will have a header: "Parameter, Cycle 1, Cycle 2, ..."
    and one row per parameter.
    """
    # Determine the number of cycles (assume all lists have the same length)
    num_cycles = len(next(iter(accum_dict.values())))
    header = ["Parameter"] + [f"Cycle {i+1}" for i in range(num_cycles)]
    
    # Build rows: one row per parameter
    rows = []
    for key, values in accum_dict.items():
        # Here, if values are arrays or dataframes, we assume they are already converted
        # to string (e.g., via json.dumps or .to_json) before accumulation.
        row = [key] + values
        rows.append(row)
    
    # Create a DataFrame and write to CSV
    df = pd.DataFrame(rows, columns=header)
    df.to_csv(state_estimation_results_file, index=False)

# -----------------------------
# Main Infinite Loop for Real-Time Operation
# -----------------------------
cycle = 0
monitoring_sleep = 5  # seconds

# arr_W = [50.0, 0.0, 250.0, 100.0,10.0,0.0,0.0,0.0,0.0,0.0]
# arr_feeder = [0.0, 0.0, 0.0, 433,433,433,600,60.0]
# arr_W = arr_W*6
# arr_W.extend(arr_feeder)

client = c104.Client()
connection_104 = client.add_connection(ip="192.168.5.3", port=2404, init=c104.Init.ALL)
# connection.on_unexpected_message(callable=con_on_unexpected_message)
station = connection_104.add_station(common_address=1)

# monitoring point preparation
PV1_P_ref  = station.add_point(io_address=16418, type=c104.Type.M_ME_NC_1)
PV1_P_rate = station.add_point(io_address=16419, type=c104.Type.M_ME_NC_1)
PV1_FDP    = station.add_point(io_address=16420, type=c104.Type.M_ME_NC_1)
PV1_Q_ref  = station.add_point(io_address=16421, type=c104.Type.M_ME_NC_1)
PV1_Q_rate = station.add_point(io_address=16423, type=c104.Type.M_ME_NC_1)
PV1_P      = station.add_point(io_address=16431, type=c104.Type.M_ME_NC_1)
PV1_Q      = station.add_point(io_address=16433, type=c104.Type.M_ME_NC_1)
PV1_V      = station.add_point(io_address=16434, type=c104.Type.M_ME_NC_1)
PV1_I      = station.add_point(io_address=16437, type=c104.Type.M_ME_NC_1)
PV1_F      = station.add_point(io_address=16442, type=c104.Type.M_ME_NC_1)

PV2_P_ref  = station.add_point(io_address=16418+25, type=c104.Type.M_ME_NC_1)
PV2_P_rate = station.add_point(io_address=16419+25, type=c104.Type.M_ME_NC_1)
PV2_FDP    = station.add_point(io_address=16420+25, type=c104.Type.M_ME_NC_1)
PV2_Q_ref  = station.add_point(io_address=16421+25, type=c104.Type.M_ME_NC_1)
PV2_Q_rate = station.add_point(io_address=16423+25, type=c104.Type.M_ME_NC_1)
PV2_P      = station.add_point(io_address=16431+25, type=c104.Type.M_ME_NC_1)
PV2_Q      = station.add_point(io_address=16433+25, type=c104.Type.M_ME_NC_1)
PV2_V      = station.add_point(io_address=16434+25, type=c104.Type.M_ME_NC_1)
PV2_I      = station.add_point(io_address=16437+25, type=c104.Type.M_ME_NC_1)
PV2_F      = station.add_point(io_address=16442+25, type=c104.Type.M_ME_NC_1)

PV3_P_ref  = station.add_point(io_address=16418+50, type=c104.Type.M_ME_NC_1)
PV3_P_rate = station.add_point(io_address=16419+50, type=c104.Type.M_ME_NC_1)
PV3_FDP    = station.add_point(io_address=16420+50, type=c104.Type.M_ME_NC_1)
PV3_Q_ref  = station.add_point(io_address=16421+50, type=c104.Type.M_ME_NC_1)
PV3_Q_rate = station.add_point(io_address=16423+50, type=c104.Type.M_ME_NC_1)
PV3_P      = station.add_point(io_address=16431+50, type=c104.Type.M_ME_NC_1)
PV3_Q      = station.add_point(io_address=16433+50, type=c104.Type.M_ME_NC_1)
PV3_V      = station.add_point(io_address=16434+50, type=c104.Type.M_ME_NC_1)
PV3_I      = station.add_point(io_address=16437+50, type=c104.Type.M_ME_NC_1)
PV3_F      = station.add_point(io_address=16442+50, type=c104.Type.M_ME_NC_1)

PV4_P_ref  = station.add_point(io_address=16418+75, type=c104.Type.M_ME_NC_1)
PV4_P_rate = station.add_point(io_address=16419+75, type=c104.Type.M_ME_NC_1)
PV4_FDP    = station.add_point(io_address=16420+75, type=c104.Type.M_ME_NC_1)
PV4_Q_ref  = station.add_point(io_address=16421+75, type=c104.Type.M_ME_NC_1)
PV4_Q_rate = station.add_point(io_address=16423+75, type=c104.Type.M_ME_NC_1)
PV4_P      = station.add_point(io_address=16431+75, type=c104.Type.M_ME_NC_1)
PV4_Q      = station.add_point(io_address=16433+75, type=c104.Type.M_ME_NC_1)
PV4_V      = station.add_point(io_address=16434+75, type=c104.Type.M_ME_NC_1)
PV4_I      = station.add_point(io_address=16437+75, type=c104.Type.M_ME_NC_1)
PV4_F      = station.add_point(io_address=16442+75, type=c104.Type.M_ME_NC_1)

PV5_P_ref  = station.add_point(io_address=16418+100, type=c104.Type.M_ME_NC_1)
PV5_P_rate = station.add_point(io_address=16419+100, type=c104.Type.M_ME_NC_1)
PV5_FDP    = station.add_point(io_address=16420+100, type=c104.Type.M_ME_NC_1)
PV5_Q_ref  = station.add_point(io_address=16421+100, type=c104.Type.M_ME_NC_1)
PV5_Q_rate = station.add_point(io_address=16423+100, type=c104.Type.M_ME_NC_1)
PV5_P      = station.add_point(io_address=16431+100, type=c104.Type.M_ME_NC_1)
PV5_Q      = station.add_point(io_address=16433+100, type=c104.Type.M_ME_NC_1)
PV5_V      = station.add_point(io_address=16434+100, type=c104.Type.M_ME_NC_1)
PV5_I      = station.add_point(io_address=16437+100, type=c104.Type.M_ME_NC_1)
PV5_F      = station.add_point(io_address=16442+100, type=c104.Type.M_ME_NC_1)

POI_Ia      = station.add_point(io_address=25114, type=c104.Type.M_ME_NC_1)
POI_Ib      = station.add_point(io_address=25115, type=c104.Type.M_ME_NC_1)
POI_Ic      = station.add_point(io_address=25116, type=c104.Type.M_ME_NC_1)
POI_Vab     = station.add_point(io_address=25117, type=c104.Type.M_ME_NC_1)
POI_Vbc     = station.add_point(io_address=25118, type=c104.Type.M_ME_NC_1)
POI_Vca     = station.add_point(io_address=25119, type=c104.Type.M_ME_NC_1)
POI_P       = station.add_point(io_address=25120, type=c104.Type.M_ME_NC_1)
POI_Q       = station.add_point(io_address=25121, type=c104.Type.M_ME_NC_1)

PV6_P_ref  = station.add_point(io_address=16418+125, type=c104.Type.M_ME_NC_1)
PV6_P_rate = station.add_point(io_address=16419+125, type=c104.Type.M_ME_NC_1)
PV6_FDP    = station.add_point(io_address=16420+125, type=c104.Type.M_ME_NC_1)
PV6_Q_ref  = station.add_point(io_address=16421+125, type=c104.Type.M_ME_NC_1)
PV6_Q_rate = station.add_point(io_address=16423+125, type=c104.Type.M_ME_NC_1)
PV6_P      = station.add_point(io_address=16431+125, type=c104.Type.M_ME_NC_1)
PV6_Q      = station.add_point(io_address=16433+125, type=c104.Type.M_ME_NC_1)
PV6_V      = station.add_point(io_address=16434+125, type=c104.Type.M_ME_NC_1)
PV6_I      = station.add_point(io_address=16437+125, type=c104.Type.M_ME_NC_1)
PV6_F      = station.add_point(io_address=16442+125, type=c104.Type.M_ME_NC_1)

PV7_V      = station.add_point(io_address=16568, type=c104.Type.M_ME_NC_1)
PV7_I      = station.add_point(io_address=16569, type=c104.Type.M_ME_NC_1)
PV7_F      = station.add_point(io_address=16570, type=c104.Type.M_ME_NC_1)
PV7_P      = station.add_point(io_address=16571, type=c104.Type.M_ME_NC_1)
PV7_Q      = station.add_point(io_address=16572, type=c104.Type.M_ME_NC_1)

PV8_V      = station.add_point(io_address=16573, type=c104.Type.M_ME_NC_1)
PV8_I      = station.add_point(io_address=16574, type=c104.Type.M_ME_NC_1)
PV8_F      = station.add_point(io_address=16575, type=c104.Type.M_ME_NC_1)
PV8_P      = station.add_point(io_address=16576, type=c104.Type.M_ME_NC_1)
PV8_Q      = station.add_point(io_address=16577, type=c104.Type.M_ME_NC_1)

PV9_V      = station.add_point(io_address=16578, type=c104.Type.M_ME_NC_1)
PV9_I      = station.add_point(io_address=16579, type=c104.Type.M_ME_NC_1)
PV9_F      = station.add_point(io_address=16580, type=c104.Type.M_ME_NC_1)
PV9_P      = station.add_point(io_address=16581, type=c104.Type.M_ME_NC_1)
PV9_Q      = station.add_point(io_address=16582, type=c104.Type.M_ME_NC_1)

# command point preparation
PV1_SET_P      = station.add_point(io_address=25089, type=c104.Type.C_SE_NC_1)
PV1_SET_P_rate = station.add_point(io_address=25090, type=c104.Type.C_SE_NC_1)
PV1_SET_FDP    = station.add_point(io_address=25091, type=c104.Type.C_SE_NC_1)
PV1_SET_Q      = station.add_point(io_address=25092, type=c104.Type.C_SE_NC_1)
PV1_SET_Q_rate = station.add_point(io_address=25093, type=c104.Type.C_SE_NC_1)

PV2_SET_P      = station.add_point(io_address=25094, type=c104.Type.C_SE_NC_1)
PV2_SET_P_rate = station.add_point(io_address=25095, type=c104.Type.C_SE_NC_1)
PV2_SET_FDP    = station.add_point(io_address=25096, type=c104.Type.C_SE_NC_1)
PV2_SET_Q      = station.add_point(io_address=25097, type=c104.Type.C_SE_NC_1)
PV2_SET_Q_rate = station.add_point(io_address=25098, type=c104.Type.C_SE_NC_1)

PV3_SET_P      = station.add_point(io_address=25099, type=c104.Type.C_SE_NC_1)
PV3_SET_P_rate = station.add_point(io_address=25100, type=c104.Type.C_SE_NC_1)
PV3_SET_FDP    = station.add_point(io_address=25101, type=c104.Type.C_SE_NC_1)
PV3_SET_Q      = station.add_point(io_address=25102, type=c104.Type.C_SE_NC_1)
PV3_SET_Q_rate = station.add_point(io_address=25103, type=c104.Type.C_SE_NC_1)

PV4_SET_P      = station.add_point(io_address=25104, type=c104.Type.C_SE_NC_1)
PV4_SET_P_rate = station.add_point(io_address=25105, type=c104.Type.C_SE_NC_1)
PV4_SET_FDP    = station.add_point(io_address=25106, type=c104.Type.C_SE_NC_1)
PV4_SET_Q      = station.add_point(io_address=25107, type=c104.Type.C_SE_NC_1)
PV4_SET_Q_rate = station.add_point(io_address=25108, type=c104.Type.C_SE_NC_1)

PV5_SET_P      = station.add_point(io_address=25109, type=c104.Type.C_SE_NC_1)
PV5_SET_P_rate = station.add_point(io_address=25110, type=c104.Type.C_SE_NC_1)
PV5_SET_FDP    = station.add_point(io_address=25111, type=c104.Type.C_SE_NC_1)
PV5_SET_Q      = station.add_point(io_address=25112, type=c104.Type.C_SE_NC_1)
PV5_SET_Q_rate = station.add_point(io_address=25113, type=c104.Type.C_SE_NC_1)

def client_IEC104():

    # start
    client.start()
    time.sleep(0.3)

    PV1_P_ref.read()
    PV1_P_rate.read()
    PV1_FDP.read()
    PV1_Q_ref.read()
    PV1_Q_rate.read()
    PV1_P.read()
    PV1_Q.read()
    PV1_V.read()
    PV1_I.read()
    PV1_F.read()

    PV2_P_ref .read()
    PV2_P_rate.read()
    PV2_FDP   .read()
    PV2_Q_ref .read()
    PV2_Q_rate.read()
    PV2_P     .read()
    PV2_Q     .read()
    PV2_V     .read()
    PV2_I     .read()
    PV2_F     .read()

    PV3_P_ref .read()
    PV3_P_rate.read()
    PV3_FDP   .read()
    PV3_Q_ref .read()
    PV3_Q_rate.read()
    PV3_P     .read()
    PV3_Q     .read()
    PV3_V     .read()
    PV3_I     .read()
    PV3_F     .read()

    PV4_P_ref .read()
    PV4_P_rate.read()
    PV4_FDP   .read()
    PV4_Q_ref .read()
    PV4_Q_rate.read()
    PV4_P     .read()
    PV4_Q     .read()
    PV4_V     .read()
    PV4_I     .read()
    PV4_F     .read()

    PV5_P_ref .read()
    PV5_P_rate.read()
    PV5_FDP   .read()
    PV5_Q_ref .read()
    PV5_Q_rate.read()
    PV5_P     .read()
    PV5_Q     .read()
    PV5_V     .read()
    PV5_I     .read()
    PV5_F     .read()

    PV6_P_ref .read()
    PV6_P_rate.read()
    PV6_FDP   .read()
    PV6_Q_ref .read()
    PV6_Q_rate.read()
    PV6_P     .read()
    PV6_Q     .read()
    PV6_V     .read()
    PV6_I     .read()
    PV6_F     .read()

    PV7_V.read()
    PV7_I.read()
    PV7_F.read()
    PV7_P.read()
    PV7_Q.read()

    PV8_V.read()
    PV8_I.read()
    PV8_F.read()
    PV8_P.read()
    PV8_Q.read()

    PV9_V.read()
    PV9_I.read()
    PV9_F.read()
    PV9_P.read()
    PV9_Q.read()

    POI_Ia .read()
    POI_Ib .read()
    POI_Ic .read()
    POI_Vab.read()
    POI_Vbc.read()
    POI_Vca.read()
    POI_P  .read()
    POI_Q  .read()

    PV1_SET_P     .value = 0.0
    PV1_SET_P_rate.value = 0.0
    PV1_SET_FDP   .value = 1.0
    PV1_SET_Q     .value = 0.0
    PV1_SET_Q_rate.value = 0.0

    PV2_SET_P     .value = 0.0
    PV2_SET_P_rate.value = 0.0
    PV2_SET_FDP   .value = 1.0
    PV2_SET_Q     .value = 0.0
    PV2_SET_Q_rate.value = 0.0

    PV3_SET_P     .value = 0.0
    PV3_SET_P_rate.value = 0.0
    PV3_SET_FDP   .value = 1.0
    PV3_SET_Q     .value = 0.0
    PV3_SET_Q_rate.value = 0.0

    PV4_SET_P     .value = 0.0
    PV4_SET_P_rate.value = 0.0
    PV4_SET_FDP   .value = 1.0
    PV4_SET_Q     .value = 0.0
    PV4_SET_Q_rate.value = 0.0

    PV5_SET_P     .value = 0.0
    PV5_SET_P_rate.value = 0.0
    PV5_SET_FDP   .value = 1.0
    PV5_SET_Q     .value = 0.0
    PV5_SET_Q_rate.value = 0.0

    PV1_SET_P     .transmit(cause=c104.Cot.ACTIVATION)
    PV1_SET_P_rate.transmit(cause=c104.Cot.ACTIVATION)
    PV1_SET_FDP   .transmit(cause=c104.Cot.ACTIVATION)
    PV1_SET_Q     .transmit(cause=c104.Cot.ACTIVATION)
    PV1_SET_Q_rate.transmit(cause=c104.Cot.ACTIVATION)

    PV2_SET_P     .transmit(cause=c104.Cot.ACTIVATION)
    PV2_SET_P_rate.transmit(cause=c104.Cot.ACTIVATION)
    PV2_SET_FDP   .transmit(cause=c104.Cot.ACTIVATION)
    PV2_SET_Q     .transmit(cause=c104.Cot.ACTIVATION)
    PV2_SET_Q_rate.transmit(cause=c104.Cot.ACTIVATION)

    PV3_SET_P     .transmit(cause=c104.Cot.ACTIVATION)
    PV3_SET_P_rate.transmit(cause=c104.Cot.ACTIVATION)
    PV3_SET_FDP   .transmit(cause=c104.Cot.ACTIVATION)
    PV3_SET_Q     .transmit(cause=c104.Cot.ACTIVATION)
    PV3_SET_Q_rate.transmit(cause=c104.Cot.ACTIVATION)

    PV4_SET_P     .transmit(cause=c104.Cot.ACTIVATION)
    PV4_SET_P_rate.transmit(cause=c104.Cot.ACTIVATION)
    PV4_SET_FDP   .transmit(cause=c104.Cot.ACTIVATION)
    PV4_SET_Q     .transmit(cause=c104.Cot.ACTIVATION)
    PV4_SET_Q_rate.transmit(cause=c104.Cot.ACTIVATION)

    PV5_SET_P     .transmit(cause=c104.Cot.ACTIVATION)
    PV5_SET_P_rate.transmit(cause=c104.Cot.ACTIVATION)
    PV5_SET_FDP   .transmit(cause=c104.Cot.ACTIVATION)
    PV5_SET_Q     .transmit(cause=c104.Cot.ACTIVATION)
    PV5_SET_Q_rate.transmit(cause=c104.Cot.ACTIVATION)

    PV1_Read = [PV1_F.value,PV1_I.value,PV1_V.value,PV1_P.value,PV1_Q.value,PV1_P_ref.value,PV1_P_rate.value,PV1_FDP.value,PV1_Q_ref.value,PV1_Q_rate.value]
    PV2_Read = [PV2_F.value,PV2_I.value,PV2_V.value,PV2_P.value,PV2_Q.value,PV2_P_ref.value,PV2_P_rate.value,PV2_FDP.value,PV2_Q_ref.value,PV2_Q_rate.value]
    PV3_Read = [PV3_F.value,PV3_I.value,PV3_V.value,PV3_P.value,PV3_Q.value,PV3_P_ref.value,PV3_P_rate.value,PV3_FDP.value,PV3_Q_ref.value,PV3_Q_rate.value]
    PV4_Read = [PV4_F.value,PV4_I.value,PV4_V.value,PV4_P.value,PV4_Q.value,PV4_P_ref.value,PV4_P_rate.value,PV4_FDP.value,PV4_Q_ref.value,PV4_Q_rate.value]
    PV5_Read = [PV5_F.value,PV5_I.value,PV5_V.value,PV5_P.value,PV5_Q.value,PV5_P_ref.value,PV5_P_rate.value,PV5_FDP.value,PV5_Q_ref.value,PV5_Q_rate.value]
    PV6_Read = [PV6_F.value,PV6_I.value,PV6_V.value,PV6_P.value,PV6_Q.value,PV6_P_ref.value,PV6_P_rate.value,PV6_FDP.value,PV6_Q_ref.value,PV6_Q_rate.value]
    PV7_Read = [PV7_V.value,PV7_I.value,PV7_F.value,PV7_P.value,PV7_Q.value]
    PV8_Read = [PV8_V.value,PV8_I.value,PV8_F.value,PV8_P.value,PV8_Q.value]
    PV9_Read = [PV9_V.value,PV9_I.value,PV9_F.value,PV9_P.value,PV9_Q.value]
    POI_Read = [POI_Ia.value,POI_Ib.value,POI_Ic.value,POI_Vab.value,POI_Vbc.value,POI_Vca.value,POI_P.value,POI_Q.value]

    # PV1_setpoint = [PV1_SET_P.value, PV1_SET_P_rate.value, PV1_SET_FDP.value, PV1_SET_Q.value, PV1_SET_Q_rate.value]
    # PV2_setpoint = [PV2_SET_P.value, PV2_SET_P_rate.value, PV2_SET_FDP.value, PV2_SET_Q.value, PV2_SET_Q_rate.value]
    # PV3_setpoint = [PV3_SET_P.value, PV3_SET_P_rate.value, PV3_SET_FDP.value, PV3_SET_Q.value, PV3_SET_Q_rate.value]
    # PV4_setpoint = [PV4_SET_P.value, PV4_SET_P_rate.value, PV4_SET_FDP.value, PV4_SET_Q.value, PV4_SET_Q_rate.value]
    # PV5_setpoint = [PV5_SET_P.value, PV5_SET_P_rate.value, PV5_SET_FDP.value, PV5_SET_Q.value, PV5_SET_Q_rate.value]


    client.stop()
    return PV1_Read, PV2_Read, PV3_Read, PV4_Read, PV5_Read, PV6_Read, PV7_Read, PV8_Read, PV9_Read, POI_Read

def write_TagArray_W(connection, t, data_COMM):

    # Inicializar diccionario vacío
    data = {}
    # Inicializar lista de claves vacía
    keys = []
    # Inicializar lista de valores con ceros
    values = data_COMM
    # Crear la lista de claves
    keys.append(f'Tag{0}_Value')
    for i in range(1,len(values)+1):
        keys.append(f'Tag{i}_Name')  # Asignar una clave única para cada valor
        keys.append(f'Tag{i}_Value')  # Asignar una clave única para cada valor
 
    data[keys[0]] = t
    #data[keys[1]] = ['Tag_1']
    for i in range(2,len(values)*2+1,2): 
        data[keys[i-1]] = [f'TAG_{int(i/2)}']
        data[keys[i]] = values[int(i/2-1)] + [random.randint(-1, 1)]

        
    df_combinado = pd.DataFrame(data)
    
    valores = [tuple(row) for row in df_combinado.itertuples(index=False)]
    consulta_insert = f"""
    INSERT INTO TagArray_W ({', '.join(df_combinado.columns)})
    VALUES ({', '.join(['?'] * len(df_combinado.columns))})
    """
    cursor = connection.cursor()
    try:
        cursor.executemany(consulta_insert, valores)
        connection.commit()
    except pyodbc.Error as e:
        print("Error al insertar registros:", e)
    finally:
        cursor.close()

def write_TagArray_Est(connection, t, Vest_array):

    # Inicializar diccionario vacío
    data = {}
    # Inicializar lista de claves vacía
    keys = []
    # Inicializar lista de valores con ceros
    Vest_array_W = Vest_array.to_numpy()
    values = Vest_array_W
    # Crear la lista de claves
    keys.append(f'Tag{0}_Value')
    for i in range(1,len(values)+1):
        keys.append(f'Tag{i}_Name')  # Asignar una clave única para cada valor
        keys.append(f'Tag{i}_Value')  # Asignar una clave única para cada valor
 
    data[keys[0]] = t
    #data[keys[1]] = ['Tag_1']
    for i in range(2,len(values)*2+1,2): 
        data[keys[i-1]] = [f'TAG_{int(i/2)}']
        data[keys[i]] = values[int(i/2-1)]

        
    df_combinado = pd.DataFrame(data)
    
    valores = [tuple(row) for row in df_combinado.itertuples(index=False)]
    consulta_insert = f"""
    INSERT INTO TagArray_Est ({', '.join(df_combinado.columns)})
    VALUES ({', '.join(['?'] * len(df_combinado.columns))})
    """
    cursor = connection.cursor()
    try:
        cursor.executemany(consulta_insert, valores)
        connection.commit()
    except pyodbc.Error as e:
        print("Error al insertar registros:", e)
    finally:
        cursor.close()

def read_TagArray_W(connection):
    cursor=connection.cursor()
      
    cursor.execute("SELECT TOP 1 Tag1_Value, Tag2_Value, Tag3_Value, Tag4_Value, Tag5_Value, Tag6_Value, Tag7_Value, Tag8_Value, Tag9_Value, Tag10_Value, Tag11_Value, Tag12_Value, Tag13_Value, Tag14_Value, Tag15_Value, Tag16_Value, Tag17_Value, Tag18_Value, Tag19_Value, Tag20_Value, Tag21_Value, Tag22_Value, Tag23_Value, Tag24_Value, Tag25_Value,Tag26_Value, Tag27_Value, Tag28_Value, Tag29_Value, Tag30_Value,Tag31_Value, Tag32_Value, Tag33_Value, Tag34_Value, Tag35_Value,Tag36_Value, Tag37_Value, Tag38_Value, Tag39_Value, Tag40_Value,Tag41_Value, Tag42_Value, Tag43_Value, Tag44_Value, Tag45_Value,Tag46_Value, Tag47_Value, Tag48_Value, Tag49_Value, Tag50_Value,Tag51_Value, Tag52_Value, Tag53_Value, Tag54_Value, Tag55_Value,Tag56_Value, Tag57_Value, Tag58_Value, Tag59_Value, Tag60_Value,Tag61_Value, Tag62_Value, Tag63_Value, Tag64_Value, Tag65_Value,Tag66_Value, Tag67_Value, Tag68_Value FROM MSG_PV.dbo.TagArray_W ORDER BY Tag0_Value DESC")
    
    data_read = cursor.fetchone()
    data_read_DB = list(data_read)  # Convierte la tupla en una lista
    return data_read_DB
        

if __name__ == '__main__':

    connection = pyodbc.connect('DRIVER={SQL Server};'
                                'SERVER=HOSTOPALRT\\SQLEXPRESS;'
                                'DATABASE=MSG_PV;'
                                'Trusted_Connection=yes;')
print("Starting dynamic state estimation loop. Press Ctrl+C to stop.")

try:
    while True:

        '''
        ===============================================================
        NOTE: Let's assume that here is called your function for extracting
        the database measurements. The function returns a numpy array called
        e.g., "meas_array". I forward "meas_array" to function "process_measurements"
        to create arrays with P,Q, and V measurements (can be easily extended for current measurements)
        ===============================================================
        '''
        now = dt.datetime.now()
        # Format the timestamp with decimal seconds
        t = now.strftime('%Y%m%d %H:%M:%S') + f".{now.microsecond // 1000:03d}"
        PV1_Read, PV2_Read, PV3_Read, PV4_Read, PV5_Read, PV6_Read, PV7_Read, PV8_Read, PV9_Read, POI_Read = client_IEC104()
        data_COMM_W = np.concatenate([np.array(PV1_Read), np.array(PV2_Read), np.array(PV3_Read), np.array(PV4_Read), np.array(PV5_Read),np.array(PV5_Read),np.array(PV6_Read),np.array(PV7_Read),np.array(PV8_Read),np.array(PV9_Read),np.array(POI_Read)])
        print(data_COMM_W, '\n')
        # data_COMM_W = np.array(arr_W)
        # Escritura en la base de datos, de comunicación a base de datos (DB)
        # write_TagArray_W(connection, t, data_COMM_W)
        # print('Rellenando Tabla  TagArray_W con las medidas del IEC104')
        # #meas_array = read_TagArray_W(connection)
        # meas_array = [51.0, 0.0, 249.0, 2.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 50.0, 1.0, 251.0, 0.0, 2.0, -1.0, 1.0, -1.0, 0.0, 0.0, 49.0, 1.0, 250.0, 2.0, 0.0, 1.0, -1.0, 0.0, -1.0, 1.0, 50.0, -1.0, 249.0, 0.0, 1.0, 0.0, 0.0, -1.0, 0.0, -1.0, 49.0, 1.0, 249.0, 2.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 49.0, 1.0, 249.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0, -1.0, 0.0, 19999.0, 19999.0, 20001.0, 60.0, 21.0]
        # print(meas_array)
        
        time.sleep(1.0)

        # Pmes, Qmes, Vmes = process_measurements(
        #     pseudo_measurement_filepath, pseudo_measurement_sheet_name, 
        #     tag_correspondence_filepath, tag_correspondence_sheet_name, 
        #     Pmes, Qmes, Vmes, hashmap_names, hashmap_reduction, 
        #     meas_array, slack_bus
        # )

    
        # # Call state estimation function
        # (max_residual_measurement_type, max_residual_bus_index, max_residual_index, max_residual_val,
        #  Vest_array, Pest_array, Qest_array, Vmesp_array, Pmesp_array, Qmesp_array,
        #  residuals_df_P, residuals_df_Q, residuals_df_V, removed_residuals) = State_Estimation_generic_function(
        #     num_buses, slack_bus, der_positions_ratings, zero_injection_buses, hashmap_reduction2, hashmap_names2,
        #     H_v_full, H_p_full, H_q_full, slack_bus_row_P, slack_bus_row_Q, injection_buses, Pmes, Qmes, Vmes,
        #     adjacency_matrix_buses, adjacency_matrix_branches, parent_child_adjacency, R, X, Bshunt, Gshunt, S_n
        # )

        # # For each state estimation parameter, convert outputs to strings if necessary.
        # # (For arrays, we use json.dumps after converting to list; for DataFrames, use .to_json.)
        # se_accum["max_residual_measurement_type"].append(str(max_residual_measurement_type))
        # se_accum["max_residual_bus_index"].append(str(max_residual_bus_index))
        # se_accum["max_residual_index"].append(str(max_residual_index))
        # se_accum["max_residual_val"].append(str(max_residual_val))
        # se_accum["Vest_array"].append(json.dumps(Vest_array.tolist() if hasattr(Vest_array, 'tolist') else Vest_array))
        # se_accum["Pest_array"].append(json.dumps(Pest_array.tolist() if hasattr(Pest_array, 'tolist') else Pest_array))
        # se_accum["Qest_array"].append(json.dumps(Qest_array.tolist() if hasattr(Qest_array, 'tolist') else Qest_array))
        # se_accum["Vmesp_array"].append(json.dumps(Vmesp_array.tolist() if hasattr(Vmesp_array, 'tolist') else Vmesp_array))
        # se_accum["Pmesp_array"].append(json.dumps(Pmesp_array.tolist() if hasattr(Pmesp_array, 'tolist') else Pmesp_array))
        # se_accum["Qmesp_array"].append(json.dumps(Qmesp_array.tolist() if hasattr(Qmesp_array, 'tolist') else Qmesp_array))
        # se_accum["residuals_df_P"].append(residuals_df_P.to_json() if hasattr(residuals_df_P, "to_json") else str(residuals_df_P))
        # se_accum["residuals_df_Q"].append(residuals_df_Q.to_json() if hasattr(residuals_df_Q, "to_json") else str(residuals_df_Q))
        # se_accum["residuals_df_V"].append(residuals_df_V.to_json() if hasattr(residuals_df_V, "to_json") else str(residuals_df_V))
        # se_accum["removed_residuals"].append(
        #     json.dumps(removed_residuals, default=lambda x: int(x) if isinstance(x, np.integer) else x)
        # )
        # write_TagArray_Est(connection, t, Vest_array)
        # print('Rellenando Tabla  TagArray_Est with the estimated values')
        # # Write the accumulated state estimation results to CSV
        # write_state_estimation_csv(se_accum)
        # logging.info("Cycle %d: State estimation results saved in restructured CSV.", cycle + 1)

        # time.sleep(monitoring_sleep)
        # cycle += 1

except KeyboardInterrupt:
    logging.info("Dynamic state estimation loop terminated by user.")
    print("Terminated by user.")
finally:
    if connection:
        connection.close()
        logging.info("SQL connection closed.")
