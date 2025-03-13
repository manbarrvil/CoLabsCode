import struct
from pymodbus.client import ModbusTcpClient
import sys

# Add the directory containing the script or function to sys.path
sys.path.append('C:/workspace/CoLabsCode/PV_Plant_Cuerva/fcns')

# Nimport your function
from fcn_conv_uint16_int16 import toSigned16

def read_elec_SS2(IP):
    client = ModbusTcpClient(IP)
    
    # Read values
    # int 16 bits
    CT2_Vab_mb = client.read_holding_registers(40575, 1)
    CT2_Vbc_mb = client.read_holding_registers(40576, 1)
    CT2_Vca_mb = client.read_holding_registers(40577, 1)
    CT2_Ia_mb = client.read_holding_registers(40572, 1)
    CT2_Ib_mb = client.read_holding_registers(40573, 1)
    CT2_Ic_mb = client.read_holding_registers(40574, 1)
    # int 32 bits
    CT2_P_mb = client.read_holding_registers(40525, 2)
    CT2_Q_mb = client.read_holding_registers(40544, 2)
    CT2_P_ref_mb = client.read_holding_registers(40424, 2)
    CT2_Q_ref_mb = client.read_holding_registers(40426, 2)
    
    CT2_Vab = CT2_Vab_mb.registers[0]
    CT2_Vbc = CT2_Vbc_mb.registers[0]
    CT2_Vca = CT2_Vca_mb.registers[0]
    CT2_Ia = CT2_Ia_mb.registers[0] 
    CT2_Ib = CT2_Ib_mb.registers[0] 
    CT2_Ic = CT2_Ic_mb.registers[0]
    
    CT2_P = CT2_P_mb.registers[0] << 16 | CT2_P_mb.registers[1]
    CT2_P = toSigned16(CT2_P, 32)
    CT2_Q = CT2_Q_mb.registers[0] << 16 | CT2_Q_mb.registers[1]
    CT2_Q = toSigned16(CT2_Q, 32)
    CT2_P_ref = CT2_P_ref_mb.registers[0] << 16 | CT2_P_ref_mb.registers[1]
    CT2_Q_ref = CT2_Q_ref_mb.registers[0] << 16 | CT2_Q_ref_mb.registers[1]
    CT2_Q_ref = toSigned16(CT2_Q_ref, 32)
    
    client.close()
    return CT2_Vab, CT2_Vbc, CT2_Vca, CT2_Ia, CT2_Ib, CT2_Ic, CT2_P, CT2_Q, CT2_P_ref, CT2_Q_ref