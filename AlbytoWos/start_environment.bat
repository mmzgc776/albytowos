@echo on

cd C:\Users\user\AppData\Local\Android\Sdk\emulator
C:
start "" emulator @Pixel_7_Pro_API_34
timeout /t 20
::echo "Please choose the port"
::set /p port=Port:
::adb connect xxx.xxx.xxx.xxx:%port%

start "" appium --base-path /wd/hub
