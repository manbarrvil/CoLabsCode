import struct
from pymodbus.client import ModbusTcpClient

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