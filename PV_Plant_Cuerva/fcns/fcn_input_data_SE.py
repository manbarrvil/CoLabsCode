import numpy as np

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
            Lines = [{'id': 1,  'From': 'Nodo 1',  'To': 'Nodo 2',  'R': 0.7586/Zbase, 'X': 2.5565/Zbase, 'B': 0 , 'Transformer': False, 'rt': 1},  
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