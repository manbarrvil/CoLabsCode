import psycopg2

try:
    # Connection to the data base
    conn = psycopg2.connect(
        database="products", #This data base must be created in PostgreSQL using pgAdmin4
        user='postgres', #Replace by your username
        password='postgres', #Replace by your password
        host='localhost', #local host or IP enabled for accessing in remote mode
        port= '5432' #usual local port enabled in PostgreSQL
    )

    # Creaation of a cursor
    cur = conn.cursor()

    # Define the name of the table and structure
    # In this case, a table called 'usuarios_v1' is created
    create_table_query = """
    CREATE TABLE IF NOT EXISTS usuarios_v1 (
        id SERIAL PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    # Execute the command for creating the tableEjecutar el comando para crear la tabla
    cur.execute(create_table_query)

    # Confirma changes
    conn.commit()

    print("Table 'usuarios_v1' is succesfully created.")

    # close cursor and conecction
    cur.close()
    conn.close()

except Exception as e:
    print(f"Exist an error: {e}")

