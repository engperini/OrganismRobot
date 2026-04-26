

#robozim antigo

import random
import multiprocessing
import os
import argparse

from PIL import Image
import cv2
import numpy as np

import sys
import time
import threading
from threading import Thread

import importlib.util

import gpiozero
from gpiozero import Servo
from time import sleep
from gpiozero.pins.pigpio import PiGPIOFactory

import pygame #to robot face pygame
from itertools import cycle #to robot face pygame
from sound import sound #to robot face pygame


factory = PiGPIOFactory()
servo = Servo(12, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory,initial_value=None)
servoy = Servo(13, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory, initial_value=None)

actualx=-0.2 #posicoes de inicio do robo
actualy=0.3 

servo.value= actualx #iniciando servos
servoy.value=actualy

servo.detach() #colocando servos em stand-by
servoy.detach()

auxx=actualx #armazenamento da posicao inicial dos servos
auxy=actualy


ctr=1
ctrexplor=0


def mover(ctr, ctrexplor, x,y):
        global factory, servo, servoy, actualx, actualy, auxx, auxy #incluido 24/01/22 
                
        if (0.9>x and x>-0.9) and (0.9>y and y>-0.9):
        
            servo.value=auxx
            servoy.value=auxy
            
            actualx=servo.value
            actualy=servoy.value
            
            def seq(start, stop, step=1):
                n = int(round((stop - start)/float(step)))
                if n > 1:
                    return([start + step*i for i in range(n+1)])
                elif n == 1:
                    return([start])
                else:
                    return([])

            if actualx < x:
                i=seq(actualx,x,0.01) #0.1 was
            else:
                i=seq(actualx,x,-0.01)
                
            if actualy < y:
                j=seq(actualy,y,0.01)
            else:
                j=seq(actualy,y,-0.01)   
                
            try:
                for x1 in i:
                    sleep(0.1)
                    servo.value = round(x1,2)
                    #servo.detach()
                    if ctr==0 or ctrexplor==0:
                        servo.detach()
                        break
                        
        
                    
                for y1 in j:
                    sleep(0.1)
                    servoy.value = round(y1,2)
                    #servy.detach()
                    if ctr==0 or ctrexplor==0:
                        servo.detach() 
                        break
                        
                auxx=servo.value
                auxy=servoy.value
                
                servo.detach()
                servoy.detach()
                return servo.value,servoy.value
              
            except KeyboardInterrupt:
                print("Ending program Mover")
                servo.close()
                servoy.close()
                servo.detach()
                servoy.detach()

        else:
            print("out of range")
            servo.close()
            servoy.close()
            return (servo.value,servoy.value)

imW = 320
imH = 240

def robot_video(ctr, ctrobjeto):
    
    global servo, servoy, actualx, actualy, auxx, auxy,express, imW, imH
    express=2
    
    #moveresq = actualx
    #movery = actualy
    
    moveresq = auxx
    movery = auxy
    
    class VideoStream:
        #Camera object that controls video streaming from the Picamera
        def __init__(self,resolution=(640,480),framerate=30):
            # Initialize the PiCamera and the camera image stream
            self.stream = cv2.VideoCapture(0)
            ret = self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
            ret = self.stream.set(3,resolution[0])
            ret = self.stream.set(4,resolution[1])
                
            # Read first frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

        # Variable to control when the camera is stopped
            self.stopped = False

        def start(self):
        # Start the thread that reads frames from the video stream
            Thread(target=self.update,args=()).start()
            return self

        def update(self):
            # Keep looping indefinitely until the thread is stopped
            while True:
                # If the camera is stopped, stop the thread
                if self.stopped:
                    # Close camera resources
                    self.stream.release()
                    return

                # Otherwise, grab the next frame from the stream
                (self.grabbed, self.frame) = self.stream.read()

        def read(self):
        # Return the most recent frame
            return self.frame

        def stop(self):
        # Indicate that the camera and thread should be stopped
            self.stopped = True

    MODEL_NAME = 'Sample_TFLite_model'
    GRAPH_NAME = 'detect.tflite'
    LABELMAP_NAME = 'labelmap.txt'
    min_conf_threshold = 0.7 #confiaca
    #resW, resH = "720","480"
    imW, imH = int(imW), int(imH)
    use_TPU = True

    # Import TensorFlow libraries
    # If tflite_runtime is installed, import interpreter from tflite_runtime, else import from regular tensorflow
    # If using Coral Edge TPU, import the load_delegate library
    pkg = importlib.util.find_spec('tflite_runtime')
    if pkg:
        from tflite_runtime.interpreter import Interpreter
        if use_TPU:
            from tflite_runtime.interpreter import load_delegate
    else:
        from tensorflow.lite.python.interpreter import Interpreter
        if use_TPU:
            from tensorflow.lite.python.interpreter import load_delegate

    # If using Edge TPU, assign filename for Edge TPU model
    if use_TPU:
        # If user has specified the name of the .tflite file, use that name, otherwise use default 'edgetpu.tflite'
        if (GRAPH_NAME == 'detect.tflite'):
            GRAPH_NAME = 'edgetpu.tflite'       

    # Get path to current working directory
    CWD_PATH = os.getcwd()

    # Path to .tflite file, which contains the model that is used for object detection
    PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,GRAPH_NAME)

    # Path to label map file
    PATH_TO_LABELS = os.path.join(CWD_PATH,MODEL_NAME,LABELMAP_NAME)

    # Load the label map
    with open(PATH_TO_LABELS, 'r') as f:
        labels = [line.strip() for line in f.readlines()]

    # Have to do a weird fix for label map if using the COCO "starter model" from
    # https://www.tensorflow.org/lite/models/object_detection/overview
    # First label is '???', which has to be removed.
    if labels[0] == '???':
        del(labels[0])

    # Load the Tensorflow Lite model.
    # If using Edge TPU, use special load_delegate argument
    if use_TPU:
        interpreter = Interpreter(model_path=PATH_TO_CKPT,
                                  experimental_delegates=[load_delegate('libedgetpu.so.1.0')])
        #print(PATH_TO_CKPT)
    else:
        interpreter = Interpreter(model_path=PATH_TO_CKPT)

    interpreter.allocate_tensors()

    # Get model details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    height = input_details[0]['shape'][1]
    width = input_details[0]['shape'][2]

    floating_model = (input_details[0]['dtype'] == np.float32)

    input_mean = 127.5
    input_std = 127.5

    #servo pan tilt object tracking
    
    #moveresq = 0
    #movery = 0.5
    #servo.value = moveresq
    #servoy.value = movery

    # Initialize frame rate calculation
    frame_rate_calc = 1
    freq = cv2.getTickFrequency()

    # Initialize video stream
    videostream = VideoStream(resolution=(imW,imH),framerate=30).start()
    time.sleep(1)

    # Create window
    #cv2.namedWindow('Object detector', cv2.WINDOW_AUTOSIZE)
    
    start=time.time()
    timer=random.randint(5,30)      
    detected=""
    done=False
    #for frame1 in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):
    while not done:#falta colocar parada ctr1
        #dist=distancia()
        actual=time.time()     
        elapsed=actual-start
        if (ctr==0) or(ctrobjeto==0)or(elapsed>timer):
            #done=True
            break #para pelo tempo
            
        
        # Start timer (for calculating frame rate)
        t1 = cv2.getTickCount()

        # Grab frame from video stream
        frame1 = videostream.read()

        # Acquire frame and resize to expected shape [1xHxWx3]
        frame = frame1.copy()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (width, height))
        input_data = np.expand_dims(frame_resized, axis=0)

        # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
        if floating_model:
            input_data = (np.float32(input_data) - input_mean) / input_std

        # Perform the actual detection by running the model with the image as input
        interpreter.set_tensor(input_details[0]['index'],input_data)
        interpreter.invoke()

        # Retrieve detection results
        boxes = interpreter.get_tensor(output_details[0]['index'])[0] # Bounding box coordinates of detected objects
        classes = interpreter.get_tensor(output_details[1]['index'])[0] # Class index of detected objects
        scores = interpreter.get_tensor(output_details[2]['index'])[0] # Confidence of detected objects
        #num = interpreter.get_tensor(output_details[3]['index'])[0]  # Total number of detected objects (inaccurate and not needed)
        
        #Rotina para object tracking
        #Desenha quadrado no meio da tela
        xmeio = int(round((imW / 2)))
        ymeio = int(round((imH / 2)))
        retang =int(round((imW*0.15))) 
        #cv2.rectangle(frame, (xmeio-retang,ymeio-retang), (xmeio+retang,ymeio+retang),(0,0,255))
          
        
            
        
        # Loop over all detections and draw detection box if confidence is above minimum threshold
        #classes[i]==0 reconhecendo apenas pessoas ==person
        for i in range(len(scores)):
            if ((scores[i] > min_conf_threshold) and (scores[i] <= 1.0) ):
                 
                
                
                    
                # Get bounding box coordinates and draw box
                # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
                ymin = int(max(1,(boxes[i][0] * imH)))
                xmin = int(max(1,(boxes[i][1] * imW)))
                ymax = int(min(imH,(boxes[i][2] * imH)))
                xmax = int(min(imW,(boxes[i][3] * imW)))
                
                cv2.rectangle(frame, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)
             
               
                
                # Draw label
                object_name = labels[int(classes[i])] # Look up object name from "labels" array using class index
                label = '%s: %d %d%%' % (object_name,i, int(scores[i]*100)) # Example: 'person: 72%'
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
                label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
                cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
                cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text

                # Draw circle in center
                xcenter = xmin + (int(round((xmax - xmin) / 2)))
                ycenter = ymin + (int(round((ymax - ymin) / 2)))
                cv2.circle(frame, (xcenter, ycenter), 5, (0,0,255), thickness=-1)
               
                # Print info circle
                #print('Object ' + str(i) + ': ' + object_name + ' at (' + str(xcenter) + ', ' + str(ycenter) + ')')

                detected=object_name
                #para se encontrar pessoa
                #if (detected == "person"):# and elapsed>timer/4):                        
                 #   #ctrexplor=0
                #  done=True
                 #   break
                
                #object tracking eixo horizontal
                
                #print(moveresq, movery)
                if (classes[i] == 10): #rastrear pessoas #era 0 mudei class 10
                    ctrexplor=0
                    sleep(1)
                    if (xcenter < (xmeio-retang)): 
                        moveresq = moveresq + 0.02
                        servo.value = moveresq
                       
                    if (xcenter > (xmeio+retang)):
                        moveresq = moveresq - 0.02
                        servo.value = moveresq 

                    if (moveresq < -0.9):moveresq = -0.9
                    if (moveresq > +0.9):moveresq = +0.9
                    
        #inicia codigo y
                        
                    if (ycenter < (ymeio-retang)): 
                        movery = movery - 0.02
                        servoy.value = movery  

                    if (ycenter > (ymeio+retang)):            
                        movery = movery + 0.02
                        servoy.value = movery
                        
                    if (movery < -0.9):movery = -0.9
                    if (movery > +0.9):movery = +0.9
                    
                    detected=object_name
                    
                    if (elapsed>timer):
                        done=True
                        break
        #break
        
        # Draw framerate in corner of frame
        cv2.putText(frame,'FPS: {0:.2f}'.format(frame_rate_calc),(30,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2,cv2.LINE_AA)
        cv2.putText(frame,'Analisando ',(30,20),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2,cv2.LINE_AA)
        #cv2.putText(frame,'Distancia: {0:.2f}'.format(dist)+'m',(xmeio,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2,cv2.LINE_AA)
        # All the results have been drawn on the frame, so it's time to display it.
        cv2.imshow('Object detector', frame)
        
      
        # Calculate framerate
        t2 = cv2.getTickCount()
        time1 = (t2-t1)/freq
        frame_rate_calc= 1/time1
        #dist=distancia() 
        #fecha=acordar()
        # Press 'q' to quit
        if cv2.waitKey(1) == ord('q'):
            break
        if ctr==0 or ctrobjeto==0:
            break
        
    cv2.destroyAllWindows()
    videostream.stop()
    return detected, ctr

def detect_face(ctr, ctrface):

    global factory, servo, servoy, actualx, actualy, auxx, auxy,express,imW,imH #inclui em 24/01

    #servo = Servo(12, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory,initial_value=None)
    #servoy = Servo(13, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory, initial_value=None)
    
    #servo.value= actualx #iniciando servos
    #servoy.value=actualy
    
    
    express=2
    
    #moveresq = servo.value
    #movery = servoy.value
    
    moveresq = auxx
    movery = auxy
    
    
    
    #servo.value = moveresq
    #servoy.value = movery
    

    
    class VideoStream:
       #Camera object that controls video streaming from the Picamera
        def __init__(self,resolution=(640,480),framerate=30):
            # Initialize the PiCamera and the camera image stream
            self.stream = cv2.VideoCapture(0)
            ret = self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
            ret = self.stream.set(3,resolution[0])
            ret = self.stream.set(4,resolution[1])
                
            # Read first frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

        # Variable to control when the camera is stopped
            self.stopped = False

        def start(self):
        # Start the thread that reads frames from the video stream
            Thread(target=self.update,args=()).start()
            return self

        def update(self):
            # Keep looping indefinitely until the thread is stopped
            while True:
                # If the camera is stopped, stop the thread
                if self.stopped:
                    # Close camera resources
                    self.stream.release()
                    return

                # Otherwise, grab the next frame from the stream
                (self.grabbed, self.frame) = self.stream.read()

        def read(self):
        # Return the most recent frame
            return self.frame

        def stop(self):
        # Indicate that the camera and thread should be stopped
            self.stopped = True

    
    def draw_boundary(img, classifier, scaleFactor, minNeighbors, color, text, clf):
        global ctr
        
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        features = classifier.detectMultiScale(gray_img, scaleFactor, minNeighbors)
        name=""
        coords = []
        id=0
        for (x,y,w,h) in features:
            cv2.rectangle(img, (x,y), (x+w,y+h), color, 2 )
            
            id, pred = clf.predict(gray_img[y:y+h,x:x+w])
            confidence = int(100*(1-pred/300))
            
            if confidence>74:
                if id==1:
                    name="arthur"
                    cv2.putText(img, name, (x,y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 1, cv2.LINE_AA)
                if id==2:
                    name="cida"
                    cv2.putText(img, name, (x,y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 1, cv2.LINE_AA)
                
            else:
                cv2.putText(img, "UNKNOWN", (x,y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 1, cv2.LINE_AA)
                id=0
                name="desconhecido"    
            coords=[x,y,w,h]
            
        #print(id,name)    
        return coords,id,name
        

    def recognize(img,clf,faceCascade):
        coords,id,name = draw_boundary(img,faceCascade,1.1,10,(255,255,255),"Face",clf)
        
        return img,coords,id,name

    # loading classifier
    #faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    #faceCascade = cv2.CascadeClassifier("/home/pi/tflite1/tflite1-env/lib/python3.7/site-packages/cv2/data/haarcascade_frontalface_default.xml")
    clf = cv2.face.LBPHFaceRecognizer_create()
    #clf = cv2.face.createLBPHFaceRecognizer()
    clf.read("/home/pi/GassistPi/classifier.xml")
    
    imW=imW
    imH=imH
    
    #video_capture = cv2.VideoCapture(0)
    video_capture = VideoStream(resolution=(imW,imH),framerate=30).start()
    #sleep(1)
    
    start=time.time()
    timer=random.randint(5,15)
    #timer=10
    while True:
        #print("detectando face")
        actual=time.time()     
        elapsed=actual-start
        if ctr==0 or ctrface==0 or elapsed>timer:
            print("terminando detectar face")
            break
        
        
        #ret, img = video_capture.read()
        img = video_capture.read()
        img,coords,id,name=  recognize(img,clf,faceCascade) 
        cv2.putText(img,'Detectando Face',(30,20),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2,cv2.LINE_AA)
        cv2.imshow("face Detection", img) #mostra face detection
        
        if coords:
            [x,y,w,h]=coords
             
            
            #Desenha quadrado no meio da tela
            xmeio = int(round((imW / 2)))
            ymeio = int(round((imH / 2)))
            retang =int(round((imW*0.12))) 
            #cv2.rectangle(img, (xmeio-retang,ymeio-retang), (xmeio+retang,ymeio+retang),color,2)
            
        # Draw circle in center
            xcenter = (x+w) - (int(round((w) / 2)))
            ycenter = (y+h) - (int(round((h) / 2)))
            #cv2.circle(img, (xcenter, ycenter), 5, (0,0,255), thickness=-1)
               
            # Print info circle
            #print('Object ' + str(i) + ': ' + object_name + ' at (' + str(xcenter) + ', ' + str(ycenter) + ')')
            
            if (xcenter < (xmeio-retang)):
                moveresq = moveresq + 0.02
                servo.value = moveresq
               
            if (xcenter > (xmeio+retang)):
                moveresq = moveresq - 0.02
                servo.value = moveresq 

            if (moveresq < -0.9):moveresq = -0.9
            if (moveresq > +0.9):moveresq = +0.9
            
        #inicia codigo y
                
            if (ycenter < (ymeio-retang)):
                movery = movery - 0.02
                servoy.value = movery  

            if (ycenter > (ymeio+retang)):
                movery = movery + 0.02
                servoy.value = movery
                
            if (movery < -0.9):movery = -0.9
            if (movery > +0.9):movery = +0.9
            
            
        if cv2.waitKey(1)==27:
            break
        if (id==1 or id==2):
            express=3
            break
        if ctr==0 or ctrface==0:
            break    
        
    #video_capture.release()
    auxx=servo.value
    auxy=servoy.value
    
    servo.detach()
    servoy.detach()
    
    video_capture.stop()
    cv2.destroyAllWindows()
    #ctr=1
    return ctr,id,name,servo.value,servoy.value