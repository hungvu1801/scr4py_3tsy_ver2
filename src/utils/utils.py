import base64
from datetime import datetime
import os
import pandas as pd
import re
import tkinter as tk
from tkinter.filedialog import askopenfilename
import time
from typing import List, Union, Optional, Tuple, Generator, Dict, Any



from src.logger import setup_logger
from src.settings import LOG_DIR

os.makedirs(f"{LOG_DIR}/utils_logs", exist_ok=True)
logger = setup_logger(name="UtilsLogger", log_dir=f"{LOG_DIR}/utils_logs")

def download_directly_with_selenium(driver, url, save_path):
    try:
        # Navigate to the image URL directly
        driver.get(url)
        time.sleep(1)
        # Method A: Get image as base64 (for images displayed in browser)
        try:
            # Execute JavaScript to get image as base64
            canvas_script = """
            var img = document.querySelector('img') || document.body;
            var canvas = document.createElement('canvas');
            var ctx = canvas.getContext('2d');
            
            if (img.tagName === 'IMG') {
                canvas.width = img.naturalWidth;
                canvas.height = img.naturalHeight;
                ctx.drawImage(img, 0, 0);
                return canvas.toDataURL('image/png').split(',')[1];
            }
            return null;
            """
            
            base64_image = driver.execute_script(canvas_script)
            
            if base64_image:
                # Decode and save
                image_data = base64.b64decode(base64_image)
                with open(save_path, 'wb') as f:
                    f.write(image_data)
                logger.info(f"Error - Downloaded via base64 : {save_path}")
                return True
                
        except Exception as e:
            logger.error(f"Error - Base64 method failed : {e}")
        
        # Method B: Use browser's fetch API
        fetch_script = f"""
        return fetch('{url}')
            .then(response => response.blob())
            .then(blob => {{
                return new Promise((resolve) => {{
                    const reader = new FileReader();
                    reader.onloadend = () => resolve(reader.result.split(',')[1]);
                    reader.readAsDataURL(blob);
                }});
            }});
        """
        
        try:
            base64_data = driver.execute_async_script(f"""
                var callback = arguments[arguments.length - 1];
                {fetch_script}.then(callback);
            """)
            
            if base64_data:
                image_data = base64.b64decode(base64_data)
                with open(save_path, 'wb') as f:
                    f.write(image_data)
                logger.info(f"Error - Downloaded via fetch: {save_path}")
                return True
                
        except Exception as e:
            logger.error(f"Error - Fetch method failed: {e}")
        
        return False
    
    except Exception as e:
        logger.error(f"Error: Fetch method all failed: {e}")

def sku_generator(last_sku: str) -> str:
    try:
        prefix = "THSP"
        date_today = datetime.now().strftime("%d%m%y")
        lst_sku_match = re.search(rf"{prefix}\d{{6}}(\d+)$", last_sku)
        if lst_sku_match:
            last_order_num = int(lst_sku_match.group(1))
        date_extract = re.search(rf"{prefix}(\d{{6}})\d+$", last_sku)
        if date_extract:
            date_last_sku = date_extract.group(1)
            date_last = datetime.strptime(date_last_sku, "%d%m%y").date()
            if date_last == datetime.today().date():
                next_order_num = last_order_num + 1
            else:
                next_order_num = 1
        if next_order_num < 999:
            next_sku = f"{prefix}{date_today}{next_order_num:03d}"
        return next_sku
    except Exception as e:
        logger.error(f"Error {e}")
        return "THSP01012025001" # Fallback SKUs

def data_construct_for_gsheet(
        data: Union[list, str], 
        length: Optional[int] = None) -> List[List[str]]:
    try:
        if isinstance(data, list):
            return [[item] for item in data]
        elif isinstance(data, str) and length:
            return [[data] for _ in range(length)]
        else:
            return []
    except Exception as e:
        logger.error(f"Error : {e}")
        return []


def get_imgs_and_zip(data_directory) -> Tuple[List[str], Union[str, int]]:
    try:
        list_images = list()
        for f in os.listdir(data_directory):
            _, extension = os.path.splitext(f)
            if extension in [".jpg", ".png", ".jpeg"]:
                list_images.append(f)
            else:
                zip_file = f
        list_images.sort()
        return list_images, zip_file
    except Exception as err:
        logger.error(f'Error in get_imgs_and_zip {err}')
        return [], "Error"
    
def generator_items(df) -> Generator[Dict[str, Any], None, None]:
    upload_dir = os.path.join(os.getcwd(), "data", "upload_data")
    for _, item in df.iterrows():
        try:
            item_dict: Dict[str, Any] = {}
            item_dir = os.path.join(upload_dir, item.loc["ID"])

            item_dict["ID"] = item.loc["ID"]
            item_dict["title"] = item.loc["title"]
            item_dict["description"] = item.loc["description"]
            item_dict["price"] = item.loc["price"]
            item_dict["category"] = item.loc["category"]
            item_dict["tag"] = item.loc["tag"]
            
            item_dict["item_dir"] = item_dir
            list_images, zip_file = get_imgs_and_zip(item_dir)

            item_dict["zip_file"] = zip_file
            count_img = 1
            for img in list_images:
                item_dict[f"img_file_{count_img}"] = img
                count_img += 1

            yield item_dict
        except Exception as e:
            logger.error(f"Error in generator_items: {e}. \nItem: {item.get("ID", "Unknown")}")
            continue
    # return item_dict

def prompt_open_file() -> pd.DataFrame:
    try:
        root = tk.Tk()
        root.withdraw()
        fileDir = askopenfilename(title="Open excel file")
        df = pd.DataFrame()
        if fileDir:
            df = pd.read_excel(fileDir)
        return df
    except Exception as e:
        logger.error(f"Error in prompt_open_file {e}")