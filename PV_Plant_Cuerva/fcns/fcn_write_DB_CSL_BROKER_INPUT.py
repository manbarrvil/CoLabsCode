import psycopg2
def write_DB_CSL_BROKER_INPUT(t, POI_Va, POI_Vb, POI_Vc, f, POI_P, POI_Q, POI_Ia, POI_Ib, POI_Ic, POI_In, POI_U12, POI_U23, POI_U31, POI_U1, POI_U2, POI_U3, 
                          CT1_Vab, CT1_Vbc, CT1_Vca, CT1_Ia, CT1_Ib, CT1_Ic, CT1_P, CT1_Q, CT1_P_ref, CT1_Q_ref, 
                          CT2_Vab, CT2_Vbc, CT2_Vca, CT2_Ia, CT2_Ib, CT2_Ic, CT2_P, CT2_Q, CT2_P_ref, CT2_Q_ref,conexion):
    
    cursor=conexion.cursor()
    sql="insert into DB_CSL_BROKER_INPUT(Date_Time, Ua_POI,Ub_POI,Uc_POI,F_POI,P_POI,Q_POI,Ia_POI,Ib_POI,Ic_POI,In_POI,U12_POI,U23_POI,U31_POI,U1_POI,U2_POI,U3_POI,Uab_CT1,Ubc_CT1,Uca_CT1,Ia_CT1,Ib_CT1,Ic_CT1,P_CT1,Q_CT1,P_REF_CT1,Q_REF_CT1,Uab_CT2,Ubc_CT2,Uca_CT2,Ia_CT2,Ib_CT2,Ic_CT2,P_CT2,Q_CT2,P_REF_CT2,Q_REF_CT2) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    data_input=((t,), POI_Va, POI_Vb, POI_Vc, f, POI_P, POI_Q, POI_Ia, POI_Ib, POI_Ic, POI_In, POI_U12, POI_U23, POI_U31, POI_U1, POI_U2, POI_U3, 
                              CT1_Vab, CT1_Vbc, CT1_Vca, CT1_Ia, CT1_Ib, CT1_Ic, CT1_P, CT1_Q, CT1_P_ref, CT1_Q_ref, 
                              CT2_Vab, CT2_Vbc, CT2_Vca, CT2_Ia, CT2_Ib, CT2_Ic, CT2_P, CT2_Q, CT2_P_ref, CT2_Q_ref)
    cursor.execute(sql, data_input)
    conexion.commit()
    #conexion1.close()