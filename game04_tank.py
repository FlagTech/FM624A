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
t1=(
b"     111     "
b"     111     "
b"      1      "
b"11    1    11"
b"      1      "
b"11111 1 11111"
b"  111 1 111  "
b"1111 111 1111"
b"  1 11 11 1  "
b"111 1   1 111"
b"  1 11111 1  "
b"1111 111 1111"
b"  111   111  "
b"1111111111111"
b"             "
b"11         11"
b"             "
)
t2=(
b"     111     "
b"     111     "
b"      1      "
b"      1      "
b"11    1    11"
b"  111 1 111  "
b"11111 1 11111"
b"  11 111 11  "
b"111 11 11 111"
b"  1 1   1 1  "
b"111 11111 111"
b"  11 111 11  "
b"11111   11111"
b"  111111111  "
b"11         11"
b"             "
b"11         11"
)
uf=(
b" 1 "
b"111"
b"111"
b"1 1"
)
# -----------------
e1=(
b"             "
b"11         11"
b"             "
b"1111111111111"
b"  111   111  "
b"1111 111 1111"
b"  1 11111 1  "
b"111 1   1 111"
b"  1 11 11 1  "
b"1111 111 1111"
b"  111 1 111  "
b"11111 1 11111"
b"      1      "
b"11    1    11"
b"      1      "
b"     111     "
b"     111     "
)
e2=(
b"11         11"
b"             "
b"11         11"
b"  111111111  "
b"11111   11111"
b"  11 111 11  "
b"111 11111 111"
b"  1 1   1 1  "
b"111 11 11 111"
b"  11 111 11  "
b"11111 1 11111"
b"  111 1 111  "
b"11    1    11"
b"      1      "
b"      1      "
b"     111     "
b"     111     "
)
df=(
b"1 1"
b"111"
b"111"
b" 1 "
)

redTank = Character([t1,t2], 13, 17, screen, LCD.RED)
purFire = Character(uf, 3, 4, screen, LCD.PURPLE)

bluTank = Character([e1,e2], 13, 17, screen, LCD.BLUE)
cyaFire = Character(df, 3, 4, screen, LCD.CYAN)

# 宣告全域變數
end=False
score=0
dx=-3

# 建立常用函式
def resetGame():
    global end,score
    redTank.show(60,140)
    bluTank.show(60,20)
    purFire.show(150,-50)
    cyaFire.show(-20,180)
    screen.text(30,70, "Game Over",LCD.BLACK)
    end=False
    score=0

def printScore():
    global score 
    screen.text(10, 5,"score:"+str(score)+'   ')
    
resetGame()
printScore()

while True:
    key=getKey(adc.read())
    if not end :
        # 控制紅坦克
        if key=='r' and redTank.x<110 :
            redTank.move(3,0)
            toot()
        elif key=='l' and redTank.x>0:
            redTank.move(-3,0)
            toot()
        else:
            redTank.plot()
        
        # 敵方藍坦克移動
        bluTank.move(dx,0)
        if bluTank.x>120:
            dx=-3
        if bluTank.x<0:
            dx=3
            
        # 紅坦克手動發射砲彈        
        if key=="m" and purFire.y<=-10:
            ding()
            purFire.show(redTank.x+5,redTank.y-10)
            printScore()           
        if purFire.y>-10:
            purFire.move(0,-10)
        else:
            purFire.show(150,-50)
            purFire.hide()
            
        # 藍坦克自動發射砲彈
        if cyaFire.y<160 :
            cyaFire.move(0,10)
        elif cyaFire.y>=160 and abs(bluTank.x-redTank.x)<5:
            ding()
            cyaFire.show(bluTank.x+5,bluTank.y+10)
        
        # 紅坦克被打到，遊戲結束
        if redTank.touch(cyaFire):
            cyaFire.show(60,190)
            buzz()
            screen.text(30,70, "Game Over",LCD.YELLOW)
            end=True
            
        # 打到藍坦克得分
        if bluTank.touch(purFire):
            purFire.show(150,-50)
            purFire.hide()
            score+=1
            buzz()
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