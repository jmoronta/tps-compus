#!/usr/bin/python3

import os
import sys 
import binascii
import fnmatch
import re

from concurrent import futures
import array

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


def aplicarfiltro(imagen,filtro, intensidad,size,directorio,hilos):
    try:
        archivo = os.open(directorio + "/" + imagen, os.O_RDONLY)
    except FileNotFoundError:
        print("El archivo no se encuentra en el directorio")
        sys.exit()
    if size % 3 != 0: #VEO si es multiplo de 3
        size += (3 - (size % 3))
    leido = os.read(archivo, size)
    estado = 0
    valor=0 
    calcularencabezado=True 
    
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
            rojo = thread.submit(cambiar_colores_red,encabezado,cuerpo,intensidad,directorio,imagen)
            
        elif filtro == 'B' :
            azul = thread.submit(cambiar_colores_blue,encabezado,cuerpo,intensidad,directorio,imagen)
           
        elif filtro == 'G' :
            verde = thread.submit(cambiar_colores_green,encabezado,cuerpo,intensidad,directorio,imagen)
        
        elif filtro == 'W' :
            blanco = thread.submit(cambiar_colores_bw,encabezado,cuerpo,intensidad,directorio,imagen)
            
        else: 
            print("No se pudo aplicar el filtro")
            estado = 1
        leido = os.read(archivo, size)
        #print(leido)

                    
    return estado

def cambiar_colores_red(encabezado,cuerpo2, intensidad,directorio,imagen):
    imager = []
    cuerpo = b''
    #print(len(cuerpo2))
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
    #print(image_r)
    #print("Imprimiendo tamaño: ",len(image_r))
    try:
        with open(directorio + imagen+'-red.ppm', 'ab') as f:
            #print("creando archivo...")
            if encabezado != "":
                #print(len(encabezado))
                f.write(bytearray(encabezado, 'ascii'))
                #print(encabezado)
            #f.write(bytearray(image_r, 'ascii'))
            image_r.tofile(f)
            #print(image_r)
        os.close(f)
    except FileNotFoundError:
        print("El archivo no se encuentra en el directorio")
        #sys.exit()'''
    #print("Aca muestro que salio:",len(image_r))
    #return image_r

def cambiar_colores_green(encabezado,lista, intensidad,directorio,imagen):
    imageg = []
    #print("viene",type(lista))
    cuerpo = b''
    cuerpo = cuerpo + lista
    #print("se vuelve",type(cuerpo))
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
    '''try:
        with open(directorio + imagen+'-green.ppm', 'ab') as f:
            if encabezado != "":
                f.write(bytearray(encabezado, 'ascii'))
                #print(encabezado)
                #f.write(bytearray(image_r, 'ascii'))
            image_g.tofile(f)
                #print(image_r)
        os.close(f)
    except FileNotFoundError:
        print("El archivo no se encuentra en el directorio")
        sys.exit()'''
    
def cambiar_colores_blue(encabezado,lista, intensidad,directorio,imagen):
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
    try:
        with open(directorio + imagen+'-blue.ppm', 'ab') as f:
            if encabezado != "":
                f.write(bytearray(encabezado, 'ascii'))
                #print(encabezado)
                #f.write(bytearray(image_r, 'ascii'))
            image_b.tofile(f)
                #print(image_r)
        os.close(f)
    except FileNotFoundError:
        print("El archivo no se encuentra en el directorio")
        sys.exit()

def cambiar_colores_bw(encabezado,lista, intensidad,directorio,imagen):
    imagebw = []
    #print(encabezado)
    #print(lista)
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
    print(image_bw)
    with open(directorio + imagen+'-blackwhite.ppm', 'ab') as f:
        f.write(bytearray(encabezado, 'ascii'))
        image_bw.tofile(f)
        os.close(f)
    '''try:
        with open(directorio + imagen+'-blackwhite.ppm', 'ab') as f:
            #print(encabezado)
            print(directorio)
            print(imagen)
            if encabezado != "":
                f.write(bytearray(encabezado, 'ascii'))
                print("aca esta:",encabezado)
            image_bw.tofile(f)
            os.close(f)
    except FileNotFoundError:
        print("El archivo no se encuentra en el directorio")
        sys.exit()'''        
 


