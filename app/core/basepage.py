"""
@package core

Base Page class implementation
It implements methods which are common to all the pages throughout the application

This class needs to be inherited by all the page classes
This should not be used by creating object instances

Example:
    Class LoginPage(BasePage)
"""
import sys 
import re
from config import settings
sys.path.append(settings.ROOT_ABSOLUTE_PATH)
from core.web_driver import SeleniumDriver
from traceback import print_stack
from utils import Util
from pathlib import Path
import requests

class BasePage(SeleniumDriver):

    def __init__(self, driver):
        """
        Inits BasePage class

        Returns:
            None
        """
        super(BasePage, self).__init__(driver)
        self.driver = driver
        self.util = Util()

    def logProcessStep(self,title):
        sep = "====================================================================="
        p_title = f"============={title}"
        self.log.info(sep)
        self.log.info(p_title)
        self.log.info(sep)
        print(sep)
        print(p_title)
        print(sep)
        
    def verifyPageTitle(self, titleToVerify):
        """
        Verify the page Title

        Parameters:
            titleToVerify: Title on the page that needs to be verified
        """
        try:
            actualTitle = self.getTitle()
            return self.util.verifyTextContains(actualTitle, titleToVerify)
        except:
            self.log.error("Failed to get page title")
            print_stack()
            return False
    

    def findElement(self,locator):
        self.waitForElement(locator, locatorType="xpath")
        return self.getElement(locator, locatorType="xpath")

    def findText(self,locator):
        self.waitForElement(locator, locatorType="xpath")
        return self.getText(locator, locatorType="xpath")

    def findImagesWithin(self, locator):
        images_div = self.findElement(locator)
        
        self.log.info("Image container div FOUND with locator: ")
        byType = self.getByType("css")
        images = images_div.find_elements(byType, "img")
        if len(images) > 0:
            self.log.info(f"Images FOUND with {byType}: " + "img")
        else:
            self.log.info(f"Images NOT FOUND with {byType}: "+ "img")
        return images
   
    

    def downloadImageFromDiv(self, image_els,product_title: str):
        paths= []

        for image in image_els:
            image_index = image_els.index(image)
            src = image.get_attribute('src')
            product_name = f"{product_title.strip(' ')}"
            product_name = re.sub('[^A-Za-z0-9]+', '', product_name)
            filename = f"image-{image_index}.png"
            path=f"products/{product_name}/{filename}"
            paths.append(path)

            file = Path(path)
            file.parent.mkdir(parents=True, exist_ok=True)
        
            r = requests.get(src, stream=True)
            if r.status_code == 200:
                with open(path, 'wb') as f:
                    for chunk in r:
                        f.write(chunk)
        if len(paths)>0:
            self.log.info(f"Sucessfully download images: " + str(paths))
        else:
            self.log.info(f"No image was imported")
        return paths
    
    def scrapProductInfo(self,link):
        """
        Verify the page Title

        Parameters:
            titleToVerify: Title on the page that needs to be verified
        """
        try:
            return self.util.verifyTextContains(link)
        except:
            self.log.error("Failed to get page title")
            print_stack()
            return False