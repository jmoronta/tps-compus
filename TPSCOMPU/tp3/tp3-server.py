#!/usr/bin/python3

import os
import sys
import argparse
import multiprocessing
import socketserver
import funciones as fc


class servidor(socketserver.ForkingTCPServer):
    def __init__(self,server_address,RequestHandlerClass,tamano,directorio,hilos):
        socketserver.ForkingTCPServer.allow_reuse_address = True
        socketserver.ForkingTCPServer.__init__(self,server_address,RequestHandlerClass)
        self.tamano = tamano
        self.directorio = directorio
        self.hilos=hilos


class Handler(socketserver.BaseRequestHandler):
        def handle(self):
            directorio = self.server.directorio
            tamano = self.server.tamano
            self.data = self.request.recv(tamano)
            hilos=self.server.hilos
            encabezado = self.data.decode().splitlines()[0]
            if encabezado.split()[1]== False:
                archivo = encabezado.split()[0]
                print(archivo)
            archivo = encabezado.split()[1]
            print(archivo)
            esunfiltro=archivo.find("?")
            print(esunfiltro)
            try:
                if esunfiltro != -1 :
                    dato = archivo.find("ppm")
                    if dato > 0:
                        image = archivo.split('&')
                        name = image[0].split('=')
                        color = image[1].split('=')
                        intensity = image[2].split('=')
                        intensidad = intensity[1]
                        imagen = name[1]
                        imagen = imagen[4:]
                        filtro = color[1]
                        print("HERE: ", imagen,filtro ,intensidad )
                        estado = fc.aplicarfiltro(imagen,filtro, intensidad,tamano,directorio,hilos)
                        
                        if estado == 0:
                            
                            #TODO: debe haber solo una pagina de exito en la raiz, no en cada uno de las rutas
                            fd2=fc.abrir_archivo(directorio+"exito.html")
                            body = os.read(fd2,tamano)                            
                            header =bytearray("HTTP/1.1 200 OK\r\n Content-Type:html \r\nContent-length:"+str(len(body))+" \r\n\r\n",'utf8')
                            
                        else:
                            #TODO: debe haber solo una pagina de error en la raiz, no en cada uno de las rutas
                            fd2=fc.abrir_archivo(directorio+"error.html")
                            body = os.read(fd2,tamano)
                            header =bytearray("HTTP/1.1 404 error\r\n Content-Type:html \r\nContent-length:"+str(len(body))+" \r\n\r\n",'utf8')
                        respuesta = header + body
                        self.request.sendall(respuesta)
                   
                elif (archivo == '/') or (archivo == '/index.html') :
                    
                    body = fc.index(directorio)
                    header =bytearray("HTTP/1.1 200 OK\r\n Content-Type: html \r\nContent-length:"+str(len(body))+" \r\n\r\n",'utf8')
                    print(body)
                    respuesta = header + body
                    self.request.sendall(respuesta)
                else: 
                    tomarextension = archivo.split('.')[1]
                    extension=fc.procesar_mimetype(tomarextension)
                    print(extension)
                    solicitud=directorio+archivo 
                    fd=fc.abrir_archivo(solicitud)
                    if os.path.isfile(fd) == False:
                        fd2=fc.abrir_archivo(directorio+"error.html")
                        body = os.read(fd2,tamano)
                        header =bytearray("HTTP/1.1 404 error\r\n Content-Type:"+extension+" \r\nContent-length:"+str(len(body))+" \r\n\r\n",'utf8')
                    if os.path.isfile(solicitud) == True:
                        body = os.read(fd,os.path.getsize(solicitud))
                        os.close(fd)
                        header =bytearray("HTTP/1.1 200 OK\r\n Content-Type:"+extension+" \r\nContent-length:"+str(len(body))+" \r\n\r\n",'utf8')
                    respuesta = header + body
                    self.request.sendall(respuesta)
            except(Exception):
                
                fd3=fc.abrir_archivo("error.html")
                body = os.read(fd3,tamano) 
                header =bytearray("HTTP/1.1 404 error\r\n Content-Type:html \r\nContent-length:"+str(len(body))+" \r\n\r\n",'utf8')
                respuesta = header + body
                self.request.sendall(respuesta)  

if __name__ == "__main__":
    HOST="0.0.0.0"
    parser = argparse.ArgumentParser(description='Arrays')
    parser.add_argument('-d', '--Documentroot Dir', action="store", dest="directorio", metavar="archivo origen", type=str, required=True, help="Archivo a procesar")
    parser.add_argument('-p', '--port', action="store", dest="puerto",type=int, help="Puerto")
    parser.add_argument('-s', '--size', action="store", dest="n_bytes", metavar="numero de bytes", type=int, required=True, help="Bloque de lectura") 
    parser.add_argument('-c', '--child', action="store", dest="hilos", metavar="numero de hilos", type=int, required=True, help="numero de hilos")       
    args = parser.parse_args()

    directorio= args.directorio
    puerto=args.puerto
    tamano=args.n_bytes
    hilos=args.hilos
    with servidor((HOST,5000),Handler,tamano,directorio,hilos)as server:
       server.serve_forever()
