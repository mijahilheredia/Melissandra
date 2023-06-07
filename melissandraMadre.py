#!/usr/bin/env python
# -*- coding: utf-8 -*-
import paramiko
import requests
import re
from getpass import getpass
import time
import datetime
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, message
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

class estacion:
    def __init__(self,nombre,grupo,region,departamento,manto):
        self.__nombre = nombre
        self.__grupo = grupo
        self.__region = region
        self.__departamento = departamento
        self.__manto = manto.replace("\n","")
        
    def getNombre(self):
        return self.__nombre
    
    def getDireccion(self):
        return self.__direccion
    
    def getGrupo(self):
        return self.__grupo
    
    def getRegion(self):
        return self.__region
    
    def getDepartamento(self):
        return self.__departamento
    
    def getManto(self):
        return self.__manto
    

class melissandraMadre:
    def __init__(self):
        self.__nombreVersion = "melissandra_V2.3"
        self.__idTelegram = "insert_token_bot_telegram_here"
        self.__chatidGrupal = ""
        self.__chatid1 = ""
        self.__user = "insert_user_linux"
        self.__password = "insert_password_ssh"
        self.grupos = ["grupo1","grupo2","grupo3","Grupon"]
        self.regiones = ["COLOMI","VINTO","SACABA","VALLE ALTO","LA PAZ",
                         "CENTRO COCHABAMBA","TIQUIPAYA","SANTA CRUZ EXTERNO",
                         "EL ALTO","QUILLACOLLO","SANTA CRUZ","SUCRE"]
        self.departamentos = ["LA PAZ","COCHABAMBA","SANTA CRUZ",
                                "CHUQUISACA","TARIJA","ORURO",
                                "POTOSI","BENI","PANDO"]
        self.nombres = []
        self.nombres2 = []
        self.ips = []
        self.ports = []
        self.portsweb = []
        self.addanydesk = []
        self.est = []
        self.ids = {"user_name_telegram_boss":'chat_id',"user_name_1":'chat_id',"user_name_telegram_n":'chat_id'}
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
        self.logger = logging.getLogger()#__name__
        self.updater = Updater(self.__idTelegram,use_context=True)
        self.dp = self.updater.dispatcher
        
        
    def getNombre(self):
        return self.__nombre
    
    def getIdTelegram(self):
        return self.__idTelegram
    
    def getUser(self):
        return self.__user
    
    def getPass(self):
        return self.__password
    
    def getVersion(self,update,context):
        update.message.reply_text(self.__nombreVersion)
    
    def llenarLista(self):
        with open("lista.txt","r") as archivo:
            for linea in archivo:
                if ',IP,' in linea:
                    print('')
                else:
                    self.__l = linea.replace("\n","")
                    self.__l = self.__l.split(',')
                    self.nombres.append(self.__l[0])
                    self.ips.append(self.__l[1])
                    self.ports.append(self.__l[2])
                    self.portsweb.append(self.__l[3])
                    self.addanydesk.append(self.__l[4])
        archivo.close()
                    
    def cargarEstaciones(self):
        self.__cont = 0
        self.__total = 0
        self.__respuesta = ""
        while self.__cont < len(self.ips):
            self.__host = self.ips[self.__cont]
            self.__port = self.ports[self.__cont]
            self.__nombre = self.nombres[self.__cont]
            self.__com = "python3 /home/soporte/melissandra/melissandra.py datos"
            self.__respuesta = self.enlace(self.__host,self.__port,self.__nombre,self.__com)
            if self.__respuesta[0] != "No se pudo conectar a: "+self.__nombre:
                self.__s = self.__respuesta[0].split(",")
                print(self.__s)
                self.est.append(estacion(self.__s[0],self.__s[1],self.__s[2],self.__s[3],self.__s[4]))
                print("CARGADO")
            else:
                self.est.append(estacion(self.__nombre,"s/g","s/r","s/d","desconectado"))
                print("NO SE PUDO CARGAR")
            print("nombre: "+self.est[self.__cont].getNombre())
            print("grupo: "+self.est[self.__cont].getGrupo())
            print("Region: "+self.est[self.__cont].getRegion())
            print("Departamento: "+self.est[self.__cont].getDepartamento())
            print("Mantenimiento: "+self.est[self.__cont].getManto())
            self.__cont = self.__cont+1
        print("Cantidad de estaciones en Lista: "+str(len(self.nombres)))
    
    def recargarEstaciones(self,update,context):
        if self.verificadorUsuario(update.message.chat_id):
            self.__cont = 0
            self.__total = 0
            self.est = []
            self.nombres = []
            self.ips = []
            self.ports = []
            self.portsweb = []
            self.addanydesk = []
            self.__respuesta = ""
            with open("lista.txt","r") as archivo:
                for linea in archivo:
                    if ',IP,' in linea:
                        print('')
                    else:
                        self.__l = linea.replace("\n","")
                        self.__l = self.__l.split(',')
                        self.nombres.append(self.__l[0])
                        self.ips.append(self.__l[1])
                        self.ports.append(self.__l[2])
                        self.portsweb.append(self.__l[3])
                        self.addanydesk.append(self.__l[4])
            archivo.close()
            while self.__cont < len(self.ips):
                self.__host = self.ips[self.__cont]
                self.__port = self.ports[self.__cont]
                self.__nombre = self.nombres[self.__cont]
                self.__com = "python3 /home/soporte/melissandra/melissandra.py datos"
                self.__respuesta = self.enlace(self.__host,self.__port,self.__nombre,self.__com)
                if self.__respuesta[0] != "No se pudo conectar a: "+self.__nombre:
                    self.__s = self.__respuesta[0].split(",")
                    print(self.__s)
                    self.est.append(estacion(self.__s[0],self.__s[1],self.__s[2],self.__s[3],self.__s[4]))
                    update.message.reply_text("CARGADO: "+self.__nombre)
                else:
                    self.est.append(estacion(self.__nombre,"s/g","s/r","s/d","desconectado"))
                    update.message.reply_text("NO SE PUDO CARGAR: "+self.__nombre)
                self.__cont = self.__cont+1
            update.message.reply_text("Cantidad de estaciones en Lista: "+str(len(self.nombres)))
            self.registrar(self.getUsr(update.message.chat_id),"ejecucion /recargar")
        else:
            update.message.reply_text("Lo siento no te conozco y no hablo con desconocidos")
    
    def start(self,update,context):
        """Send a message when the command /start is issued."""
        update.message.reply_text('Hola, me presento, soy Melissandra, trabajo en Grupo CAT como asistente en soporte\nCual es tu nombre?:')
        self.telegram_bot_sendtext('Alguien a intentado entablar conversacion conmigo, id:'+str(update.message.chat_id),self.ids['user_name_telegram_boss'])
    
    def telegram_bot_sendtext(self, bot_message,chatid):
        self.__send_text = 'https://api.telegram.org/bot'+self.getIdTelegram()+'/sendMessage?chat_id='+str(chatid)+'&parse_mode=Markdown&text='+bot_message
        self.__response = requests.get(self.__send_text)
        return self.__response.json()
    
    def verificadorUsuario(self,chatid):
        self.__r = False
        for i in self.ids:
            if chatid == self.ids[i]:
                self.__r = True
                break
        return self.__r

#Esta funcion recibe un nro id de telegram y devuelve el nombre de su usuario
    def getUsr(self,chatid):
        self.__u = ""
        for i in self.ids:
            if chatid == self.ids[i]:
                self.__u = i
                break
        return self.__u
            
    def verificador(self,manto,nombre):
        if manto == "no":
            nombre = nombre +"\U0001f6a9"
        elif manto == "parcial":
            nombre = nombre +"\U0001f9e9"
        elif manto == "desconectado":
            nombre = nombre +"\U0001f50c"
        return nombre

#Esta funcion conecta via ssh con una estacion y ejecuta un comando en la terminal devolviendo la respuesta resultante
#de la ejecucion del comando, en el caso de que el comando sea de comprobacion añade el total de facturas a la respuesta
    def enlace(self,host,port,nombre,comando):
        self.__client = paramiko.SSHClient()
        self.__client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.__respuesta = ""
        self.__totale = 0
        try:
            self.__client.connect(host,username=self.getUser(),password=self.getPass(),port=port,timeout=5)
            stdin, stdout, stderr = self.__client.exec_command(comando)
            self.__respuesta = stdout.read().decode()
            if comando == "python3 /home/soporte/melissandra/melissandra.py comprobacion":
                self.__respuesta = self.__respuesta.split(";")
                self.__totale = int(self.__respuesta[1])
            else:
                self.__respuesta = [self.__respuesta]
        except:
            self.__respuesta = ["No se pudo conectar a: "+nombre]
            self.__totale = 0
        self.__client.close()
        print(self.__totale)
        return self.__respuesta[0], self.__totale
        
    def conexion(self,comando,update,context):
        self.__cont = 0
        self.__total = 0
        self.__respuesta = ""
        while self.__cont < len(self.ips):
            self.__host = self.ips[self.__cont]
            self.__port = self.ports[self.__cont]
            self.__nombre = self.verificador(self.est[self.__cont].getManto(),self.nombres[self.__cont])
            self.__respuesta = self.enlace(self.__host,self.__port,self.__nombre,comando)
            update.message.reply_text(self.__nombre+"\n"+self.__respuesta[0])
            if comando == "python3 /home/soporte/melissandra/melissandra.py comprobacion":
                self.__total = self.__total + self.__respuesta[1]
                print(self.__total)
            self.__cont = self.__cont+1
        update.message.reply_text("Cantidad de estaciones en Lista: "+str(len(self.nombres)))
        if comando == "python3 /home/soporte/melissandra/melissandra.py comprobacion":
            update.message.reply_text("Cantidad de facturas enviadas a impuestos: \n"+ str(self.__total))
            
    def conexionXgrupo(self,comando,grupo,update,context):
        self.__cont = 0
        self.__total = 0
        self.__respuesta = ""
        while self.__cont < len(self.ips):
            self.__host = self.ips[self.__cont]
            self.__port = self.ports[self.__cont]
            self.__nombre = self.verificador(self.est[self.__cont].getManto(),self.nombres[self.__cont])
            self.__estacion = self.est[self.__cont]
            if self.__estacion.getGrupo() == grupo:
                self.__respuesta = self.enlace(self.__host,self.__port,self.__nombre,comando)
                update.message.reply_text(self.__nombre+"\n"+self.__respuesta[0])
            if comando == "python3 /home/soporte/melissandra/melissandra.py comprobacion" and self.__estacion.getGrupo() == grupo:
                self.__total = self.__total + self.__respuesta[1]
                print(self.__total)
            self.__cont = self.__cont+1
        if comando == "python3 /home/soporte/melissandra/melissandra.py comprobacion":
            update.message.reply_text("Cantidad de facturas enviadas a impuestos: \n"+ str(self.__total))
            
    def conexionXregion(self,comando,region,update,context):
        self.__cont = 0
        self.__total = 0
        self.__respuesta = ""
        while self.__cont < len(self.ips):
            self.__host = self.ips[self.__cont]
            self.__port = self.ports[self.__cont]
            self.__nombre = self.verificador(self.est[self.__cont].getManto(),self.nombres[self.__cont])
            self.__estacion = self.est[self.__cont]
            if self.__estacion.getRegion() == region:
                self.__respuesta = self.enlace(self.__host,self.__port,self.__nombre,comando)
                update.message.reply_text(self.__nombre+"\n"+self.__respuesta[0])
            if comando == "python3 /home/soporte/melissandra/melissandra.py comprobacion" and self.__estacion.getRegion() == region:
                self.__total = self.__total + self.__respuesta[1]
                print(self.__total)
            self.__cont = self.__cont+1
        if comando == "python3 /home/soporte/melissandra/melissandra.py comprobacion":
            update.message.reply_text("Cantidad de facturas enviadas a impuestos: \n"+ str(self.__total))
            
    def conexionXdepartamento(self,comando,depa,update,context):
        self.__cont = 0
        self.__total = 0
        self.__respuesta = ""
        while self.__cont < len(self.ips):
            self.__host = self.ips[self.__cont]
            self.__port = self.ports[self.__cont]
            self.__nombre = self.verificador(self.est[self.__cont].getManto(),self.nombres[self.__cont])
            self.__estacion = self.est[self.__cont]
            if self.__estacion.getDepartamento() == depa:
                self.__respuesta = self.enlace(self.__host,self.__port,self.__nombre,comando)
                update.message.reply_text(self.__nombre+"\n"+self.__respuesta[0])
            if comando == "python3 /home/soporte/melissandra/melissandra.py comprobacion" and self.__estacion.getDepartamento() == depa:
                self.__total = self.__total + self.__respuesta[1]
                print(self.__total)
            self.__cont = self.__cont+1
        if comando == "python3 /home/soporte/melissandra/melissandra.py comprobacion":
            update.message.reply_text("Cantidad de facturas enviadas a impuestos: \n"+ str(self.__total))
            
    def conexionXmanto(self,comando,update,context):
        self.__cont = 0
        self.__total = 0
        self.__respuesta = ""
        while self.__cont < len(self.ips):
            self.__host = self.ips[self.__cont]
            self.__port = self.ports[self.__cont]
            self.__nombre = self.nombres[self.__cont]
            self.__estacion = self.est[self.__cont]
            if self.__estacion.getManto() == "si" or self.__estacion.getManto() == "parcial":
                self.__respuesta = self.enlace(self.__host,self.__port,self.__nombre,comando)
                update.message.reply_text(self.nombres[self.__cont]+"\n"+self.__respuesta[0])
            if comando == "python3 /home/soporte/melissandra/melissandra.py comprobacion" and self.__estacion.getManto() == "si":
                self.__total = self.__total + self.__respuesta[1]
                print(self.__total)
            self.__cont = self.__cont+1
        if comando == "python3 /home/soporte/melissandra/melissandra.py comprobacion":
            update.message.reply_text("Cantidad de facturas enviadas a impuestos: \n"+ str(self.__total))
            
    def conexionEspecial(self,comando):
        self.__cont = 0
        self.__total = 0
        self.__respuesta = ""
        while self.__cont < len(self.ips):
            self.__host = self.ips[self.__cont]
            self.__port = self.ports[self.__cont]
            self.__nombre = self.nombres[self.__cont]
            self.__respuesta = self.enlace(self.__host,self.__port,self.__nombre,comando)
            print(self.nombres[self.__cont]+"\n"+self.__respuesta)
            self.__cont = self.__cont+1
        print("Cantidad de estaciones en Lista: "+str(len(self.nombres)))

# Esta funcion recibe el mensaje que se envia por telegram
    def recepcion(self,update,context):
        if self.verificadorUsuario(update.message.chat_id):
            self.__estacion = update.message.text
            self.consultaIndividual(self.__estacion,update,context)
        elif "MI NOMBRE ES " in update.message.text.upper():
            self.__nom = update.message.text.replace("\n","")
            self.__nom = self.__nom.split(" ")
            self.telegram_bot_sendtext('Su nombre es '+self.__nom[3]+', y su id '+str(update.message.chat_id),self.ids['user_name_telegrame_boss'])
        else:
            self.telegram_bot_sendtext(update.message.text+", "+str(update.message.chat_id),self.ids['user_name_telegram_boss'])
        
# Esta funcion procesa el mensaje que se envio por telegram
    def consultaIndividual(self,estacion,update,context):       
        self.__comando = ''
        self.__cont = 0
        while self.__cont < len(self.ips):
            self.__host = self.ips[self.__cont]
            self.__port = self.ports[self.__cont]
            self.__nombre = self.nombres[self.__cont]
            self.__portweb = self.portsweb[self.__cont]
            self.__anydesk = self.addanydesk[self.__cont]
            if estacion.upper() == "*"+self.__nombre.upper():
                self.__comando = "python3 /home/soporte/melissandra/melissandra.py comprobacion"
                self.__respuesta = self.enlace(self.__host,self.__port,self.__nombre,self.__comando)
                update.message.reply_text(self.verificador(self.est[self.__cont].getManto(),self.__nombre)+"\n"+self.__respuesta[0])
                self.registrar(self.getUsr(update.message.chat_id),"consulta general de "+self.__nombre)
                self.__cont = self.__cont+1
            elif estacion.upper() == "*"+ self.__nombre.upper()+" on".upper():
                self.__comando = "python3 /home/soporte/melissandra/melissandra.py on"
                self.__respuesta = self.enlace(self.__host,self.__port,self.__nombre,self.__comando)
                update.message.reply_text(self.verificador(self.est[self.__cont].getManto(),self.__nombre)+"\n"+self.__respuesta[0])
                self.registrar(self.getUsr(update.message.chat_id),"activacion ON de "+self.__nombre)
                self.__cont = self.__cont+1      
            elif estacion.upper() == "*"+ self.__nombre.upper()+" off".upper():
                self.__comando = "python3 /home/soporte/melissandra/melissandra.py off"
                self.__respuesta = self.enlace(self.__host,self.__port,self.__nombre,self.__comando)
                update.message.reply_text(self.verificador(self.est[self.__cont].getManto(),self.__nombre)+"\n"+self.__respuesta[0])
                self.registrar(self.getUsr(update.message.chat_id),"activacion OFF de "+self.__nombre)
                self.__cont = self.__cont+1
            elif estacion.upper() == "*"+ self.__nombre.upper()+" estado".upper():
                self.__comando = "python3 /home/soporte/melissandra/melissandra.py estado"
                self.__respuesta = self.enlace(self.__host,self.__port,self.__nombre,self.__comando)
                update.message.reply_text(self.verificador(self.est[self.__cont].getManto(),self.__nombre)+"\n"+self.__respuesta[0])
                self.registrar(self.getUsr(update.message.chat_id),"Consulta del estado de "+self.__nombre)
                self.__cont = self.__cont+1
            elif estacion.upper() == "*"+ self.__nombre.upper()+" servicios".upper():
                self.__comando = "ps ax | grep python3"
                self.__respuesta = self.enlace(self.__host,self.__port,self.__nombre,self.__comando)
                update.message.reply_text(self.verificador(self.est[self.__cont].getManto(),self.__nombre)+"\n"+self.__respuesta[0])
                self.registrar(self.getUsr(update.message.chat_id),"consulta de servicios de "+self.__nombre)
                self.__cont = self.__cont+1
            elif estacion.upper() == "*"+ self.__nombre.upper()+" web".upper():
                update.message.reply_text(self.verificador(self.est[self.__cont].getManto(),self.__nombre)+"\n"+self.__host+":"+self.__portweb+"/eess_sfl")
                self.registrar(self.getUsr(update.message.chat_id),"solicitud de direccion web de "+self.__nombre)
                self.__cont = self.__cont+1
            elif estacion.upper() == "*"+ self.__nombre.upper()+" ip".upper():
                update.message.reply_text(self.verificador(self.est[self.__cont].getManto(),self.__nombre)+"\nip: "+self.__host+"\npuerto: "+self.__port)
                self.registrar(self.getUsr(update.message.chat_id),"solicitud de ip de "+self.__nombre)
                self.__cont = self.__cont+1
            if estacion.upper() == "*"+self.__nombre.upper()+"*":
                self.__comando = "python3 /home/soporte/melissandra/melissandra.py comprobacion"
                self.__respuesta = self.enlace(self.__host,self.__port,self.__nombre,self.__comando)
                update.callback_query.message.edit_text(self.verificador(self.est[self.__cont].getManto(),self.__nombre)+"\n"+self.__respuesta[0])
                self.registrar(self.getUsr(update.callback_query.message.chat_id),"consulta general a traves de boton de  "+self.__nombre)
                self.__cont = self.__cont+1
            elif estacion.upper() == "*"+ self.__nombre.upper()+" on*".upper():
                self.__comando = "python3 /home/soporte/melissandra/melissandra.py on"
                self.__respuesta = self.enlace(self.__host,self.__port,self.__nombre,self.__comando)
                update.callback_query.message.edit_text(self.verificador(self.est[self.__cont].getManto(),self.__nombre)+"\n"+self.__respuesta[0])
                self.registrar(self.getUsr(update.callback_query.message.chat_id),"mediante boton activacion ON de "+self.__nombre)
                self.__cont = self.__cont+1      
            elif estacion.upper() == "*"+ self.__nombre.upper()+" off*".upper():
                self.__comando = "python3 /home/soporte/melissandra/melissandra.py off"
                self.__respuesta = self.enlace(self.__host,self.__port,self.__nombre,self.__comando)
                update.callback_query.message.edit_text(self.verificador(self.est[self.__cont].getManto(),self.__nombre)+"\n"+self.__respuesta[0])
                self.registrar(self.getUsr(update.callback_query.message.chat_id),"mediante boton activacion OFF de "+self.__nombre)
                self.__cont = self.__cont+1
            elif estacion.upper() == "*"+ self.__nombre.upper()+" estado*".upper():
                self.__comando = "python3 /home/soporte/melissandra/melissandra.py estado"
                self.__respuesta = self.enlace(self.__host,self.__port,self.__nombre,self.__comando)
                update.callback_query.message.edit_text(self.verificador(self.est[self.__cont].getManto(),self.__nombre)+"\n"+self.__respuesta[0])
                self.registrar(self.getUsr(update.callback_query.message.chat_id),"consulta de estado por boton de "+self.__nombre)
                self.__cont = self.__cont+1
            elif estacion.upper() == "*"+ self.__nombre.upper()+" web*".upper():
                update.callback_query.message.edit_text(self.verificador(self.est[self.__cont].getManto(),self.__nombre)+"\n"+self.__host+":"+self.__portweb+"/eess_sfl")
                self.registrar(self.getUsr(update.callback_query.message.chat_id),"mediante boton solicitud de direccion web de "+self.__nombre)
                self.__cont = self.__cont+1
            elif estacion.upper() == "*"+ self.__nombre.upper()+" remoto*".upper():
                update.callback_query.message.edit_text(self.verificador(self.est[self.__cont].getManto(),self.__nombre)+"\nAnydesk: "+self.__anydesk)
                self.registrar(self.getUsr(update.callback_query.message.chat_id),"mediante boton solicitud de direccion anydesk de "+self.__nombre)
                self.__cont = self.__cont+1
            elif estacion.upper() == "*"+ self.__nombre.upper()+" ip*".upper():
                update.callback_query.message.edit_text(self.verificador(self.est[self.__cont].getManto(),self.__nombre)+"\nip: "+self.__host+"\npuerto: "+self.__port)
                self.registrar(self.getUsr(update.callback_query.message.chat_id),"mediante boton solicitud de direccion ip de "+self.__nombre)
                self.__cont = self.__cont+1
            elif estacion.upper() == "*"+ self.__nombre.upper()+" getGestion".upper():
                self.__comando = "python3 /home/soporte/melissandra/melissandra.py getGestion"
                self.__respuesta = self.enlace(self.__host,self.__port,self.__nombre,self.__comando)
                self.registrar(self.getUsr(update.callback_query.message.chat_id),"solicitud de gestion de "+self.__nombre)
                self.__cont = self.__cont+1
                return self.__respuesta[0]
            elif estacion.upper() == "*"+ self.__nombre.upper()+" setGestion".upper():
                self.__comando = "python3 /home/soporte/melissandra/melissandra.py setGestion"
                self.__respuesta = self.enlace(self.__host,self.__port,self.__nombre,self.__comando)
                update.callback_query.message.edit_text(self.verificador(self.est[self.__cont].getManto(),self.__nombre)+"\n"+self.__respuesta[0])
                self.registrar(self.getUsr(update.callback_query.message.chat_id),"mediante boton aumento de gestion de "+self.__nombre+" a "+self.__respuesta[0])
                self.__cont = self.__cont+1
            elif estacion.upper() == "*"+ self.__nombre.upper()+" getFacts".upper():
                self.__comando = "./control f v"
                self.__respuesta = self.enlace(self.__host,self.__port,self.__nombre,self.__comando)                
                self.registrar(self.getUsr(update.callback_query.message.chat_id),"entrega de lista de facturadores "+self.__nombre+" a "+self.__respuesta[0])
                self.__cont = self.__cont+1
                return self.__respuesta[0] 
            elif "mOn*" in estacion and self.__nombre.upper() in estacion.upper():
                print("entro a on")
                self.__com = estacion.split("$")
                self.__com1 = "./control f x "+self.__com[1]+" py_ravencfg.py PROTOCOLO 0\nsleep 1\n"
                self.__com2 = "./control f x "+self.__com[1]+" py_ravencfg.py FACTURACION_MANUAL 1\nsleep 1\n"
                self.__com3 = "./control f s "+self.__com[1]+"\nsleep 1\n./control f s "+self.__com[1]+"\n"
                self.__respuesta = self.enlace(self.__host,self.__port,self.__nombre,self.__com1)
                self.__respuesta = self.__respuesta+self.enlace(self.__host,self.__port,self.__nombre,self.__com2)
                self.__respuesta = self.__respuesta+self.enlace(self.__host,self.__port,self.__nombre,self.__com3)
                update.callback_query.message.edit_text(self.verificador(self.est[self.__cont].getManto(),self.__nombre)+"\n"+self.__respuesta[0])
                self.registrar(self.getUsr(update.callback_query.message.chat_id),"habilitado manual por boton de "+self.__nombre+" Facturador:"+self.__com[1])
                self.__cont = self.__cont+1
            elif "mOff*" in estacion and self.__nombre.upper() in estacion.upper():
                print("entro a off")
                self.__com = estacion.split("$")
                self.__com1 = "./control f x "+self.__com[1]+" py_ravencfg.py PROTOCOLO 11\nsleep 1\n"
                self.__com2 = "./control f x "+self.__com[1]+" py_ravencfg.py FACTURACION_MANUAL 0\nsleep 2\n"
                self.__com3 = "./control f s "+self.__com[1]+"\nsleep 1\n./control f s "+self.__com[1]+"\n"
                self.__respuesta = self.enlace(self.__host,self.__port,self.__nombre,self.__com1)
                self.__respuesta = self.__respuesta+self.enlace(self.__host,self.__port,self.__nombre,self.__com2)
                self.__respuesta = self.__respuesta+self.enlace(self.__host,self.__port,self.__nombre,self.__com3)
                update.callback_query.message.edit_text(self.verificador(self.est[self.__cont].getManto(),self.__nombre)+"\n"+self.__respuesta[0])
                self.registrar(self.getUsr(update.callback_query.message.chat_id),"deshabilitado manual por boton de "+self.__nombre+" Facturador:"+self.__com[1])
                self.__cont = self.__cont+1
            else:
                self.__cont = self.__cont+1
        self.__cont = 0
        
        while self.__cont < len(self.grupos):
            self.__grupo = self.grupos[self.__cont]
            if estacion.upper() == "*solo ".upper()+self.__grupo.upper():
                self.conexionXgrupo("python3 /home/soporte/melissandra/melissandra.py comprobacion",self.__grupo,update,context)
                self.__cont = self.__cont+1
            elif estacion.upper() == "*solo ".upper()+self.__grupo.upper()+" on".upper():
                self.conexionXgrupo("python3 /home/soporte/melissandra/melissandra.py on",self.__grupo,update,context)
                self.__cont = self.__cont+1
            elif estacion.upper() == "*solo ".upper()+self.__grupo.upper()+" off".upper():
                self.conexionXgrupo("python3 /home/soporte/melissandra/melissandra.py off",self.__grupo,update,context)
                self.__cont = self.__cont+1
            else:
                self.__cont = self.__cont+1
        self.__cont = 0
        
        while self.__cont < len(self.regiones):
            self.__region = self.regiones[self.__cont]
            if estacion.upper() == "*solo ".upper()+self.__region.upper():
                self.conexionXregion("python3 /home/soporte/melissandra/melissandra.py comprobacion",self.__region,update,context)
                self.registrar(self.getUsr(update.message.chat_id),"consulta general de la region "+self.__region)
                self.__cont = self.__cont+1
            elif estacion.upper() == "*solo ".upper()+self.__region.upper()+" on".upper():
                self.conexionXregion("python3 /home/soporte/melissandra/melissandra.py on",self.__region,update,context)
                self.registrar(self.getUsr(update.message.chat_id),"activacion ON de la region "+self.__region)
                self.__cont = self.__cont+1
            elif estacion.upper() == "*solo ".upper()+self.__region.upper()+" off".upper():
                self.conexionXregion("python3 /home/soporte/melissandra/melissandra.py off",self.__region,update,context)
                self.registrar(self.getUsr(update.message.chat_id),"activacion OFF de la region "+self.__region)
                self.__cont = self.__cont+1
            else:
                self.__cont = self.__cont+1
        self.__cont = 0
        
        while self.__cont < len(self.departamentos):
            self.__depa = self.departamentos[self.__cont]
            if estacion.upper() == "*"+self.__depa.upper():
                self.conexionXdepartamento("python3 /home/soporte/melissandra/melissandra.py comprobacion",self.__depa,update,context)
                self.registrar(self.getUsr(update.message.chat_id),"consulta general del departamento "+self.__depa)
                self.__cont = self.__cont+1
            elif estacion.upper() == "*"+self.__depa.upper()+" on":
                self.conexionXdepartamento("python3 /home/soporte/melissandra/melissandra.py on",self.__depa,update,context)
                self.registrar(self.getUsr(update.message.chat_id),"activacion OFF del departamento "+self.__depa)
                self.__cont = self.__cont+1
            elif estacion.upper() == "*"+self.__depa.upper()+" off":
                self.conexionXdepartamento("python3 /home/soporte/melissandra/melissandra.py off",self.__depa,update,context)
                self.registrar(self.getUsr(update.message.chat_id),"activacion OFF del departamento "+self.__depa)
                self.__cont = self.__cont+1
            else:
                self.__cont = self.__cont+1
            
        if "*NOMBRES CON" in estacion.upper():
            self.__fn = estacion.upper()[len(estacion)-1]
            self.__r= self.mostrarNombresXletra(self.__fn)
            update.message.reply_text(self.__r)
            self.registrar(self.getUsr(update.message.chat_id),"se consulto nombres con "+self.__fn)
        elif "*MI NOMBRE ES " in estacion.upper():
            self.setID(estacion,update,context)
        elif "ECO*" in estacion.upper() and update.message.chat_id == self.ids["david"]:
            self.__dst = estacion.replace("\n","")
            self.__dst = self.__dst.split('*')
            try:
                self.telegram_bot_sendtext(self.__dst[1],self.__dst[2])
                update.message.reply_text('enviado a '+str(self.__dst[2]))
            except:
                update.message.reply_text('Es probable que estes olvidando el id o nombre')
            else:
                try:
                    self.telegram_bot_sendtext(self.__dst[1]+'.',self.ids[self.__dst[2]])
                    update.message.reply_text('enviado a '+self.ids[self.__dst[2]])
                except:
                    update.message.reply_text('Si te dije que ya se ha enviado ignora este mensaje, caso contrario, es probable que estes olvidando el nombre destino')
        elif estacion.upper() == "*TODOS ON":
            self.registrar(self.getUsr(update.message.chat_id),"solicitud *TODOS ON")
            self.conexion("python3 /home/soporte/melissandra/melissandra.py on",update,context)
        elif estacion.upper() == "*TODOS OFF":
            self.registrar(self.getUsr(update.message.chat_id),"solicitud *TODOS OFF")
            self.conexion("python3 /home/soporte/melissandra/melissandra.py off",update,context)
        elif "*BUSCAR" in estacion.upper() or "*B " in estacion.upper():
            self.__fn = estacion.split(" ")
            self.registrar(self.getUsr(update.message.chat_id),"iniciando busqueda de ocurrencias con "+self.__fn[1])
            self.buscarNombre(self.__fn[1],update,context)
        elif estacion.upper() == "*SOLO CON MANTO" or estacion.upper() == "*SOLO CON MANTENIMIENTO":
            self.registrar(self.getUsr(update.message.chat_id),"consulta general de estaciones con mantenimiento")
            self.conexionXmanto("python3 /home/soporte/melissandra/melissandra.py comprobacion",update,context)
        elif estacion.upper() == "*SOLO CON MANTO ON" or estacion.upper() == "*SOLO CON MANTENIMIENTO ON":
            self.registrar(self.getUsr(update.message.chat_id),"activacion ON de estaciones con mantenimiento")
            self.conexionXmanto("python3 /home/soporte/melissandra/melissandra.py on",update,context)
        elif estacion.upper() == "*SOLO CON MANTO OFF" or estacion.upper() == "*SOLO CON MANTENIMIENTO OFF":
            self.conexionXmanto("python3 /home/soporte/melissandra/melissandra.py off",update,context)
            self.registrar(self.getUsr(update.message.chat_id),"activacion OFF de estaciones con mantenimiento")
        elif estacion.upper() == "*SOLO CON MANTO ESTADO" or estacion.upper() == "*SOLO CON MANTENIMIENTO ESTADO":
            self.conexionXmanto("python3 /home/soporte/melissandra/melissandra.py estado",update,context)
            self.registrar(self.getUsr(update.message.chat_id),"solicitud de estado de estaciones con mantenimiento")
        elif "**" in estacion:
                self.__com = ""
                self.__sep = estacion.replace("**","")
                self.__sep = self.__sep.split(",")
                print(self.__sep)
                print(self.__sep[len(self.__sep)-1])
                self.__fn = self.__sep[len(self.__sep)-1].split(" ")
                if self.__fn[len(self.__fn)-1] == "on":
                    self.__com = " on"
                    self.__sep[len(self.__sep)-1] = self.__sep[len(self.__sep)-1].replace(" on","")
                elif self.__fn[len(self.__fn)-1] == "off":
                    self.__com = " off"
                    self.__sep[len(self.__sep)-1] = self.__sep[len(self.__sep)-1].replace(" off","")
                print(self.__fn)
                print(self.__sep)
                for n in self.__sep:
                    print(n+self.__com)
                    print("*"+n + self.__com)
                    self.consultaIndividual("*"+n + self.__com,update,context)
            
    def servicios(self,update,context):
        if self.verificadorUsuario(update.message.chat_id):
            self.conexion("ps ax | grep python3",update,context)
            self.registrar(self.getUsr(update.message.chat_id),"ejecucion /servicios")
        else:
            update.message.reply_text("Lo siento no te conozco y no hablo con desconocidos")
            
    
    def consultando(self,update,context):
        if self.verificadorUsuario(update.message.chat_id):
            self.conexion("python3 /home/soporte/melissandra/melissandra.py comprobacion",update,context)
            self.registrar(self.getUsr(update.message.chat_id),"ejecucion /todos")
        else:
            update.message.reply_text("Lo siento no te conozco y no hablo con desconocidos")
        
    def activarOnline(self,update,context):
        if self.verificadorUsuario(update.message.chat_id):
            self.conexion("python3 /home/soporte/melissandra/melissandra.py on",update,context)
            self.registrar(self.getUsr(update.message.chat_id),"ejecucion /todosOn")
        else:
            update.message.reply_text("Lo siento no te conozco y no hablo con desconocidos")
        
    def activarOffline(self,update,context):
        if self.verificadorUsuario(update.message.chat_id):
            self.conexion("python3 /home/soporte/melissandra/melissandra.py off",update,context)
            self.registrar(self.getUsr(update.message.chat_id),"ejecucion /todosOff")
        else:
            update.message.reply_text("Lo siento no te conozco y no hablo con desconocidos")
        
    def verificando(self,update,context):
        if self.verificadorUsuario(update.message.chat_id):
            self.conexion("python3 /home/soporte/melissandra/melissandra.py estado",update,context)
            self.registrar(self.getUsr(update.message.chat_id),"ejecucion /estado")
        else:
            update.message.reply_text("Lo siento no te conozco y no hablo con desconocidos")
    
    def mostrarNombres(self,update,context):
        if self.verificadorUsuario(update.message.chat_id):
            self.__res = ""
            self.__cont = 0
            for nombre in self.nombres:
                self.__res = self.__res+str(self.__cont + 1)+": "+self.verificador(self.est[self.__cont].getManto(),nombre)+"\n"
                self.__cont = self.__cont + 1
            update.message.reply_text(self.__res)
            update.message.reply_text("Cantidad de estaciones en Lista: "+str(len(self.nombres)))
            self.registrar(self.getUsr(update.message.chat_id),"ejecucion /nombres")
        else:
            update.message.reply_text("Lo siento no te conozco y no hablo con desconocidos")
        
        
    def mostrarNombresXletra(self,letra):
        self.__res = ""
        for nombre in self.nombres:
            if nombre[0].upper() == letra:
                self.__res = self.__res+nombre+"\n"
        if self.__res == "":
            self.__res = "No hay nombres con "+letra
        return self.__res
    
    def buscarNombre(self,ocurrencia,update,context):
        self.__res = []
        for nombre in self.nombres:
            if ocurrencia.upper() in nombre.upper():
                self.__res.append(nombre.upper()) #self.__res+nombre+"\n"
        if self.__res == "":
            self.__res = "No hay nombres con "+ ocurrencia
            update.message.reply_text(self.__res)
            self.registrar(self.getUsr(update.message.chat_id),"no se encontro nombre con "+ocurrencia)
        else:
            self.creadorBotones(self.__res,update,context)
    
    def mostrarGrupos(self,update,context):
        if self.verificadorUsuario(update.message.chat_id):
            self.__res = ""
            for grupo in self.grupos:
                self.__res = self.__res+grupo+"\n"
            update.message.reply_text(self.__res)
            self.registrar(self.getUsr(update.message.chat_id),"ejecucion /grupos")
        else:
            update.message.reply_text("Lo siento no te conozco y no hablo con desconocidos")
        
    def mostrarRegiones(self,update,context):
        if self.verificadorUsuario(update.message.chat_id):
            self.__res = ""
            for region in self.regiones:
                self.__res = self.__res+region+"\n"
            update.message.reply_text(self.__res)
            self.registrar(self.getUsr(update.message.chat_id),"ejecucion /regiones")
        else:
            update.message.reply_text("Lo siento no te conozco y no hablo con desconocidos")
        
    def mostrarDepas(self,update,context):
        if self.verificadorUsuario(update.message.chat_id):
            self.__res = ""
            for dep in self.departamentos:
                self.__res = self.__res+dep+"\n"
            update.message.reply_text(self.__res)
            self.registrar(self.getUsr(update.message.chat_id),"ejecucion /departamentos")
        else:
            update.message.reply_text("Lo siento no te conozco y no hablo con desconocidos")
        
    def leyenda(self,update,context):
        if self.verificadorUsuario(update.message.chat_id):
            self.ley = []
            self.__res = ""
            self.ley.append("\U0000274c -> Corregir, facturas sin llegar a impuestos")
            self.ley.append("\U000026A0 -> Prestar atencion")
            self.ley.append("\U0001f527 -> La estacion esta en Offline forzado")
            self.ley.append("\U0001f4cc -> La estacion esta en Ofline Automatico")
            self.ley.append("\U0001f6a9 -> No tiene mantenimiento")
            self.ley.append("\U0001f9e9 -> tiene mantenimiento parcial")
            self.ley.append("\U0001f50c -> No se pudo conectar a la estacion y no se cargaron los datos correctamente")
            for dato in self.ley:
                self.__res = self.__res+dato+"\n"
            update.message.reply_text(self.__res)
            self.registrar(self.getUsr(update.message.chat_id),"ejecucion /leyenda")
        else:
            update.message.reply_text("Lo siento no te conozco y no hablo con desconocidos")
            
    def ayuda(self,update,context):
        if self.verificadorUsuario(update.message.chat_id):
            self.cm = []
            self.__res = ""
            self.cm.append("/todos: muestra facturas enviadas a impuestos y anh de una sola estacion")
            self.cm.append("\n*nombre_estacion: muestra facturas enviadas a impuestos y anh de una estacion")
            self.cm.append("\n/todosOn: coloca todas las estaciones en Online Forzado")
            self.cm.append("\n/todosOff: coloca todas las estaciones en offline forzado")
            self.cm.append("\n*nombre_estacion estado: muestra si una estacion esta en online u offline forzado")
            self.cm.append("\n/servicios: muestra los servicios de impuestos en el server en todas las estaciones")
            self.cm.append("\n*nombre_estacion servicios: muestra los servicios de impuestos en el server en una estacion")
            self.cm.append("\n*nombre_estacion on: coloca una estacion en online forzado")
            self.cm.append("\n*nombre_estacion off: coloca una estacion en offline forzado")
            self.cm.append("\n/nombres: todas las estaciones en lista")
            self.cm.append("\n*nombre_estacion ip: muestra la ip y el puerto con el que trabaja una estacion")
            self.cm.append("\n*nombre_estacion web: devuelve un link con accesso al sistema web")
            self.cm.append("\n/grupos: muestra los grupos existentes entre las estaciones")
            self.cm.append("\n/regiones: muestra las regiones a las cuales pertenecen las estaciones")
            self.cm.append("\n/departamentos: muestra los departamentos a los cuales pertenecen las estaciones")
            self.cm.append("\n*solo nombre_grupo: realiza la consulta filtrando un grupo en particular")
            self.cm.append("\n*solo nombre_region: realiza la consulta filtrando una region en particular")
            self.cm.append("\n*nombre_departamento: realiza la consulta filtrando un departamento en particular")
            self.cm.append("\n*solo manto o *solo mantenimiento: realiza la consulta solo para las estaciones com mantenimiento")
            self.cm.append("\n**nombre_estacion1,nombre_estacion2,... nombre_estacion_n comando: ejecuta un comando en varias estaciones a la vez")
            self.cm.append("\n*nombres con inserteLetra: devuelve una lista de todas las estaciones que empiezan con la letra insertada")
            self.cm.append("\n*buscar nombre_estacion o *b ocurrencia: filtra una estacion segun lo escrito a buscar")
            self.cm.append("\n*todos on: coloca todas las estaciones en Online Forzado")
            self.cm.append("\n*todos off: coloca todas las estaciones en offline forzado")
            self.cm.append("\n/recargar: Recarga los datos de todas las estaciones nuevamente")
            self.cm.append("\n/leyendas: muestra una leyenda de los iconos mostrados")
            self.cm.append("\n/ayuda: muestra los comando activos")
            for dato in self.cm:
                self.__res = self.__res+dato
            update.message.reply_text(self.__res)
            self.registrar(self.getUsr(update.message.chat_id),"ejecucion /ayuda")
        else:
            update.message.reply_text("Lo siento no te conozco y no hablo con desconocidos")
        
    def setID(self,nombre,update,context):
        self.__nom = nombre.replace("\n","")
        self.__nom = self.__nom.split(" ")
        print(update.message.chat_id,self.__nom[3])
        self.ids.append(self.__nom[3]+","+str(update.message.chat_id))
        update.message.reply_text("Tu nombre es: \n"+self.__nom[3]+"\ny tu id es: \n"+str(update.message.chat_id))
        
    def getID(self,update,context):
        if self.verificadorUsuario(update.message.chat_id):
            self.__r = ""
            for i in self.ids:
                self.__r =  self.__r+i+"\n"
            update.message.reply_text(self.__r)
        else:
            update.message.reply_text("Lo siento no te conozco y no hablo con desconocidos")
    
    def creadorBotones(self,lista,update, context) -> None:
        self.__keyboard = []
        self.__cn = 0
        for nom in lista:
            self.__keyboard.append([])
            self.__keyboard[self.__cn].append(InlineKeyboardButton( nom, callback_data=nom))
            self.__cn = self.__cn + 1
        reply_markup = InlineKeyboardMarkup(self.__keyboard)
        update.message.reply_text("Estaciones encontradas:", reply_markup=reply_markup)
        
    def submenu(self,nombre,update,context) -> None:
        self.__kb=[[InlineKeyboardButton( "GENERAL", callback_data=nombre+",*c*")],
                        [InlineKeyboardButton( "ON", callback_data=nombre+",*on*"),InlineKeyboardButton( "OFF", callback_data=nombre+",*off*")],
                        [InlineKeyboardButton( "ESTADO", callback_data=nombre+",*e*")],
                        [InlineKeyboardButton( "IP", callback_data=nombre+",*ip*"),InlineKeyboardButton( "REMOTO", callback_data=nombre+",*remoto*"),],
                        [InlineKeyboardButton( "WEB", callback_data=nombre+",*web*"),InlineKeyboardButton( "AÑO GESTION", callback_data=nombre+",*g*")],
                        [InlineKeyboardButton( "FACTURADORES", callback_data=nombre+",*fac*")]]
        reply_markup = InlineKeyboardMarkup(self.__kb)
        update.callback_query.message.edit_text(nombre+":", reply_markup=reply_markup)
    
    def menuGestion(self,nombre,update,context) -> None:
        self.__gest = self.consultaIndividual("*"+nombre+" getGestion",update,context)
        self.__gest = self.__gest.split("\n")
        self.__kb=[[InlineKeyboardButton( "ACTUALIZAR GESTION", callback_data=nombre+","+self.__gest[1]+",*gestion*")]]
        reply_markup = InlineKeyboardMarkup(self.__kb)
        update.callback_query.message.edit_text(nombre+":\nGestion actual: "+self.__gest[1], reply_markup=reply_markup)
        
    def menuFacturadores(self,nombre,update,context) -> None:
        self.__fact = self.consultaIndividual("*"+nombre+" getFacts",update,context)
        self.__fact = self.__fact.split("\n")
        self.__listFact = []
        self.__keyboard = []
        self.__pattern = "    (.+) (.+)      ->(.+)  => (.+)"
        for datos in self.__fact:
            print(datos)
            try:
                self.__match = re.search(self.__pattern, datos)
                self.__groups = self.__match.groups()
                print(self.__groups)
                self.__listFact.append(self.__groups[0].upper().replace("FACTURADOR","FAC")+" MG:"+self.__groups[2].replace(" ",""))
            except:
                print("no se pudo")
        print(self.__listFact)
        for nom in self.__listFact:
            self.__keyboard.append([InlineKeyboardButton( nom, callback_data=nombre+","+nom+",*facMen*")])
        reply_markup = InlineKeyboardMarkup(self.__keyboard)
        update.callback_query.message.edit_text(nombre+": Facturadores: ", reply_markup=reply_markup)
        
    def optionsFact(self,nombre,fact,update,context) -> None:
        self.__kb=[[InlineKeyboardButton( "MANUAL ON", callback_data=nombre+","+fact+",*mOn*"),InlineKeyboardButton( "MANUAL OFF", callback_data=nombre+","+fact+",*mOff*")]
                   ,[InlineKeyboardButton( "SALIR", callback_data=nombre+",*salir*")]]
        reply_markup = InlineKeyboardMarkup(self.__kb)
        update.callback_query.message.edit_text(nombre+" > fact: "+fact+":", reply_markup=reply_markup)
    
    def button(self,update,context) -> None:
        query = update.callback_query
        query.answer()
        self.__nm = ""
        if "*c*" in query.data:
            self.__nm = query.data.split(",")
            self.consultaIndividual("*"+self.__nm[0]+"*",update,context)
        elif "*on*" in query.data:
            self.__nm = query.data.split(",")
            self.consultaIndividual("*"+self.__nm[0]+" on*",update,context)
        elif "*off*" in query.data:
            self.__nm = query.data.split(",")
            self.consultaIndividual("*"+self.__nm[0]+" off*",update,context)
        elif "*e*" in query.data:
            self.__nm = query.data.split(",")
            self.consultaIndividual("*"+self.__nm[0]+" estado*",update,context)
        elif "*ip*" in query.data:
            self.__nm = query.data.split(",")
            self.consultaIndividual("*"+self.__nm[0]+" ip*",update,context)
        elif "*web*" in query.data:
            self.__nm = query.data.split(",")
            self.consultaIndividual("*"+self.__nm[0]+" web*",update,context)
        elif "*remoto*" in query.data:
            self.__nm = query.data.split(",")
            self.consultaIndividual("*"+self.__nm[0]+" remoto*",update,context)
        elif "*g*" in query.data:
            self.__nm = query.data.split(",")
            self.menuGestion(self.__nm[0],update,context)
        elif "*gestion*" in query.data:
            self.__nm = query.data.split(",")
            print(self.__nm)
            self.__date = datetime.date.today()
            self.__year = self.__date.strftime("%Y")
            if int(self.__year) != int(self.__nm[1]):
                print(self.__nm[0])
                self.consultaIndividual("*"+self.__nm[0]+" setGestion",update,context)
            else:
                update.callback_query.message.edit_text("La gestion ya esta actualizada")
                
        elif "*fac*" in query.data:
            self.__nm = query.data.split(",")
            self.menuFacturadores(self.__nm[0],update,context)
        
        elif "*facMen*" in query.data:
            self.__nm = query.data.split(",")
            self.__fc = self.__nm[1].split(" ")
            for i in self.__fc:
                 if not i.isdigit():
                     self.__fc.remove(i)
            self.registrar("usuario","".join(self.__fc))
            self.optionsFact(self.__nm[0],self.__fc[1],update,context)
        
        elif "*mOn*" in query.data:
            self.__nm = query.data.split(",")
            self.consultaIndividual("*"+self.__nm[0]+"$"+self.__nm[1]+"$mOn*",update,context)
        elif "*mOff*" in query.data:
            self.__nm = query.data.split(",")
            self.consultaIndividual("*"+self.__nm[0]+"$"+self.__nm[1]+"$mOff*",update,context)
        elif "*salir*" in query.data:
            self.__nm = query.data.split(",")
            update.callback_query.message.edit_text("Operaste en: "+self.__nm[0])
        elif "*web*" in query.data:
            self.__nm = query.data.split(",")
            self.consultaIndividual("*"+self.__nm[0]+" web*",update,context)
        else:
            self.submenu(query.data,update,context)
        
    def registrar(self,usuario,actividad):
        self.__fecha = datetime.datetime.now().strftime("%d-%m-%y")
        self.__nombre ="melissandraReg_"+self.__fecha+".log"
        self.__l = logging.getLogger('melissandra_v2.3')
        self.__l.setLevel(logging.DEBUG)

        # create file handler which logs even debug messages
        self.__fh1 = logging.FileHandler(self.__nombre)
        self.__fh1.setLevel(logging.DEBUG)

        # create formatter and add it to the handlers
        self.__formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.__fh1.setFormatter(self.__formatter)

        # add the handlers to the logger
        self.__l.addHandler(self.__fh1)
        self.__l.info("Usuario: "+usuario+" - comando: "+actividad)
    
    def inicializacion(self):
        self.llenarLista()
        self.cargarEstaciones()
        
    def ejecucion(self):
        self.dp.add_handler(MessageHandler(Filters.text & ~Filters.command,self.recepcion))
        self.dp.add_handler(CommandHandler("start", self.start))
        self.dp.add_handler(CommandHandler("version", self.getVersion))
        self.dp.add_handler(CommandHandler("listaID", self.getID))
        self.dp.add_handler(CommandHandler("todos", self.consultando))
        self.dp.add_handler(CommandHandler("todosOn", self.activarOnline))
        self.dp.add_handler(CommandHandler("todosOff", self.activarOffline))
        self.dp.add_handler(CommandHandler("estado", self.verificando))
        self.dp.add_handler(CommandHandler("servicios", self.servicios))
        self.dp.add_handler(CommandHandler("nombres",self.mostrarNombres))
        self.dp.add_handler(CommandHandler("grupos",self.mostrarGrupos))
        self.dp.add_handler(CommandHandler("regiones",self.mostrarRegiones))
        self.dp.add_handler(CommandHandler("departamentos",self.mostrarDepas))
        self.dp.add_handler(CommandHandler("recargar",self.recargarEstaciones))
        self.dp.add_handler(CommandHandler("leyenda",self.leyenda))
        self.dp.add_handler(CommandHandler("ayuda",self.ayuda))
        self.dp.add_handler(CallbackQueryHandler(self.button))
        self.updater.start_polling()
        self.updater.idle()
        
        
m = melissandraMadre()
#m.llenarLista()
#m.conexionEspecial("mkdir melissandra")
m.inicializacion()
m.ejecucion()
