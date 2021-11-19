# MicroPython ST7735 LCD driver with SPI interfaces
from micropython import const
from math import sqrt
import time
import machine
from machine import SPI, Pin
import framebuf

# some flags for initR() :(
INITR_GREENTAB = const(0x0)
INITR_REDTAB = const(0x1)
INITR_BLACKTAB = const(0x2)

INITR_18GREENTAB = const(INITR_GREENTAB)
INITR_18REDTAB = const(INITR_REDTAB)
INITR_18BLACKTAB = const(INITR_BLACKTAB)
INITR_144GREENTAB = const(0x1)
INITR_MINI160x80 = const(0x4)
INITR_OTHERTAB = const(0x5)       # other tab


# for 1.44 and mini
ST7735_TFTWIDTH_128 = const(128)
# for mini
ST7735_TFTWIDTH_80 = const(80)
# for 1.44" display
ST7735_TFTHEIGHT_128 = const(128)
# for 1.8" and mini display
ST7735_TFTHEIGHT_160 = const(160)

ST7735_NOP = const(0x00)
ST7735_SWRESET = const(0x01)
ST7735_RDDID = const(0x04)
ST7735_RDDST = const(0x09)

ST7735_SLPIN = const(0x10)
ST7735_SLPOUT = const(0x11)
ST7735_PTLON = const(0x12)
ST7735_NORON = const(0x13)

ST7735_INVOFF = const(0x20)
ST7735_INVON = const(0x21)
ST7735_GAMSET = const(0x26)    # add gamma curve set for new brand KMR-1.8
ST7735_DISPOFF = const(0x28)
ST7735_DISPON = const(0x29)
ST7735_CASET = const(0x2A)
ST7735_RASET = const(0x2B)
ST7735_RAMWR = const(0x2C)
ST7735_RAMRD = const(0x2E)

ST7735_PTLAR = const(0x30)
ST7735_COLMOD = const(0x3A)
ST7735_MADCTL = const(0x36)

ST7735_FRMCTR1 = const(0xB1)
ST7735_FRMCTR2 = const(0xB2)
ST7735_FRMCTR3 = const(0xB3)
ST7735_INVCTR = const(0xB4)
ST7735_DISSET5 = const(0xB6)

ST7735_PWCTR1 = const(0xC0)
ST7735_PWCTR2 = const(0xC1)
ST7735_PWCTR3 = const(0xC2)
ST7735_PWCTR4 = const(0xC3)
ST7735_PWCTR5 = const(0xC4)
ST7735_VMCTR1 = const(0xC5)

ST7735_RDID1 = const(0xDA)
ST7735_RDID2 = const(0xDB)
ST7735_RDID3 = const(0xDC)
ST7735_RDID4 = const(0xDD)

ST7735_PWCTR6 = const(0xFC)

ST7735_GMCTRP1 = const(0xE0)
ST7735_GMCTRN1 = const(0xE1)

# Color definitions
WHITE = const(0xFFFF)
BLACK = const(0x0000)
BLUE = const(0x001F)
RED = const(0xF800)
GREEN = const(0x07E0)
CYAN = const(0x07FF)
YELLOW = const(0xFFE0)
PURPLE = const(0xF81F)
GRAY = const(0x8410)

DELAY = const(0x80)

MADCTL_MY = const(0x80)
MADCTL_MX = const(0x40)
MADCTL_MV = const(0x20)
MADCTL_ML = const(0x10)
MADCTL_RGB = const(0x00)
MADCTL_BGR = const(0x08)
MADCTL_MH = const(0x04)

# --- device set table ---
Rcmd1_old = bytes([15,\
ST7735_SWRESET, DELAY, 150,\
ST7735_SLPOUT , DELAY, 255,\
ST7735_FRMCTR1, 3, 0x01, 0x2C, 0x2D,\
ST7735_FRMCTR2, 3, 0x01, 0x2C, 0x2D,\
ST7735_FRMCTR3, 6, 0x01, 0x2C, 0x2D, 0x01, 0x2C, 0x2D,\
ST7735_INVCTR , 1, 0x07,\
ST7735_PWCTR1 , 3, 0xA2, 0x02, 0x84,\
ST7735_PWCTR2 , 1, 0xC5,\
ST7735_PWCTR3 , 2, 0x0A, 0x00,\
ST7735_PWCTR4 , 2, 0x8A, 0x2A,\
ST7735_PWCTR5 , 2, 0x8A, 0xEE,\
ST7735_VMCTR1 , 1, 0x0E,\
ST7735_INVOFF , 0,\
ST7735_MADCTL , 1, 0xC8,\
ST7735_COLMOD , 1, 0x05\
])

Rcmd1_new = bytes([16,\
ST7735_SWRESET, DELAY, 150,\
ST7735_SLPOUT , DELAY, 255,\
ST7735_FRMCTR1, 3, 0x05, 0x3C, 0x3C,\
ST7735_FRMCTR2, 3, 0x05, 0x3C, 0x3C,\
ST7735_FRMCTR3, 6, 0x05, 0x3C, 0x3C, 0x05, 0x3C, 0x3C,\
ST7735_INVCTR , 1, 0x07,\
ST7735_PWCTR1 , 3, 0xA2, 0x02, 0x84,\
ST7735_PWCTR2 , 1, 0xC5,\
ST7735_PWCTR3 , 2, 0x0A, 0x00,\
ST7735_PWCTR4 , 2, 0x8A, 0x2A,\
ST7735_PWCTR5 , 2, 0x8A, 0xEE,\
ST7735_VMCTR1 , 1, 0x0E,\
ST7735_INVOFF , 0,\
ST7735_GAMSET , 1, 0x02,\
ST7735_MADCTL , 1, 0xC8,\
ST7735_COLMOD , 1, 0x05\
])

Rcmd2green = bytes([2,\
ST7735_CASET, 4, 0x00, 0x02, 0x00, 0x7F+0x02,\
ST7735_RASET, 4, 0x00, 0x01, 0x00, 0x9F+0x01\
])

Rcmd2red = bytes([2,\
ST7735_CASET, 4, 0x00, 0x00, 0x00, 0x7F,\
ST7735_RASET, 4, 0x00, 0x00, 0x00, 0x9F\
])

Rcmd2green144 = bytes([2,\
ST7735_CASET, 4, 0x00, 0x00, 0x00, 0x7F,\
ST7735_RASET, 4, 0x00, 0x00, 0x00, 0x7F\
])

Rcmd2green160x80 = ([2,\
ST7735_CASET, 4, 0x00, 0x00, 0x00, 0x7F,\
ST7735_RASET, 4, 0x00, 0x00, 0x00, 0x9F\
])

Rcmd3 = bytes([4,\
ST7735_GMCTRP1, 16, 0x02, 0x1c, 0x07, 0x12, 0x37, 0x32,\
0x29, 0x2d, 0x29, 0x25, 0x2B, 0x39, 0x00, 0x01, 0x03, 0x10,\
ST7735_GMCTRN1, 16, 0x03, 0x1d, 0x07, 0x06, 0x2E, 0x2C,\
0x29, 0x2D, 0x2E, 0x2E, 0x37, 0x3F, 0x00, 0x00, 0x02, 0x10,\
ST7735_NORON, DELAY, 10,\
ST7735_DISPON, DELAY, 100\
])


class LCD:
    
  # 繪圖用 buffer
  drawbuf = bytearray(160*2)
  # 文字用 buffer, 目前文字強制使用 8x8 字形
  charbuf = bytearray(8*8*2)
  
  # set instance
  def __init__(self, spi, CS, A0, RST=-1):
    self.cs = machine.Pin(CS, machine.Pin.OUT)
    self.cs(1)
    self.a0 = machine.Pin(A0, machine.Pin.OUT)
    self.a0(0)
    if RST >= 0: self.rst = machine.Pin(RST, Pin.OUT)
    else: self.rst = 0
    if self.rst != 0: self.rst(1)
    self.spi = spi
    self.textcolor = WHITE
    self.textbgcolor = BLACK
    self.textsize = 1
    self.cursor_x = 0
    self.cursor_y = 0
    self.tabcolor = 0
    self.rotation = 0
    self.colstart = 0
    self.rowstart = 0
    self.xstart = 0
    self.ystart = 0
    self._height = 0
    self._width = 0

  # set initialize
  def init(self, option=INITR_BLACKTAB, Ntyp=True):
    self._ntyp = Ntyp
    # reset display
    if self.rst != 0:
      self.rst(0)
      time.sleep_ms(100)
      self.rst(1)
    # setup LCD
    if Ntyp: self._commandList(Rcmd1_new)
    else: self._commandList(Rcmd1_old)
    if option == INITR_GREENTAB:
      self._commandList(Rcmd2green)
      self.colstart = 2
      self.rowstart = 1
    elif option == INITR_144GREENTAB:
      self._height = ST7735_TFTHEIGHT_128
      self._width = ST7735_TFTWIDTH_128
      self._commandList(Rcmd2green144)
      self.colstart = 2
      self.rowstart = 3
    elif option == INITR_MINI160x80:
      self._height = ST7735_TFTHEIGHT_160
      self._width = ST7735_TFTWIDTH_80
      self._commandList(Rcmd2green160x80)
      self.colstart = 24
      self.rowstart = 0
    else:
      self._commandList(Rcmd2red)
    self._commandList(Rcmd3)

    if option == INITR_BLACKTAB or option == INITR_MINI160x80:
      self._writecommand(ST7735_MADCTL)
      self._writedata(0xC0)
      
      self.colstart = 2
      self.rowstart = 1

  
    self.tabcolor = option
    
    self.setRotation(0)

  # clear display
  def clearLCD(self):
    self.fillScreen(0)

  # get rotation
  def getRotation(self):
    return self.rotation

  # invert display
  def invertDisplay(self, flg):
    self._writecommand(ST7735_INVON if flg else ST7735_INVOFF)
 
  # get 565 color
  def rgbcolor(self, r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
 
  # set cursor
  def setCursor(self, x, y):
    self.cursor_x = x
    self.cursor_y = y

  # get screen width
  def getScrnWidth(self):
    return self._width

  # get screen height
  def getScrnHeight(self):
    return self._height

  # set text size
  def setTextSize(self, s):
    # 目前沒有字放大的功能
    self.textsize = 1
    return

    ls = s
    if ls > 16: ls = 16
    elif ls == 0: ls = 1
    self.textsize = ls

  # set text color
  def setTextColor(self, c, b=0xFFFFFFFF):
    self.textcolor = c
    self.textbgcolor = c if b == 0xFFFFFFFF else b

  # set address window
  def setAddrWindow(self, x0, y0, x1, y1):
    buf = bytearray(4)
    self._writecommand(ST7735_CASET)
    buf[0] = 0
    buf[2] = 0
    buf[1] = x0+self.xstart
    buf[3] = x1+self.xstart
    self.a0(1)
    self.cs(0)
    self.spi.write(buf)
    self.cs(1)

    self._writecommand(ST7735_RASET)
    buf[1] = y0+self.ystart
    buf[3] = y1+self.ystart
    self.a0(1)
    self.cs(0)
    self.spi.write(buf)
    self.cs(1)

    self._writecommand(ST7735_RAMWR)

  # fill screen
  def fillScreen(self, color):
    self.fillRect(0, 0, self._width, self._height, color)

  # fill rect
  def fillRect(self, x, y, w, h, color):
    if x >= self._width or y >= self._height: return
    if (x + w - 1) >= self._width: w = self._width - x
    if (y + h - 1) >= self._height: h = self._height - y
    
    self.setAddrWindow(x, y, x+w-1, y+h-1)

    buf = bytearray(w*2)
    hi = color >> 8
    lo = color
    for i in range(w):
      buf[i*2] = hi
      buf[i*2+1] = lo
    
    self.a0(1)
    self.cs(0)
    for i in range(h): self.spi.write(buf)
    self.cs(1)
    
  # draw picture block
  def drawPblk(self, x, y, w, h, buf):
    if x >= self._width or y >= self._height: return
    if (x + w - 1) >= self._width: w = self._width - x
    if (y + h - 1) >= self._height: h = self._height - y
    
    self.setAddrWindow(x, y, x+w-1, y+h-1)
    
    self.a0(1)
    self.cs(0)
    for i in range(h):
      #bufl = bytearray(w*2)
      buf1_len = w*2
      view_drawbuf = memoryview(self.__class__.drawbuf)
      buf1 = memoryview(view_drawbuf[:buf1_len])
      buf1[:] = b'\x00' * buf1_len
      
      if len(buf) < (i + 1) * w * 2: break
      for j in range(w*2): buf1[j] = buf[i*w*2 + j]
      self.spi.write(buf1)
    self.cs(1)

  # write charactor
  def char(self, data):
    # check CR code
    if data == '\r':
      self.cursor_x = 0
      self.cursor_y += 8 * self.textsize
      if self.cursor_y >= self._height: return 0
    elif ord(data) < 0x20 or self.cursor_y >= self._height:
      return 0
      
    # set character data
    else:
      if self.cursor_x+8 >= self._width:
        self.cursor_x = 0
        self.cursor_y += 8*self.textsize
        if self.cursor_y >= self._height: return 0
        
      w = 8
      h = 8
      b = self.textbgcolor
      b = (b & 0xff)*256 + (b >> 8)
      c = self.textcolor
      c = (c & 0xff)*256 + (c >> 8)
      buf1_len = w*h*2
      view_charbuf = memoryview(self.__class__.charbuf)
      buf1 = memoryview(view_charbuf[:buf1_len])
      fb = framebuf.FrameBuffer(buf1, w, h, framebuf.RGB565)
      fb.fill(b)
      fb.text(data, 0, 0, c)
      self.drawPblk(self.cursor_x, self.cursor_y, w, h, buf1)
      self.cursor_x += 8

    return 1

#    # check CR code
#    if data == 0x0D:
#      self.cursor_x = 0
#      self.cursor_y += 8 * self.textsize
#      if self.cursor_y >= self._height: return 0
#    elif data < 0x20 or self.cursor_y >= self._height:
#      return 0
#      
#    # set character data
#    else:
#      for i in range(8*self.textsize):
#        if self.cursor_x < self._width:
#          xp = int(i/self.textsize)
#          txtd = 0
#          if xp > 0 and xp < 6: txtd = ASCII[(data - 0x20) * 5 + xp - 1]
#          for yp in range(8*self.textsize):
#            if (self.cursor_y + yp) >= self._height: continue
#            if (txtd & (1 << int(yp/self.textsize))) != 0:
#              self.drawPixel(self.cursor_x, self.cursor_y + yp, self.textcolor)
#            elif self.textcolor != self.textbgcolor:
#              self.drawPixel(self.cursor_x, self.cursor_y + yp, self.textbgcolor)
#        self.cursor_x += 1
#        
#        if self.cursor_x >= self._width:
#          self.cursor_x = 0
#          self.cursor_y += 8*self.textsize
#          if self.cursor_y >= self._height: return 0
#
#    return 1

  # print text charactor
  def print(self, string):
    string = str(string)
    for i in range(len(string)):
      #self.char(ord(string[i]))
      self.char(string[i])

  def text(self, x, y, string, color=WHITE, background=BLACK):
    self.setCursor(x, y)
    self.setTextColor(color, background)
    self.print(str(string))

  # set rotation
  def setRotation(self, m):
    self._writecommand(ST7735_MADCTL)
    rotation = m % 4
    tabflg = self.tabcolor == INITR_BLACKTAB or self.tabcolor == INITR_MINI160x80
    if rotation == 0:
      self._writedata(MADCTL_MX | MADCTL_MY | (MADCTL_RGB if tabflg else MADCTL_BGR))
      
      if self.tabcolor == INITR_144GREENTAB:
        self._height = ST7735_TFTHEIGHT_128
        self._width = ST7735_TFTWIDTH_128
      elif self.tabcolor == INITR_MINI160x80:
        self._height = ST7735_TFTHEIGHT_160
        self._width = ST7735_TFTWIDTH_80
      else:
        self._height = ST7735_TFTHEIGHT_160
        self._width = ST7735_TFTWIDTH_128
      
      self.xstart = self.colstart
      self.ystart = self.rowstart

    elif rotation == 1:
      self._writedata(MADCTL_MY | MADCTL_MV | (MADCTL_RGB if tabflg else MADCTL_BGR))
      
      if self.tabcolor == INITR_144GREENTAB:
        self._width = ST7735_TFTHEIGHT_128
        self._height =  ST7735_TFTWIDTH_128
      elif self.tabcolor == INITR_MINI160x80:
        self._width = ST7735_TFTHEIGHT_160
        self._height = ST7735_TFTWIDTH_80
      else:
        self._width = ST7735_TFTHEIGHT_160
        self._height = ST7735_TFTWIDTH_128
      
      self.ystart = self.colstart;
      self.xstart = self.rowstart;
      
    elif rotation == 2:
      self._writedata(MADCTL_RGB if tabflg else MADCTL_BGR)

      if self.tabcolor == INITR_144GREENTAB:
        self._height = ST7735_TFTHEIGHT_128
        self._width  = ST7735_TFTWIDTH_128
      elif self.tabcolor == INITR_MINI160x80:
        self._height = ST7735_TFTHEIGHT_160
        self._width = ST7735_TFTWIDTH_80
      else:
        self._height = ST7735_TFTHEIGHT_160
        self._width  = ST7735_TFTWIDTH_128

      self.xstart = self.colstart
      self.ystart = self.rowstart
    
    elif rotation == 3:
      self._writedata(MADCTL_MX | MADCTL_MV | (MADCTL_RGB if tabflg else MADCTL_BGR))

      if self.tabcolor == INITR_144GREENTAB:
        self._width = ST7735_TFTHEIGHT_128
        self._height = ST7735_TFTWIDTH_128
      elif self.tabcolor == INITR_MINI160x80:
        self._width = ST7735_TFTHEIGHT_160
        self._height = ST7735_TFTWIDTH_80
      else:
        self._width = ST7735_TFTHEIGHT_160
        self._height = ST7735_TFTWIDTH_128

      self.ystart = self.colstart;
      self.xstart = self.rowstart;

  # draw pixel
  def drawPixel(self, x, y, color):
    if x < 0 or x >= self._width or y < 0 or y >= self._height: return
    
    self.setAddrWindow(x, y, x+1, y+1)
    
    self.a0(1)
    self.cs(0)
    buf = bytearray(2)
    buf[0] = color >> 8
    buf[1] = color
    self.spi.write(buf)
    self.cs(1)
    
  # draw vline
  def drawFastVLine(self, x, y, h, color):
    if x >= self._width or y >= self._height: return
    if (y+h-1) >= self._height: h = self._height-y
    self.setAddrWindow(x, y, x, y+h-1)

    buf = bytearray(h*2)
    hi = color >> 8
    lo = color
    for i in range(h):
      buf[i*2] = hi
      buf[i*2+1] = lo
    
    self.a0(1)
    self.cs(0)
    self.spi.write(buf)
    self.cs(1)

  # draw hline
  def drawFastHLine(self, x, y, w, color):
    if x >= self._width or y >= self._height: return
    if (x+w-1) >= self._width: w = self._width-x
    self.setAddrWindow(x, y, x+w-1, y)

    buf = bytearray(w*2)
    hi = color >> 8
    lo = color
    for i in range(w):
      buf[i*2] = hi
      buf[i*2+1] = lo
    
    self.a0(1)
    self.cs(0)
    self.spi.write(buf)
    self.cs(1)

  # draw line
  def drawLine(self, x0, y0, x1, y1, color):
    if x0 == x1:
      if y0 > y1: self.drawFastVLine(x0, y1, y0 - y1 + 1, color)
      else: self.drawFastVLine(x0, y0, y1 - y0 + 1, color)
    elif y0 == y1:
      if x0 > x1: self.drawFastHLine(x1, y0, x0 - x1 + 1, color)
      else: self.drawFastHLine(x0, y0, x1 - x0 + 1, color)
    else: self._writeLine(x0, y0, x1, y1, color)

  # draw rectangle
  def drawRect(self, x, y, w, h, color):
    self.drawFastHLine(x, y, w, color)
    self.drawFastHLine(x, y+h-1, w, color)
    self.drawFastVLine(x, y, h, color)
    self.drawFastVLine(x+w-1, y, h, color)

  # draw circle
  def drawCircle(self, x0, y0, r, color):
    f = 1 - r
    ddF_x = 1
    ddF_y = -2 * r
    x = 0
    y = r
    
    self.drawPixel(x0, y0+r, color)
    self.drawPixel(x0, y0-r, color)
    self.drawPixel(x0+r, y0, color)
    self.drawPixel(x0-r, y0, color)
    
    while x < y:
      if f >= 0:
        y -= 1
        ddF_y += 2
        f += ddF_y
      x += 1
      ddF_x += 2
      f += ddF_x
      
      self.drawPixel(x0 + x, y0 + y, color)
      self.drawPixel(x0 - x, y0 + y, color)
      self.drawPixel(x0 + x, y0 - y, color)
      self.drawPixel(x0 - x, y0 - y, color)
      self.drawPixel(x0 + y, y0 + x, color)
      self.drawPixel(x0 - y, y0 + x, color)
      self.drawPixel(x0 + y, y0 - x, color)
      self.drawPixel(x0 - y, y0 - x, color)

  # write byte data
  def _writebyte(self, byte):
    buf = bytearray(1)
    buf[0] = byte
    self.cs(0)
    self.spi.write(buf)
    self.cs(1)

  # write data
  def _writedata(self, dat):
    self.a0(1)
    self._writebyte(dat)

  # write command
  def _writecommand(self, cmd):
    self.a0(0)
    self._writebyte(cmd)

  # execute command list
  def _commandList(self, addrpt):
    rdpt = 0
    numCommands = addrpt[rdpt]
    rdpt += 1
    for i in range(numCommands):
      self._writecommand(addrpt[rdpt])
      rdpt += 1
      numArgs = addrpt[rdpt]
      rdpt += 1
      ms = numArgs & DELAY
      numArgs &= ~DELAY
      for j in range(numArgs):
        self._writedata(addrpt[rdpt])
        rdpt += 1
      if ms != 0:
        ms = addrpt[rdpt]
        rdpt += 1
        if ms == 255: ms = 500
        time.sleep_ms(ms)

  # write line
  def _writeLine(self, x0i, y0i, x1i, y1i, color):
    steep = True if abs(y1i - y0i) > abs(x1i - x0i) else False
    x0 = y0i if steep else x0i
    y0 = x0i if steep else y0i
    x1 = y1i if steep else x1i
    y1 = x1i if steep else y1i
    if x0 > x1:
      dum = x0
      x0 = x1
      x1 = dum
      dum = y0
      y0 = y1
      y1 = dum
    
    dx = x1 - x0
    dy = abs(y1 - y0)
    
    err = dx / 2
    ystep = 1 if y0 < y1 else -1
    
    for lx in range(x0, x1+1, 1):
      if steep: self.drawPixel(y0, lx, color)
      else: self.drawPixel(lx, y0, color)
      err -= dy
      if err < 0:
        y0 += ystep
        err += dx
