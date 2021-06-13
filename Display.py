#!/usr/bin/env python
# coding=utf-8

#script das das OLED-Dispaly steuert

import sys
sys.path.append("/home/pi/lib_oled96")
import RPi.GPIO as GPIO
from lib_oled96 import ssd1306
from smbus import SMBus
from PIL  import ImageFont
import xml.etree.ElementTree as ET
import time
 


GPIO.setmode(GPIO.BOARD)

#setup Button
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(13,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#button pins
selection = 8
ok = 10
back = 13


#variablen
menueLayer = 0
ySelection = 12


#Temperaturen aus xml Lesen
tree = ET.parse('/var/www/html/data.xml')
root = tree.getroot()

tempInside = "Temp  In: " + root[0][0].text + "C"
tempOutside ="Temp Out: " + root[0][1].text + "C"

#Display einrichten
i2cbus = SMBus(1)
oled = ssd1306(i2cbus)

#weniger code
draw = oled.canvas

#schriften
font13 = ImageFont.truetype('FreeSans.ttf', 13)
font16 = ImageFont.truetype('FreeSans.ttf', 16)

#clear Display
oled.cls()
oled.display()

#array mit den wörtern die auf dem OLED display angezeigt werden können, 
menueText =         [[tempInside, tempOutside, ""],                         # menueLayer = 0    -- Messdaten anzeigen       
                    ["water config","temp config", "light config"],         # menueLayer = 1    -- Welcher einstellungsbereich soll geändert werden?
                    ["Dry plants", "Semi plants", "Wet plants"],            # menueLayer = 2    -- Bewässerungs konfiguartation ändern
                    ["", "", ""],                                           # menueLayer = 3    -- platzhalter
                    ["High temp", "Middle temp", "Low temp"],               # menueLayer = 4    -- Temperatur konfiguartation ändern
                    ["", "", ""],                                           # menueLayer = 5    -- platzhalter
                    ["Much light", "Middle light", "Less light"],           # menueLayer = 6    -- Licht konfiguartation ändern
                    ["Settings", "successfully", "changed" ]]               # menueLayer = 7    -- Änderungen erfolgreich übernommen

#anzeigen der ausgewählten ebene
def showMenue(x,y):
    oled.cls()
#    oled.display()
    for i in range(3):
        draw.text((3,(i+i)*10 + 9), menueText[x][i], font=font13,  fill=1)

    if menueLayer != 0 and menueLayer != 7: 
        draw.text((3,y), "......................", font=font13, fill=1)


    oled.display()
   
      
#einstellungen ändern
def changeSettings(menueLayer, ySelection):
    tree = ET.parse('config.xml')
    root = tree.getroot()
    
    #bodenfeuchtigkeit schwellwert ändern
    if menueLayer == 2:
        
        
        if ySelection == 12:
            root[0][0].text = "600"
        elif ySelection == 32:
            root[0][0].text = "450"
        else:
            root[0][0].text = "350"
      
    #temperatur schwellwert ändern
    elif menueLayer == 4:
        if ySelection == 12:
            root[0][1].text = "24"
        elif ySelection == 32:
            root[0][1].text = "22"
        else:
            root[0][1].text = "18"
            
    #belichtungs fenster  ändern
    elif menueLayer == 6:
        if ySelection == 12:
            root[0][2].text = "0"
        elif ySelection == 32:
            root[0][2].text = "1"
        else:
            root[0][2].text = "2"
       
    tree.write('config.xml')
    menueLayer = 7
    
#erstes mal etwas auf dem display anzeigen    
showMenue(menueLayer, ySelection)


while True:
    #Bestätigen Knopf gedrückt
    if GPIO.input(ok) == GPIO.HIGH:
        time.sleep(0.2)
        #zweite ebene anzeigen
        if menueLayer == 0:
            menueLayer = menueLayer +1
            showMenue(menueLayer, ySelection)

        #ausgewählte ebene anzeigen
        elif menueLayer == 1:
            menueLayer = (ySelection + 8) / 10  
            showMenue(menueLayer, ySelection)
        #wieder auf erste ebene gehen
        elif menueLayer == 7:
            menueLayer = 0 
            showMenue(menueLayer, ySelection)
        #änderungen übernehmen und meldung anzeigen
        elif menueLayer == 2 or menueLayer == 4 or menueLayer == 6:
            changeSettings(menueLayer,ySelection)
            menueLayer = 7
            showMenue(menueLayer, ySelection)
            
        ySelection = 12



    #Auswahl Knopf gedrückt
    elif GPIO.input(selection) == GPIO.HIGH:
        time.sleep(0.2)
        
        #nächste möglichkeit auswählen
        if ySelection != 52:
            ySelection = ySelection + 20
            showMenue(menueLayer, ySelection)
           
        #erste möglichkeit auswählen
        else:
            ySelection = 12
            showMenue(menueLayer, ySelection)
           
        
        
        
    #zurück knopf gedrückt
    elif GPIO.input(back) == GPIO.HIGH:
        #erste auswahl möglichkeit wieder auswählen
	ySelction =  12
	time.sleep(0.2)
	#zweite ebene davor anzeigen
	if menueLayer == 2 or menueLayer == 4 or menueLayer == 6:
		menueLayer = 1
	        showMenue(menueLayer, ySelection)
		
        #erste ebene anzeigen
	else:
		menueLayer = 0
		showMenue(menueLayer, ySelection)

