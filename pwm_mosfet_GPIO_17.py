#!/usr/bin/env python
# Author: Andreas Spiess
import os
import time
from time import sleep
import signal
import sys
import RPi.GPIO as GPIO


fanPin = 17 # The pin ID, edit here to change it
desiredTemp = 45 # The maximum temperature in Celsius after which we trigger the fan

logFile = "./pwm_mosfet_GPIO_17.log" #Path to logfile
speedFile = "./pwm_mosfet_GPIO_17.speed" #Path to speed file

fanSpeed=100
sum=0
pTemp=15
iTemp=0.4

def Shutdown():
    fanOFF()
    os.system("sudo shutdown -h 1")
    sleep(100)
def getCPUtemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    temp =(res.replace("temp=","").replace("'C\n",""))
    return temp
def fanOFF():
    myPWM.ChangeDutyCycle(0)   # switch fan off
    return()
def handleFan():
    global fanSpeed,sum
    actualTemp = float(getCPUtemperature())
    diff=actualTemp-desiredTemp
    sum=sum+diff
    pDiff=diff*pTemp
    iDiff=sum*iTemp
    fanSpeed=pDiff +iDiff
    if fanSpeed>100:
        fanSpeed=100
    if fanSpeed<15:
        fanSpeed=0
    if sum>100:
        sum=100
    if sum<-100:
        sum=-100
    message="actualTemp %4.2f TempDiff %4.2f pDiff %4.2f iDiff %4.2f fanSpeed %5d" % (actualTemp,diff,pDiff,iDiff,fanSpeed)
    #print message  #Uncomment here for testing

    log = open(logFile,'w')
    log.write(message)

    speed = open(speedFile,'w')
    speed.write(("{0}".format(fanSpeed)))

    myPWM.ChangeDutyCycle(fanSpeed)
    return()
def setPin(mode): # A little redundant function but useful if you want to add logging
    GPIO.output(fanPin, mode)
    return()
try:
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(fanPin, GPIO.OUT)
    myPWM=GPIO.PWM(fanPin,50)
    myPWM.start(50)
    GPIO.setwarnings(False)
    fanOFF()
    while True:
        handleFan()
        sleep(5) # Read the temperature every 5 sec, increase or decrease this limit if you want
except KeyboardInterrupt: # trap a CTRL+C keyboard interrupt
    fanOFF()
    GPIO.cleanup() # resets all GPIO ports used by this program
