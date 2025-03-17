import psycopg2

#Function for reading from the remote data base    
def read_DB_CSL_BROKER_INPUT(db_host,db_port,db_user,db_password,db_name,conexion):

    # conexion2 = psycopg2.connect(
    #     host=db_host,
    #     port=db_port,
    #     user=db_user,
    #     password=db_password,
    #     dbname=db_name
    # )
    cursor=conexion.cursor()
    cursor.execute("select Date_Time, POI_Va,POI_P,POI_Q,CT1_Vab,CT1_P,CT1_Q,CT2_Vab,CT2_P,CT2_Q from DB_CSL_BROKER_INPUT")
    #for data in cursor:
    data = cursor.fetchone()
    while data:
       # Date_Time_DB = data[0]
        V_POI_DB = data[1]
        P_POI_DB = data[2]
        Q_POI_DB = data[3]
        V_CT1_DB = data[4]
        P_CT1_DB = data[5]
        Q_CT1_DB = data[6]
        V_CT2_DB = data[7]
        P_CT2_DB = data[8]
        Q_CT2_DB = data[9]
        data = cursor.fetchone()
    #conexion.close()

            
    return V_POI_DB, V_CT1_DB, V_CT2_DB, P_POI_DB, Q_POI_DB, P_CT1_DB, Q_CT1_DB, P_CT2_DB, Q_CT2_DB