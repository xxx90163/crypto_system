import os
import time

while True:
    os.system("git add steelx_live.json")
    os.system('git commit -m "auto update"')
    os.system("git push")

    print("🚀 已推送 GitHub")

    time.sleep(60)  # 每1分鐘推一次
