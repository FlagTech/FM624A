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
    if value<80 :
        key='n'
    elif abs(value-1024)<50:
        key='u'
    elif abs(value-950)<50:
        key='d'
    elif abs(value-794)<50:
        key='l'
    elif abs(value-633)<50:
        key='r'
    elif abs(value-476)<50:
        key='m'
    elif abs(value-318)<50:
        key='set'
    elif abs(value-162)<50:
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



NOTE = [
    440.0,  # A
    493.9,  # B or H
    261.6,  # C
    293.7,  # D
    329.6,  # E
    349.2,  # F
    392.0,  # G
    0.0,    # pad

    466.2,  # A#
    0.0,
    277.2,  # C#
    311.1,  # D#
    0.0,
    370.0,  # F#
    415.3,  # G#
    0.0,
]


# You can find a description of RTTTL here:
# https://en.wikipedia.org/wiki/Ring_Tone_Transfer_Language
class RTTTL:
    def __init__(self, buzzer, defaults, tune):
        self.buzzer = buzzer
        self.tune = tune
        self.tune_idx = 0
        self.parse_defaults(defaults)
        self.repeat_play = False
        self.repeat_play_startidx = 0

    def parse_defaults(self, defaults):
        # Example: d=4,o=5,b=140
        val = 0
        id = ' '
        for char in defaults:
            char = char.lower()
            if char.isdigit():
                val *= 10
                val += ord(char) - ord('0')
                if id == 'o':
                    self.default_octave = val
                elif id == 'd':
                    self.default_duration = val
                elif id == 'b':
                    self.bpm = val
            elif char.isalpha():
                id = char
                val = 0
        # 240000 = 60 sec/min * 4 beats/whole-note * 1000 msec/sec
        self.msec_per_whole_note = 240000.0 / self.bpm

    def play_background(self, timer):
        if self.tune_idx >= 0:
            freq, msec = next(self.notes())
        else:
            freq, msec = 0, 50
            
        if freq > 0:
            self.buzzer.freq(int(freq))
            self.buzzer.duty(50)
        
        self.play_background_delay_time = int(msec * 0.1)
        timer.init(period=int(msec * 0.9), mode=timer.ONE_SHOT,
                 callback=self.play_background_delay)

    def play_background_delay(self, timer):
        self.buzzer.duty(0)
        timer.init(period=self.play_background_delay_time, mode=timer.ONE_SHOT,
            callback=self.play_background)

    def play_background_restart(self):
        self.tune_idx = 0

    def play_background_stop(self):
        self.tune_idx = -1

    def next_char(self):
        if self.tune_idx < len(self.tune):
            char = chr(self.tune[self.tune_idx])
            self.tune_idx += 1
            if char == ',':
                char = ' '
            return char
        return '|'

    def notes(self):
        """Generator which generates notes. Each note is a tuple where the
           first element is the frequency (in Hz) and the second element is
           the duration (in milliseconds).
        """
        while True:
            # Skip blank characters and commas
            char = self.next_char()
            while char == ' ':
                char = self.next_char()

            # Parse duration, if present. A duration of 1 means a whole note.
            # A duration of 8 means 1/8 note.
            duration = 0
            while char.isdigit():
                duration *= 10
                duration += ord(char) - ord('0')
                char = self.next_char()
            if duration == 0:
                duration = self.default_duration

            if char == '|':  # marker for end of tune
                if self.repeat_play:
                    if self.repeat_play_startidx:
                        self.tune_idx = self.repeat_play_startidx
                    else:
                        self.tune_idx = 0
                    yield 0, 50
                else:
                    return

            note = char.lower()
            if 'a' <= note <= 'g':
                note_idx = ord(note) - ord('a')
            elif note == 'h':
                note_idx = 1    # H is equivalent to B
            else:
                note_idx = 7    # pause
            char = self.next_char()

            # Check for sharp note
            if char == '#':
                note_idx += 8
                char = self.next_char()

            # Check for duration modifier before octave
            # The spec has the dot after the octave, but some places do it
            # the other way around.
            duration_multiplier = 1.0
            if char == '.':
                duration_multiplier = 1.5
                char = self.next_char()

            # Check for octave
            if '4' <= char <= '7':
                octave = ord(char) - ord('0')
                char = self.next_char()
            else:
                octave = self.default_octave

            # Check for duration modifier after octave
            if char == '.':
                duration_multiplier = 1.5
                char = self.next_char()

            freq = NOTE[note_idx] * (1 << (octave - 4))
            msec = (self.msec_per_whole_note / duration) * duration_multiplier

            # print('note ', note, 'duration', duration, 'octave', octave, 'freq', freq, 'msec', msec)

            yield freq, msec
