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
b1=(
b"         111        "    
b"         111        "    
b"         111        "    
b"         1          "
b"        111    1    "
b"       11 111 1     "
b"      11     1 1    "
b"      1111111  1    "
b"  111   1  1   111  "
b" 1 1 1   11   1 1 1 "
b"1  1  1   1  1  1  1"
b"1111111   1  1111111"
b"1  1  1   11 1  1  1"
b" 1 1 1        1 1 1 "
b"  111          111  "
)

b2=(
b"          111       "    
b"          111       "    
b"          111       "    
b"         1          "
b"        111    1    "
b"       11 111 1     "
b"      11     1 1    "
b"      111      1    "
b"  111    11    111  "
b" 1   1     11 1   1 "
b"1 1 1 1  11  1 1 1 1"
b"1  1  1 111  1  1  1"
b"1 1 1 1      1 1 1 1"
b" 1   1        1   1 "
b"  111          111  "
)

hy=(
b"    1111    "
b"   111111   "
b"    1111    "
b"  11111111  "
b"  11111111  "
b"    1111    "
b"    1111    "
b"    1111    "
b"    1111    "
b"    1111    "
)

r1=(
b"     111     "
b"    1111     "
b"     111     "
b"      1      "
b"    11111    "
b" 1 1 111 1   "
b"  1  111  1  "
b"     111 1   "
b"    1  1     "
b"   1    1    "
b"   1     11  "
b"   1         "
)
r2=(
b"             "
b"     111     "
b"    1111     "
b"     111     "
b"     111     "
b"     1111    "
b"   11111     "
b"     111     "
b"     1 1     "
b"    1 1      "
b"    1 1      "
b"     1 1     "
)

hydrant = Character(hy, 12, 10, screen , LCD.RED)
bicycle = Character([b1,b2], 20, 15, screen,LCD.YELLOW)
running = Character([r1,r2], 13, 12, screen,LCD.BLUE)
obstacle = hydrant

# 宣告全域變數
end = False
score=0
jump = False
vx=10;vy=0

# 建立常用函式
def resetGame():
    global end,score,obstacle,vx
    bicycle.show(10, 145)
    hydrant.show(150, 148)
    running.show(150, 148)
    vx=10
    obstacle = hydrant
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
    if not end:
        # 腳踏車起跳
        if key=='m' and jump==False:
            jump=True
            toot()
#             if vy==0:
            vy=-6
            
        # 跳躍過程中
        if jump:
            bicycle.move(0,vy)
            vy+=1
        else:
            bicycle.plot()
           
        # 著地瞬間
        if bicycle.y>145:
            vy=0
            bicycle.show(10,145)
            jump=False    

        # 障礙物相對向後
        obstacle.move(-vx)
        
        # 越過障礙物得分
        if obstacle.x<-20:
            ding()
            score+=1
            # 更換障礙物
            if score>10:
                obstacle=running
                vx=13
            obstacle.show(150,148)
            printScore()       
           
        # 發生車禍，遊戲結束
        if bicycle.touch(obstacle):
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
