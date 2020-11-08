# Gigabyte AORUS LIQUID COOLER 240
The AORUS Liquid cooler is connected to the mainboard via USB 2.0 header.
The Pump and CPU-Block combo also features a round display.
It is capable of controlling 2 LED Fans both in speed using PWM and in light effects using a standard similar to Neopixel/WS2812 LEDs.
Testing revealed, that the display is capable to display 305*x*305px BMP-Images with a 24-Bit color spectrum.
It also can display animations, text, CPU-clock and temperature, but these are not user defineable, only custoizable in color.
The Image upload tool under Windows doesn't apply any sanity checks or conversions that would ensure, that the image is displayed correctly.

* [Gigabyte Website](https://www.gigabyte.com/Thermal-Solution/AORUS-LIQUID-COOLER-240)
* [Gigabyte RGB Fusion SDK](https://www.gigabyte.com/mb/rgb/sdk)

## Information gathered on Linux

### lsusb output
```    
Bus 005 Device 003: ID 04d9:a231 Holtek Semiconductor, Inc. USB2.1 Hub
Device Descriptor:
  bLength                18
  bDescriptorType         1
  bcdUSB               1.10
  bDeviceClass            0 
  bDeviceSubClass         0 
  bDeviceProtocol         0 
  bMaxPacketSize0        64
  idVendor           0x04d9 Holtek Semiconductor, Inc.
  idProduct          0xa231 
  bcdDevice            1.01
  iManufacturer           1 HOLTEK
  iProduct                2 USB-HID Keyboard
  iSerial                 0 
  bNumConfigurations      1
  Configuration Descriptor:
    bLength                 9
    bDescriptorType         2
    wTotalLength       0x007b
    bNumInterfaces          4
    bConfigurationValue     1
    iConfiguration          0 
    bmAttributes         0xa0
      (Bus Powered)
      Remote Wakeup
    MaxPower              500mA
    Interface Descriptor:
      bLength                 9
      bDescriptorType         4
      bInterfaceNumber        0
      bAlternateSetting       0
      bNumEndpoints           1
      bInterfaceClass         3 Human Interface Device
      bInterfaceSubClass      1 Boot Interface Subclass
      bInterfaceProtocol      1 Keyboard
      iInterface              0 
        HID Device Descriptor:
          bLength                 9
          bDescriptorType        33
          bcdHID               1.11
          bCountryCode            0 Not supported
          bNumDescriptors         1
          bDescriptorType        34 Report
          wDescriptorLength      59
         Report Descriptors: 
           ** UNAVAILABLE **
      Endpoint Descriptor:
        bLength                 7
        bDescriptorType         5
        bEndpointAddress     0x81  EP 1 IN
        bmAttributes            3
          Transfer Type            Interrupt
          Synch Type               None
          Usage Type               Data
        wMaxPacketSize     0x0008  1x 8 bytes
        bInterval               1
    Interface Descriptor:
      bLength                 9
      bDescriptorType         4
      bInterfaceNumber        1
      bAlternateSetting       0
      bNumEndpoints           2
      bInterfaceClass         3 Human Interface Device
      bInterfaceSubClass      0 
      bInterfaceProtocol      0 
      iInterface              0 
        HID Device Descriptor:
          bLength                 9
          bDescriptorType        33
          bcdHID               1.11
          bCountryCode            0 Not supported
          bNumDescriptors         1
          bDescriptorType        34 Report
          wDescriptorLength      34
         Report Descriptors: 
           ** UNAVAILABLE **
      Endpoint Descriptor:
        bLength                 7
        bDescriptorType         5
        bEndpointAddress     0x83  EP 3 IN
        bmAttributes            3
          Transfer Type            Interrupt
          Synch Type               None
          Usage Type               Data
        wMaxPacketSize     0x0040  1x 64 bytes
        bInterval               1
      Endpoint Descriptor:
        bLength                 7
        bDescriptorType         5
        bEndpointAddress     0x04  EP 4 OUT
        bmAttributes            3
          Transfer Type            Interrupt
          Synch Type               None
          Usage Type               Data
        wMaxPacketSize     0x0040  1x 64 bytes
        bInterval               1
    Interface Descriptor:
      bLength                 9
      bDescriptorType         4
      bInterfaceNumber        2
      bAlternateSetting       0
      bNumEndpoints           1
      bInterfaceClass         3 Human Interface Device
      bInterfaceSubClass      0 
      bInterfaceProtocol      0 
      iInterface              0 
        HID Device Descriptor:
          bLength                 9
          bDescriptorType        33
          bcdHID               1.11
          bCountryCode            0 Not supported
          bNumDescriptors         1
          bDescriptorType        34 Report
          wDescriptorLength     181
         Report Descriptors: 
           ** UNAVAILABLE **
      Endpoint Descriptor:
        bLength                 7
        bDescriptorType         5
        bEndpointAddress     0x82  EP 2 IN
        bmAttributes            3
          Transfer Type            Interrupt
          Synch Type               None
          Usage Type               Data
        wMaxPacketSize     0x0040  1x 64 bytes
        bInterval               1
    Interface Descriptor:
      bLength                 9
      bDescriptorType         4
      bInterfaceNumber        3
      bAlternateSetting       0
      bNumEndpoints           2
      bInterfaceClass         3 Human Interface Device
      bInterfaceSubClass      0 
      bInterfaceProtocol      0 
      iInterface              0 
        HID Device Descriptor:
          bLength                 9
          bDescriptorType        33
          bcdHID               1.11
          bCountryCode            0 Not supported
          bNumDescriptors         1
          bDescriptorType        34 Report
          wDescriptorLength      31
         Report Descriptors: 
           ** UNAVAILABLE **
      Endpoint Descriptor:
        bLength                 7
        bDescriptorType         5
        bEndpointAddress     0x85  EP 5 IN
        bmAttributes            3
          Transfer Type            Interrupt
          Synch Type               None
          Usage Type               Data
        wMaxPacketSize     0x0040  1x 64 bytes
        bInterval               1
      Endpoint Descriptor:
        bLength                 7
        bDescriptorType         5
        bEndpointAddress     0x06  EP 6 OUT
        bmAttributes            3
          Transfer Type            Interrupt
          Synch Type               None
          Usage Type               Data
        wMaxPacketSize     0x0040  1x 64 bytes
        bInterval               1
can't get debug descriptor: Resource temporarily unavailable
Device Status:     0x0000
  (Bus Powered)
```

## Information gathered on Windows
There are 2 Tools for controlling this Cooler and Fans:
* AORUS ENGINE
* RGB Fusion

Both tools feature functions and settings, that are exclusive to one. Which function is available in which program doesn't follow any logic.

The tools don't work in VirtualBox and prevent the virtual machine from booting. If you want to try to virtualize them and use USB-passthroug, make a backup before installation.

[USBpacp](https://desowin.org/usbpcap/) and [Wireshark](https://www.wireshark.org/) were used under Windows to for capture.

### USBpacpCMD.exe
```
1 \\.\USBPcap1
    \??\USB#ROOT_HUB30#5&34fc1d06&0&0#{f18a0e88-c30c-11d0-8815-00a0c906bed8}
        [Port 13] USB Composite Device
            USB Mass Storage Device
                HOLTEK LCD_PLATFORM USB Device
            USB Input Device
                HID-compliant vendor-defined device
```

### Wireshark capture (using USBpcap)

I played around with both programs on Windows while using Wireshark to capture USB packets.
See the `.pcapng` file.

Here is a rough list of what I did at which package numbers:

* Using "AORUS ENGINE":
  * upload image till about 9000
  * Rotation of Display:
    * Recpmpiling? till about 17000
    * "Erasing" till about 18600
    * "Downloading Image" till about 20100
    * "Verifying Image" till about 22200 ?
  * changed fan speed multiple times thill 26000
  * changed pump speed till 28000

* Using RGBFusion 2.0:
  * changed display modes till 31800

* Using Aorus ENGINE again:
  * changed Display Data and Display Modes (RGBFusion) till 35500

* Using RGBFusion 2.0:
  * played around with Fan LED settings till 41000