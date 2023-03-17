import machine
import utime

# Define pins for Mains 12v, water pump and battery type
main12v_pin = machine.Pin(4, machine.Pin.OUT)
water_pump_pin = machine.Pin(5, machine.Pin.OUT)
battery_type_pin = machine.Pin(6, machine.Pin.OUT)

# Define Input Pins
main12v_on = machine.Pin(9)
water_pump_on = machine.Pin(10)
battery_type_on = machine.Pin(11)

# Define pins for battery capacity measurement
battery1_pin = machine.ADC(31)
battery2_pin = machine.ADC(32)

# Define pin for water level measurement
water_level_pin = machine.ADC(34)

# Define threshold values for water level measurement
water_level_threshold_low = 500
water_level_threshold_high = 800

# define states
main12v_state = False
water_pump_state = False
battery_type_state = False

# Define function to read battery capacity
def read_battery(pin):
    # Convert ADC value to voltage
    voltage = pin.read_u16() * 3.3 / 65535
    # Calculate battery capacity as a percentage
    capacity = (voltage - 10) / 2 * 100
    # Make sure capacity is within range of 0-100%
    if capacity < 0:
        capacity = 0
    elif capacity > 100:
        capacity = 100
    return capacity

# Define function to read water level
def read_water_level(pin):
    # Read ADC value
    value = pin.read_u16()
    # Determine water level based on threshold values
    if value < water_level_threshold_low:
        level = "low"
    elif value > water_level_threshold_high:
        level = "high"
    else:
        level = "medium"
    return level

# Loop indefinitely
while True:
    
    
    """
    # Read battery capacities
    battery1_capacity = read_battery(battery1_pin)
    battery2_capacity = read_battery(battery2_pin)
    # Read water level
    water_level = read_water_level(water_level_pin)
    # Switch on and off outputs based on conditions
    if battery1_capacity < 20:
        main12v_pin.value(0)
        water_pump_pin.value(0)
        battery_type_pin.value(1)
    elif battery2_capacity < 20:
        main12v_pin.value(0)
        water_pump_pin.value(0)
        battery_type_pin.value(2)
    elif water_level == "low":
        main12v_pin.value(0)
        water_pump_pin.value(1)
        battery_type_pin.value(1)
    else:
        main12v_pin.value(1)
        water_pump_pin.value(1)
        battery_type_pin.value(1)
    # Wait for a moment before reading again
    """
    utime.sleep(1)
