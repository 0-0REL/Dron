import socket
import json

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('192.168.68.96', 5000))

while True:
    data = client.recv(1024).decode()
    if data:
        json_data = json.loads(data.strip())
        print("Datos recibidos:", json_data)