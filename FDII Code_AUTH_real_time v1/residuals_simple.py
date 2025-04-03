import pandas as pd
import numpy as np

def residuals(Pest, Qest, Vest, Pmesp, Qmesp, Vmesp, Std_P, Std_Q, Std_V, mes_p, mes_q, mes_v, hashmap_reduction2, hashmap_names2):
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

    # Function to compute residuals with validation
    def compute_residuals(est, meas, std, indices):
        # Ensure indices are valid integers and within range
        valid_indices = [int(i) for i in indices if isinstance(i, int) or str(i).isdigit()]
        valid_indices = [i for i in valid_indices if i < len(est)]
        return np.array([abs(est[i] - meas[i]) / std[i] for i in valid_indices])

    # Compute normalized residuals for P, Q, and V
    normalized_residuals_P = compute_residuals(Pest_array, Pmesp_array, Std_P_array, indices_p)
    normalized_residuals_Q = compute_residuals(Qest_array, Qmesp_array, Std_Q_array, indices_q)
    normalized_residuals_V = compute_residuals(Vest_array, Vmesp_array, Std_V_array, indices_v)

    # Create DataFrames for residuals with bus names
    def create_residuals_dataframe(indices, residuals, hashmap_reduction2, hashmap_names2):
        bus_names = [
            hashmap_names2[hashmap_reduction2[new_index]]
            for new_index in indices
            if new_index in hashmap_reduction2 and hashmap_reduction2[new_index] in hashmap_names2
        ]
        return pd.DataFrame({'Bus Name': bus_names, 'Normalized Residual': residuals})

    residuals_df_P = create_residuals_dataframe(indices_p, normalized_residuals_P, hashmap_reduction2, hashmap_names2)
    residuals_df_Q = create_residuals_dataframe(indices_q, normalized_residuals_Q, hashmap_reduction2, hashmap_names2)
    residuals_df_V = create_residuals_dataframe(indices_v, normalized_residuals_V, hashmap_reduction2, hashmap_names2)

    # Concatenate all normalized residuals into a single array
    all_normalized_residuals = np.concatenate((normalized_residuals_P, normalized_residuals_Q, normalized_residuals_V))

    # Find the index of the maximum residual
    max_residual_index = np.argmax(all_normalized_residuals)
    max_residual_val = np.max(all_normalized_residuals)

    # Determine the length of each residual type array
    len_P = len(normalized_residuals_P)
    len_Q = len(normalized_residuals_Q)

    # Identify the measurement type and index
    if max_residual_index < len_P:
        measurement_type = 'P'
        bus_index = indices_p[max_residual_index]
    elif max_residual_index < len_P + len_Q:
        measurement_type = 'Q'
        bus_index = indices_q[max_residual_index - len_P]
    else:
        measurement_type = 'V'
        bus_index = indices_v[max_residual_index - len_P - len_Q]

    # Find the corresponding estimate and measurement values
    estimate_value = Pest_array[bus_index] if measurement_type == 'P' else Qest_array[bus_index] if measurement_type == 'Q' else Vest_array[bus_index]
    measurement_value = Pmesp_array[bus_index] if measurement_type == 'P' else Qmesp_array[bus_index] if measurement_type == 'Q' else Vmesp_array[bus_index]

    return measurement_type, bus_index, max_residual_index, max_residual_val, residuals_df_P, residuals_df_Q, residuals_df_V, Pest_array, Qest_array, Vest_array, Pmesp_array, Qmesp_array, Vmesp_array
