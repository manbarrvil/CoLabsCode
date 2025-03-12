'''Code of the State Estimator'''
#https://quike.it/es/como-configurar-acceso-remoto-postgresql/#elementor-toc__heading-anchor-5

from datetime import datetime, timezone
import lib
import numpy as np
import time
import psycopg2


db_host = '172.17.3.239'  # Dirección del servidor remoto de PostgreSQL
db_port = 5432  # Puerto del servidor PostgreSQL (por defecto es 5432)
db_user = 'postgres'  # Nombre de usuario para la base de datos
db_password = 'postgres'  # Contraseña para la base de datos
db_name = 'DB_CSL_BROKER'  # Nombre de la base de datos       
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

def input_data_SE(V_POI_DB, V_SS1_DB, V_SS2_DB, P_POI_DB, Q_POI_DB, P_CT1_DB, Q_CT1_DB, P_CT2_DB, Q_CT2_DB):
            '''Son los datos de entrada al estimador de estados'''
            # Definir de forma adecuada las magnitudes base
            Sbase = 5.7e6
            Ubase = 20.0e3
            Zbase = (Ubase**2)/Sbase
        
            # Por unidad
            V_POI_pu = V_POI_DB/Ubase
            P_POI_pu = P_POI_DB/Sbase
            Q_POI_pu = Q_POI_DB/Sbase
            
            V_SS1_pu = V_SS1_DB/Ubase
            P_CT1_pu = P_CT1_DB/Sbase
            Q_CT1_pu = Q_CT1_DB/Sbase
            
            V_SS2_pu = V_SS2_DB/Ubase
            P_CT2_pu = P_CT2_DB/Sbase
            Q_CT2_pu = Q_CT2_DB/Sbase
            
            # Nodos - Hay que darle id, nombre y decir si hay un elemento shunt
            Nodes = [{'id': 1, 'name': 'Nodo 1', 'B': 0},
                      {'id': 2, 'name': 'Nodo 2', 'B': 0},
                      {'id': 3, 'name': 'Nodo 3', 'B': 0},
                      {'id': 4, 'name': 'Nodo 4', 'B': 0}]
        
            # Lines -> B es la mitad de la susceptancia (la que hay en cada pata)
            # La conexión con los nodos se indica por el "name" y no por el "id"
            Lines = [{'id': 1,  'From': 'Nodo 1',  'To': 'Nodo 2',  'R': 0.7586/Zbase, 'X': 2.5565/Zbase, 'B': 0 , 'Transformer': False, 'rt': 1},  
                      {'id': 2,  'From': 'Nodo 2',  'To': 'Nodo 3',  'R': 0.206*0.153/Zbase, 'X': 0.115*0.153/Zbase, 'B': 0.235e-6*2*np.pi*50*0.153/2*Zbase , 'Transformer': False, 'rt': 1},
                      {'id': 3,  'From': 'Nodo 3',  'To': 'Nodo 4',  'R': 0.206*0.613/Zbase, 'X': 0.115*0.613/Zbase, 'B': 0.235e-6*2*np.pi*50*0.613/2*Zbase , 'Transformer': False, 'rt': 1}]
        
            # Measurements
            # Se indica el nodo o la línea por su "id"!
            Meas = [{'id': 1, 'node': 2,    'line': None, 'type': 'U', 'value': V_POI_pu,   'std': 0.008},
                    {'id': 2, 'node': None, 'line': -1,   'type': 'P', 'value': P_POI_pu,   'std': 0.008}, # Flujo de potencia de 1 a 2 medido en 2, en OPAL-RT el flujo esta medido en 2 pero de 2 a 1
                    {'id': 3, 'node': None, 'line': -1,   'type': 'Q', 'value': Q_POI_pu,   'std': 0.008},
                    {'id': 4, 'node': 4,    'line': None, 'type': 'P', 'value': P_CT1_pu,   'std': 0.008},
                    {'id': 5, 'node': 4,    'line': None, 'type': 'Q', 'value': Q_CT1_pu,   'std': 0.008},
                    {'id': 6, 'node': 3,    'line': None, 'type': 'P', 'value': P_CT2_pu,   'std': 0.008},
                    {'id': 7, 'node': 3,    'line': None, 'type': 'Q', 'value': Q_CT2_pu,   'std': 0.008},
                    {'id': 8, 'node': 1,    'line': None, 'type': 'U', 'value': 1,          'std': 0.008},
                    {'id': 9, 'node': 3,    'line': None, 'type': 'U', 'value': V_SS2_pu,   'std': 0.008},
                    {'id': 9, 'node': 4,    'line': None, 'type': 'U', 'value': V_SS1_pu,   'std': 0.008}]
            return Nodes, Lines, Meas
        
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


    try:
        while True:
            
            t = datetime.now(timezone.utc)
            
            # Lectura de la tabla DB_CSL_BROKER_INPUT para el estimador
            V_POI_DB, V_SS1_DB, V_SS2_DB, P_POI_DB, Q_POI_DB, P_CT1_DB, Q_CT1_DB, P_CT2_DB, Q_CT2_DB = read_DB_CSL_BROKER_INPUT(db_host,db_port,db_user,db_password,db_name)
            
            # Parametros de entrada al estimador
            Nodes, Lines, Meas = input_data_SE(V_POI_DB, V_SS1_DB, V_SS2_DB, P_POI_DB, Q_POI_DB, P_CT1_DB, Q_CT1_DB, P_CT2_DB, Q_CT2_DB)
            
            '''EJECUCION DE ESTIMADOR'''
            # Si se definen restricciones, al menos, hay que detallar: 'id', 'node', 'line', 'type', 'value' del mismo modo que se hizo con las medidas
            Cons =[]
        
            # Se contruye el objeto red
            net = lib.grid(Nodes, Lines, Meas, Cons)
        
            # # Se resuelve la estimación de estado utilizando WLS
            # Results_WLS = net.state_estimation(tol = 1e-4, niter = 50, Huber = False, lmb = None, rn = True)  
        
            # Se resuelve la estimación de estado utilizando Huber
            Results_Huber = net.state_estimation(tol = 1e-4, 
                                                niter = 50, 
                                                Huber = True, 
                                                lmb = 3, 
                                                rn = False)
        
            # Sacamos resultados
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
            
            write_DB_CSL_BROKER_OUTPUT(t, V_POI_EST, V_SS1_EST, V_SS2_EST, P_SS1_SS2, P_SS2_POI, P_POI_POI, Q_SS1_SS2, Q_SS2_POI, Q_POI_POI,db_host,db_port,db_user,db_password,db_name)
            time.sleep(1)


    except KeyboardInterrupt:
        print("Fin de la conexion...")

