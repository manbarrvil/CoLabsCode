Data base is the open source PostgreSQL. It is download from:
https://www.postgresql.org/

The name assigned to the Data Base is: DB_CSL_Broker. This is created using pgAdmin4 (Management tool of PostgreSQL)
The user is the one when you install PostgreSQL
The password is the one when you install PostgreSQL


-File 'sql_DB_CSL_Broker.txt' is the sql code for creating the table in the data base called DB_CSL_Broker
-File 'DB_CSL_BROKER_bup' is a backup of the SQL server for importing the table in the Query of pgAdmin4 (Management tool of PostgreSQL)
Both files allow to create two Tables in the DB_CSL_Broker:
DB_CSL_Broker_Input contains the measurements from POI, SS1 SS2
DB_CSL_Broker_Output contains the estimated values from the State Estimator

By default, the DB is created in the localhost.

For enabling a remote access to the DB follow this link:
https://quike.it/es/como-configurar-acceso-remoto-postgresql/#elementor-toc__heading-anchor-5

-File 'test_create_db.py' is a test code for creating a data base from a python scripts