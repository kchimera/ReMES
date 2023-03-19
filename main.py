import machine
import micropython
import time
import utime


print("Setting up machine.Pins...")
# Define output machine.Pins for Mains 12v, water pump and battery type
mains_on = machine.Pin(2, machine.Pin.OUT)

# Input Button machine.Pins
mains_btn = machine.Pin(6, machine.Pin.IN, machine.Pin.PULL_DOWN)

# Measurement Leasure and Vechicle Battery Inputs
lesbat_mon = machine.ADC(26) #ADC0 / 31
vehbat_mon = machine.ADC(27) #ADC1 / 32

# global value
button_pressed_count = 0

# Deal with Button Presses
def button_press(pin):
    global button_pressed_count, mains_btn
    print("Button Pushed")
    if pin is mains_btn:
        mains_on.toggle()
        time.sleep(0.1)
    button_pressed_count += 1

# Setup the outputs to be low on startup
mains_btn.irq(handler=button_press, trigger=machine.Pin.IRQ_FALLING)

button_pressed_count_old = 0

# turn on led
led = machine.Pin("LED", machine.Pin.OUT)
led.on()

# Loop indefinitely
while True:
    if button_pressed_count_old != button_pressed_count:
       print('Button 1 value:', button_pressed_count)
       button_pressed_count_old = button_pressed_count
    
    # Read battery Level and Print
    lesbat_value = str(lesbat_mon.read_u16() / (65535 / 16.5))
    lesbat_voltage = lesbat_value[:-4]
    print(lesbat_voltage)

    led.toggle()
    time.sleep(1)  
        


