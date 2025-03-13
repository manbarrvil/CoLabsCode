import numpy as np
from Information_extraction_function_clean import extract_info
from basic_plausibility import filter_measurements
from State_Estimation_meas_process import process_power_system_data
from observability_check import observability_check
from State_Estimation_execute_simple import State_Estimation_execute
from residuals_simple import residuals

def State_Estimation_generic_function(data_filepath, measurement_filepath, measurement_sheet_name):

    # Extract information from the specified sheet of the data file
    m,i,j,k,n,i2,i3,hashmap_bus, hashmap_branch, hashmap_parent, Rp,Xp,Gp, Bp, num_buses, slack_bus,der_positions_ratings, hashmap_names, hashmap_reduction, Ybus, Bshunt, Gshunt, hashmap_bus2, hashmap_branch2, zero_injection_buses, hashmap_reduction2, hashmap_names2, H_v_full, H_p_full, H_q_full, slack_bus_row_P, slack_bus_row_Q, injection_buses= extract_info(data_filepath)
    
    mes_positions_p, mes_positions_q, mes_positions_v, mes_positions_pflow, mes_positions_qflow, Pmes, Qmes, Vmes, Pflow_mes, Qflow_mes =process_power_system_data(measurement_filepath, measurement_sheet_name, num_buses, der_positions_ratings, slack_bus,hashmap_names, hashmap_reduction, injection_buses)
    column_rank=observability_check(mes_positions_p, mes_positions_q, mes_positions_v, num_buses, H_v_full, H_p_full, H_q_full, zero_injection_buses, slack_bus, slack_bus_row_P, slack_bus_row_Q)
    std_vector_v = np.ones(num_buses)
    std_vector_p = np.ones(num_buses)
    std_vector_q = np.ones(num_buses)
    
    std_vector_v[injection_buses]=0.0016666666666666668
    std_vector_p[injection_buses]=0.005666666666666667
    std_vector_q[injection_buses]=0.013333333333333334
    
    removed_residuals = []
    
    
    if column_rank == (num_buses - 1) * 2:
        Vest, Pest, Qest, Vmesp, Pmesp, Qmesp, Std_V, Std_P, Std_Q, mes_v, mes_p, mes_q = State_Estimation_execute(m, num_buses, mes_positions_p, mes_positions_q, mes_positions_v, mes_positions_pflow, mes_positions_qflow, zero_injection_buses, Pmes, Qmes, Vmes, Pflow_mes, Qflow_mes, slack_bus, Rp, Xp, Gp, Bp, hashmap_parent, hashmap_bus, hashmap_branch, hashmap_bus2, i, i2, i3, n, j, k, std_vector_p, std_vector_q, std_vector_v)
        max_residual_measurement_type, max_residual_bus_index, max_residual_index, max_residual_val, residuals_df_P, residuals_df_Q, residuals_df_V, Pest_array, Qest_array, Vest_array, Pmesp_array, Qmesp_array, Vmesp_array = residuals(Pest, Qest, Vest, Pmesp, Qmesp, Vmesp, Std_P, Std_Q, Std_V, mes_p, mes_q, mes_v, hashmap_reduction2, hashmap_names2)
        max_residual_val_init = max_residual_val.copy()
        
        if max_residual_val_init > 3:
            print("BDD to be performed")
            while max_residual_val > 3 and column_rank == (num_buses - 1) * 2:
    
                removed_residuals.append((
                    max_residual_measurement_type, 
                    max_residual_bus_index, 
                    hashmap_names2.get(hashmap_reduction2.get(max_residual_bus_index, ""), "Unknown Bus")
                ))
                if max_residual_measurement_type == 'P':
                    mes_positions_p[max_residual_bus_index] = 0
                elif max_residual_measurement_type == 'Q':
                    mes_positions_q[max_residual_bus_index] = 0
                elif max_residual_measurement_type == 'V':
                    mes_positions_v[max_residual_bus_index] = 0
                
                # Check observability and update column_rank
                column_rank = observability_check(mes_positions_p, mes_positions_q, mes_positions_v, num_buses, H_v_full, H_p_full, H_q_full, zero_injection_buses, slack_bus, slack_bus_row_P, slack_bus_row_Q)
                
                # Exit loop if column_rank is less than the required value
                if column_rank < (num_buses - 1) * 2:
                    print("Column rank is less than required value, exiting loop.")
                    break
                
                Vest, Pest, Qest, Vmesp, Pmesp, Qmesp, Std_V, Std_P, Std_Q, mes_v, mes_p, mes_q = State_Estimation_execute(m, num_buses, mes_positions_p, mes_positions_q, mes_positions_v, mes_positions_pflow, mes_positions_qflow, zero_injection_buses, Pmes, Qmes, Vmes, Pflow_mes, Qflow_mes, slack_bus, Rp, Xp, Gp, Bp, hashmap_parent, hashmap_bus, hashmap_branch, hashmap_bus2, i, i2, i3, n, j, k, std_vector_p, std_vector_q, std_vector_v)
                max_residual_measurement_type, max_residual_bus_index, max_residual_index, max_residual_val, residuals_df_P, residuals_df_Q, residuals_df_V, Pest_array, Qest_array, Vest_array, Pmesp_array, Qmesp_array, Vmesp_array = residuals(Pest, Qest, Vest, Pmesp, Qmesp, Vmesp, Std_P, Std_Q, Std_V, mes_p, mes_q, mes_v, hashmap_reduction2, hashmap_names2)
        else:
            print("No BDD needed")
    else:
        # Print a message indicating that the system is unobservable
        print("The system is unobservable, no state estimation can be performed.")

    return max_residual_measurement_type, max_residual_bus_index, max_residual_index, max_residual_val, Vest_array, Pest_array, Qest_array, Vmesp_array, Pmesp_array, Qmesp_array, residuals_df_P, residuals_df_Q, residuals_df_V, removed_residuals
    
