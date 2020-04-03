# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 16:25:06 2020

@author: ASUS
"""

import socket
while True:
    sk = socket.socket()
    sk.connect(("localhost",25565))
    print(sk.recv(1024))
    sk.close()