import supervisor
import storage
import usb_hid

# Set Manufacturer / Product / VID / PID
supervisor.set_usb_identification(manufacturer='CJ', product='CJs Macro Pad', vid=0xC107, pid=0x1316)
# Disable CIRCUITPY / appearing as USB drive
storage.disable_usb_drive()  
# Set interface name for the gamepad
usb_hid.set_interface_name("CJs Macro Pad")
