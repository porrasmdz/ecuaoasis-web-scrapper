from app.models import Product as ProductObject
from app.config import settings
from app.utils import Util
from logging_instance import customLogger
from typing import List
import shopify

logger = customLogger(filename="logs/shopify.log",logger_name="__shopify__")
shop_url = "%s.myshopify.com" % (settings.SH_SHOP_NAME)
api_version = "2024-04"
token = settings.SH_API_TOKEN
scope = ["write_files", "read_files", "write_channels", "read_channels",
            "write_payment_terms", "read_payment_terms", "write_metaobject_definitions",
            "read_metaobject_definitions", "write_metaobjects", "read_metaobjects",
            "write_shipping", "read_shipping", "write_script_tags", "read_script_tags",
            "write_product_feeds", "read_product_feeds", "write_inventory", "read_inventory",
            "write_purchase_options", "read_purchase_options", "write_products",
            "read_products", "write_publications", "read_publications", "write_product_listings",
            "read_product_listings", "write_locales", "read_locales", "write_locations",
            "read_locations"]


def attachImages(new_product, path_list: list):
    product_id = new_product.id
    images = []
    for path in path_list:
        image = shopify.Image({'product_id': product_id})
        filename = path.split("/")[-1:][0]
        with open(path, "rb") as f:
            encoded= f.read()
            image.attach_image(encoded, filename=filename)
        images.append(image)
    
    new_product.images = images
    success = new_product.save() 
    if success:
        logger.info(f"Imagenes agregadas exitosamente")
    if new_product.errors:
        logger.info(f"Error al subir imagenes {new_product.errors.full_messages()}")

def publishProductsToShopify(product_list: List[ProductObject], logs_cb:callable=None):
    
    logger.info("Iniciando conexion con Shopify...")
    logs_cb()
    session = shopify.Session(shop_url, api_version, token, scope)
    shopify.ShopifyResource.activate_session(session)
    logger.info("Iniciando conexion con Shopify...")
    logs_cb()
    logger.info("Conexión Establecida")
    logs_cb()
    logger.info(f"Se van a cargar {str(len(product_list))} productos")
    logs_cb()


    for product in product_list:
        try:
            new_product = shopify.Product()
            new_product.title = product.title
            new_product.body_html = product.description
            new_product.vendor = product.vendor
            new_product.product_type = product.product_type
            new_product.tags = product.tags
            
            # new_product.options = [
            #     {"name" : "Size"},
            #     {"name" : "Colour"},
            #     {"name" : "Material"}
            # ]

            # colors = ['Black', 'Blue', 'Green', 'Red']
            # sizes = ['S', 'M', 'L', 'XL']
            # new_product.variants = []
            # new_product.images = []
            # new_product.image = None
            success = new_product.save()
            logger.info(f"Creado el producto: {product.title}")
            logs_cb()

            if success:
                
                logger.info(f"Subiendo {len(product.images_link) if product.images_link else 0} imagenes del producto")
                logs_cb()
                new_product.price = product.pricing.price
                new_product.compare_at_price = product.pricing.compare_at_price
                new_product.save()
                attachImages(new_product,product.images_link)
                
                logger.info(f"Imagenes subidas correctamente")
                logs_cb()
            if new_product.errors:
                logger.info(f"Error en la subida del producto a Shopify")
                logger.info(f"{new_product.errors.full_messages()}")
                logs_cb()
        
        except Exception as e:
            logger.info(f"Error en la carga del producto a Shopify")
            logger.info(f"{new_product.errors.full_messages()}")
            logger.info(f"{str(e)}")
            logs_cb()    
