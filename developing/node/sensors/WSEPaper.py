#!/usr/bin/env python
# -*- coding: utf-8 -*-
# All datas defined in json configuration are atributes in your code object

from node.libs import control
import Pyro4
import EPDDriver
import time
import cStringIO as IO
import spidev as SPI
from PIL import ImageFont, ImageDraw, Image
# 3V3
# GND
# DIN  -> MOSI
# CLK  -> SCLK
# CS   -> CE0
# DC   -> 25
# RST  -> 17
# BUSY -> 24
@Pyro4.expose
class WSEPaper(control.Control):
    @control.load_config
    def __init__(self, data, **kwargs):
        self.EPD_WIDTH = self.width
        self.EPD_HEIGHT = self.height
        #self.gpioservice.setup(
        #    [self.CS, self.DC, self.RST, self.DIN, self.CLK], GPIO.OUT,
        #    self.pyro4id)
        #self.gpioservice.setup(
        #    [self.BUSY], GPIO.IN, self, pyro4id)
        self.disp = EPDDriver.EPDDriver(spi=SPI.SpiDev(self.bus, self.device),x_dot=self.width,y_dot=self.height)
        #self.canvas is a screen buffer
        self.canvas = Image.new("1", (self.width, self.height))
        self.clear()
        self.disp.delay()
        self.disp.EPD_init_Part()
        self.disp.delay()
        self.font_size = 40
        self.font_link ="/usr/share/fonts/truetype/freefont/FreeMono.ttf"
        self.font = ImageFont.truetype(self.font_link, size=self.font_size)
        self.buffer = []
        self.init_workers(self.worker)

    def worker(self):
        while True:
            if len(self.buffer) > 0:
                self.print_image(self.buffer.pop())
            else:
                time.sleep(0.1)

    @Pyro4.expose
    def set_image(self, im):
        self.buffer.append(im)

    @Pyro4.expose
    def clear(self, x_start=0, x_end=0, y_start=0, y_end=0):
        if (x_start, x_end, y_start, y_end) == (0, 0, 0, 0):
            self.disp.Dis_Clear_full()
        else:
            self.disp.Dis_Clear_part(x_start, x_end, y_start, y_end)

    def transform_image(self, data, size_x=None, size_y=None):
        def center_image(im, size_x, size_y):
            width, height = im.size   # Get dimensions
            left = (width - size_x)/2
            top = (height - size_x)/2
            right = (width + size_y)/2
            bottom = (height + size_y)/2
            return im.crop((left, top, right, bottom))

        if None in [size_x, size_y]:
            size_x = self.EPD_WIDTH
            size_y = self.EPD_HEIGHT
        img = IO.StringIO(data)
        im = Image.open(img)
        im.thumbnail((size_x, size_y))
        im = center_image(im, size_x, size_y)
        return im.convert("1")

    def print_image(self, img, pos_x=0, pos_y=0):
        self.canvas.paste(self.transform_image(img),
                          (pos_x, pos_y))
        im = self.canvas.transpose(Image.ROTATE_90)
        listim = list(im.getdata())
        listim2 = []
        for y in range(0, im.size[1]):
            for x in range(0, im.size[0] / 8):
                val = 0
                for x8 in range(0, 8):
                    if listim[(im.size[1]-y-1)*im.size[0] + x*8 + (7-x8)] > 128:
                        val = val | 0x01 << x8
                listim2.append(val)
        listim2.extend([0] * 1000)
        self.disp.EPD_Dis_Part(pos_x, pos_x+im.size[0]-1, pos_y, pos_y+im.size[1]-1, listim2) # xStart, xEnd, yStart, yEnd, DisBuffer

    @staticmethod
    def get_size(text, font):
        test_img = Image.new('RGB', (1, 1))
        test_draw = ImageDraw.Draw(test_img)
        return test_draw.textsize(text, font)

    def set_text(self, text, font=0):
        if font not in [0, self.font_size]:
            self.font = ImageFont.truetype(self.font_link, font)
        img = Image.new('RGB', (200, 200), (255, 255, 255))
        d = ImageDraw.Draw(img)
        d.text((20, 20), text, fill=(255, 0, 0),font=self.font)
        img.save("image.jpg")
        self.set_image(open("image.jpg").read())
