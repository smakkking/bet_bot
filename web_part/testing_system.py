# здесь тестируем все модули по группам и букмекеркам

import manage
from moduls.bet_manage import get_text_from_image, create_webdriver



url = ''
browser = create_webdriver()

text = get_text_from_image(browser, url)


browser.close()
browser.quit()
