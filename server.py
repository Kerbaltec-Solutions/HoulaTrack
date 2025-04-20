import socket

# Define the UDP IP and port
UDP_IP = "0.0.0.0"  # Listen on all available interfaces
UDP_PORT = 5501

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening for UDP packets on port {UDP_PORT}...")

    # Define the client port to send data

# Create a new UDP socket for sending data
send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Send received data to the client
try:
    while True:
        data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
        print(f"Received message: {data.decode('utf-8')} from {addr}")
except KeyboardInterrupt:
    print("\nServer stopped.")
finally:
    send_sock.close()
    sock.close()