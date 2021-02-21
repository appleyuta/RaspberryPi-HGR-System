import platform
import serial
from serial.tools import list_ports

pf = platform.system()
ir_serial = None

if pf == "Windows":
    print("on Windows")
    """import win32com.client
    wmi = win32com.client.GetObject("winmgmts:")
    for usb in wmi.InstancesOf("Win32_SerialPort"):
        print(usb.DeviceID)
        print(usb.Name)
        try:
            ir_serial = serial.Serial(usb.DeviceID, 9600, timeout = 10)
        except Exception as e:
            print(e)"""
elif pf == "Darwin":
    print("on Mac")
    ir_serial = serial.Serial()
    ir_serial.baudrate = 9600
    devices = list_ports.comports()
    for device in devices:
        print(device[1])
        print("irM" in device[1])
        if "irM" in device[1]:
            ir_serial.port = device[0]
    try:
        ir_serial.open()
    except Exception as e:
        ir_serial = None
        print(e)
elif pf == "Linux":
    print("on Linux")
    ir_serial = serial.Serial()
    ir_serial.baudrate = 9600
    devices = list_ports.comports()
    for device in devices:
        print(device[1])
        print("irM" in device[1])
        if "irM" in device[1]:
            ir_serial.port = device[0]
    try:
        ir_serial.open()
    except Exception as e:
        ir_serial = None
        print(e)

print(ir_serial)