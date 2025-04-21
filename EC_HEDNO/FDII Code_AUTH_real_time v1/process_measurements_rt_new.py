import pandas as pd


def process_measurements(meas_array, num_buses, np):
    
    """
    Since the topology and the tags will always be the same, 
    we can use a fast approach to convert meas_array to 
    Pmes, Qmes, and Vmes for all PVs and the slack bus.
    No pseudomeasurements are needed.
    """  
    Sb= 1e6
    Vb = 400
    Ib = Sb/(np.sqrt(3)*Vb)
    Pmes = np.ones(num_buses, dtype=float)
    Qmes = np.ones(num_buses, dtype=float)
    Vmes = np.ones(num_buses, dtype=float)
    Imes = np.ones(num_buses, dtype=float)
    # Codigo correcto
    Imes[24] = meas_array[1]/Ib
    Vmes[24] = meas_array[2]/231 ### PV 1, GIOUNA LAKKA ###
    Pmes[24] = meas_array[3]*0.001
    Qmes[24] = meas_array[4]*0.001
    
    Imes[15] = meas_array[11]/Ib
    Vmes[15] = meas_array[12]/231 ### PV 2, ARSENA AMPELIA ###
    Pmes[15] = meas_array[13]*0.001
    Qmes[15] = meas_array[14]*0.001

    # # try
    # Imes[15] = meas_array[1]/Ib
    # Vmes[15] = meas_array[2]/231 ### PV 1, GIOUNA LAKKA ###
    # Pmes[15] = meas_array[3]*0.001
    # Qmes[15] = meas_array[4]*0.001
    
    # Imes[24] = meas_array[11]/Ib
    # Vmes[24] = meas_array[12]/231 ### PV 2, ARSENA AMPELIA ###
    # Pmes[24] = meas_array[13]*0.001
    # Qmes[24] = meas_array[14]*0.001
    
    Imes[7] = meas_array[21]/Ib
    Vmes[7] = meas_array[22]/231 ### PV 3, VAFTSA ###
    Pmes[7] = meas_array[23]*0.001
    Qmes[7] = meas_array[24]*0.001
    
    Imes[22] = meas_array[31]/Ib
    Vmes[22] = meas_array[32]/231 ### PV 4, VASILINO ###
    Pmes[22] = meas_array[33]*0.001
    Qmes[22] = meas_array[34]*0.001
    
    Imes[13] = meas_array[41]/Ib
    Vmes[13] = meas_array[42]/231 ### PV 5, PASA NERO ###
    Pmes[13] = meas_array[43]*0.001
    Qmes[13] = meas_array[44]*0.001

    Imes[10] = meas_array[51]/Ib
    Vmes[10] = meas_array[52]/231 ### Assuming LV 116310 ###
    Pmes[10] = meas_array[53]*0.001
    Qmes[10] = meas_array[54]*0.001

    Imes[3] = meas_array[61]/Ib 
    Vmes[3] = meas_array[62]/231 ### Assuming LV 116308 ###
    Pmes[3] = meas_array[63]*0.001
    Qmes[3] = meas_array[64]*0.001
    
    Imes[18] = meas_array[71]/Ib
    Vmes[18] = meas_array[72]/231 ### Assuming LV 114875 ###
    Pmes[18] = meas_array[73]*0.001
    Qmes[18] = meas_array[74]*0.001
    
    Imes[27] = meas_array[81]/Ib
    Vmes[27] = meas_array[82]/231 ### Assuming LV Aggregated ### 
    Pmes[27] = meas_array[83]*0.001
    Qmes[27] = meas_array[84]*0.001
    
    Imes[0] = np.mean([meas_array[90], meas_array[91], meas_array[92]])/Ib ### Assuming Slack bus ### 
    Vmes[0] = np.mean([meas_array[93], meas_array[94], meas_array[95]])/20000
    Pmes[0] = meas_array[96]*0.001
    Qmes[0] = meas_array[97]*0.001
    
    return Pmes, Qmes, Vmes, Imes