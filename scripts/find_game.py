#!/usr/bin/env python

import numpy as np
import cv2
import math
import time
import os
import rospy
from std_msgs.msg import String

def base_angle():
	pub = rospy.Publisher('chatter', String, queue_size=10)
	rospy.init_node('base_angle', anonymous=True)
	rate = rospy.Rate(1)
	while not rospy.is_shutdown():
#while True:

		os.system('fswebcam -d /dev/video0 --no-banner -q --png --save /home/josh/catkin_ws/src/locate_hub/scripts/img_in/test.png')	


		img = cv2.imread("/home/josh/catkin_ws/src/locate_hub/scripts/img_in/multi.png")
		#cparse = cv2.imread("cparse.png")
		
		square = img[0:240,40:280]
		bs = square[0:240,0:240,0]
		gs = square[0:240,0:240,1]
		rs = square[0:240,0:240,2]


		bmod = cv2.subtract(bs,gs)
		bmod = cv2.subtract(bmod, rs)
		gmod = cv2.subtract(gs,bs)
		gmod = cv2.subtract(gmod,rs)
		rmod = cv2.subtract(rs,gs)
		rmod = cv2.subtract(rmod,bs)


		bmod[bmod<0] = 0
		gmod[gmod<0] = 0
		rmod[rmod<0] = 0

		maxval = 0
		maxcoord = [0,0]

		for x in range(0,bmod.shape[0]):
			for y in range(0,bmod.shape[1]):
				if maxval < bmod[x,y]:
					maxval = bmod[x,y]
					maxcoord = [x,y]
		bmax = maxcoord
		maxcoord = [0,0]
		maxval = 0

		for x in range(0,gmod.shape[0]):
			for y in range(0,gmod.shape[1]):
				if maxval < gmod[x,y]:
					maxval = gmod[x,y]
					maxcoord = [x,y]
		gmax = maxcoord
		maxcoord = [0,0]
		maxval = 0

		for x in range(0,rmod.shape[0]):
			for y in range(0,rmod.shape[1]):
				if maxval < rmod[x,y]:
					maxval = rmod[x,y]
					maxcoord = [x,y]		
		rmax = maxcoord
		maxcoord = [0,0]
		maxval = 0
		print(bmax,gmax,rmax)

		bmax[1] = bmax[1] - 120
		gmax[1] = gmax[1] - 120
		rmax[1] = rmax[1] - 120
		bmax[0] = 120 - bmax[0] 
		gmax[0] = 120 - gmax[0] 
		rmax[0] = 120 - rmax[0] 

		print(bmax,gmax,rmax)

		amax = [bmax,gmax,rmax]
		atheta = [0,0,0]

		for i in range(0,3):
			if amax[i][0] > 0 and amax[i][1] > 0:
				atheta[i] = math.degrees(math.atan(abs(float(amax[i][0]))/abs(float(amax[i][1]))))		
			if amax[i][0] > 0 and amax[i][1] < 0:
				atheta[i] = math.degrees(math.atan(abs(float(amax[i][0]))/abs(float(amax[i][1]))) + math.pi/2)		
			if amax[i][0] < 0 and amax[i][1] > 0:
				atheta[i] = math.degrees(math.atan(abs(float(amax[i][0]))/abs(float(amax[i][1]))) + 3*math.pi/2)		
			if amax[i][0] < 0 and amax[i][1] < 0:
				atheta[i] = math.degrees(math.atan(abs(float(amax[i][0]))/abs(float(amax[i][1]))) + math.pi)		

		print(atheta)

		theta_out = String(atheta[1])
		rospy.loginfo(theta_out)
		pub.publish(theta_out)
		rate.sleep()

if __name__ == '__main__':
	try:
		base_angle()
	except rospy.ROSInterruptException:
		pass


		# cv2.waitKey(0)
		# cv2.imshow('OG', square)
		# cv2.imshow('Gmod',gmod)
		# cv2.imshow('Rmod',rmod)
		# cv2.imshow('Bmod',bmod)
		# cv2.imshow('Green',gs)
		# cv2.imshow('Red',rs)
		# cv2.imshow('Blue',bs)
		# cv2.waitKey(0)


		# time.sleep(3)
		# cv2.destroyAllWindows()
