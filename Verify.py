# -*- coding: utf-8 -*-
"""
Created on Sat Mar 28 14:27:14 2020

@author: ASUS
"""

from ImageProcessing import KinectDataHandler,FacialRecognition
import numpy as np
import face_recognition
import os
import threading
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
import cv2
from kivy.graphics.texture import Texture
from threading import Thread
import png
import PIL
import socketserver

IP, PORT = ("localhost", 25565)




FR = FacialRecognition("Faces")
state = True
class HomePage(GridLayout):
    def __init__(self,**kwargs):
        super(HomePage,self).__init__(**kwargs)
        self.writer = png.Writer(width=640,height=480)
        self.cols = 1
        self.locked = True
        self.predictor_process = False
        self.img1 = Image()
        self.status = Image(source = 'lock.png')
        self.add_widget(self.img1)
        
        self.inlayout = GridLayout(cols=2)
        
#        self.add_widget(Label(text="Image Output",font_size="30sp"))
        self.btn1 = Button(text="Start Facial Recognition",font_size="30sp")
        self.btn1.bind(on_press=self.Start)
        self.btn2 = Button(text="Add face in frame",font_size="30sp")
        self.btn2.bind(on_press=self.capture)
        self.inlayout.add_widget(Label(text="Current Status:",font_size="30sp"))
        self.inlayout.add_widget(self.status)
        self.inlayout.add_widget(self.btn1)
        self.inlayout.add_widget(self.btn2)
        self.add_widget(self.inlayout)
        Clock.schedule_interval(self.update,0)
        Clock.schedule_interval(self.Unlock,0)
        #self.runloop = threading.Thread(target=self.CheckForFaces,args=())
        #self.runloop.daemon = False
        #self.runloop.start()
    def capture(self,event):
        image = PIL.Image.fromarray(FR.KinectData.lastColorFrame[:,:,[2,1,0]])
        image.save("Faces/"+str(np.random.randint(0,100000))+".png")
    def update(self,dt):
        global state
        state = self.locked
        frame = FR.KinectData.lastColorFrame[:,:,0:3]
        # convert it to texture
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr') 
        #if working on RASPBERRY PI, use colorfmt='rgba' here instead, but stick with "bgr" in blit_buffer. 
        texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        # display image from the texture
        self.img1.texture = texture1
    def Unlock(self,event):
        if not(self.locked):
            Clock.schedule_once(self.Lock,4)
            global state
            state = False
            self.status.source = 'unlock.png'

    def Lock(self,event):
        global state
        self.locked = True
        state = True
        self.status.source = 'lock.png'
        print("Locked Again For Security")
    def CheckForFaces(self):
        while True:
            try:
                k = FR.checkFrame()
                if True in k[0][0]:
                    print(k)
                    self.locked = False
                else:
                    print("Face detected : Not Unlocking")
            except:
                pass
    def Start(self,event):
        if self.predictor_process == False:
            self.predictor_process = Thread(target=self.CheckForFaces).start()
class KinectDetectorApp(App):
    def build(self):
        return HomePage()

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.request.sendall(bytes(str(state),'ascii'))

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

print("Server running at:"+str(IP)+","+str(PORT))
server = ThreadedTCPServer((IP, PORT), ThreadedTCPRequestHandler)
server_thread = threading.Thread(target=server.serve_forever)
server_thread.daemon = True
server_thread.start()

Mapp = KinectDetectorApp().run()
    
