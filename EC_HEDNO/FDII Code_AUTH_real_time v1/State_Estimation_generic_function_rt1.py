import numpy as np
from observability_check import observability_check
from residuals_simple import residuals

def State_Estimation_generic_function(estimation, column_rank, num_buses, hashmap_names2, hashmap_reduction2, mes_positions_p, mes_positions_q, mes_positions_v, H_v_full, H_p_full, H_q_full, slack_bus_row_P, slack_bus_row_Q, mes_positions_virtual, slack_bus, Pmesp, Qmesp, Vmesp, Std_P, Std_Q, Std_V, mes_p, mes_q, mes_v,Vest, Pest, Qest):
          
    removed_residuals = []

    # estimation.solve(solver="CONOPT")
    estimation.solve(solver="IPOPT")
    
    max_residual_measurement_type, max_residual_bus_index, max_residual_val, Pest_array, Qest_array, Vest_array, normalized_residuals_V, indices_v_test= residuals(Pest, Qest, Vest, Pmesp, Qmesp, Vmesp, Std_P, Std_Q, Std_V, mes_p, mes_q, mes_v)
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
            column_rank = observability_check(mes_positions_p, mes_positions_q, mes_positions_v, num_buses, H_v_full, H_p_full, H_q_full, mes_positions_virtual, slack_bus, slack_bus_row_P, slack_bus_row_Q)
            # Exit loop if column_rank is less than the required value
            if column_rank < (num_buses - 1) * 2:
                print("Column rank is less than required value, exiting loop.")
                break

            mes_p.setRecords(np.where(mes_positions_p.copy()==1)[0])
            mes_q.setRecords(np.where(mes_positions_q.copy()==1)[0])
            mes_v.setRecords(np.where(mes_positions_v.copy()==1)[0])
            # estimation.solve(solver="CONOPT")
            estimation.solve(solver="IPOPT")
            max_residual_measurement_type, max_residual_bus_index, max_residual_val, Pest_array, Qest_array, Vest_array, normalized_residuals_V,indices_v = residuals(Pest, Qest, Vest, Pmesp, Qmesp, Vmesp, Std_P, Std_Q, Std_V, mes_p, mes_q, mes_v)
    else:
        print("No BDD needed")
    
    return Vest_array, Pest_array, Qest_array, removed_residuals, Vmesp.records['value'].values, normalized_residuals_V,indices_v_test