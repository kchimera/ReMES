import machine
import utime
import struct
import os
from LCD3inch5 import *
from sdcard import SDCard

# Wait 5 Seconds for GPIO
utime.sleep(2)

# Define output machine.Pins for Mains 12v, water pump and battery type
mains_on = machine.Pin(2, machine.Pin.OUT)
pump_on = machine.Pin(3, machine.Pin.OUT)
battery_on = machine.Pin(4, machine.Pin.OUT)

# Input Button machine.Pins
#mains_btn = machine.Pin(6, machine.Pin.IN, machine.Pin.PULL_DOWN)
#pump_btn = machine.Pin(7, machine.Pin.IN, machine.Pin.PULL_DOWN)

# Measurement Leasure and Vechicle Battery Inputs
lesbat_mon = machine.ADC(26) #ADC0 / 31
vehbat_mon = machine.ADC(27) #ADC1 / 32


# States
mains_on.off()
pump_on.off()
battery_on.off()
mains_state = False
pump_state = False
battery_state = False

# settings
button_pressed_count = 0
wifi_enabled = False
led = machine.Pin("LED", machine.Pin.OUT)
led.off
LCD = LCD_3inch5()
ticks = 0
lesbat_voltage = "INIT"
vehbat_voltage = "INIT"

# sd
# Max baudrate produced by Pico is 31_250_000. ST7789 datasheet allows <= 62.5MHz.
# Note non-standard MISO pin. This works, verified by SD card.
#spi = machine.SPI(1, 60_000_000, sck=machine.Pin(10), mosi=machine.Pin(11), miso=machine.Pin(12))


# Setup screen
def screen_init():
    LCD.bl_ctrl(20)
    #color BRG
    #LCD.fill(LCD.BLACK)
    LCD.fill_rect(1,1,220,30,LCD.RED)
    LCD.text("ReMES - Control Panel Test",1,11,LCD.WHITE)
    display_color = 0x001F
    LCD.text("3.5' IPS LCD TEST",170,57,LCD.BLACK)
    for i in range(0,12):      
        LCD.fill_rect(i*30+60,100,30,20,(display_color))
        display_color = display_color << 1
    LCD.show_up()

# Setup SD Card Access
#def sdcard_init():    
 #    sd = SDCard(spi, machine.Pin(22, machine.Pin.OUT), 30_000_000)
  #   os.mount(sd, "/sd", readonly=True)


def print_directory(path, tabs = 0):
    for file in os.listdir(path):
        stats = os.stat(path+"/"+file)
        filesize = stats[6]
        isdir = stats[0] & 0x4000
    
        if filesize < 1000:
            sizestr = str(filesize) + " by"
        elif filesize < 1000000:
            sizestr = "%0.1f KB" % (filesize/1000)
        else:
            sizestr = "%0.1f MB" % (filesize/1000000)
    
        prettyprintname = ""
        for i in range(tabs):
            prettyprintname += "   "
        prettyprintname += file
        if isdir:
            prettyprintname += "/"
        print('{0:<40} Size: {1:>10}'.format(prettyprintname, sizestr))
        
        # recursively print directory contents
        if isdir:
            print_directory(path+"/"+file, tabs+1)

# Start Screen
screen_init()

# Setup SDCard
#sdcard_init()
#print_directory("/sd")

# turn on led to indicate starting
led.on()

# Loop indefinitely
while True:
    
    # Every 100 Ticks..
    if(ticks>20):
        ticks=0
        # Read battery Level and Print
        if((lesbat_mon.read_u16() / (65535 / 16.5)) < 8):
            lesbat_value = "0"
        else:
            lesbat_value = str(lesbat_mon.read_u16() / (65535 / 16.5))
        if ((vehbat_mon.read_u16() / (65535 / 16.5)) < 8):
            vehbat_value = "0" 
        else:       
            vehbat_value = str(vehbat_mon.read_u16() / (65535 / 16.5))
        # Clean up Voltage Levels
        lesbat_voltage = lesbat_value[:-4]
        vehbat_voltage = vehbat_value[:-4]
        # Led Flash
        led.toggle()
    
    get = LCD.touch_get()
    if get != None: 
        X_Point = int((get[1]-430)*480/3270)
        if(X_Point>480):
            X_Point = 480
        elif X_Point<0:
            X_Point = 0
        Y_Point = 320-int((get[0]-430)*320/3270)
        if(Y_Point>220):
            LCD.fill(LCD.WHITE)
            if(X_Point<160):
                if(mains_state==True):
                    # Turn off Mains 12V
                    mains_on.off()
                    mains_state = False
                else:
                    # Turn on Mains 12V
                    mains_on.on()
                    mains_state = True
            elif(X_Point<320):
                if(pump_state==True):
                    # Turn off Water Pump
                    pump_on.off()
                    pump_state = False
                else:
                    # Turn on Water Pump
                    pump_on.on()
                    pump_state = True
            elif(X_Point<480):
                if(battery_state==True):
                    # Turn from Vechicle charge
                    battery_on.off()
                    battery_state = False
                else:
                    # Turn to Vechicle Charge
                    battery_on.on()
                    battery_state = True    
            utime.sleep(0.3)
    
    LCD.fill(LCD.WHITE)
    LCD.text("Leisure Battery: "+lesbat_voltage+"V",30,30,LCD.BLACK)
    LCD.text("Vechicle Battery:"+vehbat_voltage+"V",250,30,LCD.BLACK)
    
    # Check and Show States
    if(mains_state):
        LCD.fill_rect(0,60,160,100,LCD.RED)
        LCD.text("12V System",40,110,LCD.WHITE)
        LCD.rect(0,60,160,100,LCD.BLUE)
    else:
        LCD.fill_rect(0,60,160,100,LCD.BLACK)
        LCD.text("12V System",40,110,LCD.WHITE)
        LCD.rect(0,60,160,100,LCD.WHITE)
    if(pump_state):
        LCD.fill_rect(160,60,160,100,LCD.RED)
        LCD.text("Water Pump",200,110,LCD.WHITE)
        LCD.rect(160,60,160,100,LCD.BLUE)
    else:
        LCD.fill_rect(160,60,160,100,LCD.BLACK)
        LCD.text("Water Pump",200,110,LCD.WHITE)
        LCD.rect(160,60,160,100,LCD.WHITE)
    if(battery_state):
        LCD.fill_rect(320,60,160,100,LCD.RED)
        LCD.text("Battery Select",340,110,LCD.WHITE)
        LCD.rect(320,60,160,100,LCD.BLUE)
    else:
        LCD.fill_rect(320,60,160,100,LCD.BLACK)
        LCD.text("Battery Select",340,110,LCD.WHITE)
        LCD.rect(320,60,160,100,LCD.WHITE)

    LCD.show_down() 
    ticks += 1


