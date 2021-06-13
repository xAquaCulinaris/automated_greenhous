#!/usr/bin/env python
# coding=utf-8

#script das alle Sensoren ausliest

import sys
import RPi.GPIO as GPIO
import time
import Adafruit_DHT
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import array as arr
import xml.etree.ElementTree as ET
import ausfuehren 

#logfile path 
logfilePath = '/var/www/html/logfile.log'



##############################################################
######################## Variablen ###########################
##############################################################
tempInside = 0
tempOutside = 0
MCParray = [0,0,0]
plant0 = 0
plant1 = 0
lightLevel = 0

##############################################################
################# Konfig Ultraschall #########################
##############################################################
#GPIO Pins zuweisen
GPIO_TRIGGER = 36
GPIO_ECHO = 37

#Richtung der GPIO-Pins festlegen (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

##############################################################
#################### SPI konfig ##############################
##############################################################
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))






##############################################################
############# Messung Temp and Feuchtigkeit ##################
##############################################################
sensor = Adafruit_DHT.DHT11

humidity, temperature = Adafruit_DHT.read_retry(sensor, 20)
humidity1, temperature1 = Adafruit_DHT.read_retry(sensor, 12)

tempInside  = str(temperature)
tempOutside  = str(temperature1)
##############################################################

##############################################################
############### MCP3008 Daten auslesen #######################
##############################################################
#Licht ausschalten, damit ergebnisse nicht verfälscht werden
ausfuehren.light(1000)
time.sleep(1)
#alle drei kanäle durchgehen
for x in range(3):
    #fünf mal messen
    for i in range(5):
        #messdaten zum jeweiligen slot im array addieren
        MCParray[x] += mcp.read_adc(x)

#in eigenen variablen speichern und durch 5 teilen       
plant0 = MCParray[0]/5
plant1 = MCParray[1]/5
lightLevel = MCParray[2]/5   
##############################################################

##############################################################
#################### Wassserstand ############################
###############################################################
# setze Trigger auf HIGH
GPIO.output(GPIO_TRIGGER, True)

# setze Trigger nach 0.01ms aus LOW
time.sleep(0.00001)
GPIO.output(GPIO_TRIGGER, False)

StartZeit = time.time()
StopZeit = time.time()

# speichere Startzeit
while GPIO.input(GPIO_ECHO) == 0:
    StartZeit = time.time()

# speichere Ankunftszeit
while GPIO.input(GPIO_ECHO) == 1:
    StopZeit = time.time()

# Zeit Differenz zwischen Start und Ankunft
TimeElapsed = StopZeit - StartZeit
# mit der Schallgeschwindigkeit (34300 cm/s) multiplizieren
 # und durch 2 teilen, da hin und zurueck
distance = (TimeElapsed * 34300) / 2
################################################################
#ausgabe der messergebnisse
print(tempInside)
print(tempOutside)
print(str(plant0) +'\n')
print(str(plant1) +'\n')
print(str(lightLevel) +'\n')
print(str(distance) + '\n')

#aufrufen der Funktionen in der anderen datei
ausfuehren.waterLevel(distance)
ausfuehren.light(lightLevel)
ausfuehren.water(plant0, plant1)
ausfuehren.air(float(tempInside))


#########################################################
############ XML File ###################################
#########################################################
#messdaten in XML datei schreiben
tree = ET.parse('/var/www/html/data.xml')
root = tree.getroot()

root[0][0].text = tempInside
root[0][1].text = tempOutside
root[0][2].text = str(plant0)
root[0][3].text = str(plant1)
root[0][4].text = str(distance)
root[0][5].text = str(lightLevel)


tree.write('/var/www/html/data.xml')
#########################################################



##########################################################################
########### save log messages to log file ################################
##########################################################################
# log file öffnen
file = open(logfilePath,"a")

#log nachricht zusammenbauen
"tempInside: " + tempInside + "\n-TempOutside: " + tempOutside + "\n-Plant[0]: " + str(plant0) + "\n-Plant[1]: " + str(plant1) + "\n-Water level: " + str(distance) + "\n\n"

# log nachricht in datei schreiben
file.write("%s: %s\n" % (time.strftime("%d.%m.%Y %H:%M:%S"),logfileMessage ))

# speichern und schließen
file.close
##########################################################################

