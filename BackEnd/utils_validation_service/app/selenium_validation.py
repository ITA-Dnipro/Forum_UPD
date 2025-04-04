from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

import logging.config
from settings import LOGGING

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('utils_validation_service')

YOUCONTROL_URL = "https://youcontrol.com.ua/"

def get_selenium_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920x1080")
    return webdriver.Chrome(options=chrome_options)

def validate_code(code: str):
    driver = get_selenium_driver()
    status = 'Valid'
    try:
        driver.get(YOUCONTROL_URL)

        WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.ID, "q-l"))).send_keys(code)

        search_button = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CSS_SELECTOR, ".visible-711")))
        driver.execute_script("arguments[0].scrollIntoView();", search_button)
        driver.execute_script("arguments[0].click();", search_button)

        try:
            result_text = WebDriverWait(driver, 5).until(ec.presence_of_element_located((By.CSS_SELECTOR, "h4"))).text
            if 'контрагентів не знайдено' in result_text:
                status = 'Invalid'
            logger.info(f'{code} is {status.lower()}')
        except Exception:
            pass

    except Exception as e2:
        logger.error(e2)
        return f'Error {e2}'
    finally:
        try:
            driver.quit()
        except Exception as e:
            logger.error(f"Error while closing driver: {e}")
    return status
