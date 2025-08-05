import base64
from datetime import datetime
import os
from functools import wraps
import pandas as pd
import re
import tkinter as tk
from tkinter.filedialog import askopenfilename
import time
from typing import List, Union, Optional, Generator, Dict, Any


from src.logger import setup_logger
from src.settings import LOG_DIR
from src.creative_fabrica.elems import CreateFabricaItems

os.makedirs(f"{LOG_DIR}/utils_logs", exist_ok=True)
logger = setup_logger(name="UtilsLogger", log_dir=f"{LOG_DIR}/utils_logs")

upload_dir = os.path.join(os.getcwd(), "data")

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
        else:
            next_sku = f"{prefix}{date_today}{next_order_num}"
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


def get_imgs_and_zip(data_directory) -> Union[Dict[str, list], None]:
    try:
        files = {
            "img_files": [],
            "zip_file": []
        }
        for f in os.listdir(data_directory):
            _, ext = os.path.splitext(f)
            f = os.path.join(data_directory, f)
            if ext in [".jpg", ".png", ".jpeg"]:
                files["img_files"].append(f)
            else:
                files["zip_file"].append(f)
        files["img_files"].sort()
        return files
    except Exception as err:
        logger.error(f'Error in get_imgs_and_zip {err}')
        return None
    
def generator_items(df) -> Generator[Dict[str, Any], None, None]:
    
    total_items = len(df)
    processed_items = 0
    skipped_items = 0
    
    logger.info(f"Starting to process {total_items} items from DataFrame")
    
    for index, item in df.iterrows():
        processed_items += 1
        item_id = item.get('ID', f'Row_{index}')
        
        try:
            logger.info(f"Processing item {processed_items}/{total_items}: {item_id}")
            
            item_dict: Dict[str, Any] = {}
            item_dir = os.path.join(upload_dir, item.loc["ID"])

            item_dict["ID"] = item.loc["ID"]
            item_dict["title"] = item.loc["title"]
            item_dict["description"] = item.loc["description"]
            item_dict["price"] = str(item.loc["price"])
            item_dict["category"] = item.loc["category"]
            item_dict["tag"] = item.loc["tag"]
            
            # item_dict["item_dir"] = item_dir
            files = get_imgs_and_zip(item_dir)
            if not files:
                logger.error(f"No images or zip file found for item {item_id}")
                skipped_items += 1
                continue
                
            img_files: List[str] = files.get("img_files")
            zip_file: str = files.get("zip_file")[0]
            item_dict["zip_file"] = zip_file
            item_dict["img_files"] = img_files

            # count_img = 1
            # for img in list_images:
            #     count_img += 1
            item = CreateFabricaItems(**item_dict)
            logger.info(f"Successfully prepared item {item_id} for processing")
            yield item
            
        except Exception as e:
            logger.error(f"Error in generator_items: {e}. \nItem: {item_id}")
            skipped_items += 1
            continue
    
    logger.info(f"Generator completed. Processed: {processed_items}, Skipped: {skipped_items}, Yielded: {processed_items - skipped_items}")
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
        return df