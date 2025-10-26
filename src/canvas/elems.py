class CanvasItems:
    ...

class CanvasElems:
    PROJECT_BTN: str = "//div[@id='projects']"
    # PROJECT_FOLDER: str = "//div[@aria-label='new']"
    IMG_CONTAINER: str = "//div[@class='SwlpcA']/div"

    IMG_ELEM: str = "(//div[@class='SwlpcA']/div)[{number}]"
    IMG_NAME: str = ".//span[@class='kb_Bkw giqgPw lA2MVA']"
    IMG_MENU: str = ".//span[@class='vxQy1w']"

    EDIT_IMG_BTN: str = "//button[@aria-label='Edit image']"
    REMOVE_BG_BTN: str = "//button[@aria-label='BG Remover']"
    SAVE_BTN: str = "//button[@aria-label='Save to Canva and close']"