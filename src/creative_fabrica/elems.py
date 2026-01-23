from dataclasses import dataclass
from typing import List


class CreateFabricaElems:
    PAGE_TITLE: str = "//div[@class='page-title']"
    PRODUCT: str = "//input[@name='title']"
    CATEGORY: str = "//span[@role='combobox']"
    CATEGORY_INPUT: str = "//input[@class='select2-search__field']"
    DESCRIPTION: str = "//textarea[@class='form-control']"
    PRICE: str = "//input[@id='price']"
    TAGS: str = "//div[@class='bootstrap-tagsinput']/input"
    UPLOAD_PRODUCT_IMGS: str = "(//div[@class='fileuploader-input-button'])[1]"
    UPLOAD_PRODUCT_IMGS_INPUT: str = "//input[@id='product_images']"
    UPLOAD_PRODUCT_FILE: str = "(//div[@class='fileuploader-input-button'])[2]"
    UPLOAD_PRODUCT_FILE_INPUT: str = "//input[@id='product_files']"
    UPLOAD_ITEMS_STATUS: str = "//div[@class='column-actions']/a"
    # CHECKBOX_FREEBIE: str = "//input[@name='in_freebie']"
    # CHECKBOX_DEALS: str = "//input[@name='in_discount_deals']"
    CHECKBOX_FREEBIE: str = "(//div[@id='product-property-checklist']/div)[1]"
    CHECKBOX_DEALS: str = "(//div[@id='product-property-checklist']/div)[2]"
    CHECKBOX_TERMS: str = "//ins[@class='iCheck-helper']"
    SUBMIT: str = "//button[@type='submit']"


@dataclass
class CreateFabricaItems:
    ID: str
    title: str
    description: str
    price: str
    category: str
    tag: str
    zip_file: str
    img_files: List[str] = None
