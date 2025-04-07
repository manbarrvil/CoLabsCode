'''Code of the State Estimator'''

from datetime import datetime, timezone
import lib
import numpy as np
import time
import psycopg2
import matplotlib.pyplot as plt
import json


db_host = '172.17.3.239'  # Address of the remote PostgreSQL serverQL
db_port = 5432  # PostgreSQL server port (default is 5432)
db_user = 'postgres'  # Username for the database
db_password = 'postgres'  # Password for the database
db_name = 'DB_CSL_BROKER'  # name for the databases   

#Function for reading from the remote data base    
def read_DB_CSL_BROKER_INPUT(db_host,db_port,db_user,db_password,db_name):

    conexion2 = psycopg2.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        dbname=db_name
    )
    cursor2=conexion2.cursor()
    cursor2.execute("select Date_Time, POI_Va,POI_P,POI_Q,CT1_Vab,CT1_P,CT1_Q,CT2_Vab,CT2_P,CT2_Q from DB_CSL_BROKER_INPUT")
    for data in cursor2:
       # Date_Time_DB = data[0]
        V_POI_DB = data[1]
        P_POI_DB = data[2]
        Q_POI_DB = data[3]
        V_CT1_DB = data[4]
        P_CT1_DB = data[5]
        Q_CT1_DB = data[6]
        V_CT2_DB = data[7]
        P_CT2_DB = data[8]
        Q_CT2_DB = data[9]
    conexion2.close()

            
    return V_POI_DB, V_CT1_DB, V_CT2_DB, P_POI_DB, Q_POI_DB, P_CT1_DB, Q_CT1_DB, P_CT2_DB, Q_CT2_DB

#Function defining the input to the state estimator_ topology and measurements 
def input_data_SE(V_POI_DB, V_SS1_DB, V_SS2_DB, P_POI_DB, Q_POI_DB, P_CT1_DB, Q_CT1_DB, P_CT2_DB, Q_CT2_DB):
            '''Input data of the state estimator'''
            # Base value of the systems
            Sbase = 5.7e6
            Ubase = 20.0e3
            Zbase = (Ubase**2)/Sbase
        
            # Conversion to pu values
            V_POI_pu = V_POI_DB/Ubase
            P_POI_pu = P_POI_DB/Sbase
            Q_POI_pu = Q_POI_DB/Sbase
            
            V_SS1_pu = V_SS1_DB/Ubase
            P_CT1_pu = P_CT1_DB/Sbase
            Q_CT1_pu = Q_CT1_DB/Sbase
            
            V_SS2_pu = V_SS2_DB/Ubase
            P_CT2_pu = P_CT2_DB/Sbase
            Q_CT2_pu = Q_CT2_DB/Sbase
            
            # Nodes - You have to provide an id of the node, name and say if there is a shunt element
            Nodes = [{'id': 1, 'name': 'Nodo 1', 'B': 0},
                      {'id': 2, 'name': 'Nodo 2', 'B': 0},
                      {'id': 3, 'name': 'Nodo 3', 'B': 0},
                      {'id': 4, 'name': 'Nodo 4', 'B': 0}]
        
            # Lines -> B is half the susceptance (the one in each leg o the pi model)
            # The connection to the nodes is indicated by the "name" and not by the "id"
            Lines = [ {'id': 1,  'From': 'Nodo 1',  'To': 'Nodo 2',  'R': 0.7586/Zbase, 'X': 2.5565/Zbase, 'B': 0 , 'Transformer': False, 'rt': 1},  
                      {'id': 2,  'From': 'Nodo 2',  'To': 'Nodo 3',  'R': 0.206*0.153/Zbase, 'X': 0.115*0.153/Zbase, 'B': 0.235e-6*2*np.pi*50*0.153/2*Zbase , 'Transformer': False, 'rt': 1},
                      {'id': 3,  'From': 'Nodo 3',  'To': 'Nodo 4',  'R': 0.206*0.613/Zbase, 'X': 0.115*0.613/Zbase, 'B': 0.235e-6*2*np.pi*50*0.613/2*Zbase , 'Transformer': False, 'rt': 1}]
        
            # Measurements
            # The node or line is indicated by its "id"!
            Meas = [{'id': 1, 'node': 2,    'line': None, 'type': 'U', 'value': V_POI_pu,   'std': 0.008},
                    {'id': 2, 'node': None, 'line': -1,   'type': 'P', 'value': P_POI_pu,   'std': 0.008}, # Power flow from 1 to 2 measured in 2, in OPAL-RT the flow is measured in 2 but from 2 to 1
                    {'id': 3, 'node': None, 'line': -1,   'type': 'Q', 'value': Q_POI_pu,   'std': 0.008},
                    {'id': 4, 'node': 4,    'line': None, 'type': 'P', 'value': P_CT1_pu,   'std': 0.008},
                    {'id': 5, 'node': 4,    'line': None, 'type': 'Q', 'value': Q_CT1_pu,   'std': 0.008},
                    {'id': 6, 'node': 3,    'line': None, 'type': 'P', 'value': P_CT2_pu,   'std': 0.008},
                    {'id': 7, 'node': 3,    'line': None, 'type': 'Q', 'value': Q_CT2_pu,   'std': 0.008},
                    {'id': 8, 'node': 1,    'line': None, 'type': 'U', 'value': 1,          'std': 0.008},
                    {'id': 9, 'node': 3,    'line': None, 'type': 'U', 'value': V_SS2_pu,   'std': 0.008},
                    {'id': 9, 'node': 4,    'line': None, 'type': 'U', 'value': V_SS1_pu,   'std': 0.008}]
            return Nodes, Lines, Meas

#Function for writing into the remote data base        
def write_DB_CSL_BROKER_OUTPUT(t, V_POI_EST, V_SS1_EST, V_SS2_EST, P_SS1_SS2, P_SS2_POI, P_POI_POI, Q_SS1_SS2, Q_SS2_POI, Q_POI_POI,db_host,db_port,db_user,db_password,db_name):
    conexion3 = psycopg2.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        dbname=db_name
    )
    cursor3=conexion3.cursor()
    sql="insert into DB_CSL_BROKER_OUTPUT(Date_Time, V_POI_EST,V_SS1_EST,V_SS2_EST,P_SS1_SS2,P_SS2_POI,P_POI_POI,Q_SS1_SS2,Q_SS2_POI,Q_POI_POI) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    data_ouput=((t,), V_POI_EST, V_SS1_EST, V_SS2_EST, P_SS1_SS2, P_SS2_POI, P_POI_POI, Q_SS1_SS2, Q_SS2_POI, Q_POI_POI)
    cursor3.execute(sql, data_ouput)
    conexion3.commit()
    conexion3.close()


if __name__ == '__main__':

    latency_global=[]
    try:
        while True:
            
            t = datetime.now(timezone.utc)
            # Tic: Init timer
            tic_read_DB_CSL_BROKER_INPUT = time.time()
            # Reading from the remote data base
            V_POI_DB, V_SS1_DB, V_SS2_DB, P_POI_DB, Q_POI_DB, P_CT1_DB, Q_CT1_DB, P_CT2_DB, Q_CT2_DB = read_DB_CSL_BROKER_INPUT(db_host,db_port,db_user,db_password,db_name)
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
            write_DB_CSL_BROKER_OUTPUT(t, V_POI_EST, V_SS1_EST, V_SS2_EST, P_SS1_SS2, P_SS2_POI, P_POI_POI, Q_SS1_SS2, Q_SS2_POI, Q_POI_POI,db_host,db_port,db_user,db_password,db_name)
            #time.sleep(1)
            # Toc: End Timer
            toc_write_DB_CSL_BROKER_OUTPUT = time.time()
            # Print execution time
            print(f"Execution time write_DB_CSL_BROKER_OUTPUT: {(toc_write_DB_CSL_BROKER_OUTPUT - tic_write_DB_CSL_BROKER_OUTPUT) * 1000:.2f} ms")

            latency_global.append(toc_write_DB_CSL_BROKER_OUTPUT - tic_read_DB_CSL_BROKER_INPUT)
    except KeyboardInterrupt:
        print("Fin de la conexion...")
        plt.plot(latency_global)
        plt.title("Latency")
        with open("data.json", "w") as file:
            json.dump(latency_global, file)

