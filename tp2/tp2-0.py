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
global imagen_leida
imagen_leida = ""
	
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


def leer_mensaje(message, size):
    mensaje = os.open(message, os.O_RDONLY)  # Abro mensaje a leer
    mensaje_leido = os.read(mensaje, size)  # Leo mensaje
    # print(mensaje_leido)

    lista_mensaje = []
    for i in mensaje_leido:
        lista_mensaje.append("{0:b}".format(i))

    contador = 0

    for caracteres in lista_mensaje:
        for i in range(8-(len(caracteres))):
            caracter = "0" + caracteres
        lista_mensaje[contador] = caracter
        caracteres = "0" + caracteres

        lista_mensaje[contador] = caracteres
        contador += 1
    mensaje_binario = ""
    for i in lista_mensaje:
        mensaje_binario += i
    longuitud = len(mensaje_binario)
    return mensaje_binario, longuitud

    mensaje_binario = ""  # Queda mensaje en ceros y unos como un solo texto

    for caracteres in lista_mensaje:
        mensaje_binario = mensaje_binario + caracteres
    longitud = len(mensaje_binario)
    return mensaje_binario, longitud

if __name__ == '__main__':
    parser = ArgumentParser(description='Steganography')
    parser.add_argument("-s", "--size",dest="size", type=int, default=1024, help="Reading block")
    parser.add_argument("-f", "--file",dest="file", default="dog.ppm", help="PPM file, Image to analized")
    parser.add_argument("-m", "--message",dest="mensaje", default="message.txt", help="Steganographic message")
    parser.add_argument("-of", "--offset",dest="offset", type=int, default=15, help="Offset in pixels of raster start")
    parser.add_argument("-i", "--interleave",dest="interleave", type=int, default=10, help="pixel mod interleave")
    parser.add_argument("-o", "--output",dest="salida", default="output_message.ppm", help="Stego-message")
    args =  parser.parse_args()
	
    #global lista
	#lista = []
	
# funcion para obtener argumentos
def main():
    #tiempo_inicio = time()
    # Creo los argumentos
    #args = argumentos()
    size = int(args.size)
    # Verifico que el pixel este completo
    if size % 3 != 0:
        size += (3 - (size % 3))
    # Genero el path absoluto
    path = os.path.abspath(os.getcwd())
    # path = os.path.abspath(os.getcwd())
    # abro la imagen
    archivo = os.open(args.file, os.O_RDONLY)
    # Calculo el tamaño de la imagen
    tam_ima = os.path.getsize(path + "/" + args.file)
    # abro la imagen y lo guardo en imagen
    imagen = os.read(archivo, size)
    # abro el mensaje y obtengo una str con el mensaje en bit
    mensaje = open(path + "/" + args.mensaje, "rb")
    mensaje, long_men = leer_mensaje(args.mensaje, size)
    # mensaje = open(path + "/" + args.message, "rb")
    message, long_men = leer_mensaje(args.mensaje, size)
    # paso a int el interleave y el offset
    interleave = int(args.interleave)
    offset = int(args.offset)
    # creo la cabecera del nuevo archivo
    comentario = "#UMCOMPU2 {} {} {}".format(args.offset, args.interleave, long_men)
    texto1 = eliminar_comentario(imagen)
    cabecera = header(texto1, comentario)
    #cabecera, width, height = header(texto1, comentario)
    '''if long_men * args.interleave + args.offset > int(width) * int(height):
        raise OverflowError("No hay bytes suficientes en la imagen para"
                            "insertar el mensage con el interleave y"
                            " el offset ingresados")'''
    # Me paro donde inicia el curpo en la imagen
    #os.lseek(archivo, posicion, 0)
    # Creo el output y le paso el header
    output = open(args.salida, "wb", os.O_CREAT)
    output.write(bytearray(cabecera, 'ascii'))
    # Creo hilos
    hilos = concurrent.futures.ThreadPoolExecutor(max_workers=3)
    for i in range(3):
        # i = indice
        hilos.submit(encriptar, args.interleave, args.offset, args.mensaje, i, args.size)
    # declaro global las variables donde se almacena lo leido de la imagen y
    # la lista donde lo guardo
    global imagen_leida
    global lista
    while True:
        # Creo hilos
        hilo_rojo = threading.Thread(target=encriptar_rojo, args=(args.interleave,
                                     args.offset,args.mensaje))
        hilo_verde = threading.Thread(target=encriptar_verde, args=(args.interleave,
                                      args.offset, args.mensaje))
        hilo_azul = threading.Thread(target=encripar_azul, args=(args.interleave,
                                     args.offset,args.mensaje))
        # Pongo un lock para leer la imagen
        lc.acquire
        imagen_leida = os.read(archivo, size)
        lista = [i for i in imagen_leida]
        #lc.release
        #print("entro")
        #b.wait()
        #print("salio")
        hilo_rojo.start()
        hilo_verde.start()
        hilo_azul.start()
        # print("entro")
        hilo_rojo.join()
        hilo_verde.join()
        hilo_azul.join()
        # print("salio")
        lc.acquire
        imagen_nueva = array.array('B', lista)
        imagen_nueva.tofile(output)
        lc.release
        if len(imagen_leida) != size:
            break
    output.close()
    #print("Se genero correctamente, el proceso tardo: ")
    #print(time() - tiempo_inicio, " segundos")


def encriptar(interleave, offset, mensaje, indice, size):
    global imagen_leida
    global lista
def encriptar_rojo(interleave, offset, mensaje):
    # Indices del mensaje para cada color
    c_r = 0  # 0, 3, 6, 9
    c_v = 1  # 1, 4, 7, 10
    c_b = 2  # 2, 5, 8, 11
    global lista
    # Indices para la lista
    # Rojo
    ini_r = 0 + (3*offset)
    fin_r = ini_r + len(mensaje) * (interleave * 3)
    ini_r = 0 + ((3*offset))
    fin_r = len(lista)
    for j in range(ini_r, fin_r, (interleave*9)):
        if c_r < len(mensaje):
            lc.acquire()
            if lista[j] % 2 == 0:
                if mensaje[c_r] == "0":
                    lista[j] = lista[j]
                else:
                    lista[j] += 1
            else:
                if mensaje[c_r] == "1":
                    lista[j] = lista[j]
                else:
                    lista[j] -= 1
            lc.release()
            c_r += 3


def encriptar_verde(interleave, offset, mensaje):
    c_v = 1  # 1, 4, 7, 10
    global lista
    # verde
    ini_v = 4 + (3*(int(offset)) + ((int(interleave)-1)*3))
    if interleave == 1:
        ini_v = 4 + (3*(int(offset)))
    fin_v = ini_v + len(mensaje)*(int(interleave)*3)
    ini_v = 1 + (3*(offset)) + (3*(interleave))
    fin_v = len(lista)
    for j in range(ini_v, fin_v, (interleave*9)):
        if c_v < len(mensaje):
            lc.acquire()
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
            lc.release()
            c_v += 3


def encripar_azul(interleave, offset, mensaje):
    c_b = 2  # 2, 5, 8, 11
    global lista
    # azul
    ini_b = 8 + (3*(offset)) + interleave + (((int(interleave)-2)*3))
    if interleave == 1:
        ini_b = 8 + (3*(int(offset)))
    fin_b = ini_b + len(mensaje) * (int(interleave)*3)
    while True:
        if indice == 0:  # rojo
            # offset == pixel en el cual comienza ,
            #  interleave == Saltos de pixel
            # offset 0 == 1° pixel, interleave 1 == proximo pixel
            # offset 0 e interleave 1 el rojo se mueve cada 9 lugares
            # offset se multiplica por 3 y el interleva tambien
            if c_b < len(mensaje):
                for j in range(ini_b, fin_b, (interleave*9)):
                    lc.acquire()
                    if lista[j] % 2 == 0:
                        if mensaje[c_r] == "0":
                            lista[j] = lista[j]
                        else:
                            lista[j] += 1
                    else:
                        if mensaje[c_b] == "1":
                            lista[j] = lista[j]
                        else:
                            lista[j] -= 1
                    c_b += 3
                    lc.release()
        elif indice == 1:
            if c_b < len(mensaje):
                for j in range(ini_b, fin_b, (interleave*9)):
                    lc.acquire()
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
                    c_b += 3
                    lc.release()
        else:
            if c_b < len(mensaje):
                for j in range(ini_b, fin_b, (interleave*9)):
                    lc.acquire()
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
                    c_b += 3
                    lc.release()
        b.wait()
        if len(imagen_leida) < size:
            break
    ini_b = 2 + (3*(offset) + ((interleave)*6))
    fin_b = len(lista)
    for j in range(ini_b, fin_b, (interleave*9)):
        if c_b < len(mensaje):
            lc.acquire()
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
            lc.release()
            c_b += 3


if __name__ == "__main__":
    main()
