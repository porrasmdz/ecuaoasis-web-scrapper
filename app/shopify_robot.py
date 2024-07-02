from app.models import Product
from app.config import settings
from app.utils import Util
from logging_instance import customLogger
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

try:
    session = shopify.Session(shop_url, api_version, token, scope)
    shopify.ShopifyResource.activate_session(session)
    logger.info("La sesión en Shopify se ha iniciado correctamente")
except Exception as e:
    logger.info(f"Ha ocurrido el siguiente error al conectarse con su tienda {str(e)}")

def attachImages(new_product, path_list):
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

def publishProductsToShopify(product_list: Product):
    for product in product_list:
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
        if success:
            new_product.price = product.pricing.price
            new_product.compare_at_price = product.pricing.compare_at_price
            new_product.save()
            
            path  = "products/ElockCerradurainteligenteconBluetoothcerradurainteligenteconpantallatctildeseguridadnuevaaplicacindecerrojomuertopreciodefbricacerradurainteligente/image-1.png"
            attachImages(new_product, [path])
            
        if new_product.errors:
            logger.info(f"{new_product.errors.full_messages()}")
            
