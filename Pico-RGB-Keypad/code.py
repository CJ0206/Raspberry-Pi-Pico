# RGB Keypad Multi Deck
# V4.1 Author CJ Games Live, V4 Author Gareth Naylor, adapted from code posted on the Pimoroni Forums
# Right row of buttons assigns the function set of the keypad (with the pico to the right of the board)
# 0 - Microsoft Teams / Media
# 1 - General
# 2 - Number Pad
# 3 - F13 - F24

# Import libraries
import time
import board
import busio
import usb_hid
import random
from adafruit_bus_device.i2c_device import I2CDevice
import adafruit_dotstar
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

# Configure I2C keypad
from digitalio import DigitalInOut, Direction
cs = DigitalInOut(board.GP17)
cs.direction = Direction.OUTPUT
cs.value = 0
num_pixels = 16
pixels = adafruit_dotstar.DotStar(board.GP18, board.GP19, num_pixels, brightness=0.1, auto_write=True)
i2c = busio.I2C(board.GP5, board.GP4)
device = I2CDevice(i2c, 0x20)
kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(kbd)
consumer_control = ConsumerControl(usb_hid.devices)

# Map integer values to ConsumerControlCode
INT_TO_CONSUMER_CONTROL = {
    178: ConsumerControlCode.RECORD,
    179: ConsumerControlCode.FAST_FORWARD,
    180: ConsumerControlCode.REWIND,
    181: ConsumerControlCode.SCAN_NEXT_TRACK,
    182: ConsumerControlCode.SCAN_PREVIOUS_TRACK,
    183: ConsumerControlCode.STOP,
    184: ConsumerControlCode.EJECT,
    205: ConsumerControlCode.PLAY_PAUSE,
    233: ConsumerControlCode.VOLUME_INCREMENT,
    234: ConsumerControlCode.VOLUME_DECREMENT,
    266: ConsumerControlCode.MUTE,
    # Add more mappings if needed, see https://docs.circuitpython.org/projects/hid/en/latest/api.html#adafruit_hid.consumer_control_code.ConsumerControlCode
}

# Program functions
def read_button_states(x, y):
    pressed = [0] * 16
    with device:
        device.write(bytes([0x0]))
        result = bytearray(2)
        device.readinto(result)
        b = result[0] | result[1] << 8
        for i in range(x, y):
            if not (1 << i) & b:
                pressed[i] = 1
            else:
                pressed[i] = 0
    return pressed

def toggle(this):
    return 0 if this == 1 else 1

def debounce(amount):
    time.sleep(amount)  # Just wait a bit for the pressed signals to settle down

def handle_led(id, colour):
    latch[id] = toggle(latch[id])  # Toggle the latch
    if latch[id] == 1:
        pixels[id] = colour  # Map pixel index to 0-255 range
    else:
        pixels[id] = _base

def set_set(set_id):
    latch[set_id] = 1  # Set the key to latched
    pixels[set_id] = _green  # Set control set LED to green
    for i in range(4):
        if i != set_id:
            pixels[i] = (0, 0, 0)
            latch[i] = 0
    
    # Set all defined keys in the set to the base colour
    # Keys not defined are set to off (0,0,0)
    for i in range(4, 16):
        if button_set[i + (set_id * 16)][0] == "empty":
            pixels[i] = (0, 0, 0)
        else:
            pixels[i] = _base   

def startup(base_colour):   
    for i in range(16):
        if i < 4:
            pixels[i] = base_colour
        else:
            pixels[i] = (0, 0, 0)

def send_keycodes(k, x):
    codes = button_set[x][0]  # Codes to send
    latch = button_set[x][2]  # Latch boolean (0 or 1)
    col = button_set[x][3]    # Get the colour
    handle_led(k, col)        # Set the LED to the correct colour   

    print(f"Button index: {x}")
    print(f"Codes: {codes}")
    print(f"Type of codes: {type(codes)}")

    if isinstance(codes, int) and codes in INT_TO_CONSUMER_CONTROL:
        # Handle ConsumerControlCode based on integer mapping
        print("Sending ConsumerControlCode from INT_TO_CONSUMER_CONTROL mapping")
        consumer_control.send(INT_TO_CONSUMER_CONTROL[codes])
    elif isinstance(codes, ConsumerControlCode):
        # Directly send if it is already a ConsumerControlCode
        print("Sending ConsumerControlCode directly")
        consumer_control.send(codes)
    elif isinstance(codes, int):  # Handle as a standard HID code
        print("Sending HID code directly")
        kbd.send(codes)
    elif isinstance(codes, str):
        # Handle string-based codes (e.g., "Keycode.A,Keycode.B,Keycode.C")
        print("Processing string codes")
        symbols = codes.split(",")
        if len(symbols) == 3:
            kbd.send(eval(symbols[0]), eval(symbols[1]), eval(symbols[2]))
        elif len(symbols) == 2:
            kbd.send(eval(symbols[0]), eval(symbols[1]))
        else:
            raise ValueError("String code format is invalid. Expected format: 'keycode1,keycode2,keycode3'")
    else:
        raise TypeError("Button set code must be either a string, int (HID), or ConsumerControlCode.")

    if latch == 0:
        pixels[k] = _base  # Set LED back to base colour if not latched

def send_text(k, x):
    text = button_set[x][0]  # Text to send
    col = button_set[x][3]   # Get the colour
    handle_led(k, col)       # Set the LED to the correct colour   
    if text == "_random_":
        r = random.randint(0, len(messages) - 1)
        text = messages[r]
    
    layout.write(text)       # Send the text
    
    # Check if the text is "Thanks for a good meeting." and send Enter
    if text == "Thanks for a good meeting.":
        kbd.send(Keycode.ENTER)  # Send Enter key press

# Define colours
_red = (255, 0, 0)
_green = (0, 255, 0)
_blue = (0, 0, 255)
_yellow = (255, 255, 0)
_orange = (255, 103, 0)
_purple = (84, 22, 250)
_base = (64, 64, 64)
_black = (0, 0, 0) # Colour to light the key if defined

# Manually define F13 to F24 using their HID keycodes
F13 = 0x68
F14 = 0x69
F15 = 0x6A
F16 = 0x6B
F17 = 0x6C
F18 = 0x6D
F19 = 0x6E
F20 = 0x6F
F21 = 0x70
F22 = 0x71
F23 = 0x72
F24 = 0x73

# Define button set array
button_set = {}
for i in range(64):
    button_set[i] = ["empty", 0, 0, _red]

# ---- 1st BUTTON SET ---- 4 - 15
# (keycodes or text, flag 0=kc 1=text, latch flag 0=no 1=yes, colour)
button_set[12] = ["Keycode.CONTROL,Keycode.SHIFT,Keycode.M", 0, 1, _red] # Mute toggle in Teams
button_set[8] = ["Keycode.CONTROL,Keycode.SHIFT,Keycode.O", 0, 1, _purple] # Video toggle in Teams
button_set[4] = ["Keycode.CONTROL,Keycode.SHIFT,Keycode.K", 0, 1, _orange] # Raise hand toggle in Teams

button_set[13] = [234, 0, 0, _blue] # Volume Up
button_set[9] = [266, 0, 1, _orange] # Mute Volume
button_set[5] = [233, 0, 0, _blue] # Volume Down

button_set[14] = [180, 0, 0, _blue] # Rewind
button_set[10] = [205, 0, 1, _orange] # Play/Pause
button_set[6] = [179, 0, 0, _blue] # Fast Forward

button_set[15] = ["Thanks for a good meeting.", 1, 0, _green] # End of meeting chat
button_set[11] = ["Keycode.CONTROL,Keycode.SHIFT,Keycode.S", 0, 0, _green] # Accept audio call
button_set[7] = ["Keycode.CONTROL,Keycode.SHIFT,Keycode.H", 0, 0, _red] # Leave teams meeting

# ---- 2nd BUTTON SET ---- 20 - 31
# (keycodes or text, flag 0=kc 1=text, latch flag 0=no 1=yes, colour)
#button_set[28]
#button_set[24]
#button_set[20]

#button_set[29]
#button_set[25]
#button_set[21]

#button_set[30]
#button_set[26]
#button_set[22]

button_set[31] = ["Keycode.CONTROL,Keycode.C", 0, 0, _blue] # Copy
button_set[27] = ["Keycode.CONTROL,Keycode.X", 0, 0, _blue] # Cut
button_set[23] = ["Keycode.CONTROL,Keycode.V", 0, 0, _blue] # Paste

# ---- 3rd BUTTON SET ---- 36 - 47
# (keycodes or text, flag 0=kc 1=text, latch flag 0=no 1=yes, colour)
button_set[44] = [Keycode.SEVEN, 0, 0, _red] # 7
button_set[40] = [Keycode.EIGHT, 0, 0, _red] # 8
button_set[36] = [Keycode.NINE, 0, 0, _red] # 9

button_set[45] = [Keycode.FOUR, 0, 0, _red] # 4
button_set[41] = [Keycode.FIVE, 0, 0, _red] # 5
button_set[37] = [Keycode.SIX, 0, 0, _red] # 6

button_set[46] = [Keycode.ONE, 0, 0, _red] # 1
button_set[42] = [Keycode.TWO, 0, 0, _red] # 2
button_set[38] = [Keycode.THREE, 0, 0, _red] # 3

button_set[47] = [Keycode.PERIOD, 0, 0, _red] # .
button_set[43] = [Keycode.ZERO, 0, 0, _red] # 0
button_set[39] = [Keycode.RETURN, 0, 0, _red] # Enter

# ---- 4th BUTTON SET ---- 52 - 63
# (keycodes or text , flag 0=kc 1=text, latch flag 0=no 1=yes, colour)
button_set[60] = [F13, 0, 0, _blue] # F13
button_set[56] = [F14, 0, 0, _blue] # F14
button_set[52] = [F15, 0, 0, _blue] # F15

button_set[61] = [F16, 0, 0, _blue] # F16
button_set[57] = [F17, 0, 0, _blue] # F17
button_set[53] = [F18, 0, 0, _blue] # F18

button_set[62] = [F19, 0, 0, _blue] # F19
button_set[58] = [F20, 0, 0, _blue] # F20
button_set[54] = [F21, 0, 0, _blue] # F21

button_set[63] = [F22, 0, 0, _blue] # F22
button_set[59] = [F23, 0, 0, _blue] # F23
button_set[55] = [F24, 0, 0, _blue] # F24

# Variable setup
held = [0] * 16  # Setup
latch = [0] * 16  # Setup
_set = 5  # Set the default active button set to > 4 so i.e. no active set!
todo = False 

# Main program starts here
startup(_base)  # Light up the top row with the base colour as the keys are defined

# Main loop starts here
while True:
    pressed = read_button_states(0, 16)

    if pressed[0]:
        _set = 0
        set_set(_set)
        debounce(0.25)  # Debounce
        kbd.release_all()
        debounce(0.4)
        held = [0] * 16  # Setup
        latch = [0] * 16  # Setup
        held[_set] = 1

    elif pressed[1]:
        _set = 1
        set_set(_set)
        debounce(0.25)  # Debounce
        kbd.release_all()
        debounce(0.4)
        held = [0] * 16  # Setup
        latch = [0] * 16  # Setup
        held[_set] = 1

    elif pressed[2]:
        _set = 2
        set_set(_set)
        debounce(0.25)  # Debounce
        kbd.release_all()
        debounce(0.4)
        held = [0] * 16  # Setup
        latch = [0] * 16  # Setup
        held[_set] = 1

    elif pressed[3]:
        _set = 3
        set_set(_set)
        debounce(0.25)  # Debounce
        kbd.release_all()
        debounce(0.4)
        held = [0] * 16  # Setup
        latch = [0] * 16  # Setup
        held[_set] = 1
        
    else:
        for i in range(4, 16):
            if pressed[i] and button_set[i + (_set * 16)][0] != "empty":
                # If we get here we have something to do.
                todo = True 
                index = i + (_set * 16)
                if not held[i]:
                    if button_set[index][1] == 0:
                        send_keycodes(i, index)  # Call the function to send keycodes
                        debounce(0.25)
                    else:
                        send_text(i, index)  # Call the function to send text
                        debounce(0.25)
                        pixels[i] = _base  # Because this is sending text we do not latch the LED
                        latch[i] = 0 
            
                kbd.release_all()
                held[i] = 1
                debounce(0.4)  
                if button_set[index][2] == 0:  # If the button should not latch  
                    pixels[i] = _base  # Set LEDs back to base colour
        if todo:
            for i in range(16):
                held[i] = 0  # Set held states to off
            todo = False

