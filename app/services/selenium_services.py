import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert #investigate this
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoAlertPresentException, UnexpectedAlertPresentException

# from app.robot.constants import FILES

class SeleniumRobot:

    def __init__(self, tmp_dir):
        options = webdriver.ChromeOptions()
        prefs = {
            'download.default_directory' : tmp_dir, #FILES['DOWNLOAD_PATH'],
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'safebrowsing.disable_download_protection': True
        }
        options.add_argument("--headless=new")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_experimental_option('prefs', prefs)
        
        # options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        # self.driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=options)
        self.driver = webdriver.Chrome( options=options )
        self.driver.implicitly_wait(10)

    def get_title(self):
        return self.driver.title

    def get_current_url(self):
        return self.driver.current_url
    
    def get_page_source(self):
        return self.driver.page_source

    def get(self, url):
        try:
            self.driver.get(url)
        except TimeoutException:
            return Exception(f"TimeoutException: The page {url} took too long to load")

    def find_element_by_id(self, id):
        try:
            return self.driver.find_element( By.ID, id )
        except NoSuchElementException:
            return Exception(f"NoSuchElementException: Element with id={id} was not found")

    def find_element_by_class(self, class_name):
        try:
            return self.driver.find_element( By.CLASS_NAME, class_name )
        except NoSuchElementException:
            return Exception(f"NoSuchElementException: Element with class={class_name} was not found")

    def find_element_by_xpath(self, xpath):
        try:
            return self.driver.find_element( By.XPATH, xpath )
        except NoSuchElementException:
            return Exception(f"NoSuchElementException: Element with xpath={xpath} was not found")

    def find_elemt_by_tag_name(self, tag):
        try:
            return self.driver.find_element( By.TAG_NAME, tag )
        except NoSuchElementException:
            return Exception(f"NoSuchElementException: Element with tag={tag} was not found")

    def find_element_by_css(self, css):
        try:
            return self.driver.find_element( By.CSS_SELECTOR, css )
        except NoSuchElementException:
            return Exception(f"NoSuchElementException: Element with css={css} was not found")

    def wait_for_id_element(self, id, time=5):
        try:
            return WebDriverWait(self.driver, time).until(EC.presence_of_element_located((By.ID, id)))
        except TimeoutException:
            return Exception(f"TimeoutException: Element with id={id} was not found")

    def wait_for_xpath_element(self, xpath, time=5):
        try:
            return WebDriverWait(self.driver, time).until(EC.presence_of_element_located((By.XPATH, xpath)))
        except TimeoutException:
            return Exception(f"TimeoutException: Element with xpath={xpath} was not found")

    def wait_for_xpath_element_to_be_clickable(self, xpath, time=5):
        try:
            return WebDriverWait(self.driver, time).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        except TimeoutException:
            return Exception(f"TimeoutException: Element with xpath={xpath} was not found")

    def wait_for_title_contains(self, title, time=5):
        try:
            WebDriverWait(self.driver, time).until(EC.title_contains(title))
        except TimeoutException:
            return Exception(f"TimeoutException: Title does not contain {title}")

    def wait_for_css_element(self, css, time=5):
        try:
            return WebDriverWait(self.driver, time).until(EC.presence_of_element_located((By.CSS_SELECTOR, css)))
        except TimeoutException:
            return Exception(f"TimeoutException: Element with css={css} was not found")

    def wait_for_class_element(self, class_name, time=5):
        try:
            return WebDriverWait(self.driver, time).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
        except TimeoutException:
            return Exception(f"TimeoutException: Element with class={class_name} was not found")

    def wait_for_alert(self, time=5):
        try:
            WebDriverWait(self.driver, time).until(EC.alert_is_present())
        except TimeoutException:
            return Exception(f"TimeoutException: Alert was not found")

    def wait_for_id_element_to_be_invisble(self, id, time=5):
        try:
            return WebDriverWait(self.driver, time).until(EC.invisibility_of_element((By.ID, id)))
        except TimeoutException:
            return Exception(f"TimeoutException: Element with id={id} was not found or is not invisible")

    def wait_for_frame_id(self, id, time=5):
        try:
            return WebDriverWait(self.driver, time).until(EC.frame_to_be_available_and_switch_to_it((By.ID, id)))
        except TimeoutException:
            return Exception(f"TimeoutException: Frame with id={id} was not found")

    def accept_alert(self):
        try:
            Alert(self.driver).accept()
        except NoAlertPresentException:
            return Exception(f"NoAlertPresentException: No alert was present")

    def get_element_text(self, element):
        try:
            return element.text
        except AttributeError:
            return Exception(f"AttributeError: Element has no attribute text")

    def delete_all_cookies(self):
        self.driver.delete_all_cookies()
    
    def delete_cookie(self, name):
        self.delete_cookie(name)
    
    def write_file(self, element, file):
        element.send_keys(file)

    def write_text(self, element, text):
        try:
            element.send_keys(text)
        except AttributeError:
            return Exception(f"AttributeError: Element has no attribute send_keys")

    def click(self, element):
        try:
            element.click()
        except:
            return Exception(f"Exception: Element could not be clicked")

    def execute_script(self, script):
        try:
            self.driver.execute_script(script)
        except Exception:
            raise Exception(f"Exception: Script \n{script}\ncould not be executed")

    def get_attribute(self, element, attribute):
        try:
            return element.get_attribute(attribute)
        except AttributeError:
            return Exception(f"AttributeError: Element has no attribute {attribute}")

    def close(self):
        self.driver.close()
    
    def quit(self):
        self.driver.quit()
