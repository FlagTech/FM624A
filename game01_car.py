from machine import ADC,SPI,PWM,Pin
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

redCar = Character([c1,c2], 13, 17, screen, LCD.RED)
bluCar = Character([c1,c2], 13, 17, screen, LCD.BLUE)

# 宣告全域變數
end=False
score=0

# 建立常用函式
def resetGame():
    global end,score
    redCar.show(60,140)
    bluCar.show(randint(redCar.x-20,redCar.x+20),-20)
    screen.text(30,70, "Game Over",LCD.BLACK)
    end=False
    score=0
    printScore()

def printScore():
    global score
    screen.text(10, 5, "score:"+str(score)+'   ')

resetGame()    
printScore()

while True:
    key=getKey(adc.read())
    if not end :
        # 控制紅車
        if key=='r':
            redCar.move(3+score//2,0)
            toot()
        elif key=='l':
            redCar.move(-3-score//2,0)
            toot()
        else :
            redCar.plot()
        
        # 藍車移動 
        bluCar.move(0,3+score//2)

        # 超越藍車得分
        if bluCar.y>170 :
            score+=1
            ding()
            printScore()
            bluCar.show(randint(redCar.x-20,redCar.x+20),-20)
            if bluCar.x<0 : bluCar.x=0
            if bluCar.x>110 : bluCar.x=110
            
        if 20<bluCar.y<40:
            printScore()

        # 發生車禍，遊戲結束
        if redCar.touch(bluCar) or \
           redCar.x<0 or redCar.x>115 :
            buzz()
            screen.text(30,70, "Game Over",LCD.YELLOW)
            end=True
            
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