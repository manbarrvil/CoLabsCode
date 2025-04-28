# -*- coding: utf-8 -*-
"""
Created on Thu Apr 24 17:47:39 2025

@author: sim-intel
"""
from datetime import datetime
import time
from pymongo import MongoClient

# Conexión a MongoDB
client = MongoClient("mongodb://172.17.3.239:27017/")  # Cambia esto por tu URI si usas MongoDB Atlas

# Accede a una base de datos
db = client["scada"]  # Cambia 'mi_base_de_datos' por el nombre de tu base de datos

# Accede a una colección
collection = db["signals"]  # Cambia 'mi_coleccion' por el nombre de tu colección
id_signal = "1234"
# id_especifico = "12345"
# filtro = {"_id": id_especifico}
# # Insertar un documento
# documento = {"IdSignal": "Est_01", "tagName": "Estimador.POI.ActivePower", "$push":{"history":[{"value":8.0, "timeStamp":time.time()}]} }

# resultado = collection.update_one(filtro,documento)

collection.update_one(
    {"_id": id_signal,"tagName":"Estimador.POI.ActivePower" },
    {
     
         "$set":{
             "history": {
                 "value": 9.0,
                 #"timeStamp": datetime.utcnow()
                 }
             }
             
             
     },
    upsert=False
    
    )
#print(f"Documento insertado con ID: {resultado.inserted_id}")

# # Insertar múltiples documentos
# documentos = [
#     {"nombre": "Ana", "edad": 25, "ciudad": "Barcelona"},
#     {"nombre": "Luis", "edad": 35, "ciudad": "Sevilla"},
#     {"nombre": "Marta", "edad": 40, "ciudad": "Valencia"}
# ]
# resultados = collection.insert_many(documentos)
# print(f"Documentos insertados con IDs: {resultados.inserted_ids}")
