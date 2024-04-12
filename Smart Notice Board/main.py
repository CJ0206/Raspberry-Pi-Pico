import secrets
import time
import network
import socket
import rp2

from ubinascii import unhexlify

import machine
from machine import I2C
from lcd_api import LcdApi
from i2c_lcd import I2cLcd

LCD_ADDR = 0x27
LCD_NUM_ROWS = 2
LCD_NUM_COLS = 16
LCD_SDA = 0
LCD_SCL = 1

i2c = I2C(0, sda=machine.Pin(LCD_SDA), scl=machine.Pin(LCD_SCL), freq=400000)
lcd = I2cLcd(i2c, LCD_ADDR, LCD_NUM_ROWS, LCD_NUM_COLS)
lcd.putstr('Connect to WiFi')

rp2.country('IN')
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.ssid, secrets.pwd)

print('Connecting to WiFi...')
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    time.sleep(1)

if wlan.status() != 3:
    print('Could not connect!')

print('Connected with WiFi')
status = wlan.ifconfig()
ipserv = status[0]
print('ip = ' + ipserv)
lcd.clear()
lcd.putstr(ipserv)

html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Smart Notice Board</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background-color: #1e1e1e;
      color: #fff;
      margin: 0;
      padding: 0;
    }
    .container {
      max-width: 600px;
      margin: 50px auto;
      padding: 20px;
      border-radius: 10px;
      background-color: #333;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
    }
    h1 {
      text-align: center;
    }
    label {
      display: block;
      margin-bottom: 10px;
    }
    input[type="text"] {
      width: 97%;
    }
    input[type="submit"] {
      width: 100%;
    }
    input[type="text"], input[type="submit"] {
      padding: 10px;
      margin-bottom: 20px;
      border: none;
      border-radius: 5px;
      background-color: #555;
      color: #fff;
      cursor: pointer;
    }
    input[type="submit"] {
      background-color: #007bff;
    }
    table {
      width: 100%;
      margin-bottom: 20px;
      border-collapse: collapse;
    }
    td {
      padding: 5px;
    }
    th, td {
      padding: 10px;
      text-align: center;
    }
    th {
      color: #fff;
    }
    th:first-child {
      border-top-left-radius: 5px;
    }
    th:last-child {
      border-top-right-radius: 5px;
    }
    th, td {
      border-bottom: 1px solid #444;
    }
    tr:last-child td {
      border-bottom: none;
    }
    p {
      text-align: center;
      font-size: 20px;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Smart Notice Board</h1>
    <form method="post">
      <label for="msg">Custom message:</label>
      <input type="text" id="msg" name="Message" placeholder="Hello world!" maxlength="16">
      <input type="submit" value="Send">
    </form>
    <table>
      <tr>
        <th><form method="post"><input type="hidden" name="free" value="true"><input type="submit" value="Free &#x1F513;"></form></th>
        <th><form method="post"><input type="hidden" name="away" value="true"><input type="submit" value="Away &#128276"></form></th>
        <th><form method="post"><input type="hidden" name="brb" value="true"><input type="submit" value="BRB &#128276"></form></th>
      </tr>
      <tr>
        <th><form method="post"><input type="hidden" name="call" value="true"><input type="submit" value="Call &#128274;"></form></th>
        <th><form method="post"><input type="hidden" name="busy" value="true"><input type="submit" value="Busy &#128274;"></form></th>
        <th><form method="post"><input type="hidden" name="dnd" value="true"><input type="submit" value="DND &#128274;"></form></th>
      </tr>
    </table>
    <form method="post"><input type="hidden" name="reset" value="true"><input type="submit" value="Reset &circlearrowleft;"></form>
    <!-- Display current content here -->
    <p>Current Message:</p>
    <p>{current_display_content}</p>
  </div>
</body>
</html>

"""

current_display_content = ipserv  # Initialize current display content

def txtDecode(txt):
    res = ''
    i = 0
    while i < len(txt):
        car = txt[i]
        if car == '+':
            car = ' '
        elif car == '%':
            code = txt[i + 1:i + 3]
            try:
                car = unhexlify(code).decode('utf-8')
            except ValueError:
                car = '?'
            i += 2
        if (car >= ' ') and (car <= '~'):
            res += car
        else:
            res += '?'
        i += 1
    return res

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)

print('Connection with ', addr)

face = bytearray([0x00, 0x00, 0x0A, 0x00, 0x11, 0x0E, 0x00, 0x00])
skull = bytearray([0x00, 0x0E, 0x15, 0x1B, 0x0E, 0x0E, 0x00, 0x00])
walking = bytearray([0x1F, 0x15, 0x1F, 0x1F, 0x0E, 0x0A, 0x1B, 0x00])
lock = bytearray([0x0E, 0x11, 0x11, 0x1F, 0x1B, 0x1B, 0x1F, 0x00])
unlock = bytearray([0x0E, 0x10, 0x10, 0x1F, 0x1B, 0x1B, 0x1F, 0x00])
bell = bytearray([0x04, 0x0E, 0x0E, 0x0E, 0x1F, 0x00, 0x04, 0x00])
speaker = bytearray([0x01, 0x03, 0x07, 0x1F, 0x1F, 0x07, 0x03, 0x01])
robot = bytearray([0x04, 0x04, 0x0E, 0x1F, 0x15, 0x1F, 0x11, 0x1F])
lcd.custom_char(0, face)
lcd.custom_char(1, skull)
lcd.custom_char(2, walking)
lcd.custom_char(3, lock)
lcd.custom_char(4, unlock)
lcd.custom_char(5, bell)
lcd.custom_char(6, speaker)
lcd.custom_char(7, robot)

while True:
    try:
        cl, addr = s.accept()
        print('Client connected from', addr)

        request = cl.recv(1024)
        req = str(request)[2:-1]
        if req[0:5] == 'POST ':
            body_start = req.find('\r\n\r\n') + 4
            body = req[body_start:]
            if "reset=true" in body:
                print("Reset button clicked")
                lcd.clear()
                status = wlan.ifconfig()
                ipserv = status[0]
                lcd.putstr(ipserv + ' ' + chr(7))
                current_display_content = ipserv  # Update current display content
            # Add other conditions to update current_display_content based on actions
            elif "free=true" in body:
                lcd.clear()
                lcd.move_to(0, 0)
                resp="Free"
                lcd.putstr(resp)
                lcd.move_to(0, 1)
                lcd.putstr(chr(0)+chr(0)+chr(0)+chr(0)+chr(4))
                current_display_content = resp+' &#x1F513;'
            elif "away=true" in body:
                lcd.clear()
                lcd.move_to(0, 0)
                resp="Away"
                lcd.putstr(resp)
                lcd.move_to(0, 1)
                lcd.putstr(chr(2)+chr(2)+chr(2)+chr(2)+chr(5))
                current_display_content = resp+' &#128276'
            elif "brb=true" in body:
                lcd.clear()
                lcd.move_to(0, 0)
                resp="Be right back..."
                lcd.putstr(resp)
                lcd.move_to(0, 1)
                lcd.putstr(chr(2)+chr(2)+chr(2)+chr(2)+chr(2)+chr(2)+chr(2)+chr(2)+chr(2)+chr(2)+chr(2)+chr(2)+chr(2)+chr(5))
                current_display_content = resp+' &#128276'
            elif "call=true" in body:
                lcd.clear()
                lcd.move_to(0, 0)
                resp="ON A CALL!"
                lcd.putstr(resp)
                lcd.move_to(0, 1)
                lcd.putstr(chr(1)+chr(1)+chr(1)+chr(1)+chr(1)+chr(1)+chr(1)+chr(1)+chr(1)+chr(1)+chr(3))
                current_display_content = resp+' &#128274;'
            elif "busy=true" in body:
                lcd.clear()
                lcd.move_to(0, 0)
                resp="BUSY!"
                lcd.putstr(resp)
                lcd.move_to(0, 1)
                lcd.putstr(chr(1)+chr(1)+chr(1)+chr(1)+chr(1)+chr(3))
                current_display_content = resp+' &#128274;'
            elif "dnd=true" in body:
                lcd.clear()
                lcd.move_to(0, 0)
                resp="DO NOT DISTURB!"
                lcd.putstr(resp)
                lcd.move_to(0, 1)
                lcd.putstr(chr(1)+chr(1)+chr(1)+chr(1)+chr(1)+chr(1)+chr(1)+chr(1)+chr(1)+chr(1)+chr(1)+chr(1)+chr(1)+chr(1)+chr(1)+chr(3))
                current_display_content = resp+' &#128274;'
            else:
                # Find the start of the message parameter
                param_start = body.find('Message=')
                if param_start != -1:
                    # Extract the message
                    message = body[param_start + len('Message='):]
                    # Decode the message
                    message = message.split('&')[0]
                    message = message.replace('+', ' ')
                    resp = (txtDecode(message) + 16 * ' ')[:16]
                    lcd.clear()
                    lcd.move_to(0, 0)
                    lcd.putstr(resp)
                    current_display_content = resp
                    
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        # Include current_display_content in the HTML response
        cl.send(html.replace("{current_display_content}", current_display_content))
        cl.close()

    except OSError as e:
        cl.close()
