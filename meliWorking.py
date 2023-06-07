#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
import datetime
import time
import random
import requests
import pymysql
import subprocess
import datosEstacion


act = True


def registrar(actividad):
    # Configuración básica de logging
    logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(levelname)s - %(message)s')#datefmt='%d-%m-%Y'

    # Obtener la fecha actual
    fecha_actual = datetime.datetime.now().strftime("%d-%m-%Y")

    # Obtener el nombre del archivo log
    nombre_archivo = f"/home/suport/melissandra/melilog_{fecha_actual}.log"

    # Configurar el logger para que guarde los logs en el archivo
    logger = logging.getLogger(__name__)
    handler = logging.FileHandler(nombre_archivo)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%d-%m-%Y_%H-%M')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info(actividad)
    handler.close()
    logger.removeHandler(handler)


#importamos los datos de la estacion
est = datosEstacion.informacion()

#nombre de la estacion
nombre = est.getNombre()

#tc es el tiempo de ciclo, es decir cada cuanto se hara una revision
tc = 60

db = pymysql.connect(
        host="localhost",user= est.getUser(),
        password= est.getPassword(),
        database = est.getDB(),
        charset = "utf8mb4",
        cursorclass=pymysql.cursors.DictCursor)

cursor = db.cursor()


#Esta funcion extrae los datos de una consulta en la base de datos y devuelve
#una lista de strings con los datos
def comprobacion():
    cursor.execute("call sfl_comprobacion")
    datos = cursor.fetchall()
    dic = datos[0]
    list = []
    for data in dic:
        d2 = str(dic[data])
        d1 = data.replace("_"," ")
        list.append(d1+": "+ d2)
    return list


#Esta funcion establece los parametros del chat a enviar
def enviarMensajeTelegram(message):
    bot_token = 'insertar_token_telegram_aqui'
    bot_chatID = 'insertar_chat_id_de_telegram_aqui'
    send_text = 'https://api.telegram.org/bot'+ bot_token+ '/sendMessage?chat_id='+ bot_chatID+ '&parse_mode=Markdown&text='+ message
    response = requests.get(send_text)
    return response.json()


#Envia mensajes al grupo
def enviarMensajeGrupal(bot_message):
    bot_token = 'insertar_token_telegram_aqui'
    bot_grupoID = 'insertar_id_del_grupo_de_telegram'
    send_text = 'https://api.telegram.org/bot'+ bot_token+ '/sendMessage?chat_id='+ bot_grupoID+ '&parse_mode=Markdown&text='+ bot_message
    response = requests.get(send_text)
    return response.json()


#esta funcion elimina cualquier archivo .log que tenga mas de 1 semana.
def eliminar():
    # Establecer el tiempo de antigüedad en segundos (1 semana = 604800 segundos)
    tiempo_antiguedad = 604800    
    # Obtener la fecha y hora actual en segundos
    tiempo_actual = time.time()
    # Ruta del directorio donde se encuentran los archivos .log
    ruta_directorio = "/home/suport/melissandra/"
    # Iterar a través de los archivos en el directorio
    for archivo in os.listdir(ruta_directorio):
        # Obtener la ruta completa del archivo
        ruta_archivo = os.path.join(ruta_directorio, archivo)
        # Comprobar si el archivo es un archivo .log y si tiene más de una semana de antigüedad
        if archivo.endswith(".log") and (tiempo_actual - os.path.getctime(ruta_archivo) > tiempo_antiguedad):
            # Eliminar el archivo
            os.remove(ruta_archivo)
            
            
dic1 = {1:"Hola, hay una factura trancada verificar por favor, "+nombre,
        2:"buenos dias, tardes o noches, hay facturas trancadas en "+nombre,
        3:"Aparentemente hay una o mas facturas trancadas en "+nombre,
        4:"Holis, en "+nombre+" hay facturitas trancadas, revisar por favor",
        5:"Siento molestar, pero aparentemente hay facturas trancadas en "+nombre}

dic1_1 = {1:"Hola, hay envios de correos trancados verificar por favor, "+nombre,
        2:"buenos dias, tardes o noches, hay envios de correos trancados en "+nombre,
        3:"Aparentemente hay uno o mas envios de correos pendientes en "+nombre,
        4:"Que tal, en "+nombre+" hay envio de correos trancados, revisar por favor",
        5:"Siento molestar, pero aparentemente hay envio de correos trancados en "+nombre}

dic1_2 = {1:"Hola, hay un pendiente bsisa verificar por favor, "+nombre,
          2:"buenos dias, tardes o noches, hay pendientes bsisa en "+nombre,
          3:"Aparentemente hay uno o mas pendientes bsisa en "+nombre,
          4:"Holis, en "+nombre+" hay pendiente bsisa, revisar por favor",
          5:"Siento molestar, pero aparentemente hay pendientes bsisa en "+nombre}

dic2 = {1:"¿Pudieron revisar?, aun hay pendientes en "+nombre,
        2:"No lo revisaron aun, ¿cierto?, todavia hay pendientes en "+nombre,
        3:"chicos,nuevamente les informo, hay pendientes en "+ nombre,
        4:"por favor revisar en "+nombre+ " todavia hay pendientes trancadas",
        5: "No se olviden, hay pendientes en "+nombre}

dic3 = {1:"No puedo creerlo que no hayan revisado aun, HAY FACTURAS TRANCADAS EN "+nombre,
        2:"A quien me tengo que quejar para que revisen, hay facturas trancadas en "+nombre,
        3:"HAY FACTURAS TRANCADAS EN "+nombre+", no podemos trabajar asi",
        4:"HAY FACTURAS TRANCADAS EN "+nombre+", hasta que hora va estar asi",
        5:"POR FAVOR REVISAR "+nombre+", ya esta desde hace un buen rato las facturas trancadas"}


#Establece el envio de una notificacion para el chat privado comprobando
#que este se envie en horario de oficina y que se use el mensaje correcto
def notificacion(num):
    horario_entrada = datetime.time(8, 0, 0)
    horario_salida = datetime.time(19, 0, 0)
    
    # Obtener la hora actual
    hora_actual = datetime.datetime.now().time()

    # Verificar si la hora actual está dentro del rango deseado
    if hora_actual >= horario_entrada and hora_actual <= horario_salida:
        # Enviar la notificación
        if num == 1:
            enviarMensajeTelegram(dic1[random.randint(1,5)])
        elif num == 2:
            enviarMensajeTelegram(dic1_1[random.randint(1,5)])
        elif num == 3:
            enviarMensajeTelegram(dic2[random.randint(1,5)])
        elif num == 4:
            enviarMensajeTelegram(dic1_2[random.randint(1,5)])


#Establece el envio de una notificacion para el chat del grupo comprobando
#que este se envie en horario de oficina y que se use el mensaje correcto
def notificacionGrupal(num):
    horario_entrada = datetime.time(8, 0, 0)
    horario_salida = datetime.time(19, 0, 0)
    
    # Obtener la hora actual
    hora_actual = datetime.datetime.now().time()

    # Verificar si la hora actual está dentro del rango deseado
    if hora_actual >= horario_entrada and hora_actual <= horario_salida:
        # Enviar la notificación
        if num == 1:
            enviarMensajeGrupal(dic1[random.randint(1,5)])
        elif num == 2:
            enviarMensajeGrupal(dic1_1[random.randint(1,5)])
        elif num == 3:
            enviarMensajeGrupal(dic2[random.randint(1,5)])
        elif num == 4:
            enviarMensajeGrupal(dic1_2[random.randint(1,5)])


#Esta funcion verifica si existe envios bsisa pendiente
def verificacionBsisa(intento):
    msg = comprobacion()
    for datos in msg:
        registrar(str(datos))
        
        if "Pendiente Bsisa" in datos:
            num = 0
            num_str = ''
            for char in datos:
                if char.isdigit():
                    num_str += char

            if num_str != "":
                num = int(num_str)
                
            #se envia un notificacion cada hora
            if num >= 1 and intento > 60:
                notificacionGrupal(4)
                notificacion(4)
                intento = 0 
            elif num >= 1 and intento < 60:
                intento = intento + 1
            elif num == 0:
                intento = 0            
    return intento
                

#Esta funcion se encarga de verificar si en la consulta existe placas trancadas
def verificoGeneral(a,b,c,d):
    al = False
    off = False
    msg = comprobacion()
    for datos in msg:
        registrar(str(datos))
        
        #Si existe offline forzado o automatico en la consulta y la bandera de offline global esta en falso
        if "OFLINE FORZADO" in datos or "OFLINE AUTOMATICO" in datos and b == False:
            #se coloca la bandera offline global en verdadero
            b = True 
            
        #mismo caso que la primera condicional    
        if "OFLINE FORZADO" in datos or "OFLINE AUTOMATICO" in datos and off == False:
            #se coloca la bandera offline local en verdadero   
            off = True 
            
        #caso contrario si existe $x en la consulta y el offline local es falso y la alarma esta apagada(false)
        #y el offline global esta en falso
        elif "$x" in datos and off == False and a == False and b == False:
            num = 0
            num_str = ''
            for char in datos:
                if char.isdigit():
                    num_str += char

            if num_str != "":
                num = int(num_str)
                print(num)
                
            #si el tiempo en cola de las facturas es mayor a 10 minutos entonces se activa la alarma    
            if num > 10:
                al = True
                if "Pendiente Correos" in datos:
                    notificacion(2)
                else:
                    notificacion(1)
                registrar("Alarma activa")
            registrar("Dentro del primer ciclo")
        
        #Si hay $x en los datos y no esta en offline y la alarma esta activada entonces vuelvo a mandara notificacion
        elif "$x" in datos and off == False and a == True and b == False:
            al = True
            print(al)
            registrar("Alarma activa")
            registrar("Dentro del segundo ciclo")
            d = 0
        
        #Si hay facturas pendientes y recien salio del offline, se verifica que las facturas se esten enviando
        elif "$x" in datos and off == False and a == False and b == True:
            num = 0
            num_str = ''
            for char in datos:
                if char.isdigit():
                    num_str += char

            if num_str != "":
                num = int(num_str)
                print(num)
            #Si las facturas trancadas no han reducido y ya ha pasado mas de 1 hora entonces mando una notificacion
            if num >= c and num != 0 and d > 60:
                notificacion()
                d = 0
            #si las facturas trancadas han reducido entonces actualizo la cantidad de facturas
            elif num < c:
                c = num
                d = 0
            #Si el numero de facturas trancadas es cero entonces pongo la bandera en Falso 
            elif c == 0:
                b = False
            else:
                c = num
    registrar("fuera del ciclo")
    return al,b,c,d
    
def trabajando():
    alarma_act = False
    flag_offline = False
    intentos = 0
    facturas_trancadas = 1
    intentos_bsisa = 0
    
    # Inicia el temporizador para la notificación cada 15 minutos
    noti1 = time.time()
    
    # Inicia el temporizador para la notificación cada 2 horas
    noti2 = time.time()
    
    while True:
        if subprocess.getoutput("python3 /home/suport/melissandra/melissandra.py activado") == "no":
            break
        else:
            registrar("Entro a verificar")
            alarma_activa = verificoGeneral(alarma_act,flag_offline,facturas_trancadas, intentos)
            alarma_act = alarma_activa[0]
            flag_offline = alarma_activa[1]
            facturas_trancadas = alarma_activa[2]
            intentos = alarma_activa[3]
            intentos_bsisa = verificacionBsisa(intentos_bsisa)
            al = ""
            if alarma_activa[0]:
                al = "true"
            else:
                al = "false"
                
            # Verifica si han pasado 1 hora desde la última notificación
            registrar(str(time.time() - noti1)+">"+str(1*60*60)+al)
            if time.time() - noti1 > 1*60*60 and alarma_activa[0] == True:
                notificacion(3)
                registrar("notificacion de 1 hora")
                noti1 = time.time()
                                     
            # Verifica si han pasado 3 horas desde la última notificación
            registrar(str(time.time() - noti2)+">"+str(3*60*60)+al)
            if time.time() - noti2 > 3*60*60 and alarma_activa[0] == True:
                notificacionGrupal(3)
                registrar("notificacion de 3 de horas")
                noti2 = time.time()
        
        eliminar()
        intentos = intentos + 1
        time.sleep(tc)

trabajando()
