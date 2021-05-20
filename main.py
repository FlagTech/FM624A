import os

autorun_filename = "autorun"
game_filename = ""

try:
    with open(autorun_filename, 'r') as f:
        game_filename = f.read()
        
    os.remove(autorun_filename)
    
    __import__(game_filename)

# except OSError: # 找不到檔案
#     pass
# except ValueError: # import 錯誤
#     pass

except:
    __import__("menu")
