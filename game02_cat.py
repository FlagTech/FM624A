from machine import ADC,SPI,PWM,Pin,freq
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

# 設計遊戲音效
def ding():
    buzzer.freq(988)
    buzzer.duty(amp)
    time.sleep(.05)
    buzzer.duty(0)

def toot():
    buzzer.freq(494)
    buzzer.duty(amp)
    time.sleep(.01)
    buzzer.duty(0)
    
def buzz():
    buzzer.freq(247)
    buzzer.duty(amp)
    time.sleep(.5)
    buzzer.duty(0)

# 建立遊戲角色
cl1=(
b"   1   1         11 "
b"  11   11        11 "
b" 111111111        1 "
b" 11 111 11       11 "
b"111 111 11111 1 11  "
b" 1111 1111 11 1 111 "
b"1111   111111111111 "
b"  1111111 111111111 "
b"         1111111111 "
b"      111111111111  "
b"      11       11   "
)
cl2=(
b"  1     1       11  "
b"  11   11       11  "
b" 111111111       1  "
b" 11 111 11       1  "
b"111 111 11111 1 11  "
b" 1111 1111 11 1 111 "
b"1111   111111111111 "
b"  1111111 111111111 "
b"         1111111111 "
b"      111111111111  "
b"     1  1     1  1  "
)
# ------------------

cr1=(
b" 11        1     1  "
b" 11        11   11  "
b" 1        111111111 "
b"  1       11 111 11 "
b"  11 1 11111 111 111"
b" 111 1 11 1111 1111 "
b" 111111111111   1111"
b" 111111111 1111111  "
b" 1111111111         "
b"  111111111111      "
b"   11       11      "
)

cr2=(
b"  11        1   1   "
b"  11       11   11  "
b"  1       111111111 "
b"  1       11 111 11 "
b"  11 1 11111 111 111"
b" 111 1 11 1111 1111 "
b" 111111111111   1111"
b" 111111111 1111111  "
b" 1111111111         "
b"  111111111111      "
b"  1  1     1  1     "
)
# ------------------
m1=(
b"    1    "    
b"    1    " 
b"     1   "    
b"     1   " 
b"    1    "    
b"   111   "
b"  11111  "
b"  11111  "    
b"  11111  "
b" 1 111 1 "
b"111111111"
b" 11 1 11 "
b"   111   "
b"   111   "
b"   111   "
b"    1    "
b"    1    "
)
m2=(
b"    1    "    
b"    1    " 
b"   1     "    
b"   1     " 
b"    1    "    
b"   111   "
b"  11111  "
b"  11111  "    
b"  11111  "
b" 1 111 1 "
b"111111111"
b" 11 1 11 "
b"   111   "
b"   111   "
b"   111   "
b"    1    "
b"    1    "
)

righ = Character([cr1,cr2], 20, 11, screen, LCD.RED)
left = Character([cl1,cl2], 20, 11, screen, LCD.RED)
mouse = Character([m1,m2], 9, 17, screen, LCD.BLUE)
cat=righ

# 宣告全域變數
end=False
score=0
cx=60;cy=140
past='r'

# 建立常用函式
def resetGame():
    global end,score,cx,cy,cat,past
    left.hide()
    righ.hide()
    cat=righ
    past='r'
    cx=60;cy=140
    mouse.show(randint(0,110),20)
    screen.text(30,70, "Game Over",LCD.BLACK)
    end=False
    score=0
    printScore()

def printScore():
    global score 
    screen.text(10, 5,"score:"+str(score)+'   ')

resetGame()
printScore()

while True:
    key=getKey(adc.read())
    if not end :
        # 控制貓咪 
        if past!=key:
            cat.hide()
            past=key       
        if key=='r':
            toot()
            cat=righ
            cx=cx+3+score//2
        if key=='l':
            toot()
            cat=left
            cx=cx-3-score//2
        cat.show(cx,cy)
        
        # 老鼠移動 
        mouse.move(0,3+score//2)
        # 漏掉老鼠，遊戲結束
        if mouse.y>170:
            buzz()
            screen.text(30,70, "Game Over",LCD.YELLOW)
            end=True
            
        if 20<mouse.y<40:
            printScore()

        # 抓到老鼠得分
        if cat.touch(mouse):
            score+=1
            ding()
            mouse.show(randint(0,110),-20)
            printScore()
    
    # 遊戲重啟
    if end :
        if key=="rst":
            resetGame()
            printScore()
    # 切換靜音
    if key=="set" :
        if amp == 512 :
            amp = 0
        else :
            amp = 512
    
    
