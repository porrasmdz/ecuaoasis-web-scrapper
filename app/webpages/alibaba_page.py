import logging_instance as cl
import logging
import urllib
import re
from models import Product, Pricing, Variant
from core.basepage import BasePage
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
class AlibabaPage(BasePage):

    log = cl.customLogger(logging.DEBUG, "logs/alibaba_scraping_results.log")

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

    # Locators
    _product_title = "//*[@id=\"container\"]/div[2]/div[1]/div[1]/div[1]/div/h1" 
    _product_description = "//*[@id=\"detail_decorate_root\"]/div[2]" #down on screen
    _product_images_div="//*[@id=\"container\"]/div[2]/div[1]/div[1]/div[4]/div/div/div[1]/div[2]" 
    _product_category = "" 
    _product_type = "//*[@id=\"container\"]/div[3]/nav/ul/li[4]/a" #bottom of page
    
    #Pricing Locators
    _product_prices=["//*[@id=\"container\"]/div[2]/div[1]/div[2]/div/div/div/div[5]/div/div/div[1]/div[2]",
                    "//*[@id=\"container\"]/div[2]/div[1]/div[2]/div/div/div/div[5]/div/div/div/span",
                    "//*[@id=\"container\"]/div[2]/div[1]/div[2]/div/div/div/div[5]/div/div[2]/div[1]/div[2]/span[1]"]
    _compare_at_price="//*[@id=\"container\"]/div[2]/div[1]/div[2]/div/div/div/div[5]/div/div/div[1]/div[2]"
    
    #Inventory Locators
    #Shipping Locators
    #Variants Locators
    _variants_div="//*[@id=\"container\"]/div[2]/div[1]/div[2]/div/div/div/div[6]/div/div[2]" #/div/div[1]/div[2]"
    _close_variants_icon="//*[@id=\"container\"]/div[2]/div[3]/div[3]"
    #Each option inside variants_div
    #Each name + value inside variant_options div
    _local_variant_name_locator="/div[1]/span/text()[1]"
    _local_variant_value_locator="/div[1]/span/span"
    _local_variant_clickables_div="/div[2]/div"
    _vendor = ""  ##Defined by user
    _collections = "" ##Defined by user
    _tags = "" ##Defined by user
    _language_button_locator="//*[@id=\"the-new-header\"]/div[1]/div[2]/div[3]/div[2]"
    _language_locator="//*[@id=\"popup-2\"]/div[2]/div[4]/div/div[1]/div[2]/input"
    _currency_locator="//*[@id=\"popup-2\"]/div[2]/div[6]/div/div[1]/div[2]/input"
    _language_save_button_locator="//*[@id=\"popup-2\"]/div[2]/div[7]/div"

    _country_button_locator="//*[@id=\"the-new-header\"]/div[1]/div[2]/div[3]/div[1]"
    _country_locator="//*[@id=\"popup-1\"]/div[2]/div[3]/div/div[1]/div[2]/input"
    _country_save_button_locator="//*[@id=\"popup-1\"]/div[2]/div[6]/button"
    
    def detectSwatchVariant(self,variantEl, header):
        header_text = header.get_attribute("innerText")
        return ":" not in header_text   
    def selectLanguageAndCurrency(self, target_language, target_currency):
        byType = self.getByType("xpath")
        WebDriverWait(self.driver, 60).until(
            EC.visibility_of_element_located((byType, self._language_button_locator))
        )
        location_button = self.findElement(self._language_button_locator)
        
        location_button.click()
        
        # self.driver.execute_script("arguments[0].click();", location_button)
       
        # language_input = self.findElement(self._language_locator)
        language_input = WebDriverWait(self.driver, 60).until(
            EC.visibility_of_element_located((byType, self._language_locator))
        )
        # language_input.click()
        
        self.driver.execute_script("arguments[0].click();", language_input)
        language_input.send_keys(target_language)
        language_input.send_keys(Keys.ENTER)
        
        # language_input = self.findElement(self._language_locator)
        currency_input = WebDriverWait(self.driver, 60).until(
            EC.visibility_of_element_located((byType, self._currency_locator))
        )
        
        self.driver.execute_script("arguments[0].click();", currency_input)
        
        currency_input = self.findElement(self._currency_locator)
        save_button = self.findElement(self._language_save_button_locator)
        currency_input.send_keys(target_currency)
        currency_input.send_keys(Keys.ENTER)
        
        # WebDriverWait(self.driver, 60).until(
        #     EC.element_to_be_clickable((byType, self._language_save_button_locator))
        # )
        
        self.driver.execute_script("arguments[0].click();", save_button)
        # save_button.click()

        byType= self.getByType("xpath")
        #Wait until page reloads
        WebDriverWait(self.driver, 10).until(
            EC.staleness_of(self.driver.find_element(byType, self._language_button_locator))
        )
        self.log.info("Finished selecting language")
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((byType, self._language_button_locator))
        )

        self.log.info("Refreshed page")
    def selectCountry(self, country):
        byType = self.getByType("xpath")
        print("Before click")
        
        country_button = WebDriverWait(self.driver, 60).until(
            EC.visibility_of_element_located((byType, self._country_button_locator))
        )
        
        country_button.click()
        print("Clicked")
        # language_input = self.findElement(self._language_locator)
        country_input = WebDriverWait(self.driver, 60).until(
            EC.visibility_of_element_located((byType, self._country_locator))
        )
        country_input.click()
        print("Writing in input")
        
        country_input.send_keys(country)
        country_input.send_keys(Keys.ENTER)
        save_button = self.findElement(self._country_save_button_locator)
        save_button.click()
        byType= self.getByType("xpath")
        #Wait until page reloads
        WebDriverWait(self.driver, 10).until(
            EC.staleness_of(self.driver.find_element(byType, self._country_button_locator))
        )
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((byType, self._country_button_locator))
        )
    def findPricing(self):
        for price in self._product_prices:
            try:
                price = self.findText(price)
                # compare_price = self.findText(self._compare_at_price)
                if "-" in price:
                    price = price.split("-")[0]
                    
                price = re.sub('[^0-9\.,]','', price)
                price = price.replace(",", ".")
                compare_price = re.sub('[^0-9\.,]','', price)
                compare_price = compare_price.replace(",", ".")
                self.log.info(f"Price and Compare-at-price FOUND: {price} {price}")
                return Pricing(price=price, compare_at_price=price)          
            except:
                self.log.info(f"Error extracting price")
        return Pricing(price=0, compare_at_price=0)
    def extractVariantHeader(self, element, resultsList: list):
        variant_name = element.get_attribute("innerText")
        
        curr_variant = Variant(option_name=variant_name, option_values=[])
        resultsList.append(curr_variant)
        return curr_variant 
    def extractVariantFromElement(self, children: list, curr_variant, element, previous_html_header, resultsList: list):
        byType = self.getByType("xpath")
        if (self.detectSwatchVariant(children,previous_html_header)):
            self.driver.execute_script("arguments[0].click();", children[0])
            children = self.getElementList("//*[@id=\"container\"]/div[2]/div[3]/div[2]/div/div[1]/div[2]/div[1]/div[3]/*",byType)
            print("Scraping swatch and length is "+ str(len(children)))
            for child in children:
                print(f"class={child.get_attribute('class')} tag={child.tag_name}")
                
                self.log.info("Extracting variant value of type swatch")
                attribute_element =  child.find_element(byType, "./div/span/span/span")
                
                print(f"class={attribute_element.get_attribute('class')} tag={attribute_element.tag_name}")
                var_value = attribute_element.get_attribute("innerText")
                
                self.log.info(var_value)
                resultsList.append(var_value)
                #TODO: append variant prices
            close_icon = self.getElement(self._close_variants_icon, byType)
            close_icon.click()

        else:
            curr_variant.option_name = curr_variant.option_name.split(":")[0]
            for child in children:        
                #do something
                try:
                    self.log.info("Extracting variant value of type common")
                    self.driver.execute_script("arguments[0].click();", child)
                    WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located(("xpath",self._close_variants_icon)))
                    close_icon = self.getElement(self._close_variants_icon, byType)
                    close_icon.click()
                    variant_value = previous_html_header.get_attribute('innerText').split(":")
                    variant_value= variant_value[1]
                    self.log.info(variant_value)
                    resultsList.append(variant_value)
                except:
                    self.log.info(f"Error extracting value from variant {curr_variant.option_name}")
    def findVariants(self, locator):
        try:
            variants_div = self.findElement(locator)
            self.log.info("Variants container div FOUND with locator: " + locator)
            byType = self.getByType("xpath")
            variants = variants_div.find_elements(byType, "./*")
            self.log.info(f"Found {len(variants)//2} variants")
            previous_html_header=None
            result_variants = []
            curr_variant = None
            while len(variants) > 0:
                element = variants.pop(0)
                tag= element.tag_name

                
                self.log.info(f"{str(curr_variant)} {str(tag)} ")
                if tag in ("h1","h2","h3","h4","h5"):
                    curr_variant = self.extractVariantHeader(element, result_variants)
                    previous_html_header = element
                else:
                    var_values = []
                    children = element.find_elements(byType,"./*")
                    self.extractVariantFromElement(children=children, curr_variant=curr_variant,element=element, previous_html_header=previous_html_header, resultsList=var_values)
                    curr_variant.option_values = var_values
            
            if len(result_variants) > 0:
                self.log.info(f"Variants FOUND with {byType}: " + "div")
                self.log.info("Extracted Variants: "+ str(result_variants))
            else:
                self.log.info(f"Variants NOT FOUND with {byType}: "+ "div")
            return result_variants
        except:
            self.log.info(f"Error para extraer variantes del producto")
    def scrapProductInfo(self,logger_cb:callable=print()):
        try:
            self.selectLanguageAndCurrency("Español","USD - US Dollar")
            self.selectCountry("Ecuador")
            self.logProcessStep("Extrayendo Información General")
            logger_cb()
            title = self.findText(self._product_title)
            
            # s= input("Oprima ENTER para seguir")
            self.logProcessStep("Extrayendo imagenes")
            logger_cb()
            image_els = self.findImagesWithin(self._product_images_div)
            
            # s= input("Oprima ENTER para seguir")
            self.logProcessStep("Extrayendo Precios del Producto")
            logger_cb()
            pricing = self.findPricing()
            
            # s= input("Oprima ENTER para seguir")
            self.logProcessStep("Extrayendo variantes del Producto")
            logger_cb()
            variants = self.findVariants(self._variants_div)
            

            # s= input("Oprima ENTER para seguir")
            self.logProcessStep("Descargando Imagenes")
            logger_cb()
            image_paths = self.downloadImageFromDiv(image_els, product_title=title)
            

            # s= input("Oprima ENTER para seguir")
            self.logProcessStep("Extrayendo descripcion, tipo de producto")
            logger_cb()
            try:
                self.scrollToElement(self._product_description)
                des_element = self.findElement(self._product_description)
                description = des_element.get_attribute("innerHTML")
                type_el = self.findElement(self._product_type)
                p_type = type_el.get_attribute("innerText") 
            except:
                self.log.info("Error extracting description and type")
            
            self.logProcessStep("RESULTADO:")
            logger_cb()
            #TODO: add inventory details to products (because some are unavailable)
            product = Product(title=title, description=description, images_link=image_paths,
                              pricing=pricing, product_type=p_type, variants=variants)
            
            self.log.info(f"Extracción exitosa del producto {product.title}")
            self.log.info(f"Resultado {product.model_dump()}")
            logger_cb()
            return product

        except Exception as e:
            self.log.error(f"Error al extraer informacion de un producto en ALIBABA : {str(e)}")
            logger_cb()
    def getPageTitle(self):
        return self.getTitle()