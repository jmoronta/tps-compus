#!/usr/bin/python3

import os
import sys 
import binascii
import fnmatch
import re

from concurrent import futures
import array

_ERROR_ARCHIVO = "El archivo no se encuentra en el directorio"

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

def index(path): 
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

def aplicarfiltro(imagen,filtro, intensidad,size,directorio,hilos):
    try:
        archivo = os.open(directorio + "/" + imagen, os.O_RDONLY)
   
        if size % 3 != 0: #VEO si es multiplo de 3
            size += (3 - (size % 3))
        leido = os.read(archivo, size) 
        calcularencabezado=True
        estado = 0

        while leido:
            if calcularencabezado == True:
                dimen = False
                # sacar comentario
                i = 0
                if i == 0:
                    for i in range(leido.count(b"\n# ")):
                        barra_n_as = leido.find(b"\n# ")
                        barra_n = leido.find(b"\n", barra_n_as + 1)
                        leido = leido.replace(leido[barra_n_as:barra_n], b"")
                # sacar encabezado
                inicio = leido.find(b"\n") + 1
                medio = leido.find(b"\n", inicio) + 1
                final = leido.find(b"\n", medio) + 1
                encabezado = leido[:final].decode()
                
                # saco ancho y largo
                linea = leido.splitlines()
                for i in range(len(linea)):
                    if dimen == False:
                        word = linea[i].split()
                        if len(word) == 2:
                            dimen = True
                calcularencabezado = False
                # guardo el cuerpo
                cuerpo = leido[final:]
            else:
                cuerpo = leido
                encabezado = ""

            thread = futures.ThreadPoolExecutor()
            lista = []

            if filtro == 'R' :
                color = thread.submit(cambiar_colores_red,cuerpo,intensidad)    
                nombre = "-red.ppm"
            elif filtro == 'B' :
                color = thread.submit(cambiar_colores_blue,cuerpo,intensidad)
                nombre = "-blue.ppm"
            elif filtro == 'G' :
                color = thread.submit(cambiar_colores_green,cuerpo,intensidad)
                nombre = "-green.ppm"
            elif filtro == 'W' :
                color = thread.submit(cambiar_colores_bw,cuerpo,intensidad)
                nombre = "-blacknwhite.ppm"
                
            else:
                color = "NN"

            if (color != "NN"):
                lista = color.result()
                listafinal = array.array('B',lista)
                imagen = imagen.split(sep=".")[0]
                with open(directorio + imagen+nombre, 'ab') as f:
                    #print("creando archivo...")
                    if encabezado != "":
                        f.write(bytearray(encabezado, 'ascii'))
                    listafinal.tofile(f)

                leido = os.read(archivo, size)

                
            else:
                print("No se pudo aplicar el filtro")
                estado=1
    except FileNotFoundError:
        print(_ERROR_ARCHIVO)
        sys.exit()
<<<<<<< HEAD
=======
    if size % 3 != 0: #VEO si es multiplo de 3
        size += (3 - (size % 3))
    leido = os.read(archivo, size)
    estado = 0
    calcularencabezado=True 
    #thread = futures.ThreadPoolExecutor(max_workers=20)
    while leido:
        if calcularencabezado == True:
            dimen = False
            # sacar comentario
            i = 0
            if i == 0:
                for i in range(leido.count(b"\n# ")):
                    barra_n_as = leido.find(b"\n# ")
                    barra_n = leido.find(b"\n", barra_n_as + 1)
                    leido = leido.replace(leido[barra_n_as:barra_n], b"")
            # sacar encabezado
            inicio = leido.find(b"\n") + 1
            medio = leido.find(b"\n", inicio) + 1
            final = leido.find(b"\n", medio) + 1
            encabezado = leido[:final].decode()
            
            # saco ancho y largo
            linea = leido.splitlines()
            for i in range(len(linea)):
                if dimen == False:
                    word = linea[i].split()
                    if len(word) == 2:
                        width = int(word[0])
                        height = int(word[1])
                        dimen = True
            lista2 = []
            calcularencabezado = False
            # guardo el cuerpo
            cuerpo = leido[final:]
        else:
            cuerpo = leido
            encabezado = ""    
        #print("cuerpo es ",len(cuerpo))
        thread = futures.ThreadPoolExecutor()
        #leido = os.read(archivo, size)
        if filtro == 'R' :
            thread.submit(cambiar_colores_red,encabezado,cuerpo,intensidad,directorio,imagen)
            
        elif filtro == 'B' :
            thread.submit(cambiar_colores_blue,encabezado,cuerpo,intensidad,directorio,imagen)
            
        elif filtro == 'G' :
            thread.submit(cambiar_colores_green,encabezado,cuerpo,intensidad,directorio,imagen)

        elif filtro == 'W' :
            thread.submit(cambiar_colores_bw,encabezado,cuerpo,intensidad,directorio,imagen)

        else: 
            print("No se pudo aplicar el filtro")
            estado = 1
        leido = os.read(archivo, size)
                    
>>>>>>> f4a3bd046448f872ad360084ce8df6a8f9b4a779
    return estado

def cambiar_colores_red(cuerpo2, intensidad):
    imager = []
    cuerpo = b''
    cuerpo = cuerpo + cuerpo2
    cuerpo_c = [i for i in cuerpo]
    for j in range(0, len(cuerpo_c), 3):
        valor = int(float(cuerpo_c[j]) * float(intensidad))
        if valor > 255:
            valor = 255
        imager.append(valor)
        imager.append(0)
        imager.append(0)
    image_r = array.array('B', imager)
    return image_r

def cambiar_colores_green(lista, intensidad):
    imageg = []
    cuerpo = b''
    cuerpo = cuerpo + lista
    cuerpo_c = [i for i in cuerpo]
    for j in range(1, len(cuerpo_c), 3):
        valor = int(float(cuerpo_c[j]) * float(intensidad))
        if valor > 255:
            valor = 255
        imageg.append(0)
        imageg.append(valor)
        imageg.append(0)
    image_g = array.array('B', imageg)
    return image_g
    
def cambiar_colores_blue(lista, intensidad):
    imageb = []
    cuerpo = b''
    cuerpo = cuerpo + lista
    cuerpo_c = [i for i in cuerpo]
    for j in range(2, len(cuerpo_c), 3):
        valor = int(float(cuerpo_c[j]) * float(intensidad))
        if valor > 255:
            valor = 255
        imageb.append(0)
        imageb.append(0)
        imageb.append(valor)
    image_b = array.array('B', imageb)
    return image_b 

def cambiar_colores_bw(lista, intensidad):
    imagebw = []
    i=0
    prom=0
    cuerpo = b''    
    cuerpo = cuerpo + lista
    cuerpo_c = [i for i in cuerpo]
    for j in range(1, len(cuerpo_c), 1):
        valor = int(float(cuerpo_c[j]))
        prom += valor
        i += 1
        if i == 3:
            prom = int((prom//3) * float(intensidad))
            if prom > 255:
                prom = 255
            imagebw.append(prom)
            imagebw.append(prom)
            imagebw.append(prom)
            prom = 0
            i = 0
    image_bw = array.array('B', imagebw)
<<<<<<< HEAD
    return image_bw       
=======
    try:
        with open(directorio + imagen+'-black&white.ppm', 'ab') as f:
            print(encabezado)
            print(directorio)
            print(imagen)
            if encabezado != "":
                f.write(bytearray(encabezado, 'ascii'))
                print("aca esta:",encabezado)
            image_bw.tofile(f)
            os.close(f)
    except FileNotFoundError:
        print("El archivo no se encuentra en el directorio")
        sys.exit()        
 


>>>>>>> f4a3bd046448f872ad360084ce8df6a8f9b4a779
