import os
from pandas import DataFrame
from typing import Generator, Dict, Any, List, Union
from src.sofontsy.elems import SofontsyElems
from src.creative_fabrica.elems import CreateFabricaElems
from .utils import get_imgs_and_zip

upload_dir = os.path.join(os.getcwd(), "data")


class ItemGenerator:
    def __init__(
        self,
        ProcessingItem: Union[SofontsyElems, CreateFabricaElems],
        platform: str,
        # df: DataFrame,
    ):
        # self.df = df
        self.platform = platform
        self.ProcessingItem = ProcessingItem

        # self.total_items = len(df)
        self.processed_items = 0
        self.skipped_items = 0

    def generator_items(self, df) -> Generator[Dict[str, Any], None, None]:
        # logger.info(f"Starting to process {self.total_items} items from DataFrame")

        for index, item in df.iterrows():
            self.processed_items += 1
            # item_id = item.get('ID', f'Row_{index}')

            try:
                # logger.info(f"Processing item {self.processed_items}/{self.total_items}: {item_id}")

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
                    # logger.error(f"No images or zip file found for item {item_id}")
                    self.skipped_items += 1
                    continue

                img_files: List[str] = files.get("img_files")
                zip_file: str = files.get("zip_file")[0]
                item_dict["zip_file"] = zip_file
                item_dict["img_files"] = img_files
                if isinstance(self.ProcessingItem, SofontsyElems):
                    ...
                item = self.ProcessingItem(**item_dict)
                # logger.info(f"Successfully prepared item {item_id} for processing")
                yield item

            except Exception as e:
                # logger.error(f"Error in generator_items: {e}. \nItem: {item_id}")
                self.skipped_items += 1
                continue

        # logger.info(f"Generator completed. Processed: {self.processed_items}, Skipped: {skipped_items}, Yielded: {self.processed_items - skipped_items}")
