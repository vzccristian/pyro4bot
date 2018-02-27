import spidev
import RPi.GPIO as GPIO
import time



""" BCM GPIO """
RST = 17
DC = 25
BUSY = 24
CS = 8

class EPDDriver:
    def __init__(self, spi, x_dot, y_dot):
        # Initialize DC RST pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(RST, GPIO.OUT)
        GPIO.setup(DC, GPIO.OUT)
        GPIO.setup(CS, GPIO.OUT)
        GPIO.setup(BUSY, GPIO.IN)

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

    def ReadBusy(self):
        for i in range(0, 400):
            if GPIO.input(BUSY) == 0:
                # print 'Busy for %d s'%(0.01*i)
                return 1
            time.sleep(0.01)

    def EPD_WriteCMD(self, command):
        GPIO.output(DC, GPIO.LOW)
        #print 'send command : ' ,hex(command)
        self.spi.writebytes([command])

    def EPD_WriteCMD_p1(self, command, para):
        self.ReadBusy()
        GPIO.output(DC, GPIO.LOW)
        #print 'send command : ' ,hex(command)
        self.spi.writebytes([command])
        GPIO.output(DC, GPIO.HIGH)
        #print 'Sent to data : ' ,hex(para),
        self.spi.writebytes([para])

    def EPD_POWERON(self):
        self.EPD_WriteCMD_p1(0x22, 0xc0)
        self.EPD_WriteCMD(0x20)
        self.ReadBusy()

    def EPD_Write(self, value):
        """Send command byte to display"""
        GPIO.output(DC, GPIO.LOW)
        time.sleep(0.01)
        #print 'send command : ' ,hex(value[0])
        # The first byte is written with the command value
        self.spi.writebytes([value[0]])
        GPIO.output(DC, GPIO.HIGH)
        for i in range(0, len(value) - 1):
            data = value[i + 1]
            self.spi.writebytes([data])

    # checks dispdata list->data from list is copied, value->value is copied size times
    def EPD_WriteDispRam(self, XSize, YSize, dispdata):
        if XSize % 8 != 0:
            XSize = XSize + (8 - XSize % 8)  # pfff what ? is it a round up ?
        XSize = XSize / 8
        NUM = 0
        self.ReadBusy()
        #print 'send command : ' ,hex(0x24)
        GPIO.output(DC, GPIO.LOW)
        self.spi.writebytes([0x24])
        GPIO.output(DC, GPIO.HIGH)
        #print 'Sent to data : ',hex(dispdata),
        if isinstance(dispdata, list):
            for i in range(0, YSize):
                for j in range(0, XSize):
                    self.spi.writebytes([dispdata[NUM]])
                    NUM += 1
                    #print hex(dispdata[i+j]),
        else:
            #print 'send data : ' ,dispdata
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
        print 'EPD_Init'
        """Initialize display"""
        """2. reset driver"""
        GPIO.output(CS, GPIO.LOW)
        GPIO.output(RST, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(RST, GPIO.LOW)
        if GPIO.input(RST) == 0:
            print '[EPD] Reset is complete'
        else:
            print '[EPD] Reset is false'
        time.sleep(0.01)
        GPIO.output(RST, GPIO.HIGH)
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
        # # time.sleep(0.5)
        # self.ReadBusy()
        # self.part_display(xStart/8,xEnd/8,yEnd%256,yEnd/256,yStart%256,yStart/256)
        # self.EPD_WriteDispRam(xEnd-xStart, yEnd-yStart+1, DisBuffer)

    """***********************************************************************************************************************
                ------------------------------------------------------------------------
                |\\\																///|
                |\\\						App layer								///|
                ------------------------------------------------------------------------
    ***********************************************************************************************************************"""
    """********************************************************************************
                    clear full screen
    ********************************************************************************"""

    def Dis_Clear_full(self):
        print '1.init full screen'
        self.ReadBusy()
        self.EPD_init_Full()
        self.delay()
        # Clear screen
        print '2.clear full screen'
        self.ReadBusy()
        self.EPD_Dis_Full(0xff)
        self.delay()

    def Dis_Clear_part(self, xStart, xEnd, yStart, yEnd):
        self.ReadBusy()
        self.EPD_init_Part()
        # self.delay()
        self.ReadBusy()
        self.EPD_Dis_Part(xStart, xEnd, yStart, yEnd, 0xaa)

    def Dis_full_pic(self, DisBuffer):
        self.EPD_Dis_Full(DisBuffer)
        self.delay()

    def Dis_part_pic(self, xStart, xEnd, yStart, yEnd, DisBuffer):
        # self.EPD_init_Part()
        # self.delay()
        self.EPD_Dis_Part(xStart, xEnd, yStart, yEnd, DisBuffer)
        self.delay()

    def delay(self):
        time.sleep(self.DELAYTIME)
