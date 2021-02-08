import pyb
from pyb import SPI, Pin, Timer, udelay
import framebuf

class SharpMemLCD:
    '''
    Handles formating frame buffer and sending data to the LCD
    '''
    CS = "C4"
    DISP = "A7"
    XDIM = 144
    YDIM = 168
    CHANNEL = 2

    def __init__(self):
        # define pins
        self.spi = SPI(self.CHANNEL, SPI.MASTER, prescaler=4, polarity=0, phase=0, firstbit=SPI.LSB)
        self.cs = Pin(self.CS, Pin.OUT_PP)
        self.set_cs(0)
        self.disp = Pin(self.DISP, Pin.OUT_PP)
        self.disp.value(1)

        # define structures, related info
        self.xdim = self.XDIM
        self.ydim = self.YDIM
        self.buffer = bytearray((self.xdim//8) * self.ydim)
        self.framebuffer = framebuf.FrameBuffer(self.buffer, self.xdim, self.ydim, framebuf.MONO_HMSB)
        self.vcom = 2

        # begin by clearing screen
        self.clear_screen()

    def write(self, text):
        self.framebuffer.fill(0)
        self.framebuffer.text(text, 0, 0)
        self.sync()

    def toggle_vcom(self):
        self.vcom ^= 2

    def clear_screen(self):
        self.set_cs(1)
        udelay(6)          
        self.send(4 | self.vcom)
        self.send(0)
        udelay(2)          
        self.set_cs(0)
        udelay(6)          
        self.toggle_vcom()

    def set_cs(self, logic_level):
        self.cs.value(logic_level)

    def send(self, value):
        self.spi.send(value)

    def sync(self):
        index = 0
        for line in range(self.ydim):
            self.set_cs(1)
            udelay(6)          
            self.send(1 | self.vcom)
            self.send(line+1)
            for j in range(self.xdim//8):
                self.send(self.buffer[index])
                index += 1
            self.send(0)
            udelay(2)          
            self.set_cs(0)
            udelay(6)          