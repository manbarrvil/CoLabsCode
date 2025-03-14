'''Code of the State Estimator'''

from datetime import datetime, timezone
import lib
import time
import matplotlib.pyplot as plt
import json
import psycopg2


import sys

# Add the directory containing the script or function to sys.path
sys.path.append('C:/workspace/CoLabsCode/PV_Plant_Cuerva/fcns')

# Nimport your function
from fcn_read_DB_CSL_BROKER_INPUT import read_DB_CSL_BROKER_INPUT
from fcn_input_data_SE import input_data_SE
from fcn_write_DB_CSL_BROKER_OUTPUT import write_DB_CSL_BROKER_OUTPUT


db_host = '172.17.3.239'  # Address of the remote PostgreSQL serverQL
db_port = 5432  # PostgreSQL server port (default is 5432)
db_user = 'postgres'  # Username for the database
db_password = 'postgres'  # Password for the database
db_name = 'DB_CSL_BROKER'  # name for the databases   

conexion = psycopg2.connect(
    host=db_host,
    port=db_port,
    user=db_user,
    password=db_password,
    dbname=db_name
)

if __name__ == '__main__':

    latency_global=[]
    
    try:
        while True:
            
            
            t = datetime.now(timezone.utc)
            # Tic: Init timer
            tic_read_DB_CSL_BROKER_INPUT = time.time()
            # Readin from the remote data base
            V_POI_DB, V_SS1_DB, V_SS2_DB, P_POI_DB, Q_POI_DB, P_CT1_DB, Q_CT1_DB, P_CT2_DB, Q_CT2_DB = read_DB_CSL_BROKER_INPUT(db_host,db_port,db_user,db_password,db_name,conexion)
            # Toc: End Timer
            toc_read_DB_CSL_BROKER_INPUT = time.time()
            # Print execution time
            print(f"Execution time read_DB_CSL_BROKER_INPUT: {(toc_read_DB_CSL_BROKER_INPUT - tic_read_DB_CSL_BROKER_INPUT) * 1000:.2f} ms")
            
            # Tic: Init timer
            tic_state_estimation = time.time()
            # Parametros de entrada al estimador
            Nodes, Lines, Meas = input_data_SE(V_POI_DB, V_SS1_DB, V_SS2_DB, P_POI_DB, Q_POI_DB, P_CT1_DB, Q_CT1_DB, P_CT2_DB, Q_CT2_DB)
            
            '''STATE ESTIMATOR EXECUTION'''
            # If restrictions are defined, at least, the following must be detailed: 'id', 'node', 'line', 'type', 'value' in the same way as was done with the measures
            Cons =[]
        
            # The network object is built
            net = lib.grid(Nodes, Lines, Meas, Cons)
        
            # # State estimation is solved using WLS
            # Results_WLS = net.state_estimation(tol = 1e-4, niter = 50, Huber = False, lmb = None, rn = True)  
        
            # The state estimate is solved using Huber
            Results_Huber = net.state_estimation(tol = 1e-4, 
                                                niter = 50, 
                                                Huber = True, 
                                                lmb = 3, 
                                                rn = False)
        
            # Results
            tensiones = [node.V for node in net.nodes]
            angulos = [node.theta for node in net.nodes]
            lab_r = net.lab_results()
            
            Sbase = 5.7e6
            Ubase = 20.0e3
            
            Tensiones = lab_r['U']
            Intensidades = lab_r['Iji']
            Potencias = lab_r['Pji']
            Potencias_reac = lab_r['Qji']
            
            V_POI_EST = Tensiones[1]*Ubase
            V_SS1_EST = Tensiones[3]*Ubase
            V_SS2_EST = Tensiones[2]*Ubase
            
            P_SS1_SS2 = Potencias[2]*Sbase
            P_SS2_POI = Potencias[1]*Sbase
            P_POI_POI = Potencias[0]*Sbase
            
            
            Q_SS1_SS2 = Potencias_reac[2]*Sbase
            Q_SS2_POI = Potencias_reac[1]*Sbase
            Q_POI_POI = Potencias_reac[0]*Sbase
            
            # Toc: End Timer
            toc_state_estimation = time.time()
            # Print execution time
            print(f"Execution time state_estimation: {(toc_state_estimation - tic_state_estimation) * 1000:.2f} ms")
            
            # Tic: Init timer
            tic_write_DB_CSL_BROKER_OUTPUT = time.time()
            write_DB_CSL_BROKER_OUTPUT(t, V_POI_EST, V_SS1_EST, V_SS2_EST, P_SS1_SS2, P_SS2_POI, P_POI_POI, Q_SS1_SS2, Q_SS2_POI, Q_POI_POI,db_host,db_port,db_user,db_password,db_name,conexion)
            #time.sleep(1)
            # Toc: End Timer
            toc_write_DB_CSL_BROKER_OUTPUT = time.time()
            # Print execution time
            print(f"Execution time write_DB_CSL_BROKER_OUTPUT: {(toc_write_DB_CSL_BROKER_OUTPUT - tic_write_DB_CSL_BROKER_OUTPUT) * 1000:.2f} ms")

            latency_global.append(toc_write_DB_CSL_BROKER_OUTPUT - tic_read_DB_CSL_BROKER_INPUT)
    except KeyboardInterrupt:
        conexion.close()
        print("Fin de la conexion...")
        plt.plot(latency_global)
        plt.title("Latency")
        with open("latency_SE.json", "w") as file:
            json.dump(latency_global, file)

