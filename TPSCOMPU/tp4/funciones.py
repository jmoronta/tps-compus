#!/usr/bin/python3

import os
import sys 
import binascii
import fnmatch
import re

def abrir_archivo(file):
    '''Abre el archivo indicado en modo lectura'''
    try :
    	fd = os.open(file, os.O_RDONLY)
    	return fd
    except FileNotFoundError:
    	return 0
	
def crear_archivo(file):
    '''Crea el archivo indicado en modo escritura'''
    fd = os.open(file, os.O_WRONLY | os.O_CREAT)
    return fd

def leer_mensajes(mq, rgb_file, color):
    '''Leemos desde una cola de mensajes y guardamos en el archivo enviado'''
    msg = ""
    fd = crear_archivo(rgb_file)
    rgb_options = color.split(",")
    # print("procesando color: ", rgb_options[0])
    # print("procesando intensidad: ", rgb_options[1])
    while msg != "DONE":
        try:
            msg = mq.get()
            block = procesar_color(msg, rgb_options)
            os.write(fd, block)
        except TypeError as error:
            print("TypeError: {0}".format(error))
            #sys.exit(2)
        #finally:
        #    lock.release()

    os.close(fd)
    print("Proceso exitoso...") #os.getpid()

def procesar_mimetype(consulta):
    dic={"text":"text/plain","jpg":"image/jpeg","ppm":"image/x-portable-pixmap","html":"text/html","pdf":"application/pdf","ico":"image/x-image"}
    
    if consulta == "" :
    	tipo = 0
    	return tipo
    
    else :
    	tipo=dic[consulta]
    return tipo
    	


def parcear(dato):
        try:
            pedido = dato.split()[1]
        except:
            pass

        try:
            if pedido.count("?") == 1:
                pedido = pedido.split("?")
                archivo=pedido[0]
                print("hola el contenido de archivo es",archivo)
                #query=pedido[1]
                #query_list= query.split("&")
            #else:
             #   ruta_archivo=pedido
             #   query_list=""
            #ruta_archivo= ruta_archivo.split("/")
            #return(ruta_archivo,query_list)
        except:
            pass
           
def Index(path): 
		includes = ["*.jpg", "*.ppm","*.pdf"]
		html  = '<html>'
		html += '	<head>'
		html += '		<title>Directorio WEB</title>'
		html += '	</head>'
		html += '	<body>'
		html += '		<p>Directorio:</p>'
		html += '		<ul>'
		for root, dirs, files in os.walk(path, topdown=False):
			for name in files:
				if name.endswith(('.jpg', '.ppm', '.pdf', '.html')):	
					html += '	<li><a href="' "." '/' + name + '">' + name + '</a></li>'
		html += '		</ul>'
		html += '	</body>'
		html += '</html>'

		body = bytearray(html, 'utf8')

		return body

