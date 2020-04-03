# -*- coding: utf-8 -*-

#Created on Sat Mar 28 14:23:50 2020

#@author: ASUS

from pykinect import nui
import numpy as np
import face_recognition
import os
import cv2

class KinectDataHandler():
    def __init__(self):
        self.lastColorFrame = np.empty((480,640,4),np.uint8)
        self.lastDepthFrame = np.empty((240,320,4),np.uint8)
        self.positions = []
        self.Kinect = nui.Runtime()
        self.Kinect.depth_frame_ready += self.storeDepthFrame
        self.Kinect.video_frame_ready += self.storeColorFrame
        self.Kinect.depth_stream.open(nui.ImageStreamType.Depth, 2, nui.ImageResolution.Resolution320x240, nui.ImageType.Depth)
        self.Kinect.video_stream.open(nui.ImageStreamType.Video, 2, nui.ImageResolution.Resolution640x480, nui.ImageType.Color)
    def storeColorFrame(self,frame):
        frame.image.copy_bits(self.lastColorFrame.ctypes.data)
    def storeDepthFrame(self,frame):
        frame.image.copy_bits(self.lastDepthFrame.ctypes.data)
#        self.lastDepthFrame = (self.lastDepthFrame >> 3) & 4095
#        self.lastDepthFrame >>=4
        
    def stop(self):
        self.Kinect.close()

class FacialRecognition():
    def __init__(self,faces_to_allow_path):
        self.KinectData = KinectDataHandler()
        print("Connected to Kinect")
        self.encodings = []
        self.names = []
        for i in os.listdir(faces_to_allow_path):
            self.names.append(i)
            image_path = os.path.join(faces_to_allow_path,i)
            print("Allowing Face of "+i +" at " + image_path)
            self.encodings.append(face_recognition.face_encodings(face_recognition.load_image_file(image_path))[0])
        print("Finished Encoding Faces from images:" + str(self.names))
        
    def checkFrame(self):
        face_locations = face_recognition.face_locations(self.KinectData.lastColorFrame[:,:,[2,1,0]])
        last_frame_encoding = face_recognition.face_encodings(self.KinectData.lastColorFrame[:,:,[2,1,0]],face_locations)
        results = []
        for person in last_frame_encoding:
            results.append(face_recognition.compare_faces(self.encodings,person))
        return results,face_locations
    
    def stop(self):
        self.KH.stop()