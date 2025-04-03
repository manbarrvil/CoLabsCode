import pandas as pd
import numpy as np

def process_measurements(pseudo_measurement_filepath, pseudo_measurement_sheet_name, 
                         tag_correspondence_filepath, tag_correspondence_sheet_name, 
                         Pmes, Qmes, Vmes, hashmap_names, hashmap_reduction, 
                         meas_array, slack_bus):
    
    # Constructing required arrays from meas_array
    v_array = [meas_array[i] for i in [2, 12, 22, 32, 42]]
    p_array = [meas_array[i] for i in [3, 13, 23, 33, 43]]
    q_array = [meas_array[i] for i in [4, 14, 24, 34, 44]]
    feeder_V = np.mean([meas_array[i] for i in [63, 64, 65]])
    feeder_P = meas_array[66]
    feeder_Q = meas_array[67]
    
    # Read measurements from the specified sheet of the measurement file
    excel_data = pd.read_excel(pseudo_measurement_filepath, 
                               sheet_name=pseudo_measurement_sheet_name, 
                               usecols="B:E", skiprows=1, nrows=4, header=None)
    excel_data.columns = ['name', 'v_pu', 'p_mw', 'q_mvar']

    # Process measurement data from excel_data
    for index, row in excel_data.iterrows():
        pv_name = row['name']
        p_measurement = row['p_mw']
        q_measurement = row['q_mvar']
        v_measurement = row['v_pu']
        
        bus_index = hashmap_names[pv_name]
        bus_index_real = hashmap_reduction[bus_index]
        Pmes[bus_index_real] = -p_measurement
        Qmes[bus_index_real] = -q_measurement
        Vmes[bus_index_real] = v_measurement

    # Now load tag_data and process each row using the provided arrays
    tag_data = pd.read_excel(tag_correspondence_filepath, 
                             sheet_name=tag_correspondence_sheet_name, 
                             usecols="B:E", skiprows=1, nrows=5, header=None)
    tag_data.columns = ['tag', 'name', 'installed_power', 'node']

    for idx, row in tag_data.iterrows():
        # Get the node name from tag_data
        node_name = row['node']
        # Find the bus_index_real for this node name
        bus_index = hashmap_names[node_name]
        bus_index_real = hashmap_reduction[bus_index]
        # Populate the measurements from the provided arrays using the row index
        Pmes[bus_index_real] = -p_array[idx]*0.001
        Qmes[bus_index_real] = q_array[idx]*0.001
        Vmes[bus_index_real] = v_array[idx]/231

    Pmes[slack_bus]=-feeder_P*0.001
    Qmes[slack_bus]=-feeder_Q*0.001
    Vmes[slack_bus]=feeder_V/20e3
    
    return Pmes, Qmes, Vmes