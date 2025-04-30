import psycopg2
def write_DB_CSL_BROKER_INPUT(t, POI_Va, POI_Vb, POI_Vc, f, POI_P, POI_Q, POI_Ia, POI_Ib, POI_Ic, POI_In, POI_U12, POI_U23, POI_U31, POI_U1, POI_U2, POI_U3, 
                          CT1_Vab, CT1_Vbc, CT1_Vca, CT1_Ia, CT1_Ib, CT1_Ic, CT1_P, CT1_Q, CT1_P_ref, CT1_Q_ref, 
                          CT2_Vab, CT2_Vbc, CT2_Vca, CT2_Ia, CT2_Ib, CT2_Ic, CT2_P, CT2_Q, CT2_P_ref, CT2_Q_ref,conexion):
    
    cursor=conexion.cursor()
    sql="insert into DB_CSL_BROKER_INPUT(Date_Time, V_POI_AB,V_POI_BC,V_POI_CA,OMEGA_POI,P_POI,Q_POI,I_POI_A,I_POI_B,I_POI_C,I_POI_N,V_POI_12,V_POI_23,V_POI_31,V_POI_1,V_POI_2,V_POI_3,V_CT1_AB,V_CT1_BC,V_CT1_CA,I_CT1_A,I_CT1_B,I_CT1_C,P_CT1,Q_CT1,P_CT1_REF,Q_CT1_REF,V_CT2_AB,V_CT2_BC,V_CT2_CA,I_CT2_A,I_CT2_B,I_CT2_C,P_CT2,Q_CT2,P_CT2_REF,Q_CT2_REF) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    data_input=((t,), POI_Va, POI_Vb, POI_Vc, f, POI_P, POI_Q, POI_Ia, POI_Ib, POI_Ic, POI_In, POI_U12, POI_U23, POI_U31, POI_U1, POI_U2, POI_U3, 
                              CT1_Vab, CT1_Vbc, CT1_Vca, CT1_Ia, CT1_Ib, CT1_Ic, CT1_P, CT1_Q, CT1_P_ref, CT1_Q_ref, 
                              CT2_Vab, CT2_Vbc, CT2_Vca, CT2_Ia, CT2_Ib, CT2_Ic, CT2_P, CT2_Q, CT2_P_ref, CT2_Q_ref)
    cursor.execute(sql, data_input)
    conexion.commit()
