from pydantic import BaseModel
from typing import Optional, Literal, Any, List

class Pricing(BaseModel):
    price: float = 0
    compare_at_price: float = 0
    charge_tax: bool = True
    cost_per_item: float = 0
    profit: float = 0 #computed
    margin: float = 0 #computed

class Inventory(BaseModel):
    track_quantity: bool = False
    quantity: Optional[float] = 0
    sell_wo_stock: bool = True
    has_sku_or_barcode: bool = False
    sku: Optional[str] = ""
    barcode: Optional[str] = ""

class Shipping(BaseModel):
    physical_product: bool = True
    weight: float = 0
    measure_units: str = Literal["kg", "lb", "oz", "g"] #kg lb oz g 

class Variant(BaseModel):
    option_name: Optional[str] = None
    option_values: Optional[List[str]] = None
    
class Product(BaseModel):
    title: str 
    description: Optional[str] = "" #opt = description
    images_link: Optional[List[Any]] = [] #Images req not links
    category: Optional[str] = "" #opt
    product_type: Optional[str] = ""
    vendor: Literal["ecuaoasis", "Dropshipping", "IntegradorApp"] = "IntegradorApp" #ecuaoasis Dropshipping
    collections: List[str] = ["Dropshipping"] 
    tags: Optional[List[str]] = ["dropshipping"]
    pricing: Pricing = Pricing()
    inventory: Inventory = Inventory()
    shipping: Shipping = Shipping()
    variants: Optional[List[Any]] = None

    def summary(self):
        return {
            'title': self.title,
            'price': self.pricing.price,
            'num_variants': len(self.variants) if self.variants else 0
        }
