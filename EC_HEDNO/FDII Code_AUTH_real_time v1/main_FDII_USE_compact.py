import time
import pickle
import logging
import pyodbc
import pandas as pd
import numpy as np
from datetime import datetime, timezone
import datetime as dt
import c104
import sys

sys.path.append('C:\workspace\CoLabsCode\EC_HEDNO\fcns')
from fcn_client_104_config import client_104_config

import time
import pickle
import logging
import pandas as pd
import numpy as np
from process_voltage_write_TagArray_Est import process_voltage_write_TagArray_Est

from State_Estimation_generic_function_rt1 import State_Estimation_generic_function
from process_measurements_rt_new import process_measurements
from gamspy import Container, Set, Alias, Parameter, Variable, Equation, Model, Problem, Sum, Sense,math

# Load grid data. Assuming that the topology of the grid will not change in the framework of the WP3 tests, we do not need to extract the grid info
# each time using Pandapower. It can happen once, and then the information to be stored in an appropriate file (e.g., of pickle format). 
with open("extracted_grid_info1.pkl", "rb") as f:
    (num_buses, slack_bus, der_positions_ratings, _, _,
     zero_injection_buses, hashmap_reduction2, hashmap_names2, H_v_full, H_p_full, H_q_full, 
     slack_bus_row_P, slack_bus_row_Q, injection_buses, B, G) = pickle.load(f)
print(hashmap_names2)

##The lines below to be activated if we want to re-extract the grid information 
#data_filepath = "C:\\Users\\stdim\\EC_Network_reduced_merged_final.xlsx"
   
#num_buses, slack_bus, der_positions_ratings, hashmap_names, hashmap_reduction, zero_injection_buses, hashmap_reduction2, hashmap_names2, H_v_full, H_p_full, #H_q_full, slack_bus_row_P, slack_bus_row_Q, injection_buses, adjacency_matrix_buses,  adjacency_matrix_branches, parent_child_adjacency, R, X, Bshunt, Gshunt, S_n = extract_info (data_filepath)  


m=Container()
i = Set(m, "i", description = "network nodes", records = [aux for aux in range(0,num_buses)])
j = Alias(m,"j", alias_with=i)
i2= Set(m,"i2",  description = "network nodes without slack bus/network branches", domain=i, records = [aux for aux in range(0,num_buses) if aux!=slack_bus])
i3= Set(m,"i3",  description = "slack bus", domain=i, records = np.array([slack_bus]))
# Define zero injection buses
if len(zero_injection_buses) > 0:
    i_zero = Set(m, name="i_zero", domain=i, records=[aux for aux in range(num_buses) if aux in zero_injection_buses])
else:
    i_zero = Set(m, name="i_zero", domain=i, is_singleton=True)
    
Bp=Parameter(m,"Bp", domain=[i,j], records=B)
Gp=Parameter(m,"Gp", domain=[i,j], records=G)

std_vector_v = np.ones(num_buses)*0.0016666666666666668
std_vector_p = np.ones(num_buses)*0.005666666666666667
std_vector_q = np.ones(num_buses)*0.013333333333333334

# Define standard deviation parameters
Std_P = Parameter(m, name="Std_P", domain=i, records=std_vector_p)    
Std_Q = Parameter(m, name="Std_Q", domain=i, records=std_vector_q)
Std_V = Parameter(m, name="Std_V", domain=i, records=std_vector_v)


# Initialize measurement positions
mes_positions_p = np.ones(num_buses, dtype=int)
mes_positions_q = np.ones(num_buses, dtype=int)
mes_positions_v = np.ones(num_buses, dtype=int)

mes_positions = np.full(num_buses, 0)
        
for aux in injection_buses:
    mes_positions[aux] = 1

mes_positions_p=mes_positions.copy()
mes_positions_q=mes_positions.copy()
mes_positions_v=mes_positions.copy()

mes_positions_virtual = np.zeros(num_buses, dtype=int)
mes_positions_virtual[zero_injection_buses] = 1
column_rank = (num_buses-1)*2

mes_p=Set(m,name="mes_p",domain=i)
mes_q=Set(m,name="mes_q",domain=i)
mes_v=Set(m,name="mes_v",domain=i)
Pmesp=Parameter(m, name="Pmesp",domain=i)
Qmesp=Parameter(m, name="Qmesp",domain=i)
Vmesp=Parameter(m, name="Vmesp",domain=i)

# Define variables
Jall = Variable(m, name = "Jall", description = "overall deviation")
Vest = Variable(m, name="Vest", domain=i, description="voltage estimates", type="positive")
Pest = Variable(m, name="Pest", domain=i, description="active power estimates")
Qest = Variable(m, name="Qest", domain=i, description="reactive power estimates")
Vest_x = Variable(m, name="Vest_x", domain=i, description="real part of voltage estimate", records=np.ones(num_buses))
Vest_y = Variable(m, name="Vest_y", domain=i, description="imaginary part of voltage estimates", records=np.zeros(num_buses))
Iest_x = Variable(m, name="Iest_x", domain=i, description="real part of current estimates")
Iest_y = Variable(m, name="Iest_y", domain=i, description="imaginary part of current estimates")

Vest.up[i] = 2
Vest.lo[i] = 0.5
Vest_x.up[i]=2
Vest_x.lo[i]=0.5
Vest_y.up[i]=2
Vest_y.lo[i]=0.5

# Set default values for variables

Deviation = Equation(m, name="Deviation")

Real_nodal_current_eq1 = Equation(m, name = "Real_nodal_current_eq1", domain = [i], description = "Equations of the real part of nodal current injections")
Imag_nodal_current_eq1 = Equation(m, name = "Imag_nodal_current_eq1", domain = [i], description = "Equations of the imaginary part of nodal current injections")

Real_nodal_current_eq2 = Equation(m, name = "Real_nodal_current_eq2", domain = [i], description = "Equations of the real part of nodal current injections")
Imag_nodal_current_eq2 = Equation(m, name = "Imag_nodal_current_eq2", domain = [i], description = "Equations of the imaginary part of nodal current injections")

Nodal_active_power_eq = Equation(m, name = "Nodal_active_power", domain = [i], description = "Equations of nodal active power injections")
Nodal_reactive_power_eq = Equation(m, name = "Nodal_reactive_power", domain = [i], description = "Equations of nodal reactive power injections")
Voltage_eq=Equation(m,name="Voltage_eq", domain=[i], description= "Voltage equation")

zero_injection_P=Equation(m,name="zero_injection_P", domain=i)
zero_injection_Q=Equation(m,name="zero_injection_Q", domain=i)

Deviation[...]=Jall==Sum(i.where[mes_p[i]],math.sqr(Pest[i]-Pmesp[i])/math.sqr(Std_P[i]))+Sum(i.where[mes_q[i]],math.sqr(Qest[i]-Qmesp[i])/math.sqr(Std_Q[i]))+Sum(i.where[mes_v[i]],math.sqr(Vest[i]-Vmesp[i])/math.sqr(Std_V[i]))
    
Real_nodal_current_eq1[i].where[i2[i]] = Iest_x[i] == -Sum(j, Gp[i,j]*Vest_x[j] - Bp[i,j]*Vest_y[j])
Imag_nodal_current_eq1[i].where[i2[i]] = Iest_y[i] == -Sum(j, Gp[i,j]*Vest_y[j] + Bp[i,j]*Vest_x[j])

Real_nodal_current_eq2[i].where[i3[i]] = Iest_x[i] == Sum(j, Gp[i,j]*Vest_x[j] - Bp[i,j]*Vest_y[j])
Imag_nodal_current_eq2[i].where[i3[i]] = Iest_y[i] == Sum(j, Gp[i,j]*Vest_y[j] + Bp[i,j]*Vest_x[j])

Nodal_active_power_eq[i] = Pest[i] == (Vest_x[i]*Iest_x[i] + Vest_y[i]*Iest_y[i])
Nodal_reactive_power_eq[i] = Qest[i] == (-Vest_x[i]*Iest_y[i] + Vest_y[i]*Iest_x[i])

Voltage_eq[i] = Vest[i]== math.sqrt(math.sqr(Vest_x[i]) + math.sqr(Vest_y[i]))
    
zero_injection_P[i].where[i_zero[i]]=Pest[i]==0
zero_injection_Q[i].where[i_zero[i]]=Qest[i]==0

estimation = Model(m, "estimation", equations=m.getEquations(), problem=Problem.NLP, sense=Sense.MIN, objective=Jall)


# ------------------------------------------------------------------
# Set up a state estimation accumulator dictionary.
# Keys are the state estimation parameters and values are lists
# containing the value from each cycle.
# ------------------------------------------------------------------
se_keys = ["Vest_array", "Pest_array", "Qest_array","removed_residuals"]
se_accum = {key: [] for key in se_keys}

# Define the state estimation results CSV file.
# We will write the entire accumulator in a transposed format.
state_estimation_results_file = "state_estimation_results.csv"

def write_state_estimation_csv(accum_dict):
    """
    Write the state estimation accumulator as a CSV file.
    The output CSV will have a header: "Parameter, Cycle 1, Cycle 2, ..."
    and one row per parameter.
    """
    # Determine the number of cycles (assume all lists have the same length)
    num_cycles = len(next(iter(accum_dict.values())))
    header = ["Parameter"] + [f"Cycle {i+1}" for i in range(num_cycles)]
    
    # Build rows: one row per parameter
    rows = []
    for key, values in accum_dict.items():
        # Here, if values are arrays or dataframes, we assume they are already converted
        # to string (e.g., via json.dumps or .to_json) before accumulation.
        row = [key] + values
        rows.append(row)
    
    # Create a DataFrame and write to CSV
    df = pd.DataFrame(rows, columns=header)
    df.to_csv(state_estimation_results_file, index=False)

def client_IEC104():

    PV1_P_ref.read()
    PV1_P_rate.read()
    PV1_FDP.read()
    PV1_Q_ref.read()
    PV1_Q_rate.read()
    PV1_P.read()
    PV1_Q.read()
    PV1_V.read()
    PV1_I.read()
    PV1_F.read()

    PV2_P_ref .read()
    PV2_P_rate.read()
    PV2_FDP   .read()
    PV2_Q_ref .read()
    PV2_Q_rate.read()
    PV2_P     .read()
    PV2_Q     .read()
    PV2_V     .read()
    PV2_I     .read()
    PV2_F     .read()

    PV3_P_ref .read()
    PV3_P_rate.read()
    PV3_FDP   .read()
    PV3_Q_ref .read()
    PV3_Q_rate.read()
    PV3_P     .read()
    PV3_Q     .read()
    PV3_V     .read()
    PV3_I     .read()
    PV3_F     .read()

    PV4_P_ref .read()
    PV4_P_rate.read()
    PV4_FDP   .read()
    PV4_Q_ref .read()
    PV4_Q_rate.read()
    PV4_P     .read()
    PV4_Q     .read()
    PV4_V     .read()
    PV4_I     .read()
    PV4_F     .read()

    PV5_P_ref .read()
    PV5_P_rate.read()
    PV5_FDP   .read()
    PV5_Q_ref .read()
    PV5_Q_rate.read()
    PV5_P     .read()
    PV5_Q     .read()
    PV5_V     .read()
    PV5_I     .read()
    PV5_F     .read()

    PV6_P_ref .read()
    PV6_P_rate.read()
    PV6_FDP   .read()
    PV6_Q_ref .read()
    PV6_Q_rate.read()
    PV6_P     .read()
    PV6_Q     .read()
    PV6_V     .read()
    PV6_I     .read()
    PV6_F     .read()

    PV7_V.read()
    PV7_I.read()
    PV7_F.read()
    PV7_P.read()
    PV7_Q.read()

    PV8_V.read()
    PV8_I.read()
    PV8_F.read()
    PV8_P.read()
    PV8_Q.read()

    PV9_V.read()
    PV9_I.read()
    PV9_F.read()
    PV9_P.read()
    PV9_Q.read()

    POI_Ia .read()
    POI_Ib .read()
    POI_Ic .read()
    POI_Vab.read()
    POI_Vbc.read()
    POI_Vca.read()
    POI_P  .read()
    POI_Q  .read()

    PV1_SET_P     .value = 0.0
    PV1_SET_P_rate.value = 0.0
    PV1_SET_FDP   .value = 1.0
    PV1_SET_Q     .value = 0.0
    PV1_SET_Q_rate.value = 0.0

    PV2_SET_P     .value = 0.0
    PV2_SET_P_rate.value = 0.0
    PV2_SET_FDP   .value = 1.0
    PV2_SET_Q     .value = 0.0
    PV2_SET_Q_rate.value = 0.0

    PV3_SET_P     .value = 0.0
    PV3_SET_P_rate.value = 0.0
    PV3_SET_FDP   .value = 1.0
    PV3_SET_Q     .value = 0.0
    PV3_SET_Q_rate.value = 0.0

    PV4_SET_P     .value = 0.0
    PV4_SET_P_rate.value = 0.0
    PV4_SET_FDP   .value = 1.0
    PV4_SET_Q     .value = 0.0
    PV4_SET_Q_rate.value = 0.0

    PV5_SET_P     .value = 0.0
    PV5_SET_P_rate.value = 0.0
    PV5_SET_FDP   .value = 1.0
    PV5_SET_Q     .value = 0.0
    PV5_SET_Q_rate.value = 0.0

    PV1_SET_P     .transmit(cause=c104.Cot.ACTIVATION)
    PV1_SET_P_rate.transmit(cause=c104.Cot.ACTIVATION)
    PV1_SET_FDP   .transmit(cause=c104.Cot.ACTIVATION)
    PV1_SET_Q     .transmit(cause=c104.Cot.ACTIVATION)
    PV1_SET_Q_rate.transmit(cause=c104.Cot.ACTIVATION)

    PV2_SET_P     .transmit(cause=c104.Cot.ACTIVATION)
    PV2_SET_P_rate.transmit(cause=c104.Cot.ACTIVATION)
    PV2_SET_FDP   .transmit(cause=c104.Cot.ACTIVATION)
    PV2_SET_Q     .transmit(cause=c104.Cot.ACTIVATION)
    PV2_SET_Q_rate.transmit(cause=c104.Cot.ACTIVATION)

    PV3_SET_P     .transmit(cause=c104.Cot.ACTIVATION)
    PV3_SET_P_rate.transmit(cause=c104.Cot.ACTIVATION)
    PV3_SET_FDP   .transmit(cause=c104.Cot.ACTIVATION)
    PV3_SET_Q     .transmit(cause=c104.Cot.ACTIVATION)
    PV3_SET_Q_rate.transmit(cause=c104.Cot.ACTIVATION)

    PV4_SET_P     .transmit(cause=c104.Cot.ACTIVATION)
    PV4_SET_P_rate.transmit(cause=c104.Cot.ACTIVATION)
    PV4_SET_FDP   .transmit(cause=c104.Cot.ACTIVATION)
    PV4_SET_Q     .transmit(cause=c104.Cot.ACTIVATION)
    PV4_SET_Q_rate.transmit(cause=c104.Cot.ACTIVATION)

    PV5_SET_P     .transmit(cause=c104.Cot.ACTIVATION)
    PV5_SET_P_rate.transmit(cause=c104.Cot.ACTIVATION)
    PV5_SET_FDP   .transmit(cause=c104.Cot.ACTIVATION)
    PV5_SET_Q     .transmit(cause=c104.Cot.ACTIVATION)
    PV5_SET_Q_rate.transmit(cause=c104.Cot.ACTIVATION)

    PV1_Read = [PV1_F.value,PV1_I.value,PV1_V.value,PV1_P.value,PV1_Q.value,PV1_P_ref.value,PV1_P_rate.value,PV1_FDP.value,PV1_Q_ref.value,PV1_Q_rate.value]
    PV2_Read = [PV2_F.value,PV2_I.value,PV2_V.value,PV2_P.value,PV2_Q.value,PV2_P_ref.value,PV2_P_rate.value,PV2_FDP.value,PV2_Q_ref.value,PV2_Q_rate.value]
    PV3_Read = [PV3_F.value,PV3_I.value,PV3_V.value,PV3_P.value,PV3_Q.value,PV3_P_ref.value,PV3_P_rate.value,PV3_FDP.value,PV3_Q_ref.value,PV3_Q_rate.value]
    PV4_Read = [PV4_F.value,PV4_I.value,PV4_V.value,PV4_P.value,PV4_Q.value,PV4_P_ref.value,PV4_P_rate.value,PV4_FDP.value,PV4_Q_ref.value,PV4_Q_rate.value]
    PV5_Read = [PV5_F.value,PV5_I.value,PV5_V.value,PV5_P.value,PV5_Q.value,PV5_P_ref.value,PV5_P_rate.value,PV5_FDP.value,PV5_Q_ref.value,PV5_Q_rate.value]
    PV6_Read = [PV6_F.value,PV6_I.value,PV6_V.value,PV6_P.value,PV6_Q.value,PV6_P_ref.value,PV6_P_rate.value,PV6_FDP.value,PV6_Q_ref.value,PV6_Q_rate.value]
    # PV7_Read = [PV7_V.value,PV7_I.value,PV7_F.value,PV7_P.value,PV7_Q.value]
    # PV8_Read = [PV8_V.value,PV8_I.value,PV8_F.value,PV8_P.value,PV8_Q.value]
    # PV9_Read = [PV9_V.value,PV9_I.value,PV9_F.value,PV9_P.value,PV9_Q.value]
    PV7_Read = [PV7_F.value,PV7_I.value,PV7_V.value,PV7_P.value,PV7_Q.value,PV1_P_ref.value,PV1_P_rate.value,PV1_FDP.value,PV1_Q_ref.value,PV1_Q_rate.value]
    PV8_Read = [PV8_F.value,PV8_I.value,PV8_V.value,PV8_P.value,PV8_Q.value,PV1_P_ref.value,PV1_P_rate.value,PV1_FDP.value,PV1_Q_ref.value,PV1_Q_rate.value]
    PV9_Read = [PV9_F.value,PV9_I.value,PV9_V.value,PV9_P.value,PV9_Q.value,PV1_P_ref.value,PV1_P_rate.value,PV1_FDP.value,PV1_Q_ref.value,PV1_Q_rate.value]
    POI_Read = [POI_Ia.value,POI_Ib.value,POI_Ic.value,POI_Vab.value,POI_Vbc.value,POI_Vca.value,POI_P.value,POI_Q.value]

    # PV1_setpoint = [PV1_SET_P.value, PV1_SET_P_rate.value, PV1_SET_FDP.value, PV1_SET_Q.value, PV1_SET_Q_rate.value]
    # PV2_setpoint = [PV2_SET_P.value, PV2_SET_P_rate.value, PV2_SET_FDP.value, PV2_SET_Q.value, PV2_SET_Q_rate.value]
    # PV3_setpoint = [PV3_SET_P.value, PV3_SET_P_rate.value, PV3_SET_FDP.value, PV3_SET_Q.value, PV3_SET_Q_rate.value]
    # PV4_setpoint = [PV4_SET_P.value, PV4_SET_P_rate.value, PV4_SET_FDP.value, PV4_SET_Q.value, PV4_SET_Q_rate.value]
    # PV5_setpoint = [PV5_SET_P.value, PV5_SET_P_rate.value, PV5_SET_FDP.value, PV5_SET_Q.value, PV5_SET_Q_rate.value]

    
    return PV1_Read, PV2_Read, PV3_Read, PV4_Read, PV5_Read, PV6_Read, PV7_Read, PV8_Read, PV9_Read, POI_Read

def write_TagArray_W(connection, t, data_COMM):

    # Inicializar diccionario vacío
    data = {}
    # Inicializar lista de claves vacía
    keys = []
    # Inicializar lista de valores con ceros
    values = data_COMM
    # Crear la lista de claves
    keys.append(f'Tag{0}_Value')
    for i in range(1,len(values)+1):
        keys.append(f'Tag{i}_Name')  # Asignar una clave única para cada valor
        keys.append(f'Tag{i}_Value')  # Asignar una clave única para cada valor

    for i in range(2,len(values)*2+1,2): 
        data[keys[i-1]] = [f'TAG_{int(i/2)}']
        # data[keys[i]] = values[int(i/2-1)] + [random.randint(-1, 1)]
        data[keys[i]] = values[int(i/2-1)] 
        data[keys[0]] = t

    df_combinado = pd.DataFrame(data)
    
    valores = [tuple(row) for row in df_combinado.itertuples(index=False)]
    consulta_insert = f"""
    INSERT INTO TagArray_W ({', '.join(df_combinado.columns)})
    VALUES ({', '.join(['?'] * len(df_combinado.columns))})
    """
    cursor = connection.cursor()
    try:
        cursor.executemany(consulta_insert, valores)
        connection.commit()
    except pyodbc.Error as e:
        print("Error al insertar registros:", e)
    finally:
        cursor.close()

def write_TagArray_Est(connection, t, Vest_array, Pest_array, Qest_array):

    # Inicializar diccionario vacío
    data = {}
    # Inicializar lista de claves vacía
    keys = []
    # Inicializar lista de valores con ceros
    Sb= 1e6/1000
    Vb_LV = 231
    Vb_MV = 20000

    values = pd.concat([Vest_array, Pest_array*Sb, Qest_array*Sb], axis=0)
    values = values.to_numpy().flatten().tolist()
    values = process_voltage_write_TagArray_Est(values)


    # Crear la lista de claves
    keys.append(f'Tag{0}_Value')
    for i in range(1,len(values)+1):
        keys.append(f'Tag{i}_Name')  # Asignar una clave única para cada valor
        keys.append(f'Tag{i}_Value')  # Asignar una clave única para cada valor
 
    data[keys[0]] = t
    for i in range(2,len(values)*2+1,2): 
        data[keys[i-1]] = [f'TAG_{int(i/2)}']
        data[keys[i]] = values[int(i/2-1)]

    df_combinado = pd.DataFrame(data)
    
    valores = [tuple(row) for row in df_combinado.itertuples(index=False)]
    consulta_insert = f"""
    INSERT INTO TagArray_Est ({', '.join(df_combinado.columns)})
    VALUES ({', '.join(['?'] * len(df_combinado.columns))})
    """
    cursor = connection.cursor()
    try:
        cursor.executemany(consulta_insert, valores)
        connection.commit()
    except pyodbc.Error as e:
        print("Error al insertar registros:", e)
    finally:
        cursor.close()

def read_TagArray_W(connection):
    cursor=connection.cursor()
      
    cursor.execute("SELECT TOP 1 Tag1_Value, Tag2_Value, Tag3_Value, Tag4_Value, Tag5_Value, Tag6_Value, Tag7_Value, Tag8_Value, Tag9_Value, Tag10_Value, Tag11_Value, Tag12_Value, Tag13_Value, Tag14_Value, Tag15_Value, Tag16_Value, Tag17_Value, Tag18_Value, Tag19_Value, Tag20_Value, Tag21_Value, Tag22_Value, Tag23_Value, Tag24_Value, Tag25_Value,Tag26_Value, Tag27_Value, Tag28_Value, Tag29_Value, Tag30_Value,Tag31_Value, Tag32_Value, Tag33_Value, Tag34_Value, Tag35_Value,Tag36_Value, Tag37_Value, Tag38_Value, Tag39_Value, Tag40_Value,Tag41_Value, Tag42_Value, Tag43_Value, Tag44_Value, Tag45_Value,Tag46_Value, Tag47_Value, Tag48_Value, Tag49_Value, Tag50_Value,Tag51_Value, Tag52_Value, Tag53_Value, Tag54_Value, Tag55_Value,Tag56_Value, Tag57_Value, Tag58_Value, Tag59_Value, Tag60_Value,Tag61_Value, Tag62_Value, Tag63_Value, Tag64_Value, Tag65_Value, Tag66_Value, Tag67_Value, Tag68_Value, Tag69_Value, Tag70_Value, Tag71_Value, Tag72_Value, Tag73_Value, Tag74_Value, Tag75_Value, Tag76_Value, Tag77_Value, Tag78_Value, Tag79_Value, Tag80_Value, Tag81_Value, Tag82_Value, Tag83_Value, Tag84_Value, Tag85_Value,Tag86_Value, Tag87_Value, Tag88_Value, Tag89_Value, Tag90_Value, Tag91_Value, Tag92_Value, Tag93_Value, Tag94_Value, Tag95_Value,Tag96_Value, Tag97_Value, Tag98_Value FROM MSG_PV.dbo.TagArray_W ORDER BY Tag0_Value DESC")
    
    data_read = cursor.fetchone()
    data_read_DB = list(data_read)  # Convierte la tupla en una lista
    return data_read_DB
        

if __name__ == '__main__':

    connection = pyodbc.connect('DRIVER={SQL Server};'
                                'SERVER=HOSTOPALRT\\SQLEXPRESS02;'
                                'DATABASE=MSG_PV;'
                                'Trusted_Connection=yes;')
    client = c104.Client()
    connection_104 = client.add_connection(ip="192.168.5.3", port=2404, init=c104.Init.ALL)
    station = connection_104.add_station(common_address=1)
    PV1_P_ref, PV1_P_rate, PV1_FDP, PV1_Q_ref, PV1_Q_rate, PV1_P, PV1_Q, PV1_V, PV1_I, PV1_F, PV2_P_ref, PV2_P_rate, PV2_FDP, PV2_Q_ref, PV2_Q_rate, PV2_P, PV2_Q, PV2_V, PV2_I, PV2_F, PV3_P_ref, PV3_P_rate, PV3_FDP, PV3_Q_ref, PV3_Q_rate, PV3_P, PV3_Q, PV3_V, PV3_I, PV3_F, PV4_P_ref, PV4_P_rate, PV4_FDP, PV4_Q_ref, PV4_Q_rate, PV4_P, PV4_Q, PV4_V, PV4_I, PV4_F, PV5_P_ref, PV5_P_rate, PV5_FDP, PV5_Q_ref, PV5_Q_rate, PV5_P, PV5_Q, PV5_V, PV5_I, PV5_F, POI_Ia, POI_Ib, POI_Ic, POI_Vab, POI_Vbc, POI_Vca, POI_P, POI_Q, PV6_P_ref, PV6_P_rate, PV6_FDP, PV6_Q_ref, PV6_Q_rate, PV6_P, PV6_Q, PV6_V, PV6_I, PV6_F, PV7_P, PV7_Q, PV7_V, PV7_I, PV7_F, PV8_P, PV8_Q, PV8_V, PV8_I, PV8_F, PV9_P, PV9_Q, PV9_V, PV9_I, PV9_F, PV1_SET_P, PV1_SET_P_rate, PV1_SET_FDP, PV1_SET_Q, PV1_SET_Q_rate, PV2_SET_P, PV2_SET_P_rate, PV2_SET_FDP, PV2_SET_Q, PV2_SET_Q_rate, PV3_SET_P, PV3_SET_P_rate, PV3_SET_FDP, PV3_SET_Q, PV3_SET_Q_rate, PV4_SET_P, PV4_SET_P_rate, PV4_SET_FDP, PV4_SET_Q, PV4_SET_Q_rate, PV5_SET_P, PV5_SET_P_rate, PV5_SET_FDP, PV5_SET_Q, PV5_SET_Q_rate = client_104_config(client, station)

    print("Starting dynamic state estimation loop. Press Ctrl+C to stop.")
    cycle = 0
    meas_array_aux=[]

    try:
        while True:

            '''
            ===============================================================
            NOTE: Let's assume that here is called your function for extracting
            the database measurements. The function returns a numpy array called
            e.g., "meas_array". I forward "meas_array" to function "process_measurements"
            to create arrays with P,Q, and V measurements (can be easily extended for current measurements)
            ===============================================================
            '''
            client.start()
            time.sleep(0.3)
            now = dt.datetime.now()
            t = datetime.now(timezone.utc)
            PV1_Read, PV2_Read, PV3_Read, PV4_Read, PV5_Read, PV6_Read, PV7_Read, PV8_Read, PV9_Read, POI_Read = client_IEC104()
            data_COMM_W = np.concatenate([np.array(PV1_Read), np.array(PV2_Read), np.array(PV3_Read), np.array(PV4_Read), np.array(PV5_Read),np.array(PV6_Read),np.array(PV7_Read),np.array(PV8_Read),np.array(PV9_Read),np.array(POI_Read)])

            # Write the Data Base with measurement from IEC104
            write_TagArray_W(connection, t, data_COMM_W)
            print('Filling TagArray_W Table with measurement from IEC104')

            # Read the Data Base to run the ES
            meas_array = read_TagArray_W(connection)

            tic_ES_HEDNO = time.time()
            mes_positions_p = np.ones(num_buses, dtype=int)
            mes_positions_q = np.ones(num_buses, dtype=int)
            mes_positions_v = np.ones(num_buses, dtype=int)

            mes_positions = np.full(num_buses, 0)
                    
            for aux in injection_buses:
                mes_positions[aux] = 1

            mes_positions_p=mes_positions.copy()
            mes_positions_q=mes_positions.copy()
            mes_positions_v=mes_positions.copy()

            mes_positions_virtual = np.zeros(num_buses, dtype=int)
            mes_positions_virtual[zero_injection_buses] = 1
            column_rank = (num_buses-1)*2

            Pmes, Qmes, Vmes, Imes = process_measurements(meas_array, num_buses,np)

            Pmes = Pmes + 1e-9
            Qmes = Qmes + 1e-9
            Vmes = Vmes + 1e-9
            Imes = Imes + 1e-9

            # Vmes[5] = Vmes[5]*0.95
            
            mes_p.setRecords(np.where(mes_positions_p.copy()==1)[0])
            mes_q.setRecords(np.where(mes_positions_q.copy()==1)[0])
            mes_v.setRecords(np.where(mes_positions_v.copy()==1)[0])
        
            ### Include plausibility analysis here ###
        
            Pmesp.setRecords(Pmes)
            Qmesp.setRecords(Qmes)
            Vmesp.setRecords(Vmes)
            
            Pest.setRecords(Pmes)
            Qest.setRecords(Qmes)
            Vest.setRecords(Vmes) 

        
            # Call state estimation function
            (
                Vest_array, Pest_array, Qest_array, removed_residuals, Vtest, normalized_residuals_V,indices_v_test
            ) = State_Estimation_generic_function(estimation, column_rank, num_buses, hashmap_names2, hashmap_reduction2, mes_positions_p, mes_positions_q, mes_positions_v, H_v_full, H_p_full, H_q_full, slack_bus_row_P, slack_bus_row_Q, mes_positions_virtual, slack_bus, Pmesp, Qmesp, Vmesp, Std_P, Std_Q, Std_V, mes_p, mes_q, mes_v,Vest, Pest, Qest)
            toc_ES_HEDNO = time.time()
            print(f"Execution time ES_HEDNO: {(toc_ES_HEDNO - tic_ES_HEDNO) * 1000:.2f} ms")

            # Writing the results of the state estimator
            write_TagArray_Est(connection, t, Vest_array, Pest_array, Qest_array)
            logging.info("Cycle %d: State estimation results saved in restructured CSV.", cycle + 1)
            cycle += 1

    except KeyboardInterrupt:
        logging.info("Dynamic state estimation loop terminated by user.")
        print("Terminated by user.")
    finally:
        client.stop()
        if connection:
            connection.close()
            logging.info("SQL connection closed.")