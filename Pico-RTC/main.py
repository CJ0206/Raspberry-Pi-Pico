from machine import I2C, Pin
from pico_i2c_lcd import I2cLcd
import network
import secrets
import time
import struct
import socket
import machine

from secrets import WIFI_SSID, WIFI_PASSWORD

# Constants
NTP_DELTA = 2208988800
ntp_host = ["0.uk.pool.ntp.org", "1.uk.pool.ntp.org", "2.uk.pool.ntp.org", "3.uk.pool.ntp.org"]

# Define time tuple indices
tm_year = 0
tm_mon = 1
tm_mday = 2
tm_hour = 3
tm_min = 4
tm_sec = 5
tm_wday = 6
tm_yday = 7
tm_isdst = 8

# Initialize I2C and LCD
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
I2C_ADDR = i2c.scan()[0]
lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)

def format_time(t):
    # Format time tuple into a string
    return "{:04}-{:02}-{:02} {:02}:{:02}:{:02}".format(t[0], t[1], t[2], t[3], t[4], t[5])

def uk_time():
    now = time.time()  # Get current time in seconds since epoch
    year = time.localtime(now)[0]  # Get current year

    # Calculate the timestamps for the last Sunday in March and October
    HHMarch = time.mktime((year, 3, (31 - (int(5 * year / 4 + 4)) % 7), 1, 0, 0, 0, 0, 0))  # Last Sunday in March
    HHOctober = time.mktime((year, 10, (31 - (int(5 * year / 4 + 1)) % 7), 1, 0, 0, 0, 0, 0))  # Last Sunday in October

    # Determine if the current time is in BST or GMT
    if HHMarch <= now < HHOctober:
        # We are in BST (UTC+1)
        return time.localtime(now + 3600)  # Add 1 hour to convert from UTC to BST
    else:
        # We are in GMT (UTC+0)
        return time.localtime(now)  # No adjustment needed

def q_set_time():
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    time_is_set = False
    for host in ntp_host:
        addr = socket.getaddrinfo(host, 123)[0][-1]
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.settimeout(1)
                s.sendto(NTP_QUERY, addr)
                msg = s.recv(48)
            finally:
                s.close()
            val = struct.unpack("!I", msg[40:44])[0]
            t = val - NTP_DELTA
            tm = time.gmtime(t)
            print(f"UTC Time from NTP: {format_time(tm)}")
            # Set RTC time directly to UTC from NTP
            machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))
            time_is_set = True
        except OSError as exc:
            if exc.args[0] == 110:  # ETIMEDOUT
                print(f"ETIMEDOUT for the host {host}.")
                time_is_set = False
        if time_is_set:
            break
    if time_is_set:
        # Fetch time again after synchronization
        utc_time = time.localtime()
        print("UTC time after synchronization:", format_time(utc_time))
        t = uk_time()
        print("UK time after synchronization:", format_time(t))
        # Update RTC with correct UK time
        machine.RTC().datetime((t[tm_year], t[tm_mon], t[tm_mday], t[tm_wday] + 1, t[tm_hour], t[tm_min], t[tm_sec], 0))
        print("Local time after synchronization:", format_time(time.localtime()))
        print("NTP sync successful.")
        return True
    else:
        print("Could not sync time...")
        return False

def req_attention():
    for i in range(5):
        lcd.backlight_off()
        time.sleep(0.2)
        lcd.backlight_on()
        time.sleep(0.4)

# Initialize display
lcd.blink_cursor_on()
lcd.backlight_on()
lcd.clear()

# WiFi and synchronization settings
max_wait = 10
wifi_reconnect_time = 5
wifi_wait_time = 5

while True:
    wifi_connected = False
    lcd.blink_cursor_on()
    lcd.show_cursor()
    lcd.putstr("Connecting to Wifi...")
    
    # Connect to WiFi
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    time.sleep(wifi_wait_time)
    
    lcd.clear()
    lcd.putstr("Wifi connection:\n")
    wifi_connected = wlan.isconnected()
    lcd.putstr("Success\n" if wifi_connected else "Fail\n")
    
    if wifi_connected:
        lcd.clear()
        lcd.putstr("NTP sync...\n")
        
        while max_wait > 0:
            if wlan.status() < 0 or wlan.status() >= 3:
                break
            max_wait -= 1
            time.sleep(1)
        
        if wlan.status() != 3:
            lcd.clear()
            lcd.putstr("WiFi error.\n")
            lcd.putstr("Reconnect in " + str(wifi_reconnect_time) + "s")
            req_attention()
            wlan.active(False)
            time.sleep(wifi_reconnect_time)
            continue
        else:
            lcd.clear()
            lcd.putstr("Syncing time...\n")
            try:
                time_set_status = q_set_time()
                if time_set_status:
                    lcd.clear()
                    lcd.putstr("Synced.\n")
                    print("Sync really successful.")
                else:
                    raise Exception("Sync error.")
            except Exception as e:
                print("Sync exception!")
                print("Error message: " + str(e))
                lcd.clear()
                lcd.putstr("Sync error.\n")
                req_attention()
                wlan.active(False)
                time.sleep(wifi_reconnect_time)
                continue
        
        lcd.blink_cursor_off()
        lcd.hide_cursor()
        last_date = ""
        while True:
            # Display date and time
            t = time.localtime()  # Fetch current local time from RTC
            new_date = "{:02}/{:02}/{}".format(t[tm_mday], t[tm_mon], t[tm_year])
            if new_date != last_date:
                lcd.move_to(0, 0)
                lcd.putstr(new_date)
                last_date = new_date
            lcd.move_to(0, 1)
            lcd.putstr("{:02}:{:02}:{:02}".format(t[tm_hour], t[tm_min], t[tm_sec]))
            time.sleep(1)
    # Wait until next WiFi connect iteration
    wlan.active(False)
    time.sleep(wifi_reconnect_time)
