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
lcd.putstr('Connected to WiFi')
 

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
  raise RuntimeError('could not connect !!!')
 
print('Connected with WiFi')
status = wlan.ifconfig()
ipserv = status[0]
print('ip = ' + ipserv)
lcd.clear()
lcd.putstr(ipserv)
 

html = """<!DOCTYPE html>
<html><head>
    <SCRIPT language="JavaScript">
    <!--hide
    var password;
    var pass1="Really_Secure_Password";
    password=prompt('Please enter your password to view this page:','');
    if (password==pass1)
      alert('Password verified, click OK to enter!');
    else
       {
        window.location.reload();
        }
    //-->
    </SCRIPT>
  <title>Smart Notice Board</title>
  <meta name="viewport" content="width=device-width, initial-scale=2">
<p> <font size="7" face="sans-serif"> <center> Smart Notice Board </center> </font> </p>
  </head> <body><center>
            <form method="post">
               <label for="msg">Custom message:</label>
               <input type="text" id="msg" name="Message" placeholder=" Hello world!">
               <input type="submit" value="Send">
            </form>
            <p></p>

          <table>
              <tr>
                  <th>
                      <form method="post">
                          <input type="hidden" id="msg" name="Message" value=" Free">
                          <input type="submit" value="Free">
                      </form>
                  </th>
                  <th>
                      <form method="post">
                          <input type="hidden" id="msg" name="Message" value=" Away">
                          <input type="submit" value="Away">
                      </form>
                  </th>
                  <th>
                      <form method="post">
                          <input type="hidden" id="msg" name="Message" value=" Be right back">
                          <input type="submit" value="BRB">
                      </form>
                  </th>
              </tr>
              <tr>
                  <th>
                      <form method="post">
                          <input type="hidden" id="msg" name="Message" value=" ON A CALL!">
                          <input type="submit" value="Call">
                      </form>
                  </th>
                  <th>
                      <form method="post">
                          <input type="hidden" id="msg" name="Message" value=" BUSY!">
                          <input type="submit" value="Busy">
                      </form>
                  </th>
                  <th>
                      <form method="post">
                          <input type="hidden" id="msg" name="Message" value=" DO NOT DISTURB!">
                          <input type="submit" value="DND">
                      </form>
                  </th>
              </tr>
          </table>

            <p></p>
            <form method="post">
               <input type="hidden" id="msg" name="Message" value=" ">
               <input type="submit" value="Reset">
            </form>

            
        </center>
        </body>
        </html>
    
"""

def txtDecode(txt):
    res = ''
    i = 0
    while i < len(txt):
        car = txt[i]
        if car == '+':
            car = ' '
        elif car == '%':
            code = unhexlify(txt[i+1:i+3])
            if (code[0] >= 32) and (code[0] < 127):
                car = str(code)[2:-1]
            else:
                car = '?'
            i = i + 2
        if (car >= ' ') and (car <= '~'):
            res = res + car
            i = i + 1
        else:
            res = res + '?'
            i = i + 1
    return res

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)
  
print('Connection with ', addr)
 

while True:
    try:
        cl, addr = s.accept()
        print('client connected from', addr)
 
        request = cl.recv(1024)
        req = str(request)[2:-1]
        if req[0:5] == 'POST ':
          
            pos = req.find('Message')
            if pos != -1:
                resp = (txtDecode(req[pos+9:]) + 16*' ')[0:16]
                lcd.move_to(0,1)
                lcd.putstr(resp)
         
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(html)
        cl.close()

  
    except OSError as e:
        cl.close()
