from machine import ADC,SPI,PWM
from FlagArcade import *
import LCD

# 螢幕初始設定
spi = SPI(1, baudrate=40000000)
screen = LCD.LCD(spi, 15, 5, 0)
screen.init()
screen.clearLCD()

# 按鈕腳位設定
adc = ADC(0)

# 蜂鳴器腳位與強度設定
buzzer = PWM(Pin(4))
amp = 512

# 搖桿音效設計
def toot():
    buzzer.freq(494)
    buzzer.duty(amp)
    time.sleep(.05)
    buzzer.duty(0)

# 賽車造型設計
c1=(
b"   1111111   "
b" 11111111111 "
b"     111     "
b" 1   111   1 "
b"1 1  111  1 1"
b" 1 1111111 1 "
b"1 1  111  1 1"
b" 1   1 1   1 "
b"    11 11    "
b"1 1 1   1 1 1"
b" 1  1   1  1 "
b"1 111 1 111 1"
b" 1  11111  1 "
b"1 1 11111 1 1"
b"    1   1    "
b"  111111111  "
b"1111111111111"
)
c2=(
b"   1111111   "
b" 11111111111 "
b"     111     "
b"1 1  111  1 1"
b" 1   111   1 "
b"1 111111111 1"
b" 1   111   1 "
b"1 1  1 1  1 1"
b"    11 11    "
b" 1  1   1  1 "
b"1 1 1   1 1 1"
b" 1 11 1 11 1 "
b"1 1 11111 1 1"
b" 1  11111  1 "
b"    1   1    "
b"  111111111  "
b"1111111111111"
)

car= Character([c1,c2], 13, 17, screen, LCD.RED)
car.show(60,140)


    
while True:
    key=getKey(adc.read())
    if key == "r":
        car.move(3,0)
        toot()
    elif key == "l":
        car.move(-3,0)
        toot()
    elif key == "set":
        if amp == 512 :
            amp = 0
        else :
            amp = 512
    else :
        car.plot()
