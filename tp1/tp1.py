#!/usr/bin/python3
import multiprocessing
import os
import argparse
import sys
import funciones as fc



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tp1 - procesa ppm')
    parser.add_argument('-r', '--red',action="store",dest="rojo", type= int, default=1, help="Escala para rojo")
    parser.add_argument('-g', '--green',action="store", dest="verde", type= int, default=1, help="Escala para verde")
    parser.add_argument('-b', '--blue',action="store" , dest="azul", type= int, default=1, help="Escala para azul")
    parser.add_argument('-s', '--size',action="store", type= int, required=True, help="Bloque de lectura")
    parser.add_argument('-f', '--file',action="store", dest="file", required=True, type=str, help="archivo a procesar")
    args =  parser.parse_args()
    archivo = args.file
    size = args.size
    rojo = args.rojo
    azul = args.azul
    verde = args.verde
    
    # abrir archivo
    path = os.path.dirname(os.path.abspath(__file__))
    size = int(args.size)
    try:
        archivo = os.open(path + "/" + args.file, os.O_RDONLY)
    except FileNotFoundError:
        print("El archivo no se encuentra en el directorio")
        sys.exit()
    leido = os.read(archivo, size)
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
    # guardo el cuerpo
    cuerpo = leido[final:]

    queuered = multiprocessing.Queue()
    queuegreen = multiprocessing.Queue()
    queueblue = multiprocessing.Queue()
    queuee = multiprocessing.Queue()
    # envio primer parte del cuerpo
    queuered.put(cuerpo)
    queuegreen.put(cuerpo)
    queueblue.put(cuerpo)
    queuee.put(cuerpo)
    #print(cuerpo)
    #print(rojo)
    # creo hijos
    h_r = multiprocessing.Process(target=fc.cambiar_colores_red, args=(encabezado,queuered,rojo))
    h_g = multiprocessing.Process(target=fc.cambiar_colores_green, args=(encabezado,queuegreen,verde ))
    h_b = multiprocessing.Process(target=fc.cambiar_colores_blue, args=(encabezado,queueblue,azul ))
    h_e = multiprocessing.Process(target=fc.espejado, args=(encabezado, queuee, width, height))
    # inicio los hijos
    h_r.start()
    h_g.start()
    h_b.start()
    h_e.start()
    # paso el resto del cuerpo
    while True:
        cuerpo = os.read(archivo, args.size)
        queuered.put(cuerpo)
        queuegreen.put(cuerpo)
        queueblue.put(cuerpo)
        queuee.put(cuerpo)
        if len(cuerpo) != size:
            break
    queuered.put("Terminamos")
    queuegreen.put("Terminamos")
    queueblue.put("Terminamos")
    queuee.put("Terminamos")
    # uno al los hijos con el padre
    h_r.join()
    h_g.join()
    h_b.join()
    h_e.join()
    
    if os.path.exists('red.ppm') and os.path.exists('green.ppm') and os.path.exists('blue.ppm'):
        print("Archivos creados con exito")
