from machine import SPI,ADC
import LCD
from FlagArcade import *

# 螢幕初始設定
spi = SPI(1, baudrate=40000000, polarity=0, phase=0)
screen = LCD.LCD(spi, 15, 5, 0)
screen.init()
screen.clearLCD()

h1=(
b"  111   111  "
b" 1   1 1   1 "
b"1     1     1"
b"1           1"
b"1           1"
b" 1         1 "
b"  1       1  "
b"   1     1   "
b"    1   1    "
b"     1 1     "
b"      1      "
)
h2=(
b"             "
b"  111   111  "
b" 1   1 1   1 "
b" 1    1    1 "
b" 1         1 "
b"  1       1  "
b"   1     1   "
b"    1   1    "
b"     1 1     "
b"      1      "
b"             "
)

h3=(
b"             "
b"             "
b"   11   11   "
b"  1  1 1  1  "
b"  1   1   1  "
b"   1     1   "
b"    1   1    "
b"     1 1     "
b"      1      "
b"             "
b"             "
)

heart= Character([h1,h2,h3], 13, 11, screen, LCD.RED)
heart.show(20,20)

while True:
    heart.plot()
    heart.move(2,0)
    if heart.x>100 :
        #heart.plot(x1=-13)
        heart.x=-13