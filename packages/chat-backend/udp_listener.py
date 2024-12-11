import socket

UDP_IP = "0.0.0.0"
UDP_PORT = 12201

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening on {UDP_IP}:{UDP_PORT}")

while True:
    data, addr = sock.recvfrom(4096)  # buffer size is 4096 bytes
    print(f"Received message from {addr}: {data.decode('utf-8')}")
