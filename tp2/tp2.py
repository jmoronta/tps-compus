#!/usr/bin/python3
import multiprocessing
import os
import argparse
from os import times
from posix import times_result
import sys
import time
import funciones as fc

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tp1 - procesa ppm')
    parser.add_argument('-m', '--mensaje',action="store",dest="mensaje", type= str, default=1, help="Mensaje")
    parser.add_argument('-p', '--portador',action="store", dest="portador", type= int, default=1, help="Portador")
    parser.add_argument('-i', '--interleave',action="store" , dest="interleave", type= int, default=1, help="interleave")
    parser.add_argument('-s', '--size',action="store", type= int, required=True, help="Bloque de lectura")
    parser.add_argument('-f', '--file1',action="store", dest="file1", required=True, type=str, help="archivo a procesar")
    parser.add_argument('-o', '--file2',action="store", dest="file2", required=True, type=str, help="archivo procesado")
    args =  parser.parse_args()
    archivoOringen = args.file1
    archivoSalida = args.file2
    portador = args.portador
    interleave = args.interleave
    mensaje = args.mensaje
    
    queuec = multiprocessing.Queue()
    #start_time = Timer.time()
    # abrir archivo
    #path = os.path.dirname(os.path.abspath(__file__))
    path = /home/kbza/tps/tp2/
    size = int(args.size)
    #print(path)
    print(path+"/"+archivoOringen)
    try:
        archivo = os.open(path + "/" + archivoOringen, os.O_RDONLY)
    except FileNotFoundError:
        print("El archivo no se encuentra en el directorio")
        sys.exit()
    leido = os.read(archivo, size)
    dimen = False
    path = os.path.dirname(__file__) + "/"
    try:
        with open(path + mensaje, "rb") as archivo_msg:
                mensaje = archivo_msg.read()
    except FileNotFoundError:
        print("El archivo no se encuentra en el directorio")
        sys.exit()
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
    ultimo = leido.find(b"\n", medio) + 1
    encabezado = leido[:ultimo].decode()
    if archivoSalida != 0:
        encabezado_new = encabezado + '#UMCOMPU2 {} {} {}'.format(portador, interleave, len(mensaje) + 4)
        verdadera = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        falsa = "nopqrstuvwxyzabcdefghijklmNOPQRSTUVWXYZABCDEFGHIJKLM"
        transform = dict(zip(verdadera, falsa))
        mensaje = ''.join(transform.get(char, char) for char in str(mensaje))
    else:
        encabezado_new = encabezado + '#UMCOMPU2 {} {} {}'.format(portador, interleave, len(mensaje) + 4)
    #print(encabezado_new)
    #print(size)
    # saco ancho y largo
    linea = leido.splitlines()
    for i in range(len(linea)):
        if dimen is False:
            word = linea[i].split()
            if len(word) == 2:
                width = int(word[0])
                height = int(word[1])
                dimen = True
                num_bytes = width * height * 3 // 8
    # guardo el cuerpo
    cuerpo = leido[ultimo:]
    #print(len(cuerpo))
    #print(cuerpo)
    # envio primer parte del cuerpo
    queuec.put(cuerpo)
    # creo hijos
    h_c = multiprocessing.Process(target=fc.ocultarojo, args=(encabezado_new, queuec, num_bytes, mensaje,interleave,portador,archivoSalida))
    # inicio los hijos
    h_c.start()
    # paso el resto del cuerpo
    while True:
        cuerpo = os.read(archivo, size)
        #print(cuerpo)
        queuec.put(cuerpo)
        if len(cuerpo) != size:
            break
    queuec.put("Terminamos")
    h_c.join()
    if os.path.exists('{}'.format(archivoSalida)):
        print("Archivo creado con exito")
    else:
        print("El archivo no fue creado")
    os.close(archivo)
    # Tiempo total de ejecucion
    #elapsed_time = time.time() - start_time
    #print("Tiempo de ejecucion: %0.10f seconds." % elapsed_time)
    #os.close(archivo)
