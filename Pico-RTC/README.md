# Pico RTC <a href='https://ko-fi.com/christianjameswatkins' target='_blank'><img height='35' align='right' style='border:0px;height:46px;' src='https://az743702.vo.msecnd.net/cdn/kofi3.png?v=1' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>

This project uses a 16x2 I2C LCD display connected to a Pico W to show the current date and time synchronized from an NTP host.

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

## MicroPython Code

There isn't much code you can personalise in this project so I will just let you know that `secrets.py` is used to set up the Wi-Fi network by providing the SSID and password. You will need to update the Wi-Fi SSID and password in the code with your network details.

`calculate_countdown` is used to create a countdown to 09:00 Monday to Friday (the time I start work), and 17:00 (the time I finish work) once it reaches 09:00. On Friday/Saturday/Sunday it will count down to 09:00 on the following Monday.
