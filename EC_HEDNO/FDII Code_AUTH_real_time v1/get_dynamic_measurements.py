import pyodbc
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import os
from measurements_acquisition import meas_acq

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_dynamic_measurements(cursor, PV_meas_config, PV_names, measurement_file):
    """
    Retrieve dynamic measurements from SQL, merge with configuration, write to CSV,
    and return measurement arrays for PV devices as well as feeder measurements (TRIAD)

    Parameters:
        cursor: An open pyodbc cursor.
        PV_meas_config: A DataFrame containing IEC tag configurations.
        PV_names: List of device names to process (including 'TRIAD').
        measurement_file: Path to CSV file for logging measurements.

    Returns:
        vb_array, prt_array, qrt_array: NumPy arrays for voltage, active power, and reactive power (PV only).
        triad_values: A dictionary containing feeder measurements.
    """
    # Initialize temporary lists for PV measurements
    current_vb = []
    current_prt = []
    current_qrt = []
    # Initialize a dictionary to hold TRIAD measurements
    triad_values = {}

    for device in PV_names:
        try:
            # Acquire measurement data from SQL using meas_acq
            PV_acq_data = meas_acq(cursor, PV_meas_config['SDG_ODBC'])
            # Merge the acquired data with the configuration DataFrame
            PV_meas = pd.merge(PV_meas_config, PV_acq_data, left_on='SDG_ODBC', right_on='Tag_Name', how='left')
            
            # Optionally, reorder columns if needed
            new_order = ['tag', 'Element_Name', 'Measured_Variable', 'Value', 'Installed Power', 
                         'Category', 'DT', 'tag.1', 'SDG_ODBC', 'Tag_Name',
                         'T13 ((Measured Value), short floating point number)', 'Type', 'type', 'address']
            PV_meas = PV_meas[new_order]
            
            if device != 'TRIAD':
                # Extract PV-specific measurements
                frequency = PV_meas[(PV_meas['Element_Name'] == device) & 
                                    (PV_meas['Measured_Variable'] == 'F')]['Value'].values.item()
                voltage = PV_meas[(PV_meas['Element_Name'] == device) & 
                                  (PV_meas['Measured_Variable'] == 'Vb')]['Value'].values.item()
                power = PV_meas[(PV_meas['Element_Name'] == device) & 
                                (PV_meas['Measured_Variable'] == 'Prt')]['Value'].values.item()
                reactive_power = PV_meas[(PV_meas['Element_Name'] == device) & 
                                         (PV_meas['Measured_Variable'] == 'Qrt')]['Value'].values.item()
                power_factor = PV_meas[(PV_meas['Element_Name'] == device) & 
                                       (PV_meas['Measured_Variable'] == 'PF')]['Value'].values.item()
                timestamp = datetime.fromtimestamp(
                            PV_meas[(PV_meas['Element_Name'] == device) & 
                                    (PV_meas['Measured_Variable'] == 'PF')]['DT'].values.item() / 1e9)
                Pmax = PV_meas[(PV_meas['Element_Name'] == device) & 
                               (PV_meas['Measured_Variable'] == 'PF')]['Installed Power'].values.item()
                category = PV_meas[(PV_meas['Element_Name'] == device) & 
                                   (PV_meas['Measured_Variable'] == 'PF')]['Category'].values.item()
                ib_value = PV_meas[(PV_meas['Element_Name'] == device) & 
                                   (PV_meas['Measured_Variable'] == 'Ib')]['Value'].values.item()

                # Print results to the console
                print(f'{device}: Frequency = {frequency} Hz, Voltage = {voltage} V, '
                      f'P = {power} kW, Q = {reactive_power} kVAr, PF = {power_factor}, T = {timestamp}')

                # Write PV measurements to CSV.
                # The CSV columns are:
                # Device, Installed Power, Category, Frequency, Vout (V),
                # Pout (kW), Qout (kVAr), Power Factor, Timestamp, I1, I2, I3, V12, V23, V31, PTOT, QTOT
                with open(measurement_file, 'a') as f:
                    f.write(f'{device},{Pmax},{category},{frequency},{voltage},{power},{reactive_power},{power_factor},{timestamp}\n')

                # Append current cycle measurements to temporary lists
                current_vb.append(voltage)
                current_prt.append(power)
                current_qrt.append(reactive_power)
                
            else:
                # Process TRIAD measurements
                triad_data = PV_meas[PV_meas['Element_Name'] == 'TRIAD']
                # Extract the I and V values as well as PTOT and QTOT
                I_values = triad_data.loc[triad_data['Measured_Variable'].isin(['I1', 'I2', 'I3']), 'Value'].values
                V_values = triad_data.loc[triad_data['Measured_Variable'].isin(['V12', 'V23', 'V31']), 'Value'].values
                PTOT_values = triad_data.loc[triad_data['Measured_Variable'] == 'PTOT', 'Value'].values
                QTOT_values = triad_data.loc[triad_data['Measured_Variable'] == 'QTOT', 'Value'].values
                
                mean_voltage = np.nanmean(V_values) if len(V_values) > 0 else np.nan
                mean_current = np.nanmean(I_values) if len(I_values) > 0 else np.nan
                PTOT_val = PTOT_values[0] if len(PTOT_values) > 0 else np.nan
                QTOT_val = QTOT_values[0] if len(QTOT_values) > 0 else np.nan
                
                I1_val = I_values[0] if len(I_values) > 0 else np.nan
                I2_val = I_values[1] if len(I_values) > 1 else np.nan
                I3_val = I_values[2] if len(I_values) > 2 else np.nan
                V12_val = V_values[0] if len(V_values) > 0 else np.nan
                V23_val = V_values[1] if len(V_values) > 1 else np.nan
                V31_val = V_values[2] if len(V_values) > 2 else np.nan
                
                # Define a timestamp for TRIAD (use current time or a measurement timestamp if available)
                triad_timestamp = datetime.now()

                # Write TRIAD measurements to CSV.
                # For TRIAD, leave Installed Power, Category, Frequency, and Power Factor empty.
                with open(measurement_file, 'a') as f:
                    f.write(f'TRIAD,,,,{mean_voltage},{PTOT_val},{QTOT_val},,{triad_timestamp},'
                            f'{I1_val},{I2_val},{I3_val},{V12_val},{V23_val},{V31_val},{PTOT_val},{QTOT_val}\n')
                
                # Save TRIAD values in the dictionary to return
                triad_values = {
                    'mean_voltage': mean_voltage,
                    'mean_current': mean_current,
                    'PTOT_val': PTOT_val,
                    'QTOT_val': QTOT_val,
                    'I1': I1_val,
                    'I2': I2_val,
                    'I3': I3_val,
                    'V12': V12_val,
                    'V23': V23_val,
                    'V31': V31_val,
                    'timestamp': triad_timestamp
                }
                
        except Exception as e:
            logging.error("Error during measurement processing for %s: %s", device, e)

    # Convert the PV temporary lists to NumPy arrays
    vb_array = np.array(current_vb)
    prt_array = np.array(current_prt)
    qrt_array = np.array(current_qrt)
    
    return vb_array, prt_array, qrt_array, triad_values

if __name__ == "__main__":
    server = 'localhost\\SQLEXPRESS'
    database = 'MSG-PV'
    conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=True;'
    
    try:
        connection = pyodbc.connect(conn_str)
        cursor = connection.cursor()
        logging.info("Connected to SQL Server.")

        filepath_iec_tags = 'C:\\Users\\stdim\\IEC104_Tags.xlsx'
        PV_meas_config = pd.read_excel(filepath_iec_tags, sheet_name='T13')

        PV_names = ['PV1', 'PV2', 'PV3', 'PV4', 'PV5', 'TRIAD']
        measurement_file = 'extracted_measurements.csv'

        # Ensure CSV file exists with the proper header
        if not os.path.exists(measurement_file):
            pd.DataFrame(columns=['Device', 'Installed Power', 'Category', 'Frequency', 'Vout (V)', 
                                  'Pout (kW)', 'Qout (kVAr)', 'Power Factor', 'Timestamp',
                                  'I1', 'I2', 'I3', 'V12', 'V23', 'V31', 'PTOT', 'QTOT']).to_csv(measurement_file, index=False)

        vb_array, prt_array, qrt_array, triad_values = get_dynamic_measurements(cursor, PV_meas_config, PV_names, measurement_file)

        print("Voltage array:", vb_array)
        print("Active Power array:", prt_array)
        print("Reactive Power array:", qrt_array)
        if triad_values:
            print("TRIAD measurements:", triad_values)

    except Exception as e:
        logging.error("An error occurred: %s", e)
    
    finally:
        if 'connection' in locals():
            connection.close()
            logging.info("Database connection closed.")
