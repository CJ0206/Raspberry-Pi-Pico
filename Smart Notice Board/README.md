# Smart Notice Board

This project uses a 16x2 I2C LCD display connected to a Pico W to show a predefined or custom message, along with the notice boards IP address.

![image](https://github.com/CJ0206/Raspberry-Pi-Pico/assets/8594588/50fedc23-fe46-4256-81b4-a546205384f6)

## 16×2 I2C LCD Display
A 16×2 I2C LCD Display is a type of liquid crystal display (LCD) that can display information. Each of its two lines can contain up to 16 characters. It is called an I2C LCD because it uses the I2C communication protocol to communicate with other devices, such as microcontrollers like Raspberry Pi Pico or Arduino.

## Connecting the I2C LCD to the Pico W

The connection between the Raspberry Pi Pico and I2C LCD is straightforward as shown below in the schematic:

![image](https://github.com/CJ0206/Raspberry-Pi-Pico/assets/8594588/86e343ee-9220-401e-8f7f-2fea7113c469)

| I2C LCD Display | Raspberry Pi Pico W |
| ------------- | ------------- |
| VCC	VBUS pin. | This is the power from the microUSB bus (5-volts). |
| SDA	| GP0 (I2C0 SDA) |
| SCL	| GP1 (I2C0 SCL) |
| GND	| GND |

## MicroPython Code – Web Controlled Notice Board Using Pico W

The code is divided into four parts. Namely, the parts are i2c_lcd.py, lcd_api.py, secrets.py & the fourth part is main.py. The LCD doesn’t run directly as it requires some libraries.

`secrets.py` is used to set up the Wi-Fi network by providing the SSID and password. You will need to update the Wi-Fi SSID and password in the code with your network.

Row 17 of `main.py` sets our SDA pin, while row 18 sets our SCL pin.

Rather than type a new message each time I set up a few buttons which automatically post a message, if you wanted to update or create your own change the name and value:
 - (i.e. line 173) `<input type="hidden" name="free" value="true"><input type="submit" value="Free &#x1F513;">`
 - The `name` will be the button name, `value` will be what is displayed on the webpage.
 - Change `elif "free=true" in body:` (i.e. line 223) from `free` to your chosen button name, `resp` (i.e. line 226) to your chosen status, and `lcd.putstr(chr(0)+chr(0)+chr(0)+chr(0)+chr(4))` (i.e. line 229) to any characters you want on the second row.

Any custom messages submitted through the webform will be limited to 16 characters, the input is limited so a longer inpout cannot be entered.

## Send a POST request to the microcontroller that updates the LCD

The system can also accept post requests to update the LCD, for example you can set the status to `Hello world!` using CURL:
```
curl -X POST http://192.168.1.XXX -d "Message=Hello world!"
```

Or you can select one of the custom statuses, such as `BUSY!`, using CURL:
```
curl -X POST http://192.168.1.XXX -d "busy=true"
```
