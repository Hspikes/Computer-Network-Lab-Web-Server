#import socket module
from socket import *
from urllib.parse import unquote
import signal
import sys 
import mimetypes
import os

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
server_address = ('0.0.0.0',8080)
serverSocket.bind(server_address)
serverSocket.listen(5)


def graceful_shutdown(signum, frame):
    print("Shutting down server...")
    serverSocket.close()
    sys.exit(0)

signal.signal(signal.SIGINT, graceful_shutdown)
signal.signal(signal.SIGCHLD, signal.SIG_IGN)

WEB_ROOT = os.path.abspath('./sourse')

def safe_path(request_path:str) -> str | None:
    request_path = unquote(request_path)
    rel_path = request_path.lstrip("/")
    normalized = os.path.normpath(rel_path)
    abs_path = os.path.abspath(os.path.join(WEB_ROOT, normalized))
    if os.path.commonpath([WEB_ROOT, abs_path]) == WEB_ROOT:
        return abs_path
    else:
        return None

def handle_client(connectionSocket):

    try:
        message = connectionSocket.recv(2048).decode()
        print("Request message:", message)
        if (len(message) < 2):
            header = "HTTP/1.1 400 Bad Request\r\n\r\n"
            connectionSocket.send(header.encode())
            connectionSocket.close()
            return
        
        filename = message.split()[1]

        filepath = safe_path(filename)
        if filepath is None:
            header = "HTTP/1.1 403 Forbidden\r\n\r\n"
            connectionSocket.send(header.encode())
            connectionSocket.close()
            return
    
        content_type, _ = mimetypes.guess_type(filepath)
        if content_type is None:
            content_type = 'application/octet-stream'
        
        with open(filepath, 'rb') as f:
            outputdata = f.read()

        header = "HTTP/1.1 200 OK\r\n"
        header += f"Content-Type: {content_type}\r\n"
        header += f"Content-Length: {len(outputdata)}\r\n"
        header += "\r\n"
        connectionSocket.send(header.encode())

        connectionSocket.send(outputdata)
        connectionSocket.close()

    except IOError:
        header = "HTTP/1.1 404 Not Found\r\n"
        header += "Content-Type: text/html\r\n"
        header += "\r\n"
        connectionSocket.send(header.encode())
        connectionSocket.close()

    except(ConnectionResetError, BrokenPipeError):
        print("Connection with client was reset or closed.")
        connectionSocket.close()

    finally:
        connectionSocket.close()

try:
    while True:
        print('Ready to serve...')
        connectionSocket, addr = serverSocket.accept()
        pid = os.fork()
        if pid == 0:
            handle_client(connectionSocket)
            os._exit(0)
        else: 
            connectionSocket.close()

except Exception as e:
    print("Unexpected error:", e)
    serverSocket.close()
    sys.exit(1)