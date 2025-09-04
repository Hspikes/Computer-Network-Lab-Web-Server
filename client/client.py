from socket import *
import sys

if len(sys.argv) < 2:
    print(f"Usage: python3 {sys.argv[0]} <filename>")
    sys.exit(1)

filename = sys.argv[1]

clientSocket = socket(AF_INET,SOCK_STREAM)
clientSocket.connect(('localhost',8080))

message = f'GET /{filename} HTTP/1.1\r\nHost: localhost\r\n\r\n'
clientSocket.send(message.encode())

response = b""
while True:
    part = clientSocket.recv(4096)
    if not part:
        break
    response += part
clientSocket.close()

separator = b'\r\n\r\n'
header_end = response.find(separator)
if header_end == -1:
    print("Invalid HTTP response")
    sys.exit(1)

header_bytes = response[:header_end].decode(errors='replace')
body = response[header_end + 4:]

print("===HTTP Header===")
print(header_bytes)

content_type = "application/octet-stream"
for line in header_bytes.split("\r\n"):
    if line.lower().startswith("content-type:"):
        content_type = line.split(":", 1)[1].strip()
        break

status_line = header_bytes.split("\r\n")[0]
if not status_line.startswith("HTTP/1.1 200"):
    print("Request failed:", status_line)
    sys.exit(1)

with open(filename, "wb") as f:
    f.write(body)

print(f"Body saved to {filename}")
