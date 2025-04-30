import psycopg2
def write_DB_CSL_BROKER_INPUT(t, POI_Va, POI_Vb, POI_Vc, f, POI_P, POI_Q, POI_Ia, POI_Ib, POI_Ic, POI_In, POI_U12, POI_U23, POI_U31, POI_U1, POI_U2, POI_U3, 
                          CT1_Vab, CT1_Vbc, CT1_Vca, CT1_Ia, CT1_Ib, CT1_Ic, CT1_P, CT1_Q, CT1_P_ref, CT1_Q_ref, 
                          CT2_Vab, CT2_Vbc, CT2_Vca, CT2_Ia, CT2_Ib, CT2_Ic, CT2_P, CT2_Q, CT2_P_ref, CT2_Q_ref,conexion,data):
    # Inicializar la lista de columnas
    columns = []

    # Recorrer todos los tipos en "configs" (como "poi", "inv", etc.)
    for type_key, type_data in data["configs"].items():
        if "measurements" in type_data:
            # Extraer los nombres de las columnas (DB_name) si existen
            columns.extend([item["DB_name"] for item in type_data["measurements"] if "DB_name" in item])
    columns_str = ", ".join(columns)

    cursor=conexion.cursor()
    sql=f"insert into DB_CSL_BROKER_INPUT(Date_Time, {columns_str}) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    data_input=((t,), POI_Va, POI_Vb, POI_Vc, f, POI_P, POI_Q, POI_Ia, POI_Ib, POI_Ic, POI_In, POI_U12, POI_U23, POI_U31, POI_U1, POI_U2, POI_U3, 
                              CT1_Vab, CT1_Vbc, CT1_Vca, CT1_Ia, CT1_Ib, CT1_Ic, CT1_P, CT1_Q, CT1_P_ref, CT1_Q_ref, 
                              CT2_Vab, CT2_Vbc, CT2_Vca, CT2_Ia, CT2_Ib, CT2_Ic, CT2_P, CT2_Q, CT2_P_ref, CT2_Q_ref)
    cursor.execute(sql, data_input)
    conexion.commit()