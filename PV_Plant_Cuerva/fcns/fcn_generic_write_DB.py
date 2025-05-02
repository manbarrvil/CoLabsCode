import psycopg2
def write_DB(t, POI_Va, POI_Vb, POI_Vc, f, POI_P, POI_Q, POI_Ia, POI_Ib, POI_Ic, POI_In, POI_U1, POI_U2, POI_U3, 
                          CT1_Vab, CT1_Vbc, CT1_Vca, CT1_Ia, CT1_Ib, CT1_Ic, CT1_P, CT1_Q, CT1_P_ref, CT1_Q_ref, 
                          CT2_Vab, CT2_Vbc, CT2_Vca, CT2_Ia, CT2_Ib, CT2_Ic, CT2_P, CT2_Q, CT2_P_ref, CT2_Q_ref,conexion,data_json):
    

    data_input=(t, POI_Va, POI_Vb, POI_Vc, f, POI_P, POI_Q, POI_Ia, POI_Ib, POI_Ic, POI_In, POI_U1, POI_U2, POI_U3, 
                            CT1_Vab, CT1_Vbc, CT1_Vca, CT1_Ia, CT1_Ib, CT1_Ic, CT1_P, CT1_Q, CT1_P_ref, CT1_Q_ref, 
                            CT2_Vab, CT2_Vbc, CT2_Vca, CT2_Ia, CT2_Ib, CT2_Ic, CT2_P, CT2_Q, CT2_P_ref, CT2_Q_ref)
    columns = []
    config = []
    for item in data_json["devices"]:
        config = (item['config'])
        DB_name = (item['DB'])

        for measurement in data_json["configs"][config]['measurements']:
            # Verificar que 'DB_name' exista en la medición
            if 'DB_name' in measurement:
                columns.append(measurement['DB_name'])
            else:
                print(f"Advertencia: Falta 'DB_name' en la medición: {measurement}")

    # Crear cadena de columnas y placeholders
    columns_str = ", ".join(["Date_Time"] + columns)
    placeholders = ", ".join(["%s"] * (len(columns) + 1))

    sql = f"INSERT INTO {DB_name} ({columns_str}) VALUES ({placeholders})"

    cursor=conexion.cursor()
    cursor.execute(sql, data_input)
    conexion.commit()
 

