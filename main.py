import machine
import time
from LCD3inch5 import *

print("Setting up machine.Pins...")
# Define output machine.Pins for Mains 12v, water pump and battery type
mains_on = machine.Pin(2, machine.Pin.OUT)
pump_on = machine.Pin(3, machine.Pin.OUT)
battery_on = machine.Pin(4, machine.Pin.OUT)

# Input Button machine.Pins
mains_btn = machine.Pin(6, machine.Pin.IN, machine.Pin.PULL_DOWN)
pump_btn = machine.Pin(7, machine.Pin.IN, machine.Pin.PULL_DOWN)

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
lesbat_voltage = "0"
vehbat_voltage = "0"

# Setup screen
def screen_init():
    print("Configuring Screen")
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

# Deal with Button Presses
def button_press(pin):
    global button_pressed_count, mains_btn
    print("Button Pushed")
    if pin is mains_btn:
        mains_on.toggle()
        time.sleep(0.1)
    if pin is pump_btn:
        pump_on.toggle()
    button_pressed_count += 1

# Setup the outputs to be low on startup
mains_btn.irq(handler=button_press, trigger=machine.Pin.IRQ_FALLING)
button_pressed_count_old = 0

# Start Screen
screen_init()

# turn on led to indicate starting
led.on()

print("Entering Main Loop")
# Loop indefinitely
while True:
    if button_pressed_count_old != button_pressed_count:
       print('Button 1 value:', button_pressed_count)
       button_pressed_count_old = button_pressed_count
    
    # Every 100 Ticks..
    if(ticks>20):
        ticks=0
        # Read battery Level and Print
        lesbat_value = str(lesbat_mon.read_u16() / (65535 / 16.5))
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
        print(str(X_Point)+" /" + str(Y_Point))
        if(Y_Point>220):
            LCD.fill(LCD.WHITE)
            if(X_Point<160):
                if(mains_state==True):
                    # Turn off Mains 12V
                    mains_on.off()
                    mains_state = False
                    time.sleep(0.3)
                else:
                    # Turn on Mains 12V
                    mains_on.on()
                    mains_state = True
                    time.sleep(0.3)
            elif(X_Point<320):
                if(pump_state==True):
                    # Turn off Water Pump
                    pump_on.off()
                    pump_state = False
                    time.sleep(0.3)
                else:
                    # Turn on Water Pump
                    pump_on.on()
                    pump_state = True
                    time.sleep(0.3)
            elif(X_Point<480):
                if(battery_state==True):
                    # Turn from Vechicle charge
                    battery_on.off()
                    battery_state = False
                    time.sleep(0.3)
                else:
                    # Turn to Vechicle Charge
                    battery_on.on()
                    battery_state = True    
                    time.sleep(0.3) 

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


