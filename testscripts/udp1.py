import socket

tello = ("192.168.10.1", 8889)

# create our udp socket
try:
    socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print("Oops, something went wrong connecting the socket")
    exit()

while 1:
    message = raw_input("> ")
    

    # encode the message
    message = message.encode()
    
    try:
        # send the message
        socket.sendto(message, tello)
        

        # output the response (if any)
        data, ip = socket.recvfrom(1024)
        
        print("{}: {}".format(ip, data.decode()))
        

    except socket.error:
        print("Error! {}".format(socket.error))
        exit()
