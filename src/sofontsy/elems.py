from dataclasses import dataclass
from typing import List
from .config import *
class SofontsyElems:
    PAGE_TITLE: str = "//h1[@class='Polaris-DisplayText Polaris-DisplayText--sizeLarge']" #Add a New Product
    PRODUCT: str = "//input[@id='product_title']"
    CATEGORY: str = ""
    CATEGORY_INPUT: str = ""
    DESCRIPTION: str = "(//div[@role='textbox'])[1]"
    PRICE: str = "//input[@id='product_price']"
    COMPARE_PRICE: str = "//input[@id='product_compare_at_price']"
    TAGS: str = "//input[@id='tags']"
    UPLOAD_PRODUCT_IMGS: str = ""
    UPLOAD_PRODUCT_IMGS_INPUT: str = "//input[@name='product_image[]']"
    UPLOAD_PRODUCT_FILE: str = ""
    UPLOAD_PRODUCT_FILE_INPUT: str = "//input[@name='product_zip[]']"
    BARCODE = "//input[@id='product_barcode']"
    PRODUCT_TYPE = "//select[@name='product_type']"
    PROD_SHORT_DESCRIPTION: str = "(//div[@role='textbox'])[2]"
    UPLOAD_ITEMS_STATUS: str = ""
    CHECKBOX_FREEBIE: str = ""
    CHECKBOX_DEALS: str = ""
    CHECKBOX_TERMS: str = ""
    SUBMIT: str = ""


@dataclass
class SofontsyItems:
    ID: str
    title: str
    description: str
    price: str
    compare_at_price: str
    category: str
    tags: str
    zip_file: str
    img_files: List[str] = None
    product_type: str
    product_short_description: str

    def __post_init__(self):
        self.tags = self.capitalize_tags(self.tags)
        self.tags = self.tag_limit(self.tags)

    def capitalize_tags(self, tags: str) -> str:
        list_tags = tags.split(",")
        tags_list = []
        for tag in list_tags:
            # Split each tag by space to handle capitalize
            lst_word = tag.strip(" ")
            lst_word = [word.strip().capitalize() for word in lst_word]
            tag = " ".join(lst_word)
            tags_list.append(tag)
        return ",".join(tags_list)

    def tag_limit(self, tags: str) -> str:
        list_tags = tags.split(",")
        list_tags = list_tags[:TAG_LIMIT]
        return ",".join(list_tags)
    
    def clean_tag(self, tags: str) -> str:
        list_tags = tags.split(",")
        tags_list = []
        for tag in list_tags:
            if tag != "" and tag != " ":
                tags_list.append(tag)
        return ",".join(tags_list)from dataclasses import dataclass
from typing import List
from .config import *
class SofontsyElems:
    PAGE_TITLE: str = ""
    PRODUCT: str = ""
    CATEGORY: str = ""
    CATEGORY_INPUT: str = ""
    DESCRIPTION: str = ""
    PRICE: str = ""
    TAGS: str = ""
    UPLOAD_PRODUCT_IMGS: str = ""
    UPLOAD_PRODUCT_IMGS_INPUT: str = ""
    UPLOAD_PRODUCT_FILE: str = ""
    UPLOAD_PRODUCT_FILE_INPUT: str = ""
    UPLOAD_ITEMS_STATUS: str = ""
    CHECKBOX_FREEBIE: str = ""
    CHECKBOX_DEALS: str = ""
    CHECKBOX_TERMS: str = ""
    SUBMIT: str = ""


@dataclass
class SofontsyItems:
    ID: str
    title: str
    description: str
    price: str
    compare_at_price: str
    category: str
    tags: str
    zip_file: str
    img_files: List[str] = None
    product_type: str
    product_short_description: str

    def __post_init__(self):
        self.tags = self.capitalize_tags(self.tags)
        self.tags = self.tag_limit(self.tags)

    def capitalize_tags(self, tags: str) -> str:
        list_tags = tags.split(",")
        tags_list = []
        for tag in list_tags:
            # Split each tag by space to handle capitalize
            lst_word = tag.strip(" ")
            lst_word = [word.strip().capitalize() for word in lst_word]
            tag = " ".join(lst_word)
            tags_list.append(tag)
        return ",".join(tags_list)

    def tag_limit(self, tags: str) -> str:
        list_tags = tags.split(",")
        list_tags = list_tags[:TAG_LIMIT]
        return ",".join(list_tags)
    
    def clean_tag(self, tags: str) -> str:
        list_tags = tags.split(",")
        tags_list = []
        for tag in list_tags:
            if tag != "" and tag != " ":
                tags_list.append(tag)
        return ",".join(tags_list)