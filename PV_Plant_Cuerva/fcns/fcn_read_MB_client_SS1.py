import struct
from pymodbus.client import ModbusTcpClient
import sys

# Add the directory containing the script or function to sys.path
sys.path.append('C:/workspace/CoLabsCode/PV_Plant_Cuerva/fcns')

# Nimport your function
from fcn_conv_uint16_int16 import toSigned16

def read_elec_SS1(IP):
    client = ModbusTcpClient(IP)
    
    # Read values
    # int 16 bits
    CT1_Vab_mb = client.read_holding_registers(40575, 1)
    CT1_Vbc_mb = client.read_holding_registers(40576, 1)
    CT1_Vca_mb = client.read_holding_registers(40577, 1)
    CT1_Ia_mb = client.read_holding_registers(40572, 1)
    CT1_Ib_mb = client.read_holding_registers(40573, 1)
    CT1_Ic_mb = client.read_holding_registers(40574, 1)
    # int 32 bits
    CT1_P_mb = client.read_holding_registers(40525, 2)
    CT1_Q_mb = client.read_holding_registers(40544, 2)
    CT1_P_ref_mb = client.read_holding_registers(40424, 2)
    CT1_Q_ref_mb = client.read_holding_registers(40426, 2)
    
    
    CT1_Vab = CT1_Vab_mb.registers[0]
    CT1_Vbc = CT1_Vbc_mb.registers[0]
    CT1_Vca = CT1_Vca_mb.registers[0]
    CT1_Ia = CT1_Ia_mb.registers[0]
    CT1_Ib = CT1_Ib_mb.registers[0] 
    CT1_Ic = CT1_Ic_mb.registers[0]
    
    CT1_P = CT1_P_mb.registers[0] << 16 | CT1_P_mb.registers[1]
    CT1_P = toSigned16(CT1_P, 32)
    CT1_Q = CT1_Q_mb.registers[0] << 16 | CT1_Q_mb.registers[1]
    CT1_Q = toSigned16(CT1_Q, 32)
    CT1_P_ref = CT1_P_ref_mb.registers[0] << 16 | CT1_P_ref_mb.registers[1]
    CT1_Q_ref = CT1_Q_ref_mb.registers[0] << 16 | CT1_Q_ref_mb.registers[1]
    CT1_Q_ref = toSigned16(CT1_Q_ref, 32)

    client.close()
    return CT1_Vab, CT1_Vbc, CT1_Vca, CT1_Ia, CT1_Ib, CT1_Ic, CT1_P, CT1_Q, CT1_P_ref, CT1_Q_ref