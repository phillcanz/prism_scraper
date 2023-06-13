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
import pprint
from bs4 import BeautifulSoup
import json


class PrismScraper:
    def __init__(self):
        options = Options()
        options.add_experimental_option("detach", True)
        # options.add_argument("--headless")
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
            wait.until(EC.visibility_of_element_located((By.XPATH, '//div/h1[text()="Policies issued"]')))
            wait.until(EC.visibility_of_element_located((By.XPATH, '//label[text()="MULTIPLE USERS"]')))
            ok_btn = wait.until(EC.visibility_of_element_located((By.XPATH, '//span[text()="OK"]')))
            ok_btn.click()
            wait.until(EC.invisibility_of_element_located((By.XPATH, '//label[text()="MULTIPLE USERS"]')))
        except:
            pass
        # navigate to Policy Information > ALL
        parent_menu = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[text()="Servicing"]')))
        ActionChains(driver).move_to_element(parent_menu).perform()
        policyinfo_btn = wait.until(EC.visibility_of_element_located((By.XPATH, '//span[text()="Policy information"]')))
        ActionChains(driver).move_to_element(policyinfo_btn).click(policyinfo_btn).perform()
        time.sleep(2)
        wait.until(EC.visibility_of_element_located((By.XPATH, '//label[text()="ALL"]'))).click()
        wait.until(EC.visibility_of_element_located((By.XPATH, '//*[contains(@id,"-record-") and contains(@id, "gridview-")]')))

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
                print(json.dumps({elem:elem_info}, indent=4))
                all_policy = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'ALL')))
                all_policy.click()
                time.sleep(2)

            wait.until(EC.visibility_of_element_located((By.XPATH, xpath_grid)))

            try:
                next_btn = driver.find_element('xpath', '//*[@class="fa fa-angle-right"]')
                next_btn.click()
                time.sleep(2)
                wait.until(EC.invisibility_of_element_located((By.XPATH, '//*[@id="walking-pruman"]')))
                wait.until(EC.visibility_of_element_located((By.XPATH, xpath_grid)))
            except ElementClickInterceptedException:
                break

        self.driver.close()

    def scrape_info(self, driver):
        wait = WebDriverWait(driver, 10)

        wait.until(EC.visibility_of_element_located((By.XPATH, '//input[@name="agent_name"]')))

        while True:
            agent_name = wait.until(EC.visibility_of_element_located((By.XPATH, '//input[@name="agent_name"]'))).get_attribute('value')
            if len(agent_name.strip()) > 0:
                break
        policy_number = driver.find_element('xpath', '//*[@aria-labelledby="policyNumber-labelEl"]').get_attribute('innerText')
        branch_name = driver.find_element('xpath', '//input[@name="branch_name"]').get_attribute('value')
        owner_name = driver.find_element('xpath', '//input[@name="owner_name"]').get_attribute('value')
        insured_name = driver.find_element('xpath', '//input[@name="insured_name"]').get_attribute('value')
        plan_description = driver.find_element('xpath', '//input[@name="planCodeDescription"]').get_attribute('value')
        plan_currency = driver.find_element('xpath', '//input[@name="currency"]').get_attribute('value')
        contract_status = driver.find_element('xpath', '//input[@name="contract_status"]').get_attribute('value')
        premium_status = driver.find_element('xpath', '//input[@name="premium_status"]').get_attribute('value')
        sum_assured = driver.find_element('xpath', '//input[@name="face_amount"]').get_attribute('value')
        non_forfeiture_option = driver.find_element('xpath', '//input[@name="non_forfeiture_option"]').get_attribute('value')
        dividend_option = driver.find_element('xpath', '//input[@name="dividend_option"]').get_attribute('value')
        assigned_status = driver.find_element('xpath', '//input[@name="assigned_status"]').get_attribute('value')
        effectivity_date = driver.find_element('xpath', '//input[@name="effectivity_date"]').get_attribute('value')
        first_issue_date = driver.find_element('xpath', '//input[@name="first_issue_date"]').get_attribute('value')
        mailing_address = driver.find_element('xpath', '//input[@name="despatch_address"]').get_attribute('value')
        residence_address = driver.find_element('xpath', '//input[@name="residence_address"]').get_attribute('value')
        general_information = {'POLICY_NUMBER':policy_number, 'AGENT_NAME':agent_name, 'BRANCH_NAME':branch_name, 'OWNER_NAME':owner_name,
                        'INSURED_NAME':insured_name, 'PLAN_DESCRIPTION':plan_description, 'PLAN_CURRENCY':plan_currency,
                        'CONTRACT_STATUS':contract_status, 'PREMIUM_STATUS':premium_status, 'SUM_ASSURED':sum_assured,
                        'NON_FORFEITURE_OPTION':non_forfeiture_option, 'DIVIDEND_OPTION':dividend_option,
                        'ASSIGNED_STATUS':assigned_status, 'EFFECTIVITY_DATE':effectivity_date, 'FIRST_ISSUE_DATE':first_issue_date,
                        'MAILING_ADDRESS':mailing_address, 'RESIDENCE_ADDRESS':residence_address}
        
        wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Payment Information')]"))).click()
        time.sleep(2)

        wait.until(EC.visibility_of_element_located((By.XPATH, '//input[@name="payment_method"]')))

        while True:
            payment_method = wait.until(EC.visibility_of_element_located((By.XPATH, '//input[@name="payment_method"]'))).get_attribute('value')
            if len(payment_method.strip()) > 0:
                break
        due_date = driver.find_element('xpath', '//input[@name="paid_to_date"]').get_attribute('value')
        billing_frequency = driver.find_element('xpath', '//input[@name="billing_frequency"]').get_attribute('value')
        modal_premium = driver.find_element('xpath', '//input[@name="modal_premium"]').get_attribute('value')
        single_premium = driver.find_element('xpath', '//input[@name="single_premium"]').get_attribute('value')
        payment_information = {'PAYMENT_METHOD':payment_method,
                               'DUE_DATE':due_date, 'BILLING_FREQUENCY':billing_frequency,
                               'MODAL_PREMIUM':modal_premium, 'SINGLE_PREMIUM':single_premium}
        
        wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Plan Details')]"))).click()
        time.sleep(2)

        wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'COMPONENT DESCRIPTION')]")))

        xpath_grid = '//*[contains(@id,"-record-") and contains(@id, "gridview-")]/tbody/tr/td[1]'
        wait.until(EC.visibility_of_element_located((By.XPATH, xpath_grid)))
        xpath_grid = '//*[contains(@id,"-record-") and contains(@id, "gridview-")]/tbody/tr'
        rows = driver.find_elements('xpath', xpath_grid)
        plan_details = {}
        for row in rows:
            cols = row.find_elements('xpath', './/td')
            component_description = cols[0].text.strip().replace(' ', '_')
            component_details = {'SUM_ASSURED':f'{" ".join([word.strip() for word in cols[1].text.split()])}',
                                 'CONTRACT_STATUS':f'{" ".join([word.strip() for word in cols[2].text.split()])}',
                                 'PREMIUM_STATUS':f'{" ".join([word.strip() for word in cols[3].text.split()])}'}
            plan_details.update({component_description:component_details})
        # xpath_grid = '//*[contains(@id,"-record-") and contains(@id, "gridview-")]/tbody/tr/td[2]'
        # sum_assured_col = [elem.text for elem in driver.find_elements('xpath', xpath_grid)]
        # xpath_grid = '//*[contains(@id,"-record-") and contains(@id, "gridview-")]/tbody/tr/td[3]'
        # contract_status_col = [elem.text for elem in driver.find_elements('xpath', xpath_grid)]
        # xpath_grid = '//*[contains(@id,"-record-") and contains(@id, "gridview-")]/tbody/tr/td[4]'
        # premium_status_col = [elem.text for elem in driver.find_elements('xpath', xpath_grid)]

        # elems = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@tagName="TABLE"]')))
        # elems = [elem.text for elem in elems]
        # print(elems)

        inner_dict = {'GENERAL_INFORMATION':general_information,
                      'PAYMENT_INFORMATION':payment_information,
                      'PLAN_DETAILS':plan_details}


        # print(json.dumps(inner_dict))

        return inner_dict

if __name__ == "__main__":

    prismscraper = PrismScraper()
    prismscraper.policyinfo_flow()