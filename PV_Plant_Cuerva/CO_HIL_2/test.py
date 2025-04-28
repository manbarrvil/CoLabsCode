import psycopg2

db_host = '192.168.40.10'  # Address of the remote PostgreSQL serverQL
db_port = 5432  # PostgreSQL server port (default is 5432)
db_user = 'postgres'  # Username for the database
db_password = 'postgres'  # Password for the database
db_name = 'DB_CSL_BROKER'  # name for the databases  

conexion = psycopg2.connect(
    host=db_host,
    port=db_port,
    user=db_user,
    password=db_password,
    dbname=db_name
)
cursor=conexion.cursor()
cursor.execute("select Date_Time, POI_Va,POI_P,POI_Q,CT1_Vab,CT1_P,CT1_Q,CT2_Vab,CT2_P,CT2_Q FROM DB_CSL_BROKER_INPUT ORDER BY Date_Time DESC LIMIT 1")

data = cursor.fetchone()
while data:
    Date_Time_DB = data[0]
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


print(V_CT1_DB)