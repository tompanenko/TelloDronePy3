# A template that shpuld setup all that is needed to control a drone swarm

# Import the necessary modules
import socket
import threading
import time

# Enter the number of tellos to be controled
tello_number = 2 ## Change to the number you plan on using

# IP and port of Tello
tello_address = []
for i in range(tello_number):
  tello_address.append((raw_input("Tello " + str(i+1) + " IP address: "), 8889))

# IP and port of local computer
local_address = []
for i in range(tello_number):
  local_address.append(('', 9020+i))

# Create a UDP connection that we'll send the command to
sock = []
for i in range(tello_number):
  sock.append(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))

# Bind to the local address and port
for i in range(tello_number):
  sock[i].bind(local_address[i])

################################# SEND #################################

# Send the same message to all tellos and allow for a delay in seconds
def sendAll(message, delay):
  # Try to send the message otherwise print the exception
  try:
    for i in range(tello_number):
      sock[i].sendto(message.encode(), tello_address[i])
      print("Sending message: " + message + " to tello " + str(i+1))
  except Exception as e:
    print("Error sending: " + str(e))

  # Delay for a user-defined period of time
  time.sleep(delay)

# Send the message to one tello 
def sendToOne(tello, message):
  # Try to send the message otherwise print the exception
  try:
    sock[tello - 1].sendto(message.encode(), tello_address[tello - 1])
    print("Sending message: " + message + " to tello " + str(tello))
  except Exception as e:
    print("Error sending: " + str(e))

# Send the message to a group of tellos 
def sendToGroup(tellos, message):
  # Try to send the message otherwise print the exception
  try:
    for i in range(len(tellos)):
      sock[tellos[i] - 1].sendto(message.encode(), tello_address[tellos[i] - 1])
      print("Sending message: " + message + " to tello " + str(tellos[i]))
  except Exception as e:
    print("Error sending: " + str(e))

# Send the message to one tello and allow for a delay in seconds
def sendToOneDelay(tello, message, delay):
  # Try to send the message otherwise print the exception
  try:
    sock[tello - 1].sendto(message.encode(), tello_address[tello - 1])
    print("Sending message: " + message + " to tello " + str(tello))
  except Exception as e:
    print("Error sending: " + str(e))

  # Delay for a user-defined period of time
  time.sleep(delay)

# Send the message to a group of tellos and allow for a delay in seconds
def sendToGroupDelay(tellos, message, delay):
  # Try to send the message otherwise print the exception
  try:
    for i in range(len(tellos)):
      sock[tellos[i] - 1].sendto(message.encode(), tello_address[tellos[i] - 1])
      print("Sending message: " + message + " to tello " + str(tellos[i]))
  except Exception as e:
    print("Error sending: " + str(e))

  # Delay for a user-defined period of time
  time.sleep(delay)

################################ RECEIVE ################################

# Receive the message from Tello
def receive():
  # Continuously loop and listen for incoming messages
  while True:
    # Try to receive the message otherwise print the exception
    try:
      #print ''
      for i in range(tello_number):
        response, ip_address = sock[i].recvfrom(128)
        print("Received message: from tello " + str(i + 1) + " : " + response.decode(encoding='utf-8'))
    except Exception as e:
      # If there's an error close the socket and break out of the loop
      for i in range(tello_number):
        sock[i].close()
      print("Error receiving: " + str(e))
      break

# Create and start a listening thread that runs in the background
# This utilizes our receive functions and will continuously monitor for incoming messages
receiveThread = threading.Thread(target=receive)
receiveThread.daemon = True
receiveThread.start()

# Put Tello into command mode
sendAll("command", 2)

# Send the takeoff command
#sendAll("takeoff", 5)

sendToOne(1, "battery?")
time.sleep(2)
sendToOne(2, "battery?")
time.sleep(2)

# Land
#sendAll("land", 5)

# Print message
print("Mission completed successfully!")

# Close the sockets
for i in range(tello_number):
  sock[i].close()
