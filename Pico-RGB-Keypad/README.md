# Pico-RGB-Keypad <a href='https://ko-fi.com/christianjameswatkins' target='_blank'><img height='35' align='right' style='border:0px;height:46px;' src='https://az743702.vo.msecnd.net/cdn/kofi3.png?v=1' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>

This project used the [Pico RGB Keypad Base](https://shop.pimoroni.com/products/pico-rgb-keypad-base?variant=32369517166675) as a 4 layerd, 12 key macro keypad (4 * 12 = 48 usable keys).

![image](https://github.com/user-attachments/assets/438fed37-d691-4ad6-a2e1-42421bc10cae)

## Circuit Python installation
The Pico comes with micro python installed, but at the time I wrote the software, micro-python did not yet fully support the key-pad, so I installed Adafruit’s circuit python onto the Pico. Here are the instructions, original credit for these go to ColinD from the Pimoroni forums, I have updated them here:

1. Connect your Keypad to your computer via USB while holding down the onboard button. The Pico will appear as a storage drive on the computer.
2. Download latest release (or lastest stable) from [Pico](https://circuitpython.org/board/raspberry_pi_pico/) or [Pico W](https://circuitpython.org/board/raspberry_pi_pico_w/) download.
3. Copy the UF2 file to the Pico top level directory.
4. The Pico reboots automatically.

We still need two libraries to ensure that we can use the RGB Keypad. The adafruit_dotstar library that drives the leds under the keys and the adafruit_hid (human interface device = keyboard) library, that makes the device appear as a keyboard to the computer that it is connected to. To install these libraries:

From the [July 30, 2024 auto-release adafruit/Adafruit_CircuitPython_Bundle on GitHub](https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/tag/20240730), download the [adafruit-circuitpython-bundle-py-20210403.zip](https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/download/20240730/adafruit-circuitpython-bundle-py-20240730.zip) file to your computer.

Unzip the file (this may take a while) and copy the following into the lib folder on the Pico drive:
- The `adafruit_hid` folder and all its contents.
- The `adafruit_dotstar.py` file.
- The `adafruit_pixelbuf.py` file.

The last step is to save the [code.py](code.py) onto the top level of the Pico. To get it to run at bootup up name the file code.py

## How to configure the software
Keys are defined in sets of 12, in the button_set{} array. You only need to define the keys you want to program. All other keys will be automatically set to empty and not lit.

Key definitions start at line 185 of the programme. The syntax is like this:

`button_set[4] = [“Keycode.CONTROL,Keycode.SHIFT,Keycode.M”, 0, 1, _red]`

the number [4] is the unique reference to the key and set. The first key set uses 4-15, the second keyset uses 20-31 etc.

The first entry on the right hand side of the `=` is either a Keyboard sequence of two or 3 keys separated by commas, or Text. So the above example sends CTRL+SHIFT+M. A full list of KeyCodes can be found [here](https://circuitpython.readthedocs.io/projects/hid/en/latest/api.html#adafruit-hid-keycode-keycode).

For media control keys, these needed to be defined manually at the start of line 38, I have left a few unused common controls in the code which can be used or expanded upon. These can be seen on line 189 - 195:

```
button_set[13] = [234, 0, 0, _blue] # Volume Up
button_set[9] = [266, 0, 1, _orange] # Mute Volume
button_set[5] = [233, 0, 0, _blue] # Volume Down

button_set[14] = [180, 0, 0, _blue] # Rewind
button_set[10] = [205, 0, 1, _orange] # Play/Pause
button_set[6] = [179, 0, 0, _blue] # Fast Forward
```

The extended function keys also needed to be manually defined by their HID values from line 165, you could add to these or change them to F1 - F12 but my keyboard already has a function row and I wanted to expand on it, this can be useful for things such as setting hotkeys in OBS. The code has been implimented on the 4th button set:

```
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
```

The second entry is 0 if we are sending Keycodes/HID Codes/ConsumerControlCode or 1 if we are sending text.

The third entry determines if the key latches [0 = no, 1 = yes], this determines the behaviour of the LED under the key. If the key is set to latch, then the LED will toggle every time the key is pressed. If the key is set to not latch, then the LED will light for a short period of time when pressed and then go out.

The last entry is a RGB tuple (e.g. `(124,125,126)` or the colours defined from row 155 `_red = (255, 0, 0)`) which configures the colour the LED turns to when the key is pressed.

If you find the LEDs too dim, or too bright, just amend the brightness on line 29 from `0.3` to anything between 0 (off) and 1 (full brightness):

```
pixels = adafruit_dotstar.DotStar(board.GP18, board.GP19, num_pixels, brightness=0.3, auto_write=True)
```

## boot.py
`boot.py` runs before `code.py` is run by the micro controller, it seems to make things a little unreliable in my testing on a USB hub so use at your own risk and ensure you have a backup of your code/library before experimenting. It seems to work fine plugged directly into the PC.

The main annoyance faced when using the keypad is that circuit python will launch as a USB storage device when plugged in to a computer (which may be against company policies if you plan to use it on a work computer).

The following line disables the drive launching, meaning you will need to either wipe your drive and start from scratch, or use Thonny to update any code (note `import storage` needs to be at the top of the file):
```
storage.disable_usb_drive()  
```

I did not like the keypad showing as Pico W in the device menager, when searching I found there had been a PR to allow users to set the interface name (note `import usb_hid` needs to be at the top of the file):
```
usb_hid.set_interface_name("CJs Macro Pad")
```

The above change does not always work due to the vendor and product ID's, from a comment on GitHub I decided to try and set my own using their example which worked. You can decide your own name and manufacturer, make sure any VID or PID you set is valid or you will get an error in `boot_output.txt` (note `import supervisor` needs to be at the top of the file):
```
supervisor.set_usb_identification(manufacturer='CJ', product='CJs Macro Pad', vid=0xC116, pid=0x1316)
```
I went for a vendor ID of C 10 (J) 16 (P) for CJ Pico and a product ID of 13 (M) 16 (P) for Macro Pad.

## safemode.py
This file is completely optional, if an error occurs and forces the Pico into safe mode it will reboot the board as if a reset button has been pressed. This will hopfully mitigate any errors caused by a dodgy USB cable or hub and allow the board to boot correctly on the second attempt.
