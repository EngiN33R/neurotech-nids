import sys
import socket
import struct

print("Creating socket...")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(("127.0.0.1", 1111))

data = [0.0, 0, 0, 0, 0, 0, 0, 0, 0]

for i in range(1, len(sys.argv)-1):
    if i == 1:
        data[i-1] = float(sys.argv[i]) if i == 1 else int(sys.argv[i])

print("Sending datagram: " + str(data))
sock.send(struct.pack("=dHHHHHHHH", *data))

print("Closing socket...")
sock.close()
