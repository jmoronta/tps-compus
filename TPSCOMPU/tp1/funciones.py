#!/usr/bin/python3
import os
import queue
import sys 
import binascii
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

