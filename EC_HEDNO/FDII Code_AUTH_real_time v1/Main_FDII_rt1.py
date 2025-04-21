import time
import pickle
import logging
import pandas as pd
import numpy as np
import json

from State_Estimation_generic_function_rt1 import State_Estimation_generic_function
from process_measurements_rt_new import process_measurements
from gamspy import Container, Set, Alias, Parameter, Variable, Equation, Model, Problem, Sum, Sense,math

# Load grid data. Assuming that the topology of the grid will not change in the framework of the WP3 tests, we do not need to extract the grid info
# each time using Pandapower. It can happen once, and then the information to be stored in an appropriate file (e.g., of pickle format). 
with open("extracted_grid_info1.pkl", "rb") as f:
    (num_buses, slack_bus, der_positions_ratings, _, _,
     zero_injection_buses, hashmap_reduction2, hashmap_names2, H_v_full, H_p_full, H_q_full, 
     slack_bus_row_P, slack_bus_row_Q, injection_buses, B, G) = pickle.load(f)

##The lines below to be activated if we want to re-extract the grid information 
#data_filepath = "C:\\Users\\stdim\\EC_Network_reduced_merged_final.xlsx"
   
#num_buses, slack_bus, der_positions_ratings, hashmap_names, hashmap_reduction, zero_injection_buses, hashmap_reduction2, hashmap_names2, H_v_full, H_p_full, #H_q_full, slack_bus_row_P, slack_bus_row_Q, injection_buses, adjacency_matrix_buses,  adjacency_matrix_branches, parent_child_adjacency, R, X, Bshunt, Gshunt, S_n = extract_info (data_filepath)  

monitoring_sleep=1
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

# -----------------------------
# Main Infinite Loop for Real-Time Operation
# -----------------------------
cycle = 0
print("Starting dynamic state estimation loop. Press Ctrl+C to stop.")

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

        Pmes, Qmes, Vmes, Imes = process_measurements(meas_array, num_buses,np)
        
        mes_p.setRecords(np.where(mes_positions_p.copy()==1)[0])
        mes_q.setRecords(np.where(mes_positions_q.copy()==1)[0])
        mes_v.setRecords(np.where(mes_positions_v.copy()==1)[0])
    
        ### Include plausibility analysis here ###
    
        Pmesp.setRecords(Pmes)
        Qmesp.setRecords(Qmes)
        Vmesp.setRecords(Vmes)
        Pest.setRecords(Pmesp.records['value'].to_numpy())
        Qest.setRecords(Qmesp.records['value'].to_numpy())
        Vest.setRecords(Vmesp.records['value'].to_numpy()) 
    
        # Call state estimation function
        (
            Vest, Pest, Qest, removed_residuals
        ) = State_Estimation_generic_function(estimation, column_rank, num_buses, hashmap_names2, hashmap_reduction2, mes_positions_p, mes_positions_q, mes_positions_v, H_v_full, H_p_full, H_q_full, slack_bus_row_P, slack_bus_row_Q, mes_positions_virtual, slack_bus, Pmesp, Qmesp, Vmesp, Std_P, Std_Q, Std_V, mes_p, mes_q, mes_v,Vest, Pest, Qest)
        
        # For each state estimation parameter, convert outputs to strings if necessary.
        # (For arrays, we use json.dumps after converting to list; for DataFrames, use .to_json.)
        se_accum["Vest_array"].append(json.dumps(Vest_array.tolist() if hasattr(Vest_array, 'tolist') else Vest))
        se_accum["Pest_array"].append(json.dumps(Pest_array.tolist() if hasattr(Pest_array, 'tolist') else Pest))
        se_accum["Qest_array"].append(json.dumps(Qest_array.tolist() if hasattr(Qest_array, 'tolist') else Qest))
        se_accum["removed_residuals"].append(
            json.dumps(removed_residuals, default=lambda x: int(x) if isinstance(x, np.integer) else x)
        )

        # Write the accumulated state estimation results to CSV
        write_state_estimation_csv(se_accum)
        logging.info("Cycle %d: State estimation results saved in restructured CSV.", cycle + 1)

        time.sleep(monitoring_sleep)
        cycle += 1

except KeyboardInterrupt:
    logging.info("Dynamic state estimation loop terminated by user.")
    print("Terminated by user.")

