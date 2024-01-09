import WoS.Configuration as Configuration
from appium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By
import time
import pytest
import json

config = Configuration.Configuration()

class Functions:

    def __init__(self):
        self.json_strings = {}
        self.device = {}
        self.desired_caps = {}
        self.driver = None


    def get_json_file(self, file, path=config.devices_resources):
        json_path = path + "/" + file + '.json'
        #print (json_path)
        try:
            with open(json_path, "r") as read_file:
                self.json_strings = json.loads(read_file.read())
                return self.json_strings
        except FileNotFoundError:
            pytest.skip(u"get_json_file: No se encontro el Archivo " + file)
            return False

    def get_device(self, entity):
        if self.json_strings is False:
            pytest.skip(u"Define el device para esta prueba " + entity)
        else:
            try:
                self.device = self.json_strings[entity]
                return self.device
            except KeyError:
                pytest.skip(u"get_device: No se encontro el device al cual se hace referencia: " + entity)

    def get_capabilities(self, test_device=config.device):
        Functions.get_json_file(self, "Devices")
        #print(config)
        self.desired_caps = Functions.get_device(self, test_device)    
        self.desired_caps['appPackage'] = config.appPackage
        self.desired_caps['appActivity'] = config.appActivity        
        return self.desired_caps

    def get_driver(self, capabilities,  local_server=config.local):
        capabilities_options = UiAutomator2Options().load_capabilities(capabilities)
        self.driver = webdriver.Remote(local_server, capabilities, options=capabilities_options)
        return self.driver

    def setText(self, locator, text):
        try:
            Functions.implicit_wait_visible(self,locator)
            self.driver.find_element(*locator).send_keys(text)
        except ValueError:
            print("The element is not clickable/editable")

    def implicit_wait_visible(self, locator):
        try:
            wait = WebDriverWait(self.driver, 20)
            wait.until(EC.visibility_of_element_located(locator))            
        except TimeoutError:
            print("The element didn't appeared")

    def explicit_wait(self, secs):
        time.sleep(secs)

    def check_itsrunning(self):
        activity = self.driver.current_activity
        assert ".MainActivity" == activity,f"The main activity name is wrong"

    def click_element(self, locator):
        try:
            Functions.implicit_wait_visible(self, locator)
            self.driver.find_element(*locator).click()
        except TimeoutError:
            print("The element didn't appeared")

    def list_elements(self):    
        elements = self.driver.find_elements(By.XPATH, "//*")
        return elements
    
    def wait_for_text(self, locator):
        try:
            Functions.implicit_wait_visible(self,locator)  
            element = self.driver.find_element(*locator)           
        except ValueError:
            print("The element didn't appeared")
        return element

    def get_balance_text(self):       
        locator = (By.XPATH, "//android.widget.TextView[contains (@text, 'sats')][1]")
        element = Functions.wait_for_text(self, locator)
        balance = element.get_attribute("text")        
        return (balance)
    
    def click_send_button(self):
        locator = (By.XPATH, "//android.widget.Button[@text='scan Send']")        
        Functions.click_element(self, locator)
        

    def click_send_button2(self):
        locator = (By.XPATH, "//android.widget.Button[@text='Send']")
        Functions.click_element(self, locator)             
        

    def click_paste(self):
        locator = (By.XPATH, "//android.widget.Button[@text='custom paste']")
        Functions.click_element(self, locator)

    def close_application(self):
        #self.driver.close_app()
        self.driver.quit()