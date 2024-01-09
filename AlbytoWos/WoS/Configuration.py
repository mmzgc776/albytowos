import os

class Configuration:
    Environment = 'Test'

    basedir = os.path.abspath(os.path.join(__file__, ".."))
    #print(basedir)
    DateFormat = '%d/%m/%Y'
    HourFormat = "%H%M%S"

    devices_resources = basedir #+ u"/resources/devices/"

    if Environment == 'Local':
        device = "MyPhone"
        port = 4723
        local = f"http://127.0.0.1:{port}/wd/hub"
        appPackage = "com.livingroomofsatoshi.wallet"
        appActivity = ".MainActivity"


    if Environment == 'Test':
        #app = basedir + u'/resources/binaries/apkpureT.com.apk'        
        device = "PixelPro"
        port = 4723
        local = f"http://127.0.0.1:{port}/wd/hub"
        appPackage = "com.livingroomofsatoshi.wallet"
        appActivity = ".MainActivity"
