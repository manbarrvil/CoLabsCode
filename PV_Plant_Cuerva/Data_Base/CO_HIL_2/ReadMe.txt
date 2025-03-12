-File 'DB_CSL_BROKER_PostgreSQL.py' is a python scripts with the following functions:
1. read_elec_POI. It is a modbus client for reading all the measurements from the server corresponding to the PLC
2. read_elec_CT1. It is a modbus client for reading all the measurements/references from the server corresponding to the CT1
3. read_elec_CT2. It is a modbus client for reading all the measurements/references from the server corresponding to the CT2
4. write_DB_CSL_BROKER_INPUT. It is a function for writing in the table DB_CSL_BROKER_INPUT of the data base DB_CSL_Broker, all the measurements/references collected in the previous functions