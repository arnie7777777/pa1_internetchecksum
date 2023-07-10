import socket
import sys
import struct

def internet_checksum(data):
    n = len(data)
    if n % 2:
        data += b'\0'
        n += 1
    w = [0] * (n // 2)
    for i in range(0, n, 2):
        w[i // 2] = (data[i] << 8) + data[i + 1]
    s = sum(w)
    s = (s >> 16) + (s & 0xffff)
    s += s >> 16
    s = ~s & 0xffff
    return struct.pack('>H', s)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = socket.gethostname()

port = int(sys.argv[1])

server_socket.bind((host, port))

server_socket.listen(1)

print('Server listening on {}:{}'.format(host, port))
client_socket, addr = server_socket.accept()
print('Connected by', addr)

while True:
    data = client_socket.recv(512)
    if not data:
        break
    # Computing the checksum of the newly received message
    received_checksum = data[:2]
    message = data[2:]
    computed_checksum = internet_checksum(b'\0\0' + message)

    # Checking to see if the checksum is correct
    if received_checksum == computed_checksum:
        modified_data = message.decode('utf-8', errors='replace').swapcase()
        response_checksum = internet_checksum(b'\0\0' + modified_data.encode())
        client_socket.send(response_checksum + modified_data.encode())
    else:
        client_socket.send(b'\0\0ERROR')

client_socket.close()

