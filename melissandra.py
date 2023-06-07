#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pymysql
import sys
import datosEstacion

parametro = sys.argv
est = datosEstacion.informacion()
act = "si"

db = pymysql.connect(host="localhost",
                     user= est.getUser(),
                     password= est.getPassword(),
                     database = est.getDB(),
                     charset = "utf8mb4",
                     cursorclass=pymysql.cursors.DictCursor)

cursor = db.cursor()
def comprobacion():
    cursor.execute("call sfl_comprobacion()")
    datos = cursor.fetchall()
    dic = datos[0]
    for data in dic:
        d2 = str(dic[data])
        d1 = data.replace("_"," ")
        d1 = d1.replace(d1[0],d1[0].upper())
        d2 = d2.replace("$x","\U0000274c")
        d2 = d2.replace("$b","\U00002714")
        d2 = d2.replace("$p","\U0001f4cc")
        d2 = d2.replace("$f","\U0001f600")
        d2 = d2.replace("$t","\U00002639")
        d2 = d2.replace("$a","\U000026A0")
        d2 = d2.replace("$i","\U00002753")
        d2 = d2.replace("$r","\U00002699")
        d2 = d2.replace("$l","\U0001f527")
        print(d1+": "+ d2)
    print(";"+ str(getTotal()))
    db.close()
 
def getTotal():
    cursor.execute("call sfl_comprobacion()")
    datos = cursor.fetchall()
    dic = datos[0]
    for data in dic:
        if data.upper() == "COLA_FACTURAS" or data.upper() == "COLAFACTURAS":
            return(dic[data])
            break
    db.close()
    
def offline(tipo):
    cursor.execute("call sfl_offline('"+tipo+"')")
    datos = cursor.fetchall()
    for data in datos[0]:
        print(datos[0][data])
    db.close()
    
def setGestion():
    cursor.execute("select * from con_gestion order by id_gestion desc limit 1")
    datos = cursor.fetchall()
    suc = ""
    dic = datos[0]
    for data in dic:
        if data == "id_sucursal":
            suc=str(dic[data])
            break
    for data in dic:
        if data == "gestion":
            cursor.execute("insert into con_gestion values(0,"+str(dic[data]+1)+","+suc+")")
            db.commit()
            print("Actualizado a gestion "+str(dic[data]+1))
            break
    db.close()
    
def getGestion():
    cursor.execute("select * from con_gestion order by id_gestion desc limit 1")
    datos = cursor.fetchall()
    for data in datos[0]:
        print(str(datos[0][data]))
    db.close()
    
    
def getDatos():
    print(est.getNombre(),est.getGrupo(),est.getRegion(),est.getDepartamento(),est.getManto(),sep=',')
    
def getDatosTotal():
    print(est.getNombre(),est.getDireccion(),est.getGrupo(),est.getRegion(),est.getDepartamento(),est.getManto(),
          est.getPassword(),est.getDB(),est.getUser(),sep=",")
    
def activado():
    print(act)

if parametro[1] == "comprobacion":
    comprobacion()
elif parametro[1] == "getGestion":
    getGestion()
elif parametro[1] == "setGestion":
    setGestion()
elif parametro[1] == "total":
    getTotal()
elif parametro[1] == "off":
    offline("off")
elif parametro[1] == "on":
    offline("on")
elif parametro[1] == "estado":
    offline("estado")
elif parametro[1] == "datos":
    getDatos()
elif parametro[1] == "ttottal":
    getDatosTotal()
elif parametro[1] == "activado":
    activado()