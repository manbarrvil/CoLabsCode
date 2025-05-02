# -*- coding: utf-8 -*-
'''Data base code'''
from datetime import datetime, timezone
import time
import matplotlib.pyplot as plt
import json
import sys
import psycopg2


# Add the directory containing the script or function to sys.path
sys.path.append('C:/workspace/CoLabsCode/PV_Plant_Cuerva/fcns')

# Nimport your function
from fcn_read_MB_client_POI import read_elec_POI
from fcn_read_MB_client_SS1 import read_elec_SS1
from fcn_read_MB_client_SS2 import read_elec_SS2
from fcn_write_DB_CSL_BROKER_INPUT import write_DB_CSL_BROKER_INPUT
from fcn_generic_modbus_client import client_Modbus
from fcn_generic_write_DB import write_DB

# Conexion con la base de datos del SCADA
conexion = psycopg2.connect(database="DB_CSL_BROKER", user="postgres", password="postgres")

# Cargar el fichero JSON del cliente de Modbus
with open('modbus_server_test_main.json', 'r') as file:
    data_json = json.load(file)

ident_emec_id_POI = "poi" #Select "poi", "inv1", "inv2"
ident_emec_id_SS1 = "inv1" 
ident_emec_id_SS2 = "inv2" 

if __name__ == '__main__':

    latency_global=[]
    try:
        while True:
            
            '''Modbus client reading from servers'''
            
            # Modbus Client POI
            # Tic: Init timer
            tic_read_elec_POI = time.time()
            dict_POI = client_Modbus(ident_emec_id_POI, data_json)
            # print(dict_POI, '\n')
            meas_POI = [subdiccionario["value"] for subdiccionario in dict_POI.values()]
            # Toc: End Timer
            toc_read_elec_POI = time.time()
            # Print execution time
            print(f"Execution time read_elec_POI: {(toc_read_elec_POI - tic_read_elec_POI) * 1000:.2f} ms")
            
            # Modbus Client SS1
            tic_read_elec_SS1 = time.time()
            dict_SS1 = client_Modbus(ident_emec_id_SS1, data_json)
            # print(dict_SS1, '\n')
            meas_SS1 = [subdiccionario["value"] for subdiccionario in dict_SS1.values()]
            # Toc: End Timer
            toc_read_elec_SS1 = time.time()
            # Print execution time
            print(f"Execution time read_elec_SS1: {(toc_read_elec_SS1 - tic_read_elec_SS1) * 1000:.2f} ms")
            
            # Modbus Client SS2
            # Tic: Init timer
            tic_read_elec_SS2 = time.time()
            dict_SS2 = client_Modbus(ident_emec_id_SS2, data_json)
            # print(dict_SS2, '\n')
            meas_SS2 = [subdiccionario["value"] for subdiccionario in dict_SS2.values()]
            # Toc: End Timer
            toc_read_elec_SS2 = time.time()
            # Print execution time
            print(f"Execution time read_elec_SS2: {(toc_read_elec_SS2 - tic_read_elec_SS2) * 1000:.2f} ms")
            
        
            t = datetime.now(timezone.utc)
                        
            '''Writing into the data base with the data read from Modbus''' 
           
            # Writing into the table DB_CSL_BROKER_INPUT of the DB server DB_CSL_BROKER the data from POI, SS1 and SS2 
            # Tic: Init timer
            tic_write_DB_CSL_BROKER_INPUT = time.time()
            # write_DB_CSL_BROKER_INPUT(t, meas_POI[0], meas_POI[1], meas_POI[2], meas_POI[3], meas_POI[4], meas_POI[5], meas_POI[6], meas_POI[7], meas_POI[8], meas_POI[9], meas_POI[0], meas_POI[1], meas_POI[2], meas_POI[10], meas_POI[11], meas_POI[12], 
            #                 meas_SS1[0], meas_SS1[1], meas_SS1[2], meas_SS1[3], meas_SS1[4], meas_SS1[5], meas_SS1[6], meas_SS1[7], meas_SS1[8], meas_SS1[9], 
            #                 meas_SS2[0], meas_SS2[1], meas_SS2[2], meas_SS2[3], meas_SS2[4], meas_SS2[5], meas_SS2[6], meas_SS2[7], meas_SS2[8], meas_SS2[9],conexion)
            write_DB(t, meas_POI[0], meas_POI[1], meas_POI[2], meas_POI[3], meas_POI[4], meas_POI[5], meas_POI[6], meas_POI[7], meas_POI[8], meas_POI[9], meas_POI[10], meas_POI[11], meas_POI[12], 
                meas_SS1[0], meas_SS1[1], meas_SS1[2], meas_SS1[3], meas_SS1[4], meas_SS1[5], meas_SS1[6], meas_SS1[7], meas_SS1[8], meas_SS1[9], 
                meas_SS2[0], meas_SS2[1], meas_SS2[2], meas_SS2[3], meas_SS2[4], meas_SS2[5], meas_SS2[6], meas_SS2[7], meas_SS2[8], meas_SS2[9],conexion,data_json)
            # Toc: End Timer
            toc_write_DB_CSL_BROKER_INPUT = time.time()
            # Print execution time
            print(f"Execution time write_DB_CSL_BROKER_INPUT: {(toc_write_DB_CSL_BROKER_INPUT - tic_write_DB_CSL_BROKER_INPUT) * 1000:.2f} ms")
            print(f"Execution time DB server: {(toc_write_DB_CSL_BROKER_INPUT - tic_read_elec_POI) * 1000:.2f} ms")
            latency_global.append(toc_write_DB_CSL_BROKER_INPUT - tic_read_elec_POI)
            
            print("Filling the DB_CSL_BROKER_INPUT table with Modbus TCP/IP measurements...")
            meas_POI = []
            meas_SS1 = []
            meas_SS2 = []

    except KeyboardInterrupt:
        conexion.close()
        print("End of connection...")
        plt.plot(latency_global)
        plt.title("Latency")
        with open("latency_DB.json", "w") as file:
            json.dump(latency_global, file)
        

