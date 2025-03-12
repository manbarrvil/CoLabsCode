# -*- coding: utf-8 -*-
'''Código de PPC'''
#https://quike.it/es/como-configurar-acceso-remoto-postgresql/#elementor-toc__heading-anchor-5
# Convertidor de uint16 a int16
def toSigned16(n,bit):
    mask = (2**bit) - 1
    if n & (1 << (bit - 1)):
        return n | ~mask
    else: 
        return n & mask
    
# Convertidor de int16 a uint16
def toUnsigned16(n,bit):
    if (n>=0 and n<(2**(bit-1))):
        n_uns=n
    elif (n<0 and n>-2**(bit-1)):
        n_uns=n+2**bit
    elif (n>(2**(bit-1))):
        n_uns = (2**(bit-1))-1
    elif (n<-(2**(bit-1))):
        n_uns = (2**(bit-1))
    return n_uns

def int32_to_2int16(n):
    n16=[]
    n16.append((n>>16) & 0xFFFF)
    n16.append(n & 0xFFFF)     
    return n16

import struct
from datetime import datetime, timezone
from pymodbus.client import ModbusTcpClient
import time
import psycopg2

# Direccines IP
IP = "192.168.5.15"
IP1 = "192.168.1.10"
IP2 = "192.168.2.10"

# Funciones de Modbus
def read_elec_POI(IP):
    client = ModbusTcpClient(IP)
    
    # Leer valores
    Va_mb = client.read_holding_registers(32768, 2)
    Vb_mb = client.read_holding_registers(32770, 2)
    Vc_mb = client.read_holding_registers(32772, 2)
    F_mb = client.read_holding_registers(32780, 2)
    P_mb = client.read_holding_registers(32790, 2)
    Q_mb = client.read_holding_registers(49176, 2)
    Ia_mb = client.read_holding_registers(32782, 2)
    Ib_mb = client.read_holding_registers(32784, 2)
    Ic_mb = client.read_holding_registers(32786, 2)
    In_mb = client.read_holding_registers(32788, 2)
    U12_mb = client.read_holding_registers(32768, 2)
    U23_mb = client.read_holding_registers(32770, 2)
    U31_mb = client.read_holding_registers(32772, 2)
    U1_mb = client.read_holding_registers(32774, 2)
    U2_mb = client.read_holding_registers(32776, 2)
    U3_mb = client.read_holding_registers(32778, 2)
    
    
    Va = (Va_mb.registers[1] << 16) | Va_mb.registers[0]
    Va = struct.unpack('>f', Va.to_bytes(4, byteorder='big'))[0]
    Vb = (Vb_mb.registers[1] << 16) | Vb_mb.registers[0]
    Vb = struct.unpack('>f', Vb.to_bytes(4, byteorder='big'))[0]
    Vc = (Vc_mb.registers[1] << 16) | Vc_mb.registers[0]
    Vc = struct.unpack('>f', Vc.to_bytes(4, byteorder='big'))[0]
    

    f = (F_mb.registers[1] << 16) | F_mb.registers[0]
    f = struct.unpack('>f', f.to_bytes(4, byteorder='big'))[0]

    P = (P_mb.registers[1] << 16) | P_mb.registers[0]
    P = struct.unpack('>f', P.to_bytes(4, byteorder='big'))[0]
    Q = (Q_mb.registers[1] << 16) | Q_mb.registers[0]
    Q = struct.unpack('>f', Q.to_bytes(4, byteorder='big'))[0]
    
    Ia = (Ia_mb.registers[1] << 16) | Ia_mb.registers[0]
    Ia = struct.unpack('>f', Ia.to_bytes(4, byteorder='big'))[0]
    Ib = (Ib_mb.registers[1] << 16) | Ib_mb.registers[0]
    Ib = struct.unpack('>f', Ib.to_bytes(4, byteorder='big'))[0]
    Ic = (Ic_mb.registers[1] << 16) | Ic_mb.registers[0]
    Ic = struct.unpack('>f', Ic.to_bytes(4, byteorder='big'))[0]
    In = (In_mb.registers[1] << 16) | In_mb.registers[0]
    In = struct.unpack('>f', In.to_bytes(4, byteorder='big'))[0]
    
    U12 = (U12_mb.registers[1] << 16) | U12_mb.registers[0]
    U12 = struct.unpack('>f', U12.to_bytes(4, byteorder='big'))[0]
    U23 = (U23_mb.registers[1] << 16) | U23_mb.registers[0]
    U23 = struct.unpack('>f', U23.to_bytes(4, byteorder='big'))[0]
    U31 = (U31_mb.registers[1] << 16) | U31_mb.registers[0]
    U31 = struct.unpack('>f', U31.to_bytes(4, byteorder='big'))[0]
    
    U1 = (U1_mb.registers[1] << 16) | U1_mb.registers[0]
    U1 = struct.unpack('>f', U1.to_bytes(4, byteorder='big'))[0]
    U2 = (U2_mb.registers[1] << 16) | U2_mb.registers[0]
    U2 = struct.unpack('>f', U2.to_bytes(4, byteorder='big'))[0]
    U3 = (U3_mb.registers[1] << 16) | U3_mb.registers[0]
    U3 = struct.unpack('>f', U3.to_bytes(4, byteorder='big'))[0]
    
    client.close()
    return Va, Vb, Vc, f, P, Q, Ia, Ib, Ic, In, U12, U23, U31, U1, U2, U3

def read_elec_CT1(IP):
    client = ModbusTcpClient(IP)
    
    # Leer valores
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


def read_elec_CT2(IP):
    client = ModbusTcpClient(IP)
    
    # Leer valores
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



    
def write_DB_CSL_BROKER_INPUT(t, POI_Va, POI_Vb, POI_Vc, f, POI_P, POI_Q, POI_Ia, POI_Ib, POI_Ic, POI_In, POI_U12, POI_U23, POI_U31, POI_U1, POI_U2, POI_U3, 
                          CT1_Vab, CT1_Vbc, CT1_Vca, CT1_Ia, CT1_Ib, CT1_Ic, CT1_P, CT1_Q, CT1_P_ref, CT1_Q_ref, 
                          CT2_Vab, CT2_Vbc, CT2_Vca, CT2_Ia, CT2_Ib, CT2_Ic, CT2_P, CT2_Q, CT2_P_ref, CT2_Q_ref):
    conexion1 = psycopg2.connect(database="DB_CSL_BROKER", user="postgres", password="postgres")
    cursor1=conexion1.cursor()
    sql="insert into DB_CSL_BROKER_INPUT(Date_Time, POI_Va,POI_Vb,POI_Vc,POI_f,POI_P,POI_Q,POI_Ia,POI_Ib,POI_Ic,POI_In,POI_U12,POI_U23,POI_U31,POI_U1,POI_U2,POI_U3,CT1_Vab,CT1_Vbc,CT1_Vca,CT1_Ia,CT1_Ib,CT1_Ic,CT1_P,CT1_Q,CT1_P_REF,CT1_Q_REF,CT2_Vab,CT2_Vbc,CT2_Vca,CT2_Ia,CT2_Ib,CT2_Ic,CT2_P,CT2_Q,CT2_P_REF,CT2_Q_REF) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    data_input=((t,), POI_Va, POI_Vb, POI_Vc, f, POI_P, POI_Q, POI_Ia, POI_Ib, POI_Ic, POI_In, POI_U12, POI_U23, POI_U31, POI_U1, POI_U2, POI_U3, 
                              CT1_Vab, CT1_Vbc, CT1_Vca, CT1_Ia, CT1_Ib, CT1_Ic, CT1_P, CT1_Q, CT1_P_ref, CT1_Q_ref, 
                              CT2_Vab, CT2_Vbc, CT2_Vca, CT2_Ia, CT2_Ib, CT2_Ic, CT2_P, CT2_Q, CT2_P_ref, CT2_Q_ref)
    cursor1.execute(sql, data_input)
    conexion1.commit()
    conexion1.close()


if __name__ == '__main__':


    try:
        while True:
            
            # Extracción de datos por Modbus
            POI_Va, POI_Vb, POI_Vc, f, POI_P, POI_Q, POI_Ia, POI_Ib, POI_Ic, POI_In, POI_U12, POI_U23, POI_U31, POI_U1, POI_U2, POI_U3 = read_elec_POI(IP)
            CT1_Vab, CT1_Vbc, CT1_Vca, CT1_Ia, CT1_Ib, CT1_Ic, CT1_P, CT1_Q, CT1_P_ref, CT1_Q_ref = read_elec_CT1(IP1)
            CT2_Vab, CT2_Vbc, CT2_Vca, CT2_Ia, CT2_Ib, CT2_Ic, CT2_P, CT2_Q, CT2_P_ref, CT2_Q_ref = read_elec_CT2(IP2)
            t = datetime.now(timezone.utc)
                        
            
            # Escritura en la base de datos, de comunicación a base de datos (DB)
            write_DB_CSL_BROKER_INPUT(t, POI_Va, POI_Vb, POI_Vc, f, POI_P, POI_Q, POI_Ia, POI_Ib, POI_Ic, POI_In, POI_U12, POI_U23, POI_U31, POI_U1, POI_U2, POI_U3, 
                                      CT1_Vab, CT1_Vbc, CT1_Vca, CT1_Ia, CT1_Ib, CT1_Ic, CT1_P, CT1_Q, CT1_P_ref, CT1_Q_ref, 
                                      CT2_Vab, CT2_Vbc, CT2_Vca, CT2_Ia, CT2_Ib, CT2_Ic, CT2_P, CT2_Q, CT2_P_ref, CT2_Q_ref)
            
            print("Rellenado tabla DB_CSL_BROKER_INPUT con medidas de Modbus TCP/IP...")
            

            time.sleep(1)


    except KeyboardInterrupt:
        print("Fin de la conexión...")

