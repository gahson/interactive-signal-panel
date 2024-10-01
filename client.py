from time import sleep
from random import randint
import socket
from socket import AF_INET, SOCK_DGRAM

server_socket = socket.socket(AF_INET, SOCK_DGRAM)
N = 12 # liczba wyswietlanych zmiennych

while True:
  x = bytearray([randint(0,1) for n in range(N)])
  print('==',x)
  server_socket.sendto(x, ("localhost", 9001))
  sleep(1)
