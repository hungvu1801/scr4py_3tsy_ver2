
class IdeoElems:
    main_text_box: str = "//textarea[@placeholder='Describe what you want to see']"
    generate_button: str = "//button/span[contains(text(), 'Generate')]"
    policy_elem: str = "//p[contains(text(),'meet our content policy')]"
    
    generating_notifier: str = "//p[@class='MuiTypography-root MuiTypography-body1 css-1bhxqar']"
    img_elems: str = "//div[contains(@class, 'MuiGrid-root MuiGrid-container MuiGrid-spacing-xs-1')]/div"

    ratio_elem: str = "//div[@class='MuiBox-root css-1br965i']/div[2]"
    ratio_input_width = "//div[@class='MuiBox-root css-1px0l42']/div[1]//input"
    ratio_input_heigth = "//div[@class='MuiBox-root css-1px0l42']/div[2]//input"
    ratio_save_btn: str = "//div[contains(text(), 'Save')]"

    image_num_elem: str = "//div[@class='MuiBox-root css-1br965i']/div[3]"
    image_num_elem_btn: str = "//div[@class='MuiToggleButtonGroup-root css-1s9svmu']/button[{image_num}]"

    design_elem: str = "//div[@class='MuiBox-root css-1br965i']/div[6]"
    design_elem_btn: str = "//div[@class='MuiBox-root css-r7ft4d']/div[{design}]"