#!/usr/bin/python
from PIL import Image
import cv2
import time
import sliplib
import serial

import numpy as np

import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("media_file", type=str, help="The media file to play")

parser.add_argument("--resize", default=None, help="Resize image to dimensions eg. 32x32")
parser.add_argument("--output", default="oled_mono", choices=["oled_mono", "oled_rgb24"], help="Output type")
parser.add_argument("--serial-port", default="/dev/ttyUSB0", help="The serial port")
parser.add_argument("--serial-baud", type=int, default=9600, help="The serial baudrate")
parser.add_argument("--fps", type=int, default=1, help="Frames per second")

args = parser.parse_args()

ser = serial.Serial(args.serial_port, args.serial_baud) # Establish the connection on a specific port
driver = sliplib.Driver()

def set_bit(value, bit):
    return value | (1<<bit)

def clear_bit(value, bit):
    return value & ~(1<<bit)

def send_image_oled_mono(image):
    # Gather basic information.
    size = image.size
    n_pixels = size[0] * size[1]

    image_array = bytearray()
    image_array.append(size[0])
    image_array.append(size[1])

    # Pack all pixels into bytes.
    image = np.array(image).flatten()
    for i in range(0, n_pixels, 8):
        block = 0
        for j in range(8):
            if (image[i+j]):
                block = set_bit(block, j)
            else:
                block = clear_bit(block, j)
        image_array.append(block)

    # Send bytes to serial using SLIP protocol.
    encoded = driver.send(image_array)
    ser.write(encoded)
    ser.flush()
    # print(ser.readline())
    msg = ser.read_until(b'\xc0')
    msg = ser.read_until(b'\xc0')
    result = driver.receive(msg)
    print(".")
#    print([x for x in result])

media = cv2.VideoCapture(args.media_file)

if media.isOpened():
    rval , frame = media.read()
else:
    rval = False

frame_interval = 1.0/args.fps

# Read video frame by frame
while rval:
    # Read frame.
    rval, frame = media.read()
    if rval:
        # Convert and resize image to appropriate format.
        image = Image.fromarray(frame)
        size = image.size
        if (args.resize != None):
            size = map(int, args.resize.split('x'))
            image = image.resize(size, resample=Image.ANTIALIAS)
        # Send image to external device.
        if args.output == "oled_mono":
            image = image.convert('1')
            send_image_oled_mono(image)
        else:
            image = image.convert('RGB')
            exit("Not supported for now")
    time.sleep(frame_interval)
media.release()
    #
    # filename = "RgbMatrixDrawingTool/matrix.png"
    #
    # grayscale = True
    # #size = (32, 32)
    # #size = (112, 112)
    # size = (128, 128)
    #
    # # Bitmap example w/graphics prims
    # image = Image.open(filename)
    # image.load()
    # image = image.resize(size, resample=Image.ANTIALIAS)
    # image = image.resize(size, resample=Image.ANTIALIAS)
    #
    # print("#define IMAGE_WIDTH {}".format(image.size[0]))
    # print("#define IMAGE_HEIGHT {}".format(image.size[1]))
    # if grayscale:
    #     print("static const uint8_t U8X8_PROGMEM IMAGE[] = {")
    #     image = image.convert('1')
    #     for y in range(0,image.size[1]):
    #         print("  ", end="")
    #         for x in range(0, image.size[0], 8):
    #             color = 0
    #             for k in range(8):
    #                 if (image.getpixel((x+k, y)) > 0):
    #                     color = set_bit(color, k)
    #                 else:
    #                     color = clear_bit(color, k)
    #             print(hex(color), end=", ")
    #         print()
    #     print("};")
    # else:
    #     print("const int16_t PROGMEM IMAGE[] = {")
    #     for y in range(0,image.size[1]):
    #         print("  ", end="")
    #         for x in range(0,image.size[0]):
    #             r, g, b, a = image.getpixel((x, y))
    #             r = int(r / 8)
    #             g = int(g / 4)
    #             b = int(b / 8)
    #             color = 2048*r + 32*g + b
    #             color = 65535 - color
    #             print(hex(color), end=", ")
    #         print()
    #     print("};")
