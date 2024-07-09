"""
@package core

"""

#todo connection here
#establishing connection TODO
#Ip rotation TODO
#proxy usage and rotation TODO
#user agent switching TODO

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from utils import Util

BASE_URL = "https://sslproxies.org/" #settings.SHOPIFY_ADMIN_LINK
#Transform into array
utils = Util()
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15"
proxies=[]    
ips_xpath = "//table[@class='table table-striped table-bordered']/tbody/tr/td[1]"
ports_xpath = "//table[@class='table table-striped table-bordered']/tbody/tr/td[2]"
class WebDriverFactory():

    def __init__(self, browser):
        self.browser = browser
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_argument(f"--user-agent={user_agent}")
        self.chrome_options.add_argument("--headless=new")
        self.chrome_options.add_experimental_option("useAutomationExtension", False) 
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        

    def getWebDriverInstance(self, baseURL=BASE_URL, logger_cb: callable=print()):
        if self.browser == "chrome":
            driver = webdriver.Chrome(options=self.chrome_options)
            driver = self.mask_ip_address(driver,logger_cb=logger_cb)
        else:
            driver = webdriver.Chrome(options=self.chrome_options)
            driver = self.mask_ip_address(driver, logger_cb=logger_cb)
      
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") 
        driver.implicitly_wait(5)
        driver.maximize_window()
        driver.get(baseURL)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") 
        
        return driver
    
    def mask_ip_address(self, driver,logger_cb:callable):
        driver.get(BASE_URL)
        driver.execute_script("return arguments[0].scrollIntoView(true);", WebDriverWait(driver, 20, poll_frequency=0.5).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='list']/div/div[2]/div/table/thead/tr/th[1]"))))
        ips = [my_elem.get_attribute("innerHTML") for my_elem in WebDriverWait(driver, 5, poll_frequency=0.5).until(EC.visibility_of_all_elements_located((By.XPATH, ips_xpath)))]
        ports = [my_elem.get_attribute("innerHTML") for my_elem in WebDriverWait(driver, 5, poll_frequency=0.5).until(EC.visibility_of_all_elements_located((By.XPATH, ports_xpath)))]
        driver.quit()
        for i in range(0, len(ips)):
            proxies.append(ips[i]+':'+ports[i])
        for i in range(0, len(proxies)):
            try:
                
                utils.log.info(f"Configurando conexion del bot con Proxy IP {proxies[i]}")
                # 189.240.60.169:9090
                self.chrome_options.add_argument('--proxy-server={}'.format(proxies[i]))
                driver = webdriver.Chrome(options=self.chrome_options)
                driver.get("https://www.whatismyip.com/proxy-check/?iref=home")
                
                validator_el= WebDriverWait(driver, 10, poll_frequency=0.5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div#return-date ul li")))
                validator_str = validator_el.get_attribute("innerText")
                if "Proxy Detected" in validator_str:
                    utils.log.info(f"Proxy configurado exitosamente {proxies[i]}")
                    logger_cb()
                    break
            except Exception as e:
                utils.log.info(f"Reintentando configuracion de red...")
                logger_cb()
                driver.quit()

        #config everything here
        n_driver = webdriver.Chrome(options=self.chrome_options) 
        return n_driver