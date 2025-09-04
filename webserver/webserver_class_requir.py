#import socket module
from socket import *
import signal
import sys # In order to terminate the program
serverSocket = socket(AF_INET, SOCK_STREAM)
#Prepare a sever socket
#Fill in start
server_address = ('0.0.0.0',8080)
serverSocket.bind(server_address)
serverSocket.listen(5)
#Fill in end

def graceful_shutdown(signum, frame):
    print("Shutting down server...")
    serverSocket.close()
    sys.exit(0)

signal.signal(signal.SIGINT, graceful_shutdown)

while True:
    #Establish the connection
    print('Ready to serve...')
    connectionSocket, addr = serverSocket.accept()
    try:
        message = connectionSocket.recv(2048).decode()
        print("Request message:", message)
        filename = message.split()[1]
        f = open(filename[1:])
        outputdata = f.read()
        #Send one HTTP header line into socket
        #Fill in start
        header = "HTTP/1.1 200 OK\r\n"
        header += "Content-Type: text/html\r\n"
        header += "\r\n"
        connectionSocket.send(header.encode())
        #Fill in end
        #Send the content of the requested file to the client
        for i in range(0, len(outputdata)):
            connectionSocket.send(outputdata[i].encode())
        connectionSocket.send("\r\n".encode())
        connectionSocket.close()
    except IOError:
        #Send response message for file not found
        #Fill in start
        header = "HTTP/1.1 404 Not Found\r\n"
        header += "Content-Type: text/html\r\n"
        header += "\r\n"
        connectionSocket.send(header.encode())
        #Fill in end
        #Close client socket
        #Fill in start
        connectionSocket.close()
        #Fill in end
    except(ConnectionResetError, BrokenPipeError):
        print("Connection with client was reset or closed.")
        connectionSocket.close()