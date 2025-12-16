
class IdeoElems:
    main_text_box: str = "//textarea[@placeholder='Describe what you want to see']"
    generate_button: str = "//button/p[contains(text(), 'Generate')]"
    policy_elem: str = "//p[contains(text(),'meet our content policy')]"
    
    generating_notifier: str = "//div[@class='MuiBox-root css-18o6q3k']/p"
    img_elems: str = "//div[contains(@class, 'MuiGrid-root MuiGrid-container css-1yek722')]/div"

    ratio_elem: str = "//div[@class='MuiBox-root css-ritwfp']/div[2]"
    ratio_elem_width_clickable: str = "(//p[@class='MuiTypography-root MuiTypography-body1 css-1t1m8m6'])[1]"
    ratio_input_width = "(//div[@class=' MuiBox-root css-ndvclx']/div[1]/input)[1]"
    ratio_input_heigth = "(//div[@class=' MuiBox-root css-ndvclx']/div[1]/input)[2]"
    ratio_save_btn: str = "//div[contains(text(), 'Save')]"

    image_num_elem: str = "//div[@class='MuiBox-root css-ritwfp']/div[1]"
    image_num_elem_btn: str = "//div[@class='MuiToggleButtonGroup-root css-1mfgcko']/button[{image_num}]"

    design_elem: str = "//div[@class='MuiBox-root css-ritwfp']/div[3]"
    design_elem_btn: str = "//div[@class='MuiBox-root css-nyw7za']/div[{design}]"