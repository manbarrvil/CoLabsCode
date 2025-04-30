# -*- coding: utf-8 -*-
"""
Created on Sun Mar 16 19:22:36 2025

@author: manba
"""
import json
import struct
from pymodbus.client import ModbusTcpClient
import sys

# Add the directory containing the script or function to sys.path
sys.path.append('C:/workspace/CoLabsCode/PV_Plant_Cuerva/fcns')

# Nimport your function
from fcn_conv_uint16_int16 import toSigned16

# # Cargar el fichero JSON
# with open('pv0102_mininet_local_modbus.json', 'r') as file:
#     data = json.load(file)

# #print(f"{data}")
# ident_emec_id = "inv1" #Select "poi", "inv1", "inv2"

def client_Modbus(ident_emec_id, data):
    '''Comienzo de futura función de lectura modbus'''
    #Identification of the IP for the devies, type of configuration, port and initial register
    for item in data["devices"]:
        if item["ing_id"] == ident_emec_id:
            IP = item['modbus_ip']
            config   = item['config']
            port = item['modbus_port']
            reg_ini =  item['reg_0']
            print(f"La IP del {config} es: {IP}, con puerto {port} y registro inicial {reg_ini}")

    # #Get the identification of the measurements types and format   
    # emec_prefix = [] 
    # meas_prefix = []   
    # meas_register = []
    # meas_format = []
    # meas_type = []
    # meas_units = []
    # for item1 in data["configs"][config]['measurements']:
    #         meas_prefix.append(item1['ing_name'])
    #         meas_register.append(item1['register'] + reg_ini)
    #         meas_format.append(item1['format'])
    #         meas_type.append(item1['type'])
    #         meas_units.append(item1['units'])
    #         #print(f"La medida {meas_prefix} comienza en el registro {meas_register}, es de tipo {mess_type} y formato {meas_format}")

    #Reading from modubs
    client = ModbusTcpClient(IP)
    read_meas_MB = []
    meas = [] 
    value_list = []

    keys_list = ["ing_name","value","units"]

    for item1 in data["configs"][config]['measurements']:
        
        if (item1['type'] == 'float32'):
            read_meas_MB = client.read_holding_registers(item1['register'] + reg_ini, 2)
            if(item1['format'] == 'CDAB'):
                con_meas = (read_meas_MB.registers[1] << 16) | read_meas_MB.registers[0]
                con_meas = struct.unpack('>f', con_meas.to_bytes(4, byteorder='big'))[0]
                meas.append(con_meas)
            elif(item1['format'] == 'ABCD'):
                con_meas = (read_meas_MB.registers[0] << 16) | read_meas_MB.registers[1]
                con_meas = struct.unpack('>f', con_meas.to_bytes(4, byteorder='big'))[0]


        elif(item1['type'] == 'int32'):
            read_meas_MB = client.read_holding_registers(item1['register'] + reg_ini, 2)
            if(item1['format'] == 'CDAB'):
                con_meas = (read_meas_MB.registers[1] << 16) | read_meas_MB.registers[0]
                con_meas = toSigned16(con_meas, 32)
                meas.append(con_meas)
            elif( item1['format'] == 'ABCD'):
                con_meas = (read_meas_MB.registers[0] << 16) | read_meas_MB.registers[1]
                con_meas = toSigned16(con_meas, 32)

        elif(item1['type'] == 'uint32'):
            read_meas_MB = client.read_holding_registers(item1['register'] + reg_ini, 2)
            con_meas = read_meas_MB.registers[0] << 16 | read_meas_MB.registers[1]

        elif(item1['type'] == 'int16'):
            read_meas_MB = client.read_holding_registers(item1['register'] + reg_ini, 1)
            con_meas = read_meas_MB.registers[0]

        value_list.append([item1['ing_name'], con_meas, item1['units']])

    # Convertir a diccionario
    dict_meas = {values[0]: dict(zip(keys_list[1::], values[1::])) for i, values in enumerate(value_list)}

    client.close()
    return dict_meas
