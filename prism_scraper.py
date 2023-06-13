from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import ElementClickInterceptedException
import time
from bs4 import BeautifulSoup
import json


class PrismScraper:
    def __init__(self):
        options = Options()
        options.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()
    
    def policyinfo_flow(self):
        driver = self.driver
        driver.get("https://prism.prulifeuk.com.ph/")
        self.nav_login(driver)
        self.nav_policyinfo(driver)
        self.start_mine(driver)

    def nav_login(self, driver):
        wait = WebDriverWait(driver, 20)
        # set credentials
        prism_username = '70095312'
        prism_password = 'Stark@5312!02'
        # wait until login button is available
        login_btn = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="login-wrapper"]/div[2]/div[6]/input')))
        # input credentials
        username_txt = driver.find_element('xpath', '//*[@id="username-textbox"]')
        username_txt.send_keys(prism_username)
        password_txt = driver.find_element('xpath', '//*[@id="password-textbox"]')
        password_txt.send_keys(prism_password)
        # login
        login_btn.click()
        time.sleep(2)
        
    def nav_policyinfo(self, driver):
        # wait if multiple user message prompts
        wait = WebDriverWait(driver, 20)
        try:
            wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="lx-home"]/div[1]/div[2]/div/div[2]/div[1]/div/h1')))
            wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="label-1014"]')))
            wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="label-1018"]')))
            ok_btn = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="button-1024-btnInnerEl"]')))
            ok_btn.click()
            wait.until(EC.invisibility_of_element_located((By.XPATH, '//*[@id="label-1018"]')))
            time.sleep(2)
        except:
            pass
        # navigate to Policy Information > ALL
        parent_menu = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="button-1049-btnEl"]')))
        ActionChains(driver).move_to_element(parent_menu).perform()
        time.sleep(2)
        policyinfo_btn = driver.find_element('xpath', '//*[@id="menuitem-1051-textEl"]')
        ActionChains(driver).move_to_element(policyinfo_btn).click(policyinfo_btn).perform()
        time.sleep(2)
        wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="label-1126"]'))).click()
        time.sleep(5)
        

    def start_mine(self, driver):
        xpath_grid = '//*[contains(@id,"-record-") and contains(@id, "gridview-")]/tbody/tr/td[1]/div/a'
        wait = WebDriverWait(driver, 10)
        policy_dict = {}
        while True:
            elems = [elem.text for elem in driver.find_elements('xpath', xpath_grid)]
            for elem in elems:
                print(f'Navigating: {elem}')
                # xpath_clickable = f'//*[contains(@id,"-record-") and contains(@id, "gridview-")]/tbody/tr/td[1]/div/a[contains(text(), {elem})]'
                clickable_elem = wait.until(EC.visibility_of_element_located((By.LINK_TEXT, elem)))
                clickable_elem.click()
                time.sleep(2)
                elem_info =self.scrape_info(driver)
                policy_dict.update({elem:elem_info})
                # print(policy_dict)
                print(elem_info)
                time.sleep(2)
                all_policy = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'ALL')))
                all_policy.click()
                time.sleep(2)

            wait.until(EC.visibility_of_element_located((By.XPATH, xpath_grid)))

            try:
                next_btn = driver.find_element('xpath', '//*[@class="fa fa-angle-right"]')
                next_btn.click()
                time.sleep(2)
                wait.until(EC.visibility_of_element_located((By.XPATH, xpath_grid)))
            except ElementClickInterceptedException:
                break

        self.driver.close()

    def scrape_info(self, driver):
        wait = WebDriverWait(driver, 10)
        agent_name = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@name="agent_name"]'))).get_attribute('value')
        policy_number = driver.find_element('xpath', '//*[@aria-labelledby="policyNumber-labelEl"]').get_attribute('innerText')
        branch_name = driver.find_element('xpath', '//*[@name="branch_name"]').get_attribute('value')
        owner_name = driver.find_element('xpath', '//*[@name="owner_name"]').get_attribute('value')
        insured_name = driver.find_element('xpath', '//*[@name="insured_name"]').get_attribute('value')
        plan_description = driver.find_element('xpath', '//*[@name="planCodeDescription"]').get_attribute('value')
        plan_currency = driver.find_element('xpath', '//*[@name="currency"]').get_attribute('value')
        contract_status = driver.find_element('xpath', '//*[@name="contract_status"]').get_attribute('value')
        premium_status = driver.find_element('xpath', '//*[@name="premium_status"]').get_attribute('value')
        sum_assured = driver.find_element('xpath', '//*[@name="face_amount"]').get_attribute('value')
        non_forfeiture_option = driver.find_element('xpath', '//*[@name="non_forfeiture_option"]').get_attribute('value')
        dividend_option = driver.find_element('xpath', '//*[@name="dividend_option"]').get_attribute('value')
        assigned_status = driver.find_element('xpath', '//*[@name="assigned_status"]').get_attribute('value')
        effectivity_date = driver.find_element('xpath', '//*[@name="effectivity_date"]').get_attribute('value')
        first_issue_date = driver.find_element('xpath', '//*[@name="first_issue_date"]').get_attribute('value')
        mailing_address = driver.find_element('xpath', '//*[@name="despatch_address"]').get_attribute('value')
        residence_address = driver.find_element('xpath', '//*[@name="residence_address"]').get_attribute('value')

        driver.find_element('xpath', "//*[contains(text(), 'Payment Information')]").click()
        time.sleep(2)

        payment_method = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@name="payment_method"]'))).get_attribute('value')
        due_date = driver.find_element('xpath', '//*[@name="paid_to_date"]').get_attribute('value')
        billing_frequency = driver.find_element('xpath', '//*[@name="billing_frequency"]').get_attribute('value')
        modal_premium = driver.find_element('xpath', '//*[@name="modal_premium"]').get_attribute('value')
        single_premium = driver.find_element('xpath', '//*[@name="single_premium"]').get_attribute('value')

        driver.find_element('xpath', "//*[contains(text(), 'Plan Details')]").click()
        time.sleep(2)

        wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'COMPONENT DESCRIPTION')]")))

        xpath_grid = '//*[contains(@id,"-record-") and contains(@id, "gridview-")]/tbody/tr/td[1]'
        wait.until(EC.visibility_of_element_located((By.XPATH, xpath_grid)))
        xpath_grid = '//*[contains(@id,"-record-") and contains(@id, "gridview-")]/tbody/tr'
        rows = driver.find_elements('xpath', xpath_grid)
        for row in rows:
            cols = row.find_elements('xpath', './/td')
            for col in cols:
                print(col.text)
        # xpath_grid = '//*[contains(@id,"-record-") and contains(@id, "gridview-")]/tbody/tr/td[2]'
        # sum_assured_col = [elem.text for elem in driver.find_elements('xpath', xpath_grid)]
        # xpath_grid = '//*[contains(@id,"-record-") and contains(@id, "gridview-")]/tbody/tr/td[3]'
        # contract_status_col = [elem.text for elem in driver.find_elements('xpath', xpath_grid)]
        # xpath_grid = '//*[contains(@id,"-record-") and contains(@id, "gridview-")]/tbody/tr/td[4]'
        # premium_status_col = [elem.text for elem in driver.find_elements('xpath', xpath_grid)]

        # elems = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@tagName="TABLE"]')))
        # elems = [elem.text for elem in elems]
        # print(elems)

        inner_dict = {'POLICY_NUMBER':policy_number, 'AGENT_NAME':agent_name, 'BRANCH_NAME':branch_name, 'OWNER_NAME':owner_name,
                        'INSURED_NAME':insured_name, 'PLAN_DESCRIPTION':plan_description, 'PLAN_CURRENCY':plan_currency,
                        'CONTRACT_STATUS':contract_status, 'PREMIUM_STATUS':premium_status, 'SUM_ASSURED':sum_assured,
                        'NON_FORFEITURE_OPTION':non_forfeiture_option, 'DIVIDEND_OPTION':dividend_option,
                        'ASSIGNED_STATUS':assigned_status, 'EFFECTIVITY_DATE':effectivity_date, 'FIRST_ISSUE_DATE':first_issue_date,
                        'MAILING_ADDRESS':mailing_address, 'RESIDENCE_ADDRESS':residence_address,
                        'PAYMENT_METHOD':payment_method, 'DUE_DATE':due_date, 'BILLING_FREQUENCY':billing_frequency,
                        'MODAL_PREMIUM':modal_premium, 'SINGLE_PREMIUM':single_premium}


        # print(json.dumps(inner_dict))

        return inner_dict

if __name__ == "__main__":

    prismscraper = PrismScraper()
    prismscraper.policyinfo_flow()