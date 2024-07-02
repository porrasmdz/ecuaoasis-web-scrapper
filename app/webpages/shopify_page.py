import sys
from config import settings
sys.path.append(settings.ROOT_ABSOLUTE_PATH)
import logging_instance as cl
import logging
from core.basepage import BasePage

class ShopifyPage(BasePage):

    log = cl.customLogger(logging.DEBUG,"shopify_scraping.log")

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

    # Locators
    _shop_card = "/html/body/div/div[1]/div[2]/main/div/section/div/div/div/div/section/ul/li/a/div/div[1]"#"//*[@id=\"account_email\"]"
    _login_link = "" #"//*[@id=\"account_lookup\"]/div[5]/button"
    _captcha_card="//*[@id=\"h-captcha\"]"

    _email_field = "//*[@id=\"account_email\"]"
    _email_button = "//*[@id=\"account_lookup\"]/div[5]/button"
    _password_field = "//*[@id=\"account_password\"]"
    _password_button = "//*[@id=\"login_form\"]/div[2]/div[4]/button"

    def clickLoginLink(self):
        self.elementClick(self._login_link, locatorType="xpath")

    def isCaptchaTriggered(self):
        return self.isElementDisplayed(self._captcha_card, locatorType="xpath")

    def enterEmail(self, email):
        self.waitForElement(self._email_field, locatorType="xpath")
        self.sendKeys(email, self._email_field, locatorType="xpath")

    def enterPassword(self, password):
        self.waitForElement(self._password_field, locatorType="xpath")
        self.sendKeys(password, self._password_field)
    
    def clickLoginButton(self):
        
        self.waitForElement(self._email_button, locatorType="xpath")
        self.elementClick(self._email_button, locatorType="xpath")

    def clickPasswordButton(self):
        self.waitForElement(self._password_button, locatorType="xpath")
        self.elementClick(self._password_button, locatorType="xpath")

    def attempt_login(self, email="", password=""):
        try:
            # self.clickLoginLink()
            self.enterEmail(email)
            if (self.isCaptchaTriggered()):
                self.log.warning("Captcha triggered")
            
        except:
            print("No se pudo hacer login")

    def verifyLoginTitle(self):
        return self.verifyPageTitle("Shopify")