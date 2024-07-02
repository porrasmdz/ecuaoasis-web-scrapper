from webpages.aliexpress_page import AliexpressPage
from webpages.alibaba_page import AlibabaPage
from core.driver_factory import WebDriverFactory
from utils import Util
#scrapper actions here
utils = Util()

def scrape_aliexpres_product(driver, logger_cb:callable):
 
    base_link= driver.current_url
    try: 
        aliexpress= AliexpressPage(driver)
        product = aliexpress.scrapProductInfo(logger_cb=logger_cb)
        return product
    except Exception as e:
        utils.log.info(f"Error extrayendo de Aliexpress el producto con url {base_link} {str(e)}")
        
def scrape_alibaba_product(driver, logger_cb:callable):
  
    base_link = driver.current_url 
    try: 
        alibaba= AlibabaPage(driver)
        product = alibaba.scrapProductInfo(logger_cb=logger_cb)
        return product
    except Exception as e:
        utils.log.info(f"Error extrayendo de Aliexpress el producto con url {base_link} {str(e)}")
        
def scrap_products_info(links: list):            
    wdf = WebDriverFactory("chrome")
    driver = wdf.getWebDriverInstance()
    
    results = []
    
    utils.log.info(f"Inicio de WebScraping...")
    for link in links:
        domain = utils.extractDomainName(link, allowed_domains=["alibaba", "temu", "amazon", "aliexpress"])
        if domain is not None:
            
            utils.log.info(f"Se detectó el dominio \"{domain}\" del link {link}")
            match domain:
                case "alibaba":
                    driver.get(link)
                    product = scrape_alibaba_product(driver=driver)
                    results.append(product)
                case "aliexpress":
                    
                    driver.get(link)
                    product = scrape_aliexpres_product(driver=driver)
                    results.append(product)
                    
                case "amazon":
                    print("scrape amazon product")
                case "temu":
                    print("scrape temu product")
                case _:
                    print("default")
        else:
            print(f"Invalid link {link}")
    
    utils.log.info(f"Se extrajo {str(len(results))} resultados")
    utils.log.info(f"Web Scraping finalizado con: {str(results)}")
    driver.quit()
    return results

def scrap_product_info(link: str, driver, logger_cb:callable=print()):                
    domain = utils.extractDomainName(link, allowed_domains=["alibaba", "temu", "amazon", "aliexpress"])
    if domain is not None:
        utils.log.info(f"Se detectó el dominio \"{domain}\" del link {link}")
        logger_cb()
        match domain:
            case "alibaba":
                driver.get(link)
                product = scrape_alibaba_product(driver=driver, logger_cb=logger_cb)
                utils.log.info(f"Web Scraping finalizado con éxito")
                logger_cb()
                return product
            case "aliexpress":
                driver.get(link)
                product = scrape_aliexpres_product(driver=driver, logger_cb=logger_cb)
                utils.log.info(f"Web Scraping finalizado con éxito")
                logger_cb()
                return product
            case "amazon":
                print("scrape amazon product")
            case "temu":
                print("scrape temu product")
            case _:
                print("default")
    else:
        utils.log.info(f"No se encontró ningún dominio en el link {link}")
        logger_cb()
        
    
    

