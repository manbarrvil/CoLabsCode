import psycopg2

#Function for writing into the remote data base        
def write_DB_CSL_BROKER_OUTPUT(t, V_POI_EST, V_SS1_EST, V_SS2_EST, P_SS1_SS2, P_SS2_POI, P_POI_POI, Q_SS1_SS2, Q_SS2_POI, Q_POI_POI,db_host,db_port,db_user,db_password,db_name,conexion):
    # conexion3 = psycopg2.connect(
    #     host=db_host,
    #     port=db_port,
    #     user=db_user,
    #     password=db_password,
    #     dbname=db_name
    # )
    cursor=conexion.cursor()
    sql="insert into DB_CSL_BROKER_OUTPUT(Date_Time, V_POI_EST,V_SS1_EST,V_SS2_EST,P_SS1_SS2,P_SS2_POI,P_POI_POI,Q_SS1_SS2,Q_SS2_POI,Q_POI_POI) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    data_ouput=((t,), V_POI_EST, V_SS1_EST, V_SS2_EST, P_SS1_SS2, P_SS2_POI, P_POI_POI, Q_SS1_SS2, Q_SS2_POI, Q_POI_POI)
    cursor.execute(sql, data_ouput)
    conexion.commit()
    #conexion.close()