import numpy as np

def residuals(Pest, Qest, Vest, Pmesp, Qmesp, Vmesp, 
              Std_P, Std_Q, Std_V, mes_p, mes_q, mes_v):
    # Extract arrays from input data
    Pest_array = Pest.records['level'] if Pest is not None and Pest.records is not None and not Pest.records.empty else []
    Pmesp_array = Pmesp.records['value'] if Pmesp is not None and Pmesp.records is not None and not Pmesp.records.empty else []
    Std_P_array = Std_P.records['value']
    indices_p = np.array(mes_p.records['i'].astype(int)) if mes_p is not None and mes_p.records is not None and not mes_p.records.empty else []

    Qest_array = Qest.records['level'] if Qest is not None and Qest.records is not None and not Qest.records.empty else []
    Qmesp_array = Qmesp.records['value'] if Qmesp is not None and Qmesp.records is not None and not Qmesp.records.empty else []
    Std_Q_array = Std_Q.records['value']
    indices_q = np.array(mes_q.records['i'].astype(int)) if mes_q is not None and mes_q.records is not None and not mes_q.records.empty else []

    Vest_array = Vest.records['level'] if Vest is not None and Vest.records is not None and not Vest.records.empty else []
    Vmesp_array = Vmesp.records['value'] if Vmesp is not None and Vmesp.records is not None and not Vmesp.records.empty else []
    Std_V_array = Std_V.records['value']
    indices_v = np.array(mes_v.records['i'].astype(int)) if mes_v is not None and mes_v.records is not None and not mes_v.records.empty else []

    # Helper function to compute normalized residuals
    def compute_residuals(est, meas, std, indices):
        valid_indices = [int(i) for i in indices if isinstance(i, int) or str(i).isdigit()]
        valid_indices = [i for i in valid_indices if i < len(est)]
        return np.array([abs(est[i] - meas[i]) / std[i] for i in valid_indices])
    
    normalized_residuals_P = compute_residuals(Pest_array, Pmesp_array, Std_P_array, indices_p)
    normalized_residuals_Q = compute_residuals(Qest_array, Qmesp_array, Std_Q_array, indices_q)
    normalized_residuals_V = compute_residuals(Vest_array, Vmesp_array, Std_V_array, indices_v)
    
    # Combine all normalized residuals into one array
    all_normalized_residuals = np.concatenate((normalized_residuals_P, normalized_residuals_Q, normalized_residuals_V))
    
    # Identify the maximum residual and its index
    max_residual_index = np.argmax(all_normalized_residuals)
    max_residual_val = np.max(all_normalized_residuals)
    
    # Determine the measurement type and the corresponding bus index
    len_P = len(normalized_residuals_P)
    len_Q = len(normalized_residuals_Q)
    
    if max_residual_index < len_P:
        measurement_type = 'P'
        bus_index = indices_p[max_residual_index]
    elif max_residual_index < len_P + len_Q:
        measurement_type = 'Q'
        bus_index = indices_q[max_residual_index - len_P]
    else:
        measurement_type = 'V'
        bus_index = indices_v[max_residual_index - len_P - len_Q]
    
    return measurement_type, bus_index, max_residual_val, Pest_array, Qest_array, Vest_array, normalized_residuals_V,indices_v
