# -*- coding: utf-8 -*-
"""
Created on Thu Apr 24 15:48:37 2025

@author: sim-intel
"""
from pymongo import MongoClient

#Function for reading from the remote data base    
#def read_DB_Mongo(db_server_db_port,db_name,db_collection):
def read_DB_Mongo(documents):

    # Connect to MongoDB server
    #client = MongoClient("mongodb://172.17.3.239:27017/")  # Replace with your MongoDB URI
    
    # # Access a specific database
    # db = client[db_name]  # Replace 'my_database' with your database name
    
    # # Access a specific collection
    # collection = db[db_collection]  # Replace 'my_collection' with your collection name
    
    # # Retrieve all documents in the collection
    # documents = collection.find()
    #print(documents)
    # Iterate through the documents
    for doc in documents:
        name_signal=doc.get("tagName")
        last_value = doc.get("history", [])[-1]['value'] if doc.get("history") else None
        #last_value = doc.get("history","valor")[-1]['value']
    #    print (doc.get("IdSignal"))
    #    print(doc.get("tagName"),':',last_value) 
        if name_signal=='POI.VoltageA':
            V_POI_DB = last_value
            print(V_POI_DB)
        elif name_signal=='POI.ActivePower':
            P_POI_DB = last_value
        elif name_signal=='POI.ReactivePower':
            Q_POI_DB = last_value
        elif name_signal=='CT01.VoltageAB':
            V_CT1_DB = last_value
        elif name_signal=='CT01.ActivePower':
            P_CT1_DB = last_value
        elif name_signal=='CT01.ReactivePower':
            Q_CT1_DB = last_value
        elif name_signal=='CT02.VoltageAB':
            V_CT2_DB = last_value
        elif name_signal=='CT02.ActivePower':
            P_CT2_DB = last_value
        elif name_signal=='CT02.ReactivePower':
            Q_CT2_DB = last_value
        #print (name_signal, '--->' ,last_value)
    

    return V_POI_DB, V_CT1_DB, V_CT2_DB, P_POI_DB, Q_POI_DB, P_CT1_DB, Q_CT1_DB, P_CT2_DB, Q_CT2_DB
    # if name_signal and name_signal.endswith('.ActivePower'):
    #     print(name_signal,':' , last_value)
    

# Retrieve documents with a query
# query = {"age": {"$gt": 25}}  # Example query: find documents where age > 25
# filtered_docs = collection.find(query)

# print("\nFiltered documents:")
# for doc in filtered_docs:
#     print(doc)

# Close the connection

