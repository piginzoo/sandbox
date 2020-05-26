#code=utf-8
import cv2
import dlib
from threading import Thread
import time

class WebcamVideoStream:
	def __init__(self,src,width,height):
		self.stream=cv2.VideoCapture(src)
		self.stream.set(cv2.CAP_PROP_FRAME_WIDTH,width)
		self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT,height)
		(self.grabbed,self.frame)=self.stream.read()
		self.stopped=False
	def start(self):
		Thread(target=self.update,args=()).start()
		return self
	def update(self):
		while True:
			if self.stopped:
				return
			(self.grabbed,self.frame)=self.stream.read()
	def read(self):
		return (self.grabbed,self.frame)
	def stop(self):
		self.stopped=True

video_capture = WebcamVideoStream(src=0,width=640,height=480).start()
#camera=cv2.VideoCapture(0)

success,frame=video_capture.read()

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

while success and cv2.waitKey(1) == -1:
	success,frame=video_capture.read()
	cv2.flip(frame,1)
	#cv2.imshow("Camera",frame)
	gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
	clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
	clahe_image = clahe.apply(gray)
	cv2.imshow("gray",gray)
	cv2.imshow("clahe",clahe_image)
	detections=detector(clahe_image,1)
	#faces=detector(frame,1)
	for k,d in enumerate(detections):
		shape = predictor(clahe_image,d)
		for i in range(1,68):
			cv2.circle(frame,(shape.part(i).x,shape.part(i).y),1,(0,0,255),thickness=2)
		cv2.rectangle(frame,(d.left(),d.top()),(d.right(),d.bottom()),(255,0,0),2)
	cv2.imshow("dlib",frame)
	
video_capture.stop()
#camera.release()
cv2.destroyAllWindows()
