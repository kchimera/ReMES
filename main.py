import machine
import utime
import os
from LCD3inch5 import *
from sdcard import SDCard

# Wait 5 Seconds for GPIO
#utime.sleep(5)

# Define output machine.Pins for Mains 12v, water pump and battery type
mains_on = machine.Pin(2, machine.Pin.OUT)
pump_on = machine.Pin(3, machine.Pin.OUT)
battery_on = machine.Pin(4, machine.Pin.OUT)

# Measurement Leasure and Vechicle Battery Inputs
lesbat_mon = machine.ADC(26) #ADC0 / 31
vehbat_mon = machine.ADC(27) #ADC1 / 32


# States
mains_on.on()
pump_on.off()
battery_on.off()
mains_state = True
pump_state = False
battery_state = False
sleepy = False
sleep = False

logobuf = []

# settings
button_pressed_count = 0
wifi_enabled = False
led = machine.Pin("LED", machine.Pin.OUT)
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

 

# Setup SDCard and SPI
# Max baudrate produced by Pico is 31_250_000. ST7789 datasheet allows <= 62.5MHz.
# Note non-standard MISO pin. This works, verified by SD card.
spi = machine.SPI(1, 30000000, sck=machine.Pin(10), mosi=machine.Pin(11), miso=machine.Pin(12))
sd = SDCard(spi, machine.Pin(22, machine.Pin.OUT), 30000000)
os.mount(sd, "/sd", readonly=True)

# Setup screen
def screen_init():
    LCD.bl_ctrl(20)
    LCD.text("Loading", 200, 20, LCD.WHITE)
    LCD.show_up()
    LCD.show_down()
   
     
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

def render_bg():
    with open('/sd/top_image.bmp', 'rb') as file:
        # Read the BMP header to determine the size of the image
        header = file.read(70)
        width = header[18] + (header[19] << 8)
        height = header[22] + (header[23] << 8)
        print("Reading Background Image: " + str(width) + " / " + str(height))

        # Allocate a buffer to hold one row of pixels
        row_buffer = bytearray((width * 2 + 3) & ~3)
        #row_buffer = bytearray(width * 2 + 8)
        
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
                
                

# Start Screen
screen_init()

# Setup SDCard
print_directory("/sd")
render_bg()
print("BG Presented")
LCD.show_up() 

# turn on led to indicate starting
led.on()

# Loop indefinitely
while True:
    
    # Every 100 Ticks..
    if(ticks>20):
        ticks=0
        # Read Battery Level and Update if higher
        lesbat_value_last = lesbat_mon.read_u16() / (65535 / 16.5)
        vehbat_value_last = vehbat_mon.read_u16() / (65535 / 16.5)
        
        if((lesbat_value_last > lesbat_value) and (lesbat_value_last < 14)):
            lesbat_value = lesbat_value_last
            
        if((vehbat_value_last > vehbat_value) and (vehbat_value_last < 14)):
            vehbat_value = vehbat_value_last
        
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
            lesbat_pc = int(lesbat_value - 12.0) / 100
        else:
            lesbat_pc = 0
            
        if((vehbat_value < 14.0) and (vehbat_value > 12.0)):
            vehbat_pc = int(vehbat_value - 12.0) * 100
        else:
            vehbat_pc = 0
            
        lesbat_pc = 80
        vehbat_pc = 45
            
        print("Vechicle Value" + str(vehbat_value)+ " / " + "Leisure Value" + str(lesbat_value) )
        print("Vechicle Value %" + str(vehbat_pc)+ " / " + "Leisure Value %" + str(lesbat_pc))
        print("Sleep Ticks: " + str(sleep_ticks))
        
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
        # Wake up Screen
        if((sleep == True) or (sleepy == True)):
            print("Waking Up!")
            sleep = False
            sleepy = False
            sleep_ticks = 0
        else:
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
    LCD.text("Water Level at %",200,40,LCD.BLACK)
    
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
    longticks += 1


