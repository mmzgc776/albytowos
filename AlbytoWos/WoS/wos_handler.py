from WoS.wos_functions import Functions
from WoS.wos_pages import WoS
from WoS.wos_api import wos_api_handler
from appium.webdriver.common.appiumby import AppiumBy
import time
import lnurl

MainWoS = WoS()

class StepsDefinitions():    

    def __init__(self, verbose):        
        self.verbose = verbose   

    def close_app(context):
        Functions.close_application(context)

    def open_app(context):
        desired_caps = Functions.get_capabilities(context)
        #print ("-")
        #print (desired_caps)
        #print ("-")
        Functions.get_driver(context, capabilities=desired_caps)
        time.sleep(3)

    def list_ui_elements(context):
        elements = Functions.list_elements(context)
        for element in elements:        
            print ("---")    
            print (element.get_attribute("class"))            
            print (element.get_attribute("text"))            
            print (element.get_attribute("resourceId"))    
            print (element.get_attribute("resource-id"))            
            print ("---")
            #print (element.Name)
            #print (element.TagName)       

    def get_balance(context):
        text = Functions.get_balance_text(context)
        text=text.split(" ")
        balance_text = text[0] 
        balance = int(balance_text.replace(",", ""))
        return balance
    
    def get_invoice_lnurl(context, invoice_amount):
        invoice = "test string"
        #lnurl
        lnurl_string = "" #your wos lnurl
        url = lnurl.decode(lnurl_string)
        wos_api = wos_api_handler(context.verbose)        
        response = wos_api.get_callback(url)
        #Handle internal server error 500
        while response==500:
            #Wait to aws instance to settle again this has been observed to work again after 2.5 hours
            print("Waiting for endpoint to settle back")
            time.sleep(60*30) # Half hour
            response = wos_api.get_callback(url)

        callback = response['callback']        
        response = wos_api.get_invoice_with_callback(callback, invoice_amount)

        while response==500:
            #Wait to aws instance to settle again this has been observed to work again after 2.5 hours
            print("Waiting for endpoint to settle back")
            time.sleep(60*60) # 1 hour
            response = wos_api.get_invoice_with_callback(callback, invoice_amount)
        invoice = response['pr']  

        return invoice
    
    def pay_invoice(context):
        #put the invoice in clipboard
        #click on send       
        Functions.click_send_button(context)
        #click on paste from clipboard              
        Functions.click_paste(context)
        #click on send        
        Functions.click_send_button2(context)
        return

    def get_invoice_appium():
        #print(invoice)
        #print (invoice_amount, " ", invoice, " ", lnurl)
        #click receive
        #click in copy to get lnurl to clipboard
        #click in the cross to get back to main screen
        #click receive
        #click on thunder button
        #click on amount button
        #digit the desired amount
        #click generate invoice
        #click in copy to get invoice to clipboard
        #click in the cross to get back to main screen
        pass