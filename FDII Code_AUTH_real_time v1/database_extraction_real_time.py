import pandas as pd
import pyodbc
import time
import os
import logging
import numpy as np
#from gamspy import Container

from pandas import read_excel
from measurements_acquisition import meas_acq
from datetime import datetime

#m=Container()
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Connection details
server = 'localhost\\SQLEXPRESS'
database = 'MSG-PV'
conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=True;'

try:
    connection = pyodbc.connect(conn_str)
    cursor = connection.cursor()
    logging.info("Connected to SQL Server.")
except Exception as e:
    logging.error("Error while connecting to SQL Server: %s", e)
    exit()

# File path for IEC tags
filepath_iec_tags = 'C:\\Users\\stdim\\IEC104_Tags.xlsx'

### HEDNO Configuration
meas_config = read_excel(filepath_iec_tags, sheet_name='T13')

PV_names = ['PV1', 'PV2', 'PV3', 'PV4', 'PV5']
pattern = '|'.join(PV_names)
PV_meas_config = meas_config[meas_config['T13 ((Measured Value), short floating point number)'].str.contains(pattern, na=False)]
PV_meas_config.loc[:, 'SDG_ODBC'] = PV_meas_config['SDG_ODBC'].str.replace('W', '', regex=False)

# Output CSV file for measurements
measurement_file = 'extracted_measurements.csv'
if not os.path.exists(measurement_file):
    pd.DataFrame(columns=['PV_name', 'Installed Power', 'Category', 'Frequency', 'Vout (V)', 
                          'Pout (kW)', 'Pset (kW)', 'Power Factor', 'Timestamp']).to_csv(measurement_file, index=False)

monitoring_sleep = 1  # Interval for writing data in seconds

# Inform the user how to stop the loop.
print("The data extraction loop is running continuously. Press Ctrl+C to terminate.")

# Initialize accumulator dictionaries for each quantity (persist over all cycles)
vb_dict = {pv: [] for pv in PV_names}
prt_dict = {pv: [] for pv in PV_names}
qrt_dict = {pv: [] for pv in PV_names}
ib_dict = {pv: [] for pv in PV_names}

cycle = 0
try:
    while True:
        logging.info("Starting cycle %d", cycle + 1)
        
        # Temporary lists for the current cycle (will be converted to NumPy arrays)
        current_vb = []
        current_prt = []
        current_qrt = []
        current_ib = []
        
        for pv in PV_names:
            try:
                # Get PV metadata
                PV_acq_data = meas_acq(cursor, PV_meas_config['SDG_ODBC'])
                PV_meas = pd.merge(PV_meas_config, PV_acq_data, left_on='SDG_ODBC', right_on='Tag_Name', how='left')
                new_order = ['tag', 'Element_Name', 'Measured_Variable', 'Value', 'Installed Power', 
                             'Category', 'DT', 'tag.1', 'SDG_ODBC', 'Tag_Name',
                             'T13 ((Measured Value), short floating point number)', 'Type', 'type', 'address']
                PV_meas = PV_meas[new_order]
    
                # Extract measurement values for specific PV
                frequency = PV_meas[(PV_meas['Element_Name'] == pv) & 
                                    (PV_meas['Measured_Variable'] == 'F')]['Value'].values.item()
                voltage = PV_meas[(PV_meas['Element_Name'] == pv) & 
                                  (PV_meas['Measured_Variable'] == 'Vb')]['Value'].values.item()
                power = PV_meas[(PV_meas['Element_Name'] == pv) & 
                                (PV_meas['Measured_Variable'] == 'Prt')]['Value'].values.item()
                reactive_power = PV_meas[(PV_meas['Element_Name'] == pv) & 
                                         (PV_meas['Measured_Variable'] == 'Qrt')]['Value'].values.item()
                power_factor = PV_meas[(PV_meas['Element_Name'] == pv) & 
                                       (PV_meas['Measured_Variable'] == 'PF')]['Value'].values.item()
                timestamp = datetime.fromtimestamp(
                    PV_meas[(PV_meas['Element_Name'] == pv) & 
                            (PV_meas['Measured_Variable'] == 'PF')]['DT'].values.item() / 1e9)
                Pmax = PV_meas[(PV_meas["Element_Name"] == pv) & 
                               (PV_meas['Measured_Variable'] == 'PF')]['Installed Power'].values.item()
                category = PV_meas[(PV_meas['Element_Name'] == pv) & 
                                   (PV_meas['Measured_Variable'] == 'PF')]['Category'].values.item()
    
                # Extract the Ib measurement
                ib_value = PV_meas[(PV_meas['Element_Name'] == pv) & 
                                   (PV_meas['Measured_Variable'] == 'Ib')]['Value'].values.item()
    
                # Print to console
                print(f'PV_name = {pv}, Frequency = {frequency} Hz, Voltage = {voltage} V, '
                      f'P = {power} kW, Q = {reactive_power} kVAr, PF = {power_factor}, T = {timestamp}')
    
                # Write measurements to CSV
                with open(measurement_file, 'a') as f:
                    f.write(f'{pv},{Pmax},{category},{frequency},{voltage},{power},{reactive_power},{power_factor},{timestamp}\n')
    
                # Update the accumulator dictionaries for the current PV
                vb_dict[pv].append(voltage)
                prt_dict[pv].append(power)
                qrt_dict[pv].append(reactive_power)
                ib_dict[pv].append(ib_value)
                
                # Append current cycle measurements to the temporary lists
                current_vb.append(voltage)
                current_prt.append(power)
                current_qrt.append(reactive_power)
                current_ib.append(ib_value)
    
            except Exception as e:
                logging.error("Error during monitoring or control for PV %s: %s", pv, e)
    
        # Convert current cycle lists to NumPy arrays (overwriting any previous arrays)
        vb_array = np.array(current_vb)
        prt_array = np.array(current_prt)
        qrt_array = np.array(current_qrt)
        ib_array = np.array(current_ib)
        
        # Optionally print the current cycle's NumPy arrays
        print(f"Cycle {cycle+1} numpy arrays:")
        print("Vb array:", vb_array)
        print("Prt array:", prt_array)
        print("Qrt array:", qrt_array)
        print("Ib array:", ib_array)
        
        time.sleep(monitoring_sleep)
        cycle += 1

except KeyboardInterrupt:
    logging.info("Infinite loop terminated by user.")
    print("\nProcess interrupted by the user. Exiting gracefully...")
    
if connection:
    connection.close()
    logging.info("Database connection closed after termination of the loop.")

# Optional: After termination, print the accumulated dictionaries
for pv in PV_names:
    print(f"{pv} accumulated Vb values:", vb_dict[pv])
    print(f"{pv} accumulated Prt values:", prt_dict[pv])
    print(f"{pv} accumulated Qrt values:", qrt_dict[pv])
    print(f"{pv} accumulated Ib values:", ib_dict[pv])
