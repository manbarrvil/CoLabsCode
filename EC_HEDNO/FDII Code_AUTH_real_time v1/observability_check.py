import numpy as np

def observability_check(mes_positions_p, mes_positions_q, mes_positions_v, num_buses, H_v_full, H_p_full, H_q_full, mes_positions_virtual, slack_bus, slack_bus_row_P, slack_bus_row_Q):
        
    mes_positions_p_full = np.logical_or(mes_positions_p, mes_positions_virtual).astype(int)
    mes_positions_q_full = np.logical_or(mes_positions_q, mes_positions_virtual).astype(int)
    mes_positions_v_full = mes_positions_v
    
    mes_positions_p_no_slack = np.delete(mes_positions_p_full, slack_bus)
    mes_positions_q_no_slack = np.delete(mes_positions_q_full, slack_bus)
    mes_positions_v_no_slack = np.delete(mes_positions_v_full, slack_bus)
    
    H_v = H_v_full[mes_positions_v_no_slack.astype(bool)]
    H_p = H_p_full[mes_positions_p_no_slack.astype(bool)]
    H_q = H_q_full[mes_positions_q_no_slack.astype(bool)]
    
    H = np.vstack((H_p, H_q, H_v, slack_bus_row_P, slack_bus_row_Q))
    column_rank = np.linalg.matrix_rank(H, tol=None)
    
    return column_rank




