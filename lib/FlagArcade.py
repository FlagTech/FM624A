from urandom import *
import time

def randrange(start, stop=None):
    if stop is None:
        stop = start
        start = 0
    upper = stop - start
    bits = 0
    pwr2 = 1
    while upper > pwr2:
        pwr2 <<= 1
        bits += 1
    while True:
        r = getrandbits(bits)
        if r < upper:
            break
    return r + start

def randint(start, stop):
    return randrange(start, stop + 1)

def getKey(value):
    key='n'
    if value > 975:
        key='u'
    elif value > 828:
        key='d'
    elif value > 682:
        key='l'
    elif value > 536:
        key='r'
    elif value > 390:
        key='m'
    elif value > 243:
        key='set'
    elif value > 97:
        key='rst'
    return key

class Character:
    screen_width = 160
    screen_height = 128
    
    drawbuf_len = screen_width
    drawbuf = None
    
    init_set_done = False
    
    def __init__(self, pixels, width, height, lcd, color=0xFFFF, bgcolor=0x0000):
        self.lcd = lcd
        self.w = width
        self.h = height
        self.color = color
        self.bgcolor = bgcolor
        self._x = 1
        self._y = 1

        if type(pixels) is tuple or type(pixels) is list:
            self.pixels = pixels
        else:
            self.pixels = (pixels,)
        self.pixels_idx = 0
        self.pixels_autonext = True

        self.keepms = 50  #每個畫面至少保持多少 ms, 避免動太快看不清楚圖
        
        self._nextmovetime = 0
        
        self.init_set()

    def init_set(self):
        ''' To avoid initialisation code which runs on import
            Ref: https://docs.micropython.org/en/latest/reference/constrained.html
        '''
        if self.init_set_done:
            return
        
        self.lcd_getScreenWidth = self.lcd.getScrnWidth
        self.lcd_getScreenHeight = self.lcd.getScrnHeight
        self.lcd_setWindow = self.lcd.setAddrWindow
        self.lcd_dc = self.lcd.a0
        self.lcd_cs = self.lcd.cs
        self.lcd_spi = self.lcd.spi
        self.lcd_fillRect = self.lcd.fillRect

        self.__class__.screen_width = self.lcd_getScreenWidth()
        self.__class__.screen_height = self.lcd_getScreenHeight()
        if self.__class__.screen_width > self.__class__.screen_height:
            self.__class__.drawbuf_len = self.__class__.screen_width 
        else:
            self.__class__.drawbuf_len = self.__class__.screen_height
        self.__class__.drawbuf = bytearray(self.__class__.drawbuf_len*2)
        
        self.init_set_done = True

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        if not x == self._x:
            self.plot(x0=self._x, x1=x)
        self._x = x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        if not y == self._y:
            self.plot(y0=self._y, y1=y)
        self._y = y

    def show(self, x=None, y=None):
#         if not x:
#             x = self._x
#         if not y:
#             y = self._y
        self._plot(self._x,self._y, x, y)

    def hide(self, x=None, y=None):
        if not x:
            x = self._x
        if not y:
            y = self._y
        self.lcd_fillRect(x, y, self.w, self.h, self.bgcolor)
    
    def touch(self, obj=None):
        rectAx1 = self._x
        rectAy1 = self._y
        rectAx2 = self._x + self.w
        rectAy2 = self._y + self.h
        
        rectBx1 = obj._x
        rectBy1 = obj._y
        rectBx2 = obj._x + obj.w
        rectBy2 = obj._y + obj.h
        
        if (rectAx1 < rectBx2 and rectAx2 > rectBx1 and
            rectAy1 < rectBy2 and rectAy2 > rectBy1):
            return True
        else:
            return False
            
    def move(self, dx=0, dy=0, max_x=None, max_y=None):
        '''水平移動 dx 點，垂直移動 dy 點
           dx > 0 往右，dy < 0 往左
           dx > 0 往下，dy < 0 往上
        '''
        if dx == 0 and dy == 0:
            return
        
        x1 = self._x + dx
        y1 = self._y + dy

        if max_x:
            if ((dx > 0 and x1 > max_x) or
                (dx < 0 and x1 < max_x)):
                x1 = max_x
        if max_y:
            if ((dy > 0 and y1 > max_y) or
                (dy < 0 and y1 < max_y)):
                y1 = max_y
          
        self._plot(self._x, self._y, x1, y1)

    def xplot(self, x0=None, x1=None):
        '''從 x0 移動到 x1
        '''
        self.plot(x0=x0, x1=x1)

    def yplot(self, y0=None, y1=None):
        '''從 y0 移動到 y1
        '''
        self.plot(y0=y0, y1=y1)

    def plot(self, x0=None, y0=None, x1=None, y1=None):
        '''從 (x0,y0) 移動到 (x1,y1)
        '''       
        if x0 is None:
            x0 = self._x
        if y0 is None:
            y0 = self._y
        if x1 is None:
            x1 = self._x
        if y1 is None:
            y1 = self._y

        #if x0 == x1 and y0 == y1:
        #    return

        self._plot(x0, y0, x1, y1)

    def _plot(self, x0, y0, x1, y1):
        while time.ticks_diff(self._nextmovetime, time.ticks_ms()) > 0:
            pass

        self._x = x1
        self._y = y1
        
        dx = x1 - x0
        dy = y1 - y0
        dw = abs(dx)
        dh = abs(dy)

        c = self.color        #這次要畫的色彩

        w = self.w + dw   #這次要畫的寬度
        h = self.h + dh   #這次要畫的高度
       
        x = x0                #這次要畫的左上角起點 x 
        y = y0                #這次要畫的左上角起點 y
        if dx > 0:  #右移
            x = x0
        elif dx < 0:  #左移
            x = x1
        if dy > 0:  #下移
            y = y0
        elif dy < 0:  #上移
            y = y1

        if (0-w < x < self.__class__.screen_width and
            0-h < y < self.__class__.screen_height):
            pass
        else:  #圖案完全超出螢幕
            return 

        #部份圖案超出螢幕, 進行修正
        if x+w-1 >= self.__class__.screen_width:
            w = self.__class__.screen_width - x
        
        if y+h-1 >= self.__class__.screen_height:
            h = self.__class__.screen_height - y
               
        self.lcd_setWindow(x, y, x+w-1, y+h-1) #這次要畫區域的四個頂點
        
#        print(x, y, x+w-1, y+h-1, w, h)  #########
        
        self.lcd_dc(1)
        self.lcd_cs(0)
        for i1 in range(h):
            buf1_len = w*2
            view_drawbuf = memoryview(self.__class__.drawbuf)
            buf1 = memoryview(view_drawbuf[:buf1_len])
            buf1[:] = b'\x00' * buf1_len

            i = i1
            if dy > 0:  #下移
                if i1 < dh:
                    self.lcd_spi.write(buf1)
                    continue
                else:
                    i = i1 - dh
            elif dy < 0:  #上移
                if i1 >= self.h:
                    self.lcd_spi.write(buf1)
                    continue

            for j1 in range(w):
                j = j1
                if dx > 0:  #右移
                    if j1 < dx:
                        continue
                    j = j1 - dx
                elif dx < 0:  #左移
                    if j1 >= self.w:
                        continue
                
                #print(i, j, end=', ')#######
                p = self.pixels[self.pixels_idx][i*self.w + j]

                if p == ord('1'):
                    buf1[j1*2] = c >> 8
                    buf1[j1*2+1] = c
            self.lcd_spi.write(buf1)
            #print(bytes(buf1))########
            #print(x, y, x+w-1, y+h-1)########
            #print(' ')#########
            
        self.lcd_cs(1)
        
        import gc; gc.collect()  #手動回收記憶體

        self._nextmovetime = time.ticks_add(time.ticks_ms(), self.keepms)
        if self.pixels_autonext:
            self.pixels_idx += 1
            if self.pixels_idx >= len(self.pixels):
                self.pixels_idx = 0

        #print('------------------------') #########
