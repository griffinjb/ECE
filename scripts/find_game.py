#!/usr/bin/env python

import numpy as np
import cv2
import math
import time
import os
import rospy
from std_msgs.msg import String

#Set true for debuging image content
show_image = False

################################################################################
#base_angle: Takes picture, Locates charger, publishes angle of charger (string)
#Return:     Void
################################################################################
def base_angle():
	#Initialize publisher settings
	pub = rospy.Publisher('chatter', String, queue_size=10)
	rospy.init_node('base_angle', anonymous=True)
	rate = rospy.Rate(1)

	#Takes photo, processes image, publishes angle
	while not rospy.is_shutdown():

		#Take Picture
		os.system('fswebcam -F 5 -d /dev/video0 --no-banner -q --png --save /home/ubuntu/catkin_ws/src/locate_hub/scripts/img_in/test.png')	
		
		#Read Image into numpy array
		img = cv2.imread("/home/ubuntu/catkin_ws/src/locate_hub/scripts/img_in/test.png")

		#Trim Image and separate by color		
		square = img[0:240,40:280]
		bs = square[0:240,0:240,0]
		gs = square[0:240,0:240,1]
		rs = square[0:240,0:240,2]

		#Subtract colored arrays to remove white light
		bmod = cv2.subtract(bs,gs)
		bmod = cv2.subtract(bmod, rs)
		gmod = cv2.subtract(gs,bs)
		gmod = cv2.subtract(gmod,rs)
		rmod = cv2.subtract(rs,gs)
		rmod = cv2.subtract(rmod,bs)

		bmod[bmod<0] = 0
		gmod[gmod<0] = 0
		rmod[rmod<0] = 0
	
		#Initialize Maximum color intensity value and location
		maxval = 0
		maxcoord = [0,0]
		not_found = False

		#For each color, find location of brightest pixel.
		for x in range(0,bmod.shape[0]):
			for y in range(0,bmod.shape[1]):
				if maxval < bmod[x,y]:
					maxval = bmod[x,y]
					maxcoord = [x,y]
		bmax = maxcoord
		maxcoord = [0,0]
		print(maxval)
		if maxval < 20:
			not_found = True
		maxval = 0

		for x in range(0,gmod.shape[0]):
			for y in range(0,gmod.shape[1]):
				if maxval < gmod[x,y]:
					maxval = gmod[x,y]
					maxcoord = [x,y]
		gmax = maxcoord
		maxcoord = [0,0]
		if maxval < 20:
			not_found = True

		print(maxval)
		maxval = 0

		for x in range(0,rmod.shape[0]):
			for y in range(0,rmod.shape[1]):
				if maxval < rmod[x,y]:
					maxval = rmod[x,y]
					maxcoord = [x,y]		
		rmax = maxcoord
		maxcoord = [0,0]
		if maxval < 20:
			not_found = True

		print(maxval)
		maxval = 0
		print(bmax,gmax,rmax)

		#Move origin from top left to center of image.  
		bmax[1] = bmax[1] - 120
		gmax[1] = gmax[1] - 120
		rmax[1] = rmax[1] - 120
		bmax[0] = 120 - bmax[0] 
		gmax[0] = 120 - gmax[0] 
		rmax[0] = 120 - rmax[0] 

		print(bmax,gmax,rmax)

		amax = [bmax,gmax,rmax]
		atheta = [0,0,0]
		
		#Calculate angle of Maximum intensities (degree)
		for i in range(0,3):
			if amax[i][0] > 0 and amax[i][1] > 0:
				atheta[i] = math.degrees(math.atan(abs(float(amax[i][0]))/abs(float(amax[i][1]))))		
			if amax[i][0] > 0 and amax[i][1] < 0:
				atheta[i] = 180 - math.degrees(math.atan(abs(float(amax[i][0]))/abs(float(amax[i][1]))))		
			if amax[i][0] < 0 and amax[i][1] > 0:
				atheta[i] = 360 - math.degrees(math.atan(abs(float(amax[i][0]))/abs(float(amax[i][1]))))		
			if amax[i][0] < 0 and amax[i][1] < 0:
				atheta[i] = 180 + math.degrees(math.atan(abs(float(amax[i][0]))/abs(float(amax[i][1]))))		

		print(atheta)
		
		#display camera and cv content for debugging
		if show_image:
			cv2.waitKey(0)
			cv2.imshow('OG', square)
			cv2.imshow('Gmod',gmod)
			cv2.imshow('Rmod',rmod)	
			cv2.imshow('Bmod',bmod)
			cv2.imshow('Green',gs)
			cv2.imshow('Red',rs)
			cv2.imshow('Blue',bs)
			#cv2.waitKey(0)


		#Publish angle, or "NOT_FOUND" if indicator is not present
		theta_out = str(atheta[1])
		NOT_FOUND = "NOT_FOUND"
		msg_out = NOT_FOUND
		if in_range(atheta) and not not_found:
			msg_out = theta_out
		
		rospy.loginfo(msg_out)
		pub.publish(msg_out)
		rate.sleep()

#Calculate angle difference and return TRUE if within 90 degrees.  modify this if this is too large and causes errant results, miscategorization.  
def in_range(atheta):
	tf = False
	bg = 180 - abs(abs(atheta[0]-atheta[1])-180)
	br = 180 - abs(abs(atheta[0]-atheta[2])-180)
	gr = 180 - abs(abs(atheta[1]-atheta[2])-180)

	if bg < 90 and br < 90 and gr < 90:
		tf = True
	return tf



#Run base_angle function
if __name__ == '__main__':
	try:
		base_angle()
	except rospy.ROSInterruptException:
		pass




