#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np

def process_measurements(measurement_filepath, measurement_sheet_name, Pmes, Qmes, Vmes, hashmap_names, hashmap_reduction):
    # Read measurements from the specified sheet of the measurement file
    excel_data = pd.read_excel(measurement_filepath, sheet_name=measurement_sheet_name, usecols="B:E", skiprows=1, nrows=17, header=None)
    excel_data.columns = ['name', 'v_pu', 'p_mw', 'q_mvar']

    for index, row in excel_data.iterrows():
        pv_name = row['name']
        p_measurement = row['p_mw']
        q_measurement = row['q_mvar']
        v_measurement = row['v_pu']
        
        # Find the corresponding real_index in net_sgen_updated
        bus_index=hashmap_names[pv_name]
        bus_index_real=hashmap_reduction[bus_index]
        Pmes[bus_index_real]=-p_measurement
        Qmes[bus_index_real]=-q_measurement
        Vmes[bus_index_real]=v_measurement

    return Pmes, Qmes, Vmes



