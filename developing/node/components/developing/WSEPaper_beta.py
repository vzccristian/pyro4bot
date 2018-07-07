import spidev
from node.libs.gpio.GPIO import *
import time
import Pyro4
import cStringIO as IO
from PIL import ImageFont, ImageDraw, Image



""" BCM GPIO """
RST = 17
DC = 25
BUSY = 24
CS = 8

class EPDDriver:
        """Control WSEPaper display [200x200] through GPIO."""
        __REQUIRED = ["gpioservice"]

    def __init__(self, spi, x_dot, y_dot):
        # Initialize DC RST pin
        if not self.RST:
            self.RST = RST
        if not self.DC:
            self.DC = DC:
        if not self.BUSY:
            self.BUSY = BUSY
        if not self.CS:
            self.CS = CS
        self.GPIO = GPIOCLS(self.gpioservice, self.pyro4id)
        #TODO hay que poner los pines que usa la pantalla ()
        self.GPIO.setup([self.RST, self.DC, self.CS], OUT)
        self.GPIO.setup([self.BUSY], IN)
        self.GPIO.setmode(GPIO.BCM)

        # Initialize SPI
        self.spi = spi
        self.spi.max_speed_hz = 4000000  # Spec says 250ns SPI clock cycle
        self.spi.mode = 0b00

        self.x_dot = x_dot
	self.y_dot = y_dot

	# Register initial variable
        if (x_dot, y_dot) == (200, 200):
            self.type = 'EPD1X54'
            self.DELAYTIME = 1.5
            self.LUTDefault_full = [0x32, 0x02, 0x02, 0x01, 0x11, 0x12, 0x12,
                                    0x22, 0x22, 0x66, 0x69, 0x69, 0x59, 0x58,
                                    0x99, 0x99, 0x88, 0x00, 0x00, 0x00, 0x00,
                                    0xF8, 0xB4, 0x13, 0x51, 0x35, 0x51, 0x51,
                                    0x19, 0x01, 0x00]
            self.LUTDefault_part = [0x32, 0x10, 0x18, 0x18, 0x08, 0x18, 0x18,
                                    0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                    0x13, 0x14, 0x44, 0x12, 0x00, 0x00, 0x00,
                                    0x00, 0x00, 0x00]
        elif (x_dot, y_dot) == (128, 296):
            self.type = 'EPD2X9'
            self.DELAYTIME = 1.5
            self.LUTDefault_full = [0x32, 0x02, 0x02, 0x01, 0x11, 0x12, 0x12,
                                    0x22, 0x22, 0x66, 0x69, 0x69, 0x59, 0x58,
                                    0x99, 0x99, 0x88, 0x00, 0x00, 0x00, 0x00,
                                    0xF8, 0xB4, 0x13, 0x51, 0x35, 0x51, 0x51,
                                    0x19, 0x01, 0x00]
            self.LUTDefault_part = [0x32, 0x10, 0x18, 0x18, 0x08, 0x18, 0x18,
                                    0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                    0x13, 0x14, 0x44, 0x12, 0x00, 0x00, 0x00,
                                    0x00, 0x00, 0x00]
        elif (x_dot, y_dot) == (122, 250):
            self.type = 'EPD02X13'
            self.DELAYTIME = 4
            self.LUTDefault_full = [0x32, 0x22, 0x55, 0xAA, 0x55, 0xAA, 0x55,
                                    0xAA, 0x11, 0x00, 0x00, 0x00, 0x00, 0x00,
                                    0x00, 0x00, 0x00, 0x1E, 0x1E, 0x1E, 0x1E,
                                    0x1E, 0x1E, 0x1E, 0x1E, 0x01, 0x00, 0x00,
                                    0x00, 0x00]
            self.LUTDefault_part = [0x32, 0x18, 0x00, 0x00, 0x00, 0x00, 0x00,
                                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                    0x00, 0x00, 0x00, 0x0F, 0x01, 0x00, 0x00,
                                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                    0x00, 0x00]

        self.w_buffer = [0 for i in range(5000)]
        self.EPD_Init()
    """ Waits until BUSY == 0"""
    def ReadBusy(self):
        for i in range(0, 400):
            if self.GPIO.input(self.BUSY) == 0:
                return 1
            time.sleep(0.01)

    """Writes the command in spi"""
    def EPD_WriteCMD(self, command):
        self.GPIO.output(self.DC, GPIO.LOW)
        self.spi.writebytes([command])

    def EPD_WriteCMD_p1(self, command, para):
        self.ReadBusy()
        self.GPIO.output(self.DC, GPIO.LOW)
        self.spi.writebytes([command])
        GPIO.output(self.DC, GPIO.HIGH)
        self.spi.writebytes([para])

    def EPD_POWERON(self):
        self.EPD_WriteCMD_p1(0x22, 0xc0)
        self.EPD_WriteCMD(0x20)
        self.ReadBusy()

    def EPD_Write(self, value):
        """Send command byte to display"""
        self.GPIO.output(self.DC, LOW)
        time.sleep(0.01)
        #print 'send command : ' ,hex(value[0])
        # The first byte is written with the command value
        self.spi.writebytes([value[0]])
        GPIO.output(self.DC, HIGH)
        for i in range(0, len(value) - 1):
            data = value[i + 1]
            self.spi.writebytes([data])

    # checks dispdata list->data from list is copied, value->value is copied size times
    def EPD_WriteDispRam(self, XSize, YSize, dispdata):
        if XSize % 8 != 0:
            XSize = XSize + (8 - XSize % 8)
        XSize = XSize / 8
        NUM = 0
        self.ReadBusy()
        self.GPIO.output(self.DC, GPIO.LOW)
        self.spi.writebytes([0x24])
        self.GPIO.output(self.DC, GPIO.HIGH)
        if isinstance(dispdata, list):
            for i in range(0, YSize):
                for j in range(0, XSize):
                    self.spi.writebytes([dispdata[NUM]])
                    NUM += 1
        else:
            for i in range(0, YSize):
                for j in range(0, XSize):
                    self.spi.writebytes([dispdata])

    def EPD_SetRamArea(self, Xstart, Xend, Ystart, Ystart1, Yend, Yend1):
        RamAreaX = [0x44, Xstart, Xend]
        RamAreaY = [0x45, Ystart, Ystart1, Yend, Yend1]
        self.EPD_Write(RamAreaX)
        self.EPD_Write(RamAreaY)

    def EPD_SetRamPointer(self, addrX, addrY, addrY1):
        RamPointerX = [0x4e, addrX]
        RamPointerY = [0x4f, addrY, addrY1]
        self.EPD_Write(RamPointerX)
        self.EPD_Write(RamPointerY)

    def part_display(self, RAM_XST, RAM_XEND, RAM_YST, RAM_YST1, RAM_YEND, RAM_YEND1):
        self.EPD_SetRamArea(RAM_XST, RAM_XEND, RAM_YST,
                            RAM_YST1, RAM_YEND, RAM_YEND1)
        self.EPD_SetRamPointer(RAM_XST, RAM_YST, RAM_YST1)

    def EPD_Init(self):
        # print 'EPD_Init'
        """Initialize display"""
        """2. reset driver"""
        self.GPIO.output(self.CS, LOW)
        self.GPIO.output(self.RST, HIGH)
        time.sleep(0.1)
        self.GPIO.output(self.RST, LOW)
        time.sleep(0.01)
        self.GPIO.output(self.RST, GPIO.HIGH)
        """3. set register"""
        self.EPD_Write([0x01, (self.y_dot - 1) % 256, (self.y_dot - 1) /
                        256, 0x00])  # Pannel configuration, Gate selection
        self.EPD_Write([0x0c, 0xd7, 0xd6, 0x9d])  # soft start
        self.EPD_Write([0x2c, 0xa8])           # VCOM setting
        self.EPD_Write([0x3a, 0x1a])           # dummy line per gate
        self.EPD_Write([0x3b, 0x08])           # Gage time setting
        # data entry X increase, Y decrease
        self.EPD_Write([0x11, 0x01])
        self.EPD_SetRamArea(0x00, (self.x_dot - 1) / 8, (self.y_dot - 1) %
                            256, (self.y_dot - 1) / 256, 0x00, 0x00)  # X-source area,Y-gage area
        self.EPD_SetRamPointer(0x00, (self.y_dot - 1) %
                               256, (self.y_dot - 1) / 256)  # set ram

    def EPD_Update(self):
        self.EPD_WriteCMD_p1(0x22, 0xc7)
        self.EPD_WriteCMD(0x20)
        self.EPD_WriteCMD(0xff)

    def EPD_Update_Part(self):
        self.EPD_WriteCMD_p1(0x22, 0x04)
        self.EPD_WriteCMD(0x20)
        self.EPD_WriteCMD(0xff)

    def EPD_init_Full(self):
        # self.EPD_Init()
        self.EPD_Write(self.LUTDefault_full)
        self.EPD_POWERON()

    def EPD_init_Part(self):
        # self.EPD_Init()
        self.EPD_Write(self.LUTDefault_part)
        self.EPD_POWERON()

    def EPD_Dis_Full(self, DisBuffer):
        self.ReadBusy()
        self.EPD_SetRamPointer(0x00, (self.y_dot - 1) %
                               256, (self.y_dot - 1) / 256)
        self.EPD_WriteDispRam(self.x_dot, self.y_dot, DisBuffer)
        self.EPD_Update()

    def EPD_Dis_Part(self, xStart, xEnd, yStart, yEnd, DisBuffer):
        if(xStart % 8 != 0):
            print 'EPD_Dis_Part xStart must be divable by 8 !'
        self.ReadBusy()
        self.part_display(xStart / 8, xEnd / 8, yEnd %
                          256, yEnd / 256, yStart % 256, yStart / 256)
        self.EPD_WriteDispRam(xEnd - xStart, yEnd - yStart + 1, DisBuffer)
        self.EPD_Update_Part()

    def Dis_Clear_full(self):
        self.ReadBusy()
        self.EPD_init_Full()
        self.delay()
        self.ReadBusy()
        self.EPD_Dis_Full(0xff)
        self.delay()

    def Dis_Clear_part(self, xStart, xEnd, yStart, yEnd):
        self.ReadBusy()
        self.EPD_init_Part()
        self.ReadBusy()
        self.EPD_Dis_Part(xStart, xEnd, yStart, yEnd, 0xaa)

    def Dis_full_pic(self, DisBuffer):
        self.EPD_Dis_Full(DisBuffer)
        self.delay()

    def Dis_part_pic(self, xStart, xEnd, yStart, yEnd, DisBuffer):
        self.EPD_Dis_Part(xStart, xEnd, yStart, yEnd, DisBuffer)
        self.delay()

    def delay(self):
        time.sleep(self.DELAYTIME)


"""WSEPaper Controller. It's an interface for this driver."""
@Pyro4.expose
class WSEPaperController(control.Control):
    __REQUIRED = ["bus", "device", "width", "height"]

    def __init__(self):
        self.EPD_WIDTH = self.width
        self.EPD_HEIGHT = self.height
        self.disp = EPDDriver.EPDDriver(spi=Spidev.SpiDev(
            self.bus, self.device), x_dot=self.width, y_dot=self.height)

        # self.canvas is a screen buffer
        self.canvas = Image.new("1", (self.width, self.height))
        self.clear()
        self.disp.delay()
        self.disp.EPD_init_Part()
        self.disp.delay()
        self.font_size = 40
        self.font_link = "/usr/share/fonts/truetype/freefont/FreeMono.ttf"
        self.font = ImageFont.truetype(self.font_link, size=self.font_size)
        self.buffer = []
        self.init_panel()
        self.start_worker(self.worker)
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
            left = (width - size_x) / 2
            top = (height - size_x) / 2
            right = (width + size_y) / 2
            bottom = (height + size_y) / 2
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
                    if listim[(im.size[1] - y - 1) * im.size[0] + x * 8 + (7 - x8)] > 128:
                        val = val | 0x01 << x8
                listim2.append(val)
        listim2.extend([0] * 1000)
        # xStart, xEnd, yStart, yEnd, DisBuffer
        self.disp.EPD_Dis_Part(
            pos_x, pos_x + im.size[0] - 1, pos_y, pos_y + im.size[1] - 1, listim2)

    @staticmethod
    def get_size(text, font):
        test_img = Image.new('RGB', (1, 1))
        test_draw = ImageDraw.Draw(test_img)
        return test_draw.textsize(text, font)

    @Pyro4.expose
    def set_text(self, text, font=0):
        if font not in [0, self.font_size]:
            self.font = ImageFont.truetype(self.font_link, font)
        img = Image.new('RGB', (200, 200), (255, 255, 255))
        d = ImageDraw.Draw(img)
        d.text((20, 20), text, fill=(255, 0, 0), font=self.font)
        img.save("image.jpg")
        self.set_image(open("image.jpg").read())

    def init_panel(self):
        self.first_val = '0'
        self.list_val = []

    def set_first(self, val):
        self.first_val = val

    @Pyro4.expose
    def set_values(self, val):
        if len(self.list_val) == 5:
            self.list_val.pop(0)
        self.list_val.append(val)
        self.first_val = str(len(self.list_val))

    #Precondition: init_panel()
    def write_panel(self):
        self.font = ImageFont.truetype(self.font_link, size=130)
        img = Image.new('RGB', (200, 200), (255, 255, 255))
        d = ImageDraw.Draw(img)
        d.text((10, 40), self.first_val, fill=(255, 0, 0), font=self.font)
        font = ImageFont.truetype(self.font_link, size=20)
        i = 20
        if self.list_val > 0:
            for a in self.list_val:
                d.text((90, i), a, fill=(255, 0, 0), font=font)
                i += 32
        img.save("image.jpg")
        self.set_image(open("image.jpg").read())
