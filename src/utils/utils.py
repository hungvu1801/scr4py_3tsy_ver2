import base64
from datetime import datetime
import re
import time

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
                print(f"Downloaded via base64: {save_path}")
                return True
                
        except Exception as e:
            print(f"Base64 method failed: {e}")
        
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
                print(f"Downloaded via fetch: {save_path}")
                return True
                
        except Exception as e:
            print(f"Fetch method failed: {e}")
        
        return False
    
    except Exception as e:
        print(f"Fetch method all failed: {e}")

def sku_generator(last_sku:str):
    prefix = "THSK"

    date_today = datetime.now().strftime("%y%m%d")
    lst_sku_match = re.search(rf"{prefix}\d{6}(\d{3})$", last_sku)
    if lst_sku_match:
        
    date_extract = re.search(rf"{prefix}(\d{6})\d{3}$", last_sku)
    if date_extract:
        date_last_sku = date_extract.group(1)
        date_last = datetime.strptime(date_last_sku, "%y%m%d").date()
        if date_last == datetime.today().date():


    datetime.today()
    if lst_sku_match:

    return next_sku