#!/usr/bin/python3
<<<<<<< HEAD

import os
import argparse
import array
import concurrent.futures as fut
import threading
from time import time

global reading
barrier = threading.Barrier(4)
lock = threading.Lock()


def cambiarA_LSB(byte, bit):
    if byte % 2 != bit:
        if bit == 1:
            byte += 1
        else:
            byte -= 1

    return byte


def modificar(color, total_bytes, cambio, message):
    global reading

    bits = [message[i] for i in range(color, len(message), 3)]
    written = 0
    while written < total_bytes:

        written = len(reading)

        # modifican bytes y guardan en lista
        while cambio != [] and cambio[0] < written:

            lock.acquire()

            index_to_change = cambio.pop(0)
            reading[index_to_change] = cambiarA_LSB(reading[index_to_change], int(bits.pop(0)))
            lock.release()

        barrier.wait()
def cabecera(fd):
    lines = os.read(fd, 100).splitlines()
    comments = []
    header_end = 0
    for line in lines:
        if line == b"P6":
            header_end += len(line) + 1
        elif line[0] == ord("#"):
            comments.append(line)
            header_end += len(line) + 1
        elif len(line.split()) == 2:
            words = line.split()
            width = int(words[0])
            height = int(words[1])
            header_end += len(line) + 1
        else:
            max_c = int(line)
            header_end += len(line) + 1
            break

    return header_end, width, height, max_c, comments


def crearcabecera(width, height, max_c, comments):
    return "P6\n" + comments + "\n" + str(width) + " " + str(height) + "\n" + str(max_c) + "\n"

# main del programa
def main():
    inicio = time()

    global reading
    reading = []

    # argumentos
    parser = argparse.ArgumentParser()

    parser.add_argument("-f", "--file", type=str, required=True,
                        help="ppm should be")
    parser.add_argument("-m", "--message", type=str, required=True,
                        help="file")
    parser.add_argument("-o", "--output", type=str, required=True,
                        help="file")
    parser.add_argument("-s", "--size", type=int, default=1024,
                        help="size")
    parser.add_argument("-e", "--offset", type=int, required=True,
                        help="interleave pixels")
    parser.add_argument("-i", "--interleave", type=int, required=True,
                        help="interleave pixels")

    args = parser.parse_args()

    if not args.file.endswith(".ppm"):
        raise print("la imagen tiene un formato invalido")

    # determino el path del script
    path = os.path.dirname(__file__)
    print(path)
    # determino la longitud de la imagen
    L_file = os.path.getsize(path + args.file)

    # determino el mensaje a escribir y su longitud
    with open(path + args.message, "rb") as archivo:
        message = archivo.read()
        L_TOTAL = len(message)

    x = []
    for i in message:
        bit = bin(i)[2:]
        while len(bit) < 8:
            bit = "0" + bit
        x.append(bit)

    message = "".join(x)

    # abro la imagen
    fd = os.open(path + args.file, os.O_RDONLY)

    # leo el header de la imagen
    header_end, width, height, max_c, comments = cabecera(fd)

    if len(message) * args.interleave + args.offset > width*height:
        raise print("No hay suficientes bytes en la imagen para insertar un mensaje con los valores de intercalación y desplazamiento dados")
    # muevo el puntero al primer pixel del cuerpo modificar
    os.lseek(fd, header_end, 0)

    # inserto el comentario con los datos de la codificacion
    comments = "#UMCOMPU2 " + str(args.offset) + " " + str(args.interleave) + " " + str(L_TOTAL)

    # crea el archivo imagen solo con el header
    wfd = os.open(path + args.output, os.O_WRONLY | os.O_CREAT)
    N_header = crearcabecera(width, height, max_c, comments)
    L_header = len(N_header)
    os.close(wfd)

    # determina pixels a modificar
    # Los indices de los pixels son en relacion al inicio del raster, que es donde se va a empezar a leer
    modify_indexes_R = []
    c = 0
    for pixel in range(args.offset*3, L_file - header_end, args.interleave*3):

        modify_indexes_R.append(pixel + c)
        c += 1
        if c == 3:
            c = 0

    modify_indexes_R = modify_indexes_R[:len(message)]

    r = [modify_indexes_R[i] for i in range(0, len(modify_indexes_R), 3)]
    g = [modify_indexes_R[i] for i in range(1, len(modify_indexes_R), 3)]
    b = [modify_indexes_R[i] for i in range(2, len(modify_indexes_R), 3)]

    indexes = (r, g, b)

    # lanza hilos
    hilos = fut.ThreadPoolExecutor(max_workers=3)
    [hilos.submit(modificar, i, width * height * 3, indexes[i], message) for i in range(3)]

    output = open(path + args.output, "wb", os.O_CREAT)
    output.write(bytearray(N_header, 'ascii'))

    # lee imagen
    written = 0
    while written < (width * height * 3):
        lock.acquire()
        reading += [i for i in os.read(fd, args.size)]
        lock.release()
        written = len(reading)
        barrier.wait()

    # escribe la imagen
    if reading:
        image = array.array('B', reading)
        image.tofile(output)
    try:
        barrier.wait(0.1)
    except threading.BrokenBarrierError:
        pass

    output.close()
    print("Terminamos, inicio del raster es:",L_header, "y el tamaño del mensaje es:",L_TOTAL)
    print(str(time()-inicio)[:4], "segundos")


if __name__ == "__main__":
    main()
=======
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
    path = os.path.dirname(os.path.abspath(__file__))
    size = int(args.size)
    print(path)
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
>>>>>>> f4a3bd046448f872ad360084ce8df6a8f9b4a779
