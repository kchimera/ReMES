from machine import Pin,ADC
import utime
import gc
from BMI160 import BMI160_I2C
from os import mount
from micropython import mem_info
from LCD3inch5 import *
import sdcard

#Enable Memory GC
gc.enable()

utime.sleep(5)

# Define output Pins for Mains 12v, water pump and battery type
mains_on = Pin(2, Pin.OUT)
pump_on = Pin(3, Pin.OUT)
battery_on = Pin(4, Pin.OUT)

# Measurement Leasure and Vechicle Battery Inputs
lesbat_mon = ADC(26) #ADC0 / 31
vehbat_mon = ADC(27) #ADC1 / 32

# States
mains_on.on()
pump_on.off()
battery_on.off()
mains_state = True
pump_state = False
battery_state = False
sleepy = False
sleep = False
# Colours
darkGreen = (0 << 11) | (38 << 5) | (0)

# settings
button_pressed_count = 0
wifi_enabled = False
led = Pin("LED", Pin.OUT)
led.off
LCD = LCD_3inch5()
ticks = 0
longticks = 0
lesbat_voltage = "INIT"
vehbat_voltage = "INIT"
lesbat_value = 0
vehbat_value = 0
lesbat_pc = 0
vehbat_pc = 0
sleep_ticks = 0
# The 0% / 100% Volts of the Batteries (Normally 12.7v for a Leisure)
batteryminvolts = 12.0
batterymaxvolts = 12.7


# Setup SDCard and SPI
# Max baudrate produced by Pico is 31_250_000. ST7789 datasheet allows <= 62.5MHz.
spi = SPI(1, 30_000_000, sck=Pin(10), mosi=Pin(11), miso=Pin(12))
sd = sdcard.SDCard(spi, Pin(22, Pin.OUT), 30_000_000)
mount(sd, "/sd", readonly=False)

# Setup screen
def screen_init():
    LCD.bl_ctrl(20)
    LCD.text("Loading", 200, 20, LCD.WHITE)
    LCD.show_up()
    LCD.show_down()

def render_bg():
    with open('/sd/top_image.bmp', 'rb') as file:
        # Read the BMP header to determine the size of the image
        header = file.read(70)
        width = header[18] + (header[19] << 8)
        height = header[22] + (header[23] << 8)
        
        # Allocate a buffer to hold one row of pixels
        row_buffer = bytearray((width * 2 + 3) & ~3)
        
        # Read the image data in chunks
        for y in range(height - 1, -1, -1):
            # Read one row of pixel data
            file.readinto(row_buffer)
            # Extract the pixel values from the row buffer
            for x in range(width):
                # Get the two bytes representing the pixel
                b1, b2 = row_buffer[x * 2:x * 2 + 2]
                
                # Extract the red, green, and blue values from the bytes
                r = ((b2 & 0x1f) << 3) | (b1 >> 5)
                g = ((b2 & 0x7e0) >> 3)
                b = ((b2 & 0xf800) >> 8)
                # Recompress them into 16bit Int
                pixel_value = (b1 << 8) | b2
                # Write to Framebuffer
                LCD.pixel(x,y,pixel_value)
        del row_buffer
        gc.collect()

def init_6dof():
    

               
# Start Screen
screen_init()

# Setup GFX
gc.collect()
render_bg()
LCD.show_up()

# turn on led to indicate starting
led.on()

# Loop indefinitely
while True:
    if(ticks>20):
        ticks=0
        # Read Battery Level and Update if higher
        lesbat_value_last = lesbat_mon.read_u16() / (65535 / 16.5)
        #print("LesBat" + str(lesbat_value) + " / Last:" + str(lesbat_value))
        vehbat_value_last = vehbat_mon.read_u16() / (65535 / 16.5)
        #print("VehBat Mon:" + str(vehbat_mon.read_u16()))
        if(lesbat_value_last < lesbat_value):
            lesbat_value = lesbat_value_last
           #print("Setting Leisure Bat to: " + str(lesbat_value))
        elif((lesbat_value_last > lesbat_value) and (lesbat_value_last < 14)):
            lesbat_value = lesbat_value_last
            #print("Setting Leisure Bat to: " + str(lesbat_value))
            
        
        if(vehbat_value_last < vehbat_value):
            vehbat_value = vehbat_value_last  
            #print("Setting Vehicle Bat to: " + str(vehbat_value))
        elif((vehbat_value_last > vehbat_value) and (vehbat_value_last < 14)):
            vehbat_value = vehbat_value_last
            #print("Setting Vehicle Bat to: " + str(vehbat_value))
        
        # Led Flash
        led.toggle()
    
    if(longticks>200):
        # A long tick time has passed, possibly 30 secs?
        longticks=0   
        # Update Voltage Levels
        lesbat_string = str(lesbat_value)   
        vehbat_string = str(vehbat_value)
        # Clean up Voltage Levels
        lesbat_voltage = lesbat_string[:-4]
        vehbat_voltage = vehbat_string[:-4]
        
        # Set Percentages
        if((lesbat_value < 14.0) and (lesbat_value > 12.0)):
            lesbat_pc = ((lesbat_value - batteryminvolts) / (batterymaxvolts - batteryminvolts)) * 100
        else:
            lesbat_pc = 0
            
        if((vehbat_value < 14.0) and (vehbat_value > 12.0)):
            vehbat_pc =  ((vehbat_value - batteryminvolts) / (batterymaxvolts - batteryminvolts)) * 100
        else:
            vehbat_pc = 0
            
        print("Vechicle Value" + str(vehbat_value)+ " / " + "Leisure Value" + str(lesbat_value) )
        print("Vechicle Value %" + str(vehbat_pc)+ " / " + "Leisure Value %" + str(lesbat_pc))
        print("Sleep Ticks: " + str(sleep_ticks))
        print("Memory Info"+str(mem_info()))
    
    # Work with Sleep Ticks, currently set to 500 for full sleepy and 2000 for sleep, this is reset with screen touch
    if(sleep_ticks==500):
        sleepy = True
        print("Feeling Sleepy...")
    if(sleep_ticks==2000):
        print("Going to Sleep...")
        sleep = True
        sleep_ticks = 0
    else:
        if(sleep == False):
            sleep_ticks += 1
        
    # Set Sleepy or Sleep Mode
    if((sleep == True) and (sleepy == True)):
        LCD.bl_ctrl(0)
    if((sleep == False) and (sleepy == True)):
        LCD.bl_ctrl(20)
    if((sleep == False) and (sleepy == False)):
        LCD.bl_ctrl(60)
        
    get = LCD.touch_get()
    if get != None:
        # Wake up Screen if touched and sleepy / sleep, then exit if to regain control
        if((sleep == True) or (sleepy == True)):
            print("Waking Up!")
            sleep = False
            sleepy = False
            sleep_ticks = 0
            time.sleep(0.3)
        else:
            sleep_ticks = 0
            X_Point = int((get[1]-430)*480/3270)
            if(X_Point>480):
                X_Point = 480
            elif X_Point<0:
                X_Point = 0
            Y_Point = 320-int((get[0]-430)*320/3270)
            if(Y_Point>220):
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
    
    # Fill Bottom Section in Back BG
    LCD.fill(LCD.BLACK)
    
    #Draw Battery Levels
    if (lesbat_pc<=25):
        LCD.fill_rect(0,0,(int(float(280/100)*lesbat_pc))-40,30,LCD.RED)
    elif(lesbat_pc<=50):
        LCD.fill_rect(0,0,(int(float(280/100)*lesbat_pc))-40,30,LCD.BLUE)
    elif(lesbat_pc<=100):
        LCD.fill_rect(0,0,(int(float(280/100)*lesbat_pc))-40,30,LCD.GREEN)
    
    if (vehbat_pc<=25):
        LCD.fill_rect((480-int(float(280/100)*vehbat_pc))+40,0,480,30,LCD.RED)
    elif(vehbat_pc<=50): 
        LCD.fill_rect((480-int(float(280/100)*vehbat_pc))+40,0,480,30,LCD.BLUE)
    elif(vehbat_pc<=100):
        LCD.fill_rect((480-int(float(280/100)*vehbat_pc))+40,0,480,30,LCD.GREEN)
    
    
    # Write Battery Levels
    LCD.text(lesbat_voltage+" V",30,12,LCD.WHITE)
    LCD.text(vehbat_voltage+" V",400,12,LCD.WHITE)

    # Draw Water Level Bar
    LCD.fill_rect(0,35,480,20,LCD.GREEN)
    LCD.text("Water Level at %",200,40,darkGreen)
    
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
        
    # Render lower section that contains controls & Graphs etc...        
    LCD.show_down()
    ticks += 1
    longticks += 1


