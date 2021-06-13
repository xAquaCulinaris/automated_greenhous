#!/usr/bin/env python
# coding=utf-8

#script das Bewässerung, Belichtung, Belüftung und die Wasserstand statusanzeige steuert

import RPi.GPIO as GPIO
import datetime
import time
import array as arr

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import xml.etree.ElementTree as ET
#led
from neopixel import *

#########################################################
########### LED strip configuration #####################
#########################################################
LED_COUNT      = 51      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
#########################################################

tree = ET.parse('config.xml')
root = tree.getroot()



#GPIO pins
pumpGPIO = [40,35]  #pumpen gpios
fanGPIO = 33        #lüfter gpio
r = 29              #RGB led roter pin gpio
g = 31              #rgb led grüner pin gpio



#logfile path 
logfilePath = '/var/www/html/logfile.log'

#GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(pumpGPIO[0], GPIO.OUT)
GPIO.setup(pumpGPIO[1], GPIO.OUT)
GPIO.setup(fanGPIO, GPIO.OUT)
GPIO.setup(r, GPIO.OUT)
GPIO.setup(g, GPIO.OUT)


##########################################
##############Bewässerung#################
##########################################
def water(plant0, plant1):
    #auslesen des eingestellten schwellwertes
    tree = ET.parse('config.xml')
    root = tree.getroot()
    plantValue = root[0][0].text
    
    plants = [plant0,plant1]
    #abfragen ob pflanze zu trocken (geht beide pflanzen durch)
    for i in range(2):
        if plants[i] > int(plantValue):
            
            watering(i)
        else:
            log('Plant[' + str(i) + '] doesnt need water')
#wenn pflanze zu trocken bewässern
def watering(i):
    GPIO.output(pumpGPIO[i], GPIO.HIGH)
    time.sleep(2.5)
    GPIO.output(pumpGPIO[i], GPIO.LOW)
    log('Plant[' + str(i) + '] has been watered')
##############################################
    


    
################################################
############### Wasserstand ####################
################################################
def waterLevel(abstand):
    #abfragen des wasserstandes und RGB LED farbe aktualisieren
    if abstand > 20:
        log('water level critical')
        GPIO.output(r, GPIO.LOW)
        GPIO.output(g, GPIO.HIGH)
        
    elif abstand > 15:
        log('enough water')
        GPIO.output(r, GPIO.LOW)
        GPIO.output(g, GPIO.LOW)
        
    else:
        print('water full')
        GPIO.output(r, GPIO.HIGH)
        GPIO.output(g, GPIO.LOW)

    print ("Gemessene Entfernung = %.1f cm" % abstand)
######################################################

##################################################################
##################### Air ########################################
##################################################################
def air(temp):
    #eingestellten wert aus xml holen
    tree = ET.parse('config.xml')
    root = tree.getroot()
    tempValue = root[0][1].text
    #eingestellte temperatur mit aktueller temp abgleichen
    if temp > tempValue:
        print("air start")
        GPIO.output(fanGPIO, GPIO.HIGH)
        time.sleep(100)
        print("air stop")
        GPIO.output(fanGPIO, GPIO.LOW)
##################################################################


##################################################################
##################### Licht ######################################
##################################################################
def light(lightLevel):

    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    begin = 0
    end = 0
    
    #eingestelltes zeitfenster in der xml auslesen und die werte dafür setzten
    if int(root[0][3].text) == 0:
        begin = 7
        end = 20
    elif int(root[0][3].text) == 1:
        begin = 8
        end = 18
    else:
        
        begin = 8
        end = 16
    #aktuelle uhrzeit abfragen
    now = datetime.datetime.now()
    
    #zeitfenster beginn wert setzten
    fromm = now.replace(hour=begin, minute = 0, second = 0, microsecond = 0)
    #zeitfenster ende wert setzten
    to = now.replace(hour=end, minute = 0, second = 0, microsecond = 0)

    strip.begin()
    brightness = 0
    
    #abfragen ob aktuelle uhrzeit innerhalb des zeitfensters liegt
    if now > fromm and now < to:
        #abfragen wie hell die leds gemacht werden sollen
        if lightLevel < 200:
            brightness = 255
        elif lightLevel < 300:
            brightness = 170
        elif lightLevel < 400:
            brightness = 100
        elif lightLevel < 500:
            brightness = 50
        else: 
            brightness = 0
        
    #leds ausschalten wenn die uhrzeit nicht im zeitfenster liegt
    else:
        brightness = 0
    #alle leds durchgehen, rede 4. auf rot die restlichen auf blau 
    for i in range(strip.numPixels()):
        if i%4 == 0:
            strip.setPixelColor(i, Color(0,brightness,0))
        else:
            strip.setPixelColor(i,Color(0,0,brightness))    
    #auf strip übertragen        
    strip.show()
    
    #log datei schreiben
    if lightLevel < 500 and now > fromm and now < to:
        log('light on')
    else:
        log('light off')
        

    
####################################################################


###########################################################
########### save log messages to log file #################
###########################################################
def log(msg):
    # log file öffnen
    file = open(logfilePath,"a")

    # mit zeitstempel angegebenen string in die log datei schreiben
    file.write("%s: %s\n" % (time.strftime("%d.%m.%Y %H:%M:%S"),msg ))

    # speichern und schließen
    file.close








