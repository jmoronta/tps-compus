import os
import sys
import argparse
from urllib.parse import urlparse
import multiprocessing
import funciones as fc
import socketserver
import asyncio
import time
import datetime

async def log_handle(addr,path):
    nombre=path+"login"
    date = time.strftime("%c")
    login= "Se conecto desde la IP y puerto:" +str(addr) + " la fecha y hora: " +str(date)
    print(login)
    fd=fc.abrir_archivo(nombre)
    if os.path.isfile(fd) == True:
        fd2=open(nombre, 'a')
        fd2.write(login)
    else:
        fp = open(nombre, 'w+')
        fp.write(login)
    os.close(fd)
    
async def handle_echo(reader, writer):
    global path
    global size

    data = await reader.read(size)
    message = data.decode()#consulta GET
    addr = writer.get_extra_info('peername')
    await log_handle(addr,path)
    solicitud=urlparse(message)

    pedido=solicitud.path.split()[1]
    if (pedido == '/') or (pedido == '/index.html') :
                body = fc.Index(path)
                extension='html'
                header =bytearray("HTTP/1.1 200 OK\r\n Content-Type:"+extension+" \r\nContent-length:"+str(len(body))+" \r\n\r\n",'utf8')
                #print(body)
                #respuesta = header + body
                #self.request.sendall(respuesta)
    else:
        tomarextension = pedido.split('.')[1]
        extension=fc.procesar_mimetype(tomarextension)
        print(extension)
        solicitud=path+pedido
        fd=fc.abrir_archivo(solicitud)
        if os.path.isfile(fd) == False:
                    fd2=fc.abrir_archivo(directorio+"error.html")
                    body = os.read(fd2,size)
                    #body   = "<html><head><meta<title>Mi pagina de prueba</title></head><body><p>Hola Mundo todo bien</p></body></html>"
                    header =bytearray("HTTP/1.1 404 error\r\n Content-Type:"+extension+" \r\nContent-length:"+str(len(body))+" \r\n\r\n",'utf8')
        if os.path.isfile(solicitud) == True:
                    body = os.read(fd,os.path.getsize(solicitud))
                    os.close(fd)
                    header =bytearray("HTTP/1.1 200 OK\r\n Content-Type:"+extension+" \r\nContent-length:"+str(len(body))+" \r\n\r\n",'utf8')
    respuesta = header + body
    #self.request.sendall(respuesta)
   # addr = writer.get_extra_info('peername')

   # print("Received %r from %r" % (message, addr))
   # print("Send: %r" % message)
    writer.write(respuesta)
    await writer.drain()

    #print("Close the client socket")
    #writer.close()

if __name__ == "__main__":
    HOST="0.0.0.0"
    parser = argparse.ArgumentParser(description='Arrays')
    parser.add_argument('-d', '--Documentroot Dir', action="store", dest="directorio", metavar="archivo origen", type=str, required=True, help="Archivo a procesar")
    parser.add_argument('-p', '--port', action="store", dest="puerto",type=int, help="Puerto")
    parser.add_argument('-s', '--size', action="store", dest="n_bytes", metavar="numero de bytes", type=int, required=True, help="Bloque de lectura")       
    args = parser.parse_args()

    path= args.directorio
    puerto=args.puerto
    size=args.n_bytes
    
loop = asyncio.get_event_loop()
coro = asyncio.start_server(handle_echo, HOST, puerto, loop=loop)
server = loop.run_until_complete(coro)


# Serve requests until Ctrl+C is pressed
print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()
