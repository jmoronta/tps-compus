#!/usr/bin/python3
import os
import queue
import sys 
import binascii
import array
import threading


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

def cambiar_colores_red(encabezado,cola, intensidad):
    imager = []
    cuerpo = b''
    while True:
        mensaje = cola.get()
        if mensaje == "Terminamos":
            break
        else:
            cuerpo = cuerpo + mensaje
    cuerpo_c = [i for i in cuerpo]
    for j in range(0, len(cuerpo_c), 3):
        valor = int(float(cuerpo_c[j]) * float(intensidad))
        if valor > 255:
            valor = 255
        imager.append(valor)
        imager.append(0)
        imager.append(0)
    image_r = array.array('B', imager)
    with open('red.ppm', 'wb') as f:
        f.write(bytearray(encabezado, 'ascii'))
        image_r.tofile(f)
def cambiar_colores_green(encabezado,cola, intensidad):
    imageg = []
    cuerpo = b''
    while True:
        mensaje = cola.get()
        if mensaje == "Terminamos":
            break
        else:
            cuerpo = cuerpo + mensaje
    cuerpo_c = [i for i in cuerpo]
    for j in range(1, len(cuerpo_c), 3):
        valor = int(float(cuerpo_c[j]) * float(intensidad))
        if valor > 255:
            valor = 255
        imageg.append(0)
        imageg.append(valor)
        imageg.append(0)
    image_g = array.array('B', imageg)
    with open('green.ppm', 'wb') as f:
        f.write(bytearray(encabezado, 'ascii'))
        image_g.tofile(f)
def cambiar_colores_blue(encabezado,cola, intensidad):
        
    imageb = []
    cuerpo = b''
    while True:
        mensaje = cola.get()
        if mensaje == "Terminamos":
            break
        else:
            cuerpo = cuerpo + mensaje
    cuerpo_c = [i for i in cuerpo]
    for j in range(2, len(cuerpo_c), 3):
        valor = int(float(cuerpo_c[j]) * float(intensidad))
        if valor > 255:
            valor = 255
        imageb.append(0)
        imageb.append(0)
        imageb.append(valor)
    image_b = array.array('B', imageb)
    with open('blue.ppm', 'wb') as f:
        f.write(bytearray(encabezado, 'ascii'))
        image_b.tofile(f)
           
def espejado(encabezado, queuee, width, height):
    imagee = []
    image = []
    imagene = []
    cuerpo = b''
    while True:
        mensaje = queuee.get()
        if mensaje == "Terminamos":
            break
        else:
            cuerpo = cuerpo + mensaje
    cuerpo_c = [i for i in cuerpo]
    j = 0
    for i in range(height):
        for n in range(width):
            for c in range(3):
                valor = int(float(cuerpo_c[j]))
                imagene.append(valor)
                j += 1
            imagee.append(imagene)
            imagene = []
            imagee.reverse()
            image.extend(imagee[n])
    image_e = array.array('B', image)
    with open('espejado.ppm', 'wb') as f:
        f.write(bytearray(encabezado, 'ascii'))
        image_e.tofile(f)
        
def ocultarojo(encabezado_new, queuec, num_bytes, message,interleave,portador,salida):
    imagec = []
    cuerpo = b''
    k = 0
    start = 0
    if message != " ":
        binario = ''.join(format(ord(x), '08b') for x in str(message))
    else:
        raise TypeError("Mensaje vacío. Por favor ingrese un mensaje")

    i=0
    if len(message) > num_bytes:
        raise ValueError("Error bytes insuficientes")
    while True:
        mensaje = queuec.get()
        if mensaje == "Terminamos":
            break
        else:
            cuerpo = cuerpo + mensaje
    cuerpo_c = [i for i in cuerpo]
    #print(len(cuerpo))
    x = len(binario)
    for j in range(0, len(cuerpo_c), int(interleave)):
        valor = cuerpo_c[j]
        if start < int(portador):
            start += 1
            imagec.append(cuerpo_c[j])
        else:
            if x > k:
                bit = binario[k]
                if valor % 2 != int(bit):
                    if valor > 255:
                        valor -= 1
                    else:
                        valor += 1
                k += 1
                imagec.append(valor)
            else:
                imagec.append(cuerpo_c[j])
    image_c = array.array('B', imagec)
    
    h_g = threading.Thread(target=ocultarverde, args=(encabezado_new, image_c, binario,interleave,portador,salida))
    h_g.start()
    h_g.join()    

def ocultarverde(encabezado_new, imagec, binario,interleave,portador,salida):
    k = 0
    start = 0
    x = len(binario)
    inicio_g = 1 + (3 * int(portador))
    for j in range(0, len(imagec), int(interleave)):
        valor = imagec[j]
        if start < inicio_g:
            start += 1
            imagec.append(imagec[j])
        else:
            if x > k:
                bit = binario[k]
                if valor % 2 != int(bit):
                    if valor > 255:
                        valor -= 1
                    else:
                        valor += 1
                k += 1
                imagec.append(valor)
            else:
                imagec.append(imagec[j])
    h_b = threading.Thread(target=ocultarazul, args=(encabezado_new, imagec, binario,interleave,portador,salida))
    h_b.start()
    h_b.join()

def ocultarazul(encabezado_new, imagec, binario,interleave,portador,salida):
    k = 0
    start = 0
    x = len(binario)
    inicio_b = 2 + (3 * int(portador))
    for j in range(0, len(imagec), int(interleave)):
        valor = imagec[j]
        if start < inicio_b:
            start += 1
            imagec.append(imagec[j])
        else:
            if x > k:
                bit = binario[k]
                if valor % 2 != int(bit):
                    if valor > 255:
                        valor -= 1
                    else:
                        valor += 1
                k += 1
                imagec.append(valor)
            else:
                imagec.append(imagec[j])
    image_c = array.array('B', imagec)
    with open('{}'.format(salida), 'wb') as f:
        f.write(bytearray(encabezado_new, 'ascii'))
        #print(len(image_c))
        image_c.tofile(f)
        
def eliminar_comentario(texto):
    # Le saco el comentario a la imagen
    text = texto
    for i in range(text.count(b"\n#")):
        inicio = text.find(b"\n# ")
        fin = text.find(b"\n", inicio + 1)
        text = text.replace(text[inicio:fin], b"")
    return text


def header(text, comentario):
    # Le saco el encabezado a la imagen
    header = text[:15].decode()
    # Le agrego el comentario
    header = header[0:2] + "\n" + comentario + header[2:]
    return header


def calcular_posicion(imagen):
    for i in range(imagen.count(b"\n# ")):  # Si hay comentarios en la imagen
        barra_n_numeral = imagen.find(b"\n#")+1
        barra_n = imagen.find(b"\n", barra_n_numeral)
        # Ultimo barra antes de arrancar con la imagen
    if imagen.count(b"\n# ") == 0:  # Si no hay comentarios
        barra_n = imagen.find(b"\n")
    medidas = imagen.find(b"\n", barra_n + 1)
    profundidad = imagen.find(b"\n", medidas+1)
    return profundidad + 1
   
def leer_mensaje(message,size):
    mensaje = os.open(message, os.O_RDONLY)#Abro mensaje a leer
    mensaje_leido = os.read(mensaje,size)#Leo mensaje 
    #print(mensaje_leido)

    lista_mensaje = []
    for i  in mensaje_leido:
        lista_mensaje.append("{0:b}".format(i))
    print(lista_mensaje)

    contador = 0

    for caracteres in lista_mensaje:
        for i in range(8-(len(caracteres))):
            caracteres = "0" + caracteres

        lista_mensaje[contador]= caracteres
        contador +=1

    mensaje_binario ="" #Queda mensaje en ceros y unos como un solo texto

    for caracteres in lista_mensaje:
        mensaje_binario = mensaje_binario + caracteres 
    longitud = len(mensaje_binario)
    return mensaje_binario, longitud
