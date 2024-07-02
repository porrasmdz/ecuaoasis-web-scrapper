import logging_instance as cl
import logging
import re
from models import Product, Pricing, Variant
from core.basepage import BasePage

class AliexpressPage(BasePage):

    log = cl.customLogger(logging.DEBUG,"logs/aliexpress_scraping_results.log")

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

    # Locators
    _product_title = "/html/body/div[5]/div/div[3]/div/div[1]/div[1]/div[2]/div[4]/h1" 
    _product_description = "//*[@id=\"product-description\"]/div/div/div" #"//*[@id=\"account_lookup\"]/div[5]/button"
    _product_images_div="/html/body/div[5]/div/div[3]/div/div[1]/div[1]/div[1]/div/div" #//*[@id=\"h-captcha\"]"
    _product_category = "" 
    _product_type = "" 
    
    #Pricing Locators
    _product_price="/html/body/div[5]/div/div[3]/div/div[1]/div[1]/div[2]/div[1]/div[1]/div"
    _compare_at_price="/html/body/div[5]/div/div[3]/div/div[1]/div[1]/div[2]/div[1]/div[2]/span[1]"
    
    #Inventory Locators
    #Shipping Locators
    #Variants Locators
    _variants_div="//*[@id=\"root\"]/div/div[3]/div/div[1]/div[1]/div[2]/div[7]" #/div/div[1]/div[2]"
    
    #Each option inside variants_div
    #Each name + value inside variant_options div
    _local_variant_name_locator="/div[1]/span/text()[1]"
    _local_variant_value_locator="/div[1]/span/span"
    _local_variant_clickables_div="/div[2]/div"
    _vendor = ""  ##Defined by user
    _collections = "" ##Defined by user
    _tags = "" ##Defined by user

    def findPricing(self):
        price = self.findText(self._product_price)
        compare_price = self.findText(self._compare_at_price)
        
        price = re.sub('[^0-9\.,]','', price)
        compare_price = re.sub('[^0-9\.,]','', compare_price)
        print(price, compare_price)
        return Pricing(price=price, compare_at_price=compare_price)
            
    def findVariants(self, locator):
        variants_div = self.findElement(locator)
        
        self.log.info("Variants container div FOUND with locator: " + locator)
        byType = self.getByType("xpath")
        variants = variants_div.find_elements(byType, "./div/*")
        print(f"Found {len(variants)} variants")        
        self.log.info(f"Found {len(variants)} variants")
        result_variants = []

        for var in variants:
            variant_el = var.find_element(byType,"./div/span")
            variant_value_options = var.find_elements(byType, "./div[2]/div/*")

            var_class_atr = variant_el.get_attribute("class")
            var_text = variant_el.get_attribute("innerText")
            var_name = var_text.split(":")[0]
            var_values = []
            self.log.info(f"Scraping variant with class {var_class_atr} and name {var_name}")
            self.log.info(f"Variant has {str(len(variant_value_options))} clickables")
            #TODO: Check if there is any element that Says "VER MAS" or "See More" and click
            for variant_option in variant_value_options:
                variant_option.click()
                variant_el = var.find_element(byType,"./div/span/span")
                var_text = variant_el.get_attribute("innerText")
                # var_value = var_text.split(":")[1]
                self.log.info(f"Got value: {var_text}")
                var_values.append(var_text)

            r_variant = Variant(option_name=var_name,option_values=var_values)
            result_variants.append(r_variant)
        
        if len(result_variants) > 0:
            self.log.info(f"Variants FOUND with {byType}: " + "div")
            self.log.info("Extracted Variants: "+ str(result_variants))
        else:
            self.log.info(f"Variants NOT FOUND with {byType}: "+ "div")
        return result_variants

    def scrapProductInfo(self,logger_cb:callable=print()):
        try:
            
            self.logProcessStep("Extrayendo nombre del producto")
            logger_cb()
            title = self.findText(self._product_title)
            
            self.logProcessStep("Localizando imágenes del producto")
            logger_cb()
            image_els = self.findImagesWithin(self._product_images_div)


            self.logProcessStep("Descargando imágenes del producto")
            logger_cb()
            #TODO:This might be enqueued or processed concurrently
            image_paths = self.downloadImageFromDiv(image_els, product_title=title)
            
            self.logProcessStep("Extrayendo precio del producto")
            logger_cb()
            pricing = self.findPricing()
            
            self.logProcessStep("Extrayendo variantes del producto")
            logger_cb()
            variants = self.findVariants(self._variants_div)
            
            
            self.logProcessStep("Buscando descripción con scroll hacia abajo")
            logger_cb()
            self.webScroll(direction="down")

            self.logProcessStep("Extrayendo descripción")
            logger_cb()
            des_element = self.findElement(self._product_description)
            description = des_element.get_attribute("innerHTML")

    
            self.logProcessStep("Exportando producto")
            logger_cb()
            #TODO: add inventory details to products (because some are unavailable)
            product = Product(title=title,description=description, images_link=[image_paths],
                              pricing=pricing, variants=variants)
            
            self.log.info(f"Extracción exitosa del producto {product.title}")
            self.log.info(f"Resultado {product.model_dump()}")
            return product

        except Exception as e:
            self.log.error(f"Error al extraer informacion de un producto en ALIEXPRESS : {str(e)}")
            

    def getPageTitle(self):
        return self.getTitle()