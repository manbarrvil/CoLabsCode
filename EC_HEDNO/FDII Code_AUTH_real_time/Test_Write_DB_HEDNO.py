import time
import pickle
import logging
import pyodbc
import pandas as pd
import numpy as np
import os
import json
import c104
from pandas import read_excel
from datetime import datetime
import datetime as dt
import c104


# from get_dynamic_measurements import get_dynamic_measurements
# from State_Estimation_generic_function_rt import State_Estimation_generic_function
# from process_measurements_rt import process_measurements
# from process_measurements_temp import process_measurements_temp
import random

data_read_DB=[]

# arr_W = [50.0, 0.0, 250.0, 100.0,10.0,0.0,0.0,0.0,0.0,0.0]
# arr_feeder = [0.0, 0.0, 0.0, 433,433,433,600,60.0]
# arr_W = arr_W*6
# arr_W.extend(arr_feeder)

# client, connection and station preparation
client = c104.Client()
connection_104 = client.add_connection(ip="192.168.5.3", port=2404, init=c104.Init.ALL)
# connection.on_unexpected_message(callable=con_on_unexpected_message)
station = connection_104.add_station(common_address=1)

# monitoring point preparation
PV1_P_ref  = station.add_point(io_address=16418, type=c104.Type.M_ME_NC_1)
PV1_P_rate = station.add_point(io_address=16419, type=c104.Type.M_ME_NC_1)
PV1_FDP    = station.add_point(io_address=16420, type=c104.Type.M_ME_NC_1)
PV1_Q_ref  = station.add_point(io_address=16421, type=c104.Type.M_ME_NC_1)
PV1_Q_rate = station.add_point(io_address=16423, type=c104.Type.M_ME_NC_1)
PV1_P      = station.add_point(io_address=16431, type=c104.Type.M_ME_NC_1)
PV1_Q      = station.add_point(io_address=16433, type=c104.Type.M_ME_NC_1)
PV1_V      = station.add_point(io_address=16434, type=c104.Type.M_ME_NC_1)
PV1_I      = station.add_point(io_address=16437, type=c104.Type.M_ME_NC_1)
PV1_F      = station.add_point(io_address=16442, type=c104.Type.M_ME_NC_1)

PV2_P_ref  = station.add_point(io_address=16418+25, type=c104.Type.M_ME_NC_1)
PV2_P_rate = station.add_point(io_address=16419+25, type=c104.Type.M_ME_NC_1)
PV2_FDP    = station.add_point(io_address=16420+25, type=c104.Type.M_ME_NC_1)
PV2_Q_ref  = station.add_point(io_address=16421+25, type=c104.Type.M_ME_NC_1)
PV2_Q_rate = station.add_point(io_address=16423+25, type=c104.Type.M_ME_NC_1)
PV2_P      = station.add_point(io_address=16431+25, type=c104.Type.M_ME_NC_1)
PV2_Q      = station.add_point(io_address=16433+25, type=c104.Type.M_ME_NC_1)
PV2_V      = station.add_point(io_address=16434+25, type=c104.Type.M_ME_NC_1)
PV2_I      = station.add_point(io_address=16437+25, type=c104.Type.M_ME_NC_1)
PV2_F      = station.add_point(io_address=16442+25, type=c104.Type.M_ME_NC_1)

PV3_P_ref  = station.add_point(io_address=16418+50, type=c104.Type.M_ME_NC_1)
PV3_P_rate = station.add_point(io_address=16419+50, type=c104.Type.M_ME_NC_1)
PV3_FDP    = station.add_point(io_address=16420+50, type=c104.Type.M_ME_NC_1)
PV3_Q_ref  = station.add_point(io_address=16421+50, type=c104.Type.M_ME_NC_1)
PV3_Q_rate = station.add_point(io_address=16423+50, type=c104.Type.M_ME_NC_1)
PV3_P      = station.add_point(io_address=16431+50, type=c104.Type.M_ME_NC_1)
PV3_Q      = station.add_point(io_address=16433+50, type=c104.Type.M_ME_NC_1)
PV3_V      = station.add_point(io_address=16434+50, type=c104.Type.M_ME_NC_1)
PV3_I      = station.add_point(io_address=16437+50, type=c104.Type.M_ME_NC_1)
PV3_F      = station.add_point(io_address=16442+50, type=c104.Type.M_ME_NC_1)

PV4_P_ref  = station.add_point(io_address=16418+75, type=c104.Type.M_ME_NC_1)
PV4_P_rate = station.add_point(io_address=16419+75, type=c104.Type.M_ME_NC_1)
PV4_FDP    = station.add_point(io_address=16420+75, type=c104.Type.M_ME_NC_1)
PV4_Q_ref  = station.add_point(io_address=16421+75, type=c104.Type.M_ME_NC_1)
PV4_Q_rate = station.add_point(io_address=16423+75, type=c104.Type.M_ME_NC_1)
PV4_P      = station.add_point(io_address=16431+75, type=c104.Type.M_ME_NC_1)
PV4_Q      = station.add_point(io_address=16433+75, type=c104.Type.M_ME_NC_1)
PV4_V      = station.add_point(io_address=16434+75, type=c104.Type.M_ME_NC_1)
PV4_I      = station.add_point(io_address=16437+75, type=c104.Type.M_ME_NC_1)
PV4_F      = station.add_point(io_address=16442+75, type=c104.Type.M_ME_NC_1)

PV5_P_ref  = station.add_point(io_address=16418+100, type=c104.Type.M_ME_NC_1)
PV5_P_rate = station.add_point(io_address=16419+100, type=c104.Type.M_ME_NC_1)
PV5_FDP    = station.add_point(io_address=16420+100, type=c104.Type.M_ME_NC_1)
PV5_Q_ref  = station.add_point(io_address=16421+100, type=c104.Type.M_ME_NC_1)
PV5_Q_rate = station.add_point(io_address=16423+100, type=c104.Type.M_ME_NC_1)
PV5_P      = station.add_point(io_address=16431+100, type=c104.Type.M_ME_NC_1)
PV5_Q      = station.add_point(io_address=16433+100, type=c104.Type.M_ME_NC_1)
PV5_V      = station.add_point(io_address=16434+100, type=c104.Type.M_ME_NC_1)
PV5_I      = station.add_point(io_address=16437+100, type=c104.Type.M_ME_NC_1)
PV5_F      = station.add_point(io_address=16442+100, type=c104.Type.M_ME_NC_1)

POI_Ia      = station.add_point(io_address=25114, type=c104.Type.M_ME_NC_1)
POI_Ib      = station.add_point(io_address=25115, type=c104.Type.M_ME_NC_1)
POI_Ic      = station.add_point(io_address=25116, type=c104.Type.M_ME_NC_1)
POI_Vab     = station.add_point(io_address=25117, type=c104.Type.M_ME_NC_1)
POI_Vbc     = station.add_point(io_address=25118, type=c104.Type.M_ME_NC_1)
POI_Vca     = station.add_point(io_address=25119, type=c104.Type.M_ME_NC_1)
POI_P       = station.add_point(io_address=25120, type=c104.Type.M_ME_NC_1)
POI_Q       = station.add_point(io_address=25121, type=c104.Type.M_ME_NC_1)

# command point preparation
PV1_SET_P      = station.add_point(io_address=25089, type=c104.Type.C_SE_NC_1)
PV1_SET_P_rate = station.add_point(io_address=25090, type=c104.Type.C_SE_NC_1)
PV1_SET_FDP    = station.add_point(io_address=25091, type=c104.Type.C_SE_NC_1)
PV1_SET_Q      = station.add_point(io_address=25092, type=c104.Type.C_SE_NC_1)
PV1_SET_Q_rate = station.add_point(io_address=25093, type=c104.Type.C_SE_NC_1)

PV2_SET_P      = station.add_point(io_address=25094, type=c104.Type.C_SE_NC_1)
PV2_SET_P_rate = station.add_point(io_address=25095, type=c104.Type.C_SE_NC_1)
PV2_SET_FDP    = station.add_point(io_address=25096, type=c104.Type.C_SE_NC_1)
PV2_SET_Q      = station.add_point(io_address=25097, type=c104.Type.C_SE_NC_1)
PV2_SET_Q_rate = station.add_point(io_address=25098, type=c104.Type.C_SE_NC_1)

PV3_SET_P      = station.add_point(io_address=25099, type=c104.Type.C_SE_NC_1)
PV3_SET_P_rate = station.add_point(io_address=25100, type=c104.Type.C_SE_NC_1)
PV3_SET_FDP    = station.add_point(io_address=25101, type=c104.Type.C_SE_NC_1)
PV3_SET_Q      = station.add_point(io_address=25102, type=c104.Type.C_SE_NC_1)
PV3_SET_Q_rate = station.add_point(io_address=25103, type=c104.Type.C_SE_NC_1)

PV4_SET_P      = station.add_point(io_address=25104, type=c104.Type.C_SE_NC_1)
PV4_SET_P_rate = station.add_point(io_address=25105, type=c104.Type.C_SE_NC_1)
PV4_SET_FDP    = station.add_point(io_address=25106, type=c104.Type.C_SE_NC_1)
PV4_SET_Q      = station.add_point(io_address=25107, type=c104.Type.C_SE_NC_1)
PV4_SET_Q_rate = station.add_point(io_address=25108, type=c104.Type.C_SE_NC_1)

PV5_SET_P      = station.add_point(io_address=25109, type=c104.Type.C_SE_NC_1)
PV5_SET_P_rate = station.add_point(io_address=25110, type=c104.Type.C_SE_NC_1)
PV5_SET_FDP    = station.add_point(io_address=25111, type=c104.Type.C_SE_NC_1)
PV5_SET_Q      = station.add_point(io_address=25112, type=c104.Type.C_SE_NC_1)
PV5_SET_Q_rate = station.add_point(io_address=25113, type=c104.Type.C_SE_NC_1)

def client_IEC104():

    # start
    client.start()
    time.sleep(0.3)

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

    POI_Ia .read()
    POI_Ib .read()
    POI_Ic .read()
    POI_Vab.read()
    POI_Vbc.read()
    POI_Vca.read()
    POI_P  .read()
    POI_Q  .read()

    PV1_SET_P     .value = -500e3
    PV1_SET_P_rate.value = 0.0
    PV1_SET_FDP   .value = 1.0
    PV1_SET_Q     .value = 0.0
    PV1_SET_Q_rate.value = 0.0

    PV2_SET_P     .value = -500e3
    PV2_SET_P_rate.value = 0.0
    PV2_SET_FDP   .value = 1.0
    PV2_SET_Q     .value = 0.0
    PV2_SET_Q_rate.value = 0.0

    PV3_SET_P     .value = -300e3
    PV3_SET_P_rate.value = 0.0
    PV3_SET_FDP   .value = 1.0
    PV3_SET_Q     .value = 0.0
    PV3_SET_Q_rate.value = 0.0

    PV4_SET_P     .value = -500e3
    PV4_SET_P_rate.value = 0.0
    PV4_SET_FDP   .value = 1.0
    PV4_SET_Q     .value = 0.0
    PV4_SET_Q_rate.value = 0.0

    PV5_SET_P     .value = -300e3
    PV5_SET_P_rate.value = 0.0
    PV5_SET_FDP   .value = 1.0
    PV5_SET_Q     .value = 0.0
    PV5_SET_Q_rate.value = 0.0

    # PV1_SET_P     .value = 0.0
    # PV1_SET_P_rate.value = 0.0
    # PV1_SET_FDP   .value = 1.0
    # PV1_SET_Q     .value = 0.0
    # PV1_SET_Q_rate.value = 0.0

    # PV2_SET_P     .value = 0.0
    # PV2_SET_P_rate.value = 0.0
    # PV2_SET_FDP   .value = 1.0
    # PV2_SET_Q     .value = 0.0
    # PV2_SET_Q_rate.value = 0.0

    # PV3_SET_P     .value = 0.0
    # PV3_SET_P_rate.value = 0.0
    # PV3_SET_FDP   .value = 1.0
    # PV3_SET_Q     .value = 0.0
    # PV3_SET_Q_rate.value = 0.0

    # PV4_SET_P     .value = 0.0
    # PV4_SET_P_rate.value = 0.0
    # PV4_SET_FDP   .value = 1.0
    # PV4_SET_Q     .value = 0.0
    # PV4_SET_Q_rate.value = 0.0

    # PV5_SET_P     .value = 0.0
    # PV5_SET_P_rate.value = 0.0
    # PV5_SET_FDP   .value = 1.0
    # PV5_SET_Q     .value = 0.0
    # PV5_SET_Q_rate.value = 0.0

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

    PV1_Read = [PV1_F.value,PV1_I.value,PV1_V.value,PV1_P.value/1000,PV1_Q.value/1000,PV1_P_ref.value/1000,PV1_P_rate.value,PV1_FDP.value,PV1_Q_ref.value/1000,PV1_Q_rate.value]
    PV2_Read = [PV2_F.value,PV2_I.value,PV2_V.value,PV2_P.value/1000,PV2_Q.value/1000,PV2_P_ref.value/1000,PV2_P_rate.value,PV2_FDP.value,PV2_Q_ref.value/1000,PV2_Q_rate.value]
    PV3_Read = [PV3_F.value,PV3_I.value,PV3_V.value,PV3_P.value/1000,PV3_Q.value/1000,PV3_P_ref.value/1000,PV3_P_rate.value,PV3_FDP.value,PV3_Q_ref.value/1000,PV3_Q_rate.value]
    PV4_Read = [PV4_F.value,PV4_I.value,PV4_V.value,PV4_P.value/1000,PV4_Q.value/1000,PV4_P_ref.value/1000,PV4_P_rate.value,PV4_FDP.value,PV4_Q_ref.value/1000,PV4_Q_rate.value]
    PV5_Read = [PV5_F.value,PV5_I.value,PV5_V.value,PV5_P.value/1000,PV5_Q.value/1000,PV5_P_ref.value/1000,PV5_P_rate.value,PV5_FDP.value,PV5_Q_ref.value/1000,PV5_Q_rate.value]
    POI_Read = [POI_Ia.value,POI_Ib.value,POI_Ic.value,POI_Vab.value,POI_Vbc.value,POI_Vca.value,POI_P.value/1000,POI_Q.value/1000]

    PV1_setpoint = [PV1_SET_P.value, PV1_SET_P_rate.value, PV1_SET_FDP.value, PV1_SET_Q.value, PV1_SET_Q_rate.value]
    PV2_setpoint = [PV2_SET_P.value, PV2_SET_P_rate.value, PV2_SET_FDP.value, PV2_SET_Q.value, PV2_SET_Q_rate.value]
    PV3_setpoint = [PV3_SET_P.value, PV3_SET_P_rate.value, PV3_SET_FDP.value, PV3_SET_Q.value, PV3_SET_Q_rate.value]
    PV4_setpoint = [PV4_SET_P.value, PV4_SET_P_rate.value, PV4_SET_FDP.value, PV4_SET_Q.value, PV4_SET_Q_rate.value]
    PV5_setpoint = [PV5_SET_P.value, PV5_SET_P_rate.value, PV5_SET_FDP.value, PV5_SET_Q.value, PV5_SET_Q_rate.value]


    client.stop()
    return PV1_Read, PV2_Read, PV3_Read, PV4_Read, PV5_Read, POI_Read


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
 
    data[keys[0]] = t
    #data[keys[1]] = ['Tag_1']
    for i in range(2,len(values)*2+1,2): 
        data[keys[i-1]] = [f'TAG_{int(i/2)}']
        #data[keys[i]] = values[int(i/2-1)] + [random.randint(-1, 1)]
        data[keys[i]] = values[int(i/2-1)]
        
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

def read_TagArray_W(connection):
    cursor=connection.cursor()
      
    cursor.execute("SELECT TOP 1 Tag1_Value, Tag2_Value, Tag3_Value, Tag4_Value, Tag5_Value, Tag6_Value, Tag7_Value, Tag8_Value, Tag9_Value, Tag10_Value, Tag11_Value, Tag12_Value, Tag13_Value, Tag14_Value, Tag15_Value, Tag16_Value, Tag17_Value, Tag18_Value, Tag19_Value, Tag20_Value, Tag21_Value, Tag22_Value, Tag23_Value, Tag24_Value, Tag25_Value,Tag26_Value, Tag27_Value, Tag28_Value, Tag29_Value, Tag30_Value,Tag31_Value, Tag32_Value, Tag33_Value, Tag34_Value, Tag35_Value,Tag36_Value, Tag37_Value, Tag38_Value, Tag39_Value, Tag40_Value,Tag41_Value, Tag42_Value, Tag43_Value, Tag44_Value, Tag45_Value,Tag46_Value, Tag47_Value, Tag48_Value, Tag49_Value, Tag50_Value,Tag51_Value, Tag52_Value, Tag53_Value, Tag54_Value, Tag55_Value,Tag56_Value, Tag57_Value, Tag58_Value, Tag59_Value, Tag60_Value,Tag61_Value, Tag62_Value, Tag63_Value, Tag64_Value, Tag65_Value,Tag66_Value, Tag67_Value, Tag68_Value FROM [MSG_PV].dbo.TagArray_W ORDER BY Tag0_Value DESC")
    
    data_read = cursor.fetchone()
    data_read_DB = list(data_read)  # Convierte la tupla en una lista
    return data_read_DB


connection = pyodbc.connect('DRIVER={SQL Server};'
                                'SERVER=DESKTOP-2BDDNMD\\SQLEXPRESS;'
                                'DATABASE=MSG_PV;'
                                'Trusted_Connection=yes;')
try:
    while True:
        
        # t = datetime.now().strftime("%Y%m%d %H:%M:%S")
        now = dt.datetime.now()
        # Format the timestamp with decimal seconds
        t = now.strftime('%Y%m%d %H:%M:%S') + f".{now.microsecond // 1000:03d}" 
        PV1_Read, PV2_Read, PV3_Read, PV4_Read, PV5_Read, POI_Read = client_IEC104()
        print(POI_Read)
        data_COMM_W = np.concatenate([np.array(PV1_Read), np.array(PV2_Read), np.array(PV3_Read), np.array(PV4_Read), np.array(PV5_Read),np.array(PV5_Read),np.array(POI_Read)])
        # arr_W = [random.randint(-1, 1) for _ in arr_W]
        # data_COMM_W = np.array(arr_W)
        write_TagArray_W(connection, t, data_COMM_W)
        print('Filling Table TagArray_W with the measurements of the IEC104')

        DB_read = read_TagArray_W(connection)
        # print(DB_read)
        # time.sleep(1)

except KeyboardInterrupt:
    logging.info("Dynamic state estimation loop terminated by user.")
    print("Terminated by user.")
finally:
    if connection:
        connection.close()
        logging.info("SQL connection closed.")
