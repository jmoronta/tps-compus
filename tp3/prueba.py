#!/usr/bin/python3

import os
import sys 
import binascii
import fnmatch
import re
from concurrent import futures
import array

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
        
        
        thread = futures.ThreadPoolExecutor()
        lista = []
                
        if filtro == 'R' :
            rojo = thread.submit(cambiar_colores_red,encabezado,cuerpo,intensidad,directorio,imagen)    
            lista = rojo.result()
            listafinal = array.array('B',lista)
            imagen = imagen.split(sep=".")[0]
            try:
                with open(directorio + imagen+'-red.ppm', 'ab') as f:
                    print("creando archivo...")
                    if encabezado != "":
                        f.write(bytearray(encabezado, 'ascii'))
                    listafinal.tofile(f)
            except FileNotFoundError:
                print("El archivo no se encuentra en el directorio")
                sys.exit()
        elif filtro == 'B' :
            azul = thread.submit(cambiar_colores_blue,encabezado,cuerpo,intensidad,directorio,imagen)
            #rojo = thread.submit(cambiar_colores_red,encabezado,cuerpo,intensidad,directorio,imagen)    
            lista = azul.result()
            listafinal = array.array('B',lista)
            imagen = imagen.split(sep=".")[0]
            try:
                with open(directorio + imagen+'-blue.ppm', 'ab') as f:
                    print("creando archivo...")
                    if encabezado != "":
                        f.write(bytearray(encabezado, 'ascii'))
                    listafinal.tofile(f)
            except FileNotFoundError:
                print("El archivo no se encuentra en el directorio")
                sys.exit()
        elif filtro == 'G' :
                verde = thread.submit(cambiar_colores_green,encabezado,cuerpo,intensidad,directorio,imagen)
                #rojo = thread.submit(cambiar_colores_red,encabezado,cuerpo,intensidad,directorio,imagen)    
                lista = verde.result()
                listafinal = array.array('B',lista)
                imagen = imagen.split(sep=".")[0]
                try:
                    with open(directorio + imagen+'-green.ppm', 'ab') as f:
                        print("creando archivo...")
                        if encabezado != "":
                            f.write(bytearray(encabezado, 'ascii'))
                        listafinal.tofile(f)
                except FileNotFoundError:
                    print("El archivo no se encuentra en el directorio")
                    sys.exit()
        elif filtro == 'W' :
                blanco = thread.submit(cambiar_colores_bw,encabezado,cuerpo,intensidad,directorio,imagen)
                #rojo = thread.submit(cambiar_colores_red,encabezado,cuerpo,intensidad,directorio,imagen)    
                lista = blanco.result()
                listafinal = array.array('B',lista)
                imagen = imagen.split(sep=".")[0]
                try:
                    with open(directorio + imagen+'-bw.ppm', 'ab') as f:
                        print("creando archivo...")
                        if encabezado != "":
                            f.write(bytearray(encabezado, 'ascii'))
                        listafinal.tofile(f)
                except FileNotFoundError:
                    print("El archivo no se encuentra en el directorio")
                    sys.exit()
        else: 
                print("No se pudo aplicar el filtro")
                estado = 1
        leido = os.read(archivo, size)
        #print(leido)

        #return estado

def cambiar_colores_red(encabezado,cuerpo2, intensidad,directorio,imagen):
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
    return image_b 

def cambiar_colores_bw(encabezado,lista, intensidad,directorio,imagen):
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
    return image_bw        
 

if __name__ == "__main__":
    
    directorio= "/home/kbza/tp3/"
    puerto=0
    size=1024
    hilos=3
    intensidad = 2
    filtro = "W"
    imagen= "dog.ppm"
    aplicarfiltro(imagen,filtro, intensidad,size,directorio,hilos)
 
