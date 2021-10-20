from argparse import ArgumentParser
import argparse
import concurrent
import sys
import threading
from concurrent import futures
import os
from time import time
import time
import array

#barrier = threading.Barrier(3)
#lock = threading.Lock()
candado = threading.Lock()
b = threading.Barrier(4)
lc = threading.Lock()
global read #Variable de la imagen en hexa
read = ""
global lista
lista=[] 

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


def read_Message(message, size):
    mes = os.open(message, os.O_RDONLY)
    mes_read = os.read(mes, size)
    mesage = []
    for i in mes_read:
        mesage.append("{0:b}".format(i))
    count = 0
    for caract in mesage:
        for j in range(8-(len(caract))):
            charact = "0" + caract
        mesage[count] = charact
        count += 1
    mes_bin = ""
    for k in mesage:
        mes_bin += k
    l_total = len(mes_bin)
    return mes_bin, l_total
    with open(message, "rb") as f:
        content = list()
        buffer = f.read(size)
        while buffer:
            content.append(bin(int.from_bytes(buffer, byteorder="big")))
            buffer = f.read(size)
        return content, len(content)



def encriptar(interleave, offset, mensaje, indice, size):
    c_rojo = 0 # 0, 3, 6, 9
    c_verde = 1 # 1, 4, 7, 10
    c_blue = 2 # 2, 5, 8, 11
    
    if indice == 0:  # rojo
        # offset == pixel en el cual comienza , interleave == Saltos de pixel
        # offset 0 == 1° pixel, interleave 1 == proximo pixel
        # offset 0 e interleave 1 el rojo se mueve cada 9 lugares
        # offset se multiplica por 3 y el interleva tambien
        #print("esto es:",lista)
        lc.acquire()
        for j in range(0, len(lista), (interleave*9)):
            if c_rojo < len(mensaje):
                if lista[j + offset * 3] % 2 == 0:
                    if mensaje[c_rojo] == "0":
                        lista[j + offset * 3] = lista[j + offset * 3]
                    else:
                        lista[j + offset * 3] += 1
                else:
                    if mensaje[c_rojo] == "1":
                        lista[j + offset * 3] = lista[j + offset * 3]
                    else:
                        lista[j + offset * 3] -= 1
            c_rojo += 3
            lc.release()
    elif indice == 1:
        lc.acquire()
        for j in range(0, len(lista), interleave*9):
            if c_verde < len(mensaje):
                if lista[j + 1 + offset * 3 + interleave*3] % 2 == 0:
                    if mensaje[c_verde] == "0":
                        lista[j + 1 + offset * 3 + interleave*3] = lista[j + 1 + offset * 3 + interleave*3]
                    else:
                        lista[j + 1 + offset * 3 + interleave*3] += 1
                else:
                    if mensaje[c_verde] == "1":
                        lista[j + 1 + offset * 3 + interleave*3] = lista[j + 1 + offset * 3 + interleave*3]
                    else:
                        lista[j + 1 + offset * 3 + interleave*3] -= 1
            c_verde += 3
            lc.release()
    else:
        lc.acquire()
        for j in range(0, len(lista), interleave*9):
            if c_blue < len(mensaje):
                if lista[j + 2 + offset * 3 + interleave*6] % 2 == 0:
                    if mensaje[c_blue] == "0":
                        lista[j + 2 + offset * 3 + interleave*6] = lista[j + 2 + offset * 3 + interleave*6]
                    else:
                        lista[j + 2 + offset * 3 + interleave*6] += 1
                else:
                    if mensaje[c_blue] == "1":
                        lista[j + 2 + offset * 3 + interleave*6] = lista[j + 2 + offset * 3 + interleave*6]
                    else:
                        lista[j + 2 + offset * 3 + interleave*6] -= 1
                c_blue += 3
                lc.release()
    b.wait()    
    #if len(read) < size:
def encriptar_rojo(interleave, offset, mensaje):
    # Indices del mensaje para cada color
    c_r = 0  # 0, 3, 6, 9
    # Indices para la lista
    # Rojo
    print(lista)
    #lista = [i for i in lista]
    ini_r = 0 + ((3*offset))
    fin_r = len(lista) 
    #print("Ini R"+str(ini_r))
    #print("Fin R"+str(fin_r))
    # sys.exit(0)
    for j in range(ini_r, fin_r, (interleave*9)):
        #print("valor de j",j)
        #print("len mensaje"+str(len(mensaje)))
        if c_r < len(mensaje):
            #print("entramos")
            candado.acquire()
            if lista[j] % 2 == 0:
                #print("dividimos por dos")
                if mensaje[c_r] != "0":
                    lista[j] += 1
            else:
                #print("esto es lista J",str(lista[j] % 2))
                if mensaje[c_r] != "1":
                    lista[j] = lista[j] - 1
            candado.release()
            c_r += 3
def encriptar_verde(interleave, offset, mensaje):
    c_v = 1  # 1, 4, 7, 10
    
    # verde
    #lista = [i for i in lista]
    ini_v = 1 + (3*(offset) + ((interleave)*3))
    fin_v = len(lista)


    for j in range(ini_v, fin_v, (interleave*9)):
        if c_v < len(mensaje):
            candado.acquire()
            if lista[j] % 2 == 0:
                if mensaje[c_v] == "0":
                    lista[j] = lista[j]
                else:
                    lista[j] += 1
            else:
                if mensaje[c_v] == "1":
                    lista[j] = lista[j]
                else:
                    lista[j] -= 1
            candado.release()
            c_v += 3
def encripar_azul(interleave, offset, mensaje):
    c_b = 2  # 2, 5, 8, 11
    
    # azul
    #lista = [i for i in lista]
    ini_b = 2 + (3*(offset) + ((interleave)*6))
    fin_b = len(lista)

    for j in range(ini_b, fin_b, (interleave*9)):
        if c_b < len(mensaje):
            candado.acquire()
            if lista[j] % 2 == 0:
                if mensaje[c_b] == "0":
                    lista[j] = lista[j]
                else:
                    lista[j] += 1
            else:
                if mensaje[c_b] == "1":
                    lista[j] = lista[j]
                else:
                   lista[j] -= 1
            candado.release()
            c_b += 3

if __name__ == '__main__':
    parser = ArgumentParser(description='Steganography')
    parser.add_argument("-s", "--size",dest="size", type=int, default=1024, help="Reading block")
    parser.add_argument("-f", "--file",dest="file", default="dog.ppm", help="PPM file, Image to analized")
    parser.add_argument("-m", "--message",dest="mensaje", default="message.txt", help="Steganographic message")
    parser.add_argument("-of", "--offset",dest="offset", type=int, default=15, help="Offset in pixels of raster start")
    parser.add_argument("-i", "--interleave",dest="interleave", type=int, default=10, help="pixel mod interleave")
    parser.add_argument("-o", "--output",dest="salida", default="output_message.ppm", help="Stego-message")
    args =  parser.parse_args()

    start_time = time.time()
    message, l_total = read_Message(args.mensaje, args.size) #Read the message to encrypt
    #size_header = 100  #  size max for cabecera
    doc = os.open(args.file, os.O_RDONLY) #archivo
    read = os.read(doc, args.size)  # read del archivo
    ##Definition of header
    #doc = os.open(args.file, os.O_RDONLY) #archivo
    #read = os.read(doc, size_header)  # read del archivo
    offset = int(args.offset)
    #header = read[:offset]  # read the information of ppm file (number of cols and lines, and the encoding)
    comment = "#UMCOMPU2 {} {} {}\n".format(args.offset, args.interleave, l_total)
    posicion = calcular_posicion(read)
    #header = (read[0:2], "\n", comment, read[2:])
    texto1 = eliminar_comentario(read) #ELIMINO #Imagen ppm
    cabecera = header(texto1, comment)
    cuerpo = read[28:]
    #global lis
    lista = cuerpo
    salida = open(args.salida, "ab", os.O_CREAT)
    #print(cabecera)
    salida.write(bytearray(cabecera, 'ascii')) #Guardo la cabecera en el nuevo archivo
    
    while read:
        #print(cuerpo)
             # Pongo un lock para leer la imagen
        #hilos = futures.ThreadPoolExecutor(max_workers=3)
        
        hilo_rojo = threading.Thread(target=encriptar_rojo, args=(args.interleave, args.offset, args.mensaje))
        hilo_verde = threading.Thread(target=encriptar_verde, args=(args.interleave, args.offset, args.mensaje))
        hilo_azul = threading.Thread(target=encripar_azul, args=(args.interleave, args.offset, args.mensaje))
        
        hilo_rojo.start()
        hilo_verde.start()
        hilo_azul.start()

        hilo_rojo.join()
        hilo_verde.join()
        hilo_azul.join()

        imagen_nueva = array.array('B', lista)
        imagen_nueva.tofile(args.salida)
        print(len(imagen_nueva))
        if len(read) != args.size:
            break
        lc.acquire()
        read= os.read(doc, args.size)
        lista += [i for i in read] #Guardo imagen del bloque leia en 
        lc.release()
        b.wait()
        
    #read.close()
    print("se genero correctamente")

