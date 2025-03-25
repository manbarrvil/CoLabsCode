# -*- coding: utf-8 -*-
"""
Created on Sun Mar 16 19:22:36 2025

@author: manba
"""

import json
import struct
from pymodbus.client import ModbusTcpClient

# Cargar el fichero JSON
with open('pv0102_mininet_local_modbus.json', 'r') as file:
    data = json.load(file)

#print(f"{data}")
# # Buscar a Ana y sacar su edad
ident_emec_id = "poi" #Select poi, inv1, inv2

#Identification of the IP for the devies, type of configuration, port and initial register
for item in data["devices"]:
     if item["ing_id"] == ident_emec_id:  # Verificamos si el nombre es "Ana"
         
         IP = item['modbus_ip']
         config   = item['config']
         port = item['modbus_port']
         reg_ini =  item['reg_0']
         print(f"La IP del {config} es: {IP}, con puerto {port} y registro inicial {reg_ini}")

#Get the identification of the measurements types and format   
emec_prefix = [] 
meas_prefix = []   
meas_register = []
meas_format = []
mess_type = []
for item1 in data["configs"][config]['measurements']:
        meas_prefix.append(item1['ing_name'])
        meas_register.append(item1['io_register'] + reg_ini)
        meas_format.append(item1['format'])
        mess_type.append(item1['type'])
        #print(f"La medida {meas_prefix} comienza en el registro {meas_register}, es de tipo {mess_type} y formato {meas_format}")

#Reading from modubs
client = ModbusTcpClient(IP)
read_meas_MB = []
for item2 in meas_register:
#     print(f"La medida {item2}")
#     print(f"{a}")
    read_meas_MB.append(client.read_holding_registers(item2,count=2))
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    