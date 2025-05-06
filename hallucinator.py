import socket
import time
import threading

# Define the UDP IP and port
UDP_IP_in = "0.0.0.0"  # Listen on all available interfaces
UDP_IP_out = "127.0.01"
UDP_PORT_in = 5501
UDP_PORT_out = 5502

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP_in, UDP_PORT_in))

print(f"Listening for UDP packets on port {UDP_PORT_in}...")

    # Define the client port to send data

# Create a new UDP socket for sending data
send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def get_fps(avg_int):
    t=[0,0]
    fps=[]
    while len(fps)<avg_int+2:
        data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
        t.pop(0)
        t.append(time.clock_gettime_ns(time.CLOCK_REALTIME))
        #print(f"Received message: {data.decode('utf-8')} from {addr}")
        fps.append(1000000000/(t[-1]-t[-2]))
    avg_fps = sum(fps[:-2]) / avg_int
    print(f"Average FPS: {avg_fps}")
    return avg_fps

#get_fps(100)

# Global array to store received packets
rx_pack = []

def udp_listener():
    global rx_pack
    ts=time.clock_gettime_ns(time.CLOCK_REALTIME)
    while True:
        try:
            data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
            rx_pack.append((data, addr, (time.clock_gettime_ns(time.CLOCK_REALTIME)-ts)/1000000))
        except socket.error:
            print("ERR")
            break

# Start the UDP listener in a separate thread
listener_thread = threading.Thread(target=udp_listener, daemon=True)
listener_thread.start()

sample_len = 100
samples = []
times = []

emptys = 0
try:
    while True:
        if len(rx_pack)>1:
            print(emptys)
            emptys = 0
            data,addr,t = rx_pack.pop(0)
            samples.append(list(map(float, data.decode('utf-8').strip().replace("[","").replace("]","").split(","))))
            times.append(t)
            #print(f"Received message: {data.decode('utf-8')} from {addr}")
        if len(times)>sample_len:
            times.pop(0)
            samples.pop(0)
            message = rx_pack[-1][0].decode('utf-8')
            sock.sendto(message.encode(), (UDP_IP_out, UDP_PORT_out))
            emptys += 1
except KeyboardInterrupt:
    print("\nServer stopped.")
finally:
    send_sock.close()
    sock.close()