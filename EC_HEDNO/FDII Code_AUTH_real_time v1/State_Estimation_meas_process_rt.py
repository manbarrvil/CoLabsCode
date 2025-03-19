import numpy as np
import pandas as pd
from basic_plausibility import filter_measurements

def process_power_system_data(Pmes, Qmes, Vmes, num_buses, der_positions_ratings, slack_bus, injection_buses):
                              
    # Initialize flow measurement arrays
    Pflow_mes = np.zeros(num_buses, dtype=float)
    Qflow_mes = np.zeros(num_buses, dtype=float)
    
       # Adjust measurements for slack bus
    Pmes[slack_bus] = -Pmes[slack_bus]
    Qmes[slack_bus] = -Qmes[slack_bus]

    # Filter erroneous measurements
    erroneous_indices_p, erroneous_indices_q = filter_measurements(Pmes, Qmes, der_positions_ratings)

    # Initialize measurement positions
    mes_positions_p = np.ones(num_buses, dtype=int)
    mes_positions_q = np.ones(num_buses, dtype=int)
    mes_positions_v = np.ones(num_buses, dtype=int)
    mes_positions_pflow = np.zeros(num_buses, dtype=int)
    mes_positions_qflow = np.zeros(num_buses, dtype=int)

    mes_positions = np.full(num_buses, 0)
    
    for aux in range(0,num_buses):
        if aux in injection_buses:
            mes_positions[aux]=1
                      
    mes_positions_p=mes_positions.copy()
    mes_positions_q=mes_positions.copy()
    mes_positions_v=mes_positions.copy()
    
    return (mes_positions_p, mes_positions_q, mes_positions_v, mes_positions_pflow, mes_positions_qflow, Pmes, Qmes, Vmes, Pflow_mes, Qflow_mes)
