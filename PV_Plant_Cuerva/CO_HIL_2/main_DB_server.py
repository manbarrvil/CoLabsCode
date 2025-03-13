# -*- coding: utf-8 -*-
'''Data base code'''
from datetime import datetime, timezone
import time
import matplotlib.pyplot as plt
import json
import sys

# Add the directory containing the script or function to sys.path
sys.path.append('C:/workspace/CoLabsCode/PV_Plant_Cuerva/fcns')

# Nimport your function
from fcn_read_MB_client_POI import read_elec_POI
from fcn_read_MB_client_SS1 import read_elec_SS1
from fcn_read_MB_client_SS2 import read_elec_SS2
from fcn_write_DB_CSL_BROKER_INPUT import write_DB_CSL_BROKER_INPUT

# IP addresses from the PLCs server
IP = "192.168.5.15"
IP1 = "192.168.1.10"
IP2 = "192.168.2.10"

if __name__ == '__main__':

    latency_global=[]
    try:
        while True:
            
            '''Modbus client reading from servers'''
            
            # Modbus Client POI
            # Tic: Init timer
            tic_read_elec_POI = time.time()
            POI_Va, POI_Vb, POI_Vc, f, POI_P, POI_Q, POI_Ia, POI_Ib, POI_Ic, POI_In, POI_U12, POI_U23, POI_U31, POI_U1, POI_U2, POI_U3 = read_elec_POI(IP)
            # Toc: End Timer
            toc_read_elec_POI = time.time()
            # Print execution time
            print(f"Execution time read_elec_POI: {(toc_read_elec_POI - tic_read_elec_POI) * 1000:.2f} ms")
            
            # Modbus Client SS1
            tic_read_elec_SS1 = time.time()
            CT1_Vab, CT1_Vbc, CT1_Vca, CT1_Ia, CT1_Ib, CT1_Ic, CT1_P, CT1_Q, CT1_P_ref, CT1_Q_ref = read_elec_SS1(IP1)
            # Toc: End Timer
            toc_read_elec_SS1 = time.time()
            # Print execution time
            print(f"Execution time read_elec_SS1: {(toc_read_elec_SS1 - tic_read_elec_SS1) * 1000:.2f} ms")
            
            # Modbus Client SS2
            # Tic: Init timer
            tic_read_elec_SS2 = time.time()
            CT2_Vab, CT2_Vbc, CT2_Vca, CT2_Ia, CT2_Ib, CT2_Ic, CT2_P, CT2_Q, CT2_P_ref, CT2_Q_ref = read_elec_SS2(IP2)
            # Toc: End Timer
            toc_read_elec_SS2 = time.time()
            # Print execution time
            print(f"Execution time read_elec_SS2: {(toc_read_elec_SS2 - tic_read_elec_SS2) * 1000:.2f} ms")
            
            
            t = datetime.now(timezone.utc)
                        
            '''Writing into the data base with the data read from Modbus''' 
           
            # Writing into the table DB_CSL_BROKER_INPUT of the DB server DB_CSL_BROKER the data from POI, SS1 and SS2 
            # Tic: Init timer
            tic_read_elec_DB = time.time()
            write_DB_CSL_BROKER_INPUT(t, POI_Va, POI_Vb, POI_Vc, f, POI_P, POI_Q, POI_Ia, POI_Ib, POI_Ic, POI_In, POI_U12, POI_U23, POI_U31, POI_U1, POI_U2, POI_U3, 
                                      CT1_Vab, CT1_Vbc, CT1_Vca, CT1_Ia, CT1_Ib, CT1_Ic, CT1_P, CT1_Q, CT1_P_ref, CT1_Q_ref, 
                                      CT2_Vab, CT2_Vbc, CT2_Vca, CT2_Ia, CT2_Ib, CT2_Ic, CT2_P, CT2_Q, CT2_P_ref, CT2_Q_ref)
            # Toc: End Timer
            toc_read_elec_DB = time.time()
            # Print execution time
            print(f"Execution time write_DB_CSL_BROKER_INPUT: {(toc_read_elec_DB - tic_read_elec_POI) * 1000:.2f} ms")
            
            latency_global.append(toc_read_elec_DB - tic_read_elec_POI)
            
            print("Filling the DB_CSL_BROKER_INPUT table with Modbus TCP/IP measurements...")
            

            #time.sleep(1)


    except KeyboardInterrupt:
        print("End of connection...")
        plt.plot(latency_global)
        plt.title("Latency")
        with open("data.json", "w") as file:
            json.dump(latency_global, file)
        

