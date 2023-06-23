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
import json
import os
import sys
import pandas as pd


class PrismScraper:
    def __init__(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--allow-insecure-localhost")
        options.add_argument("--window-size=1280,800")
        self.driver = webdriver.Chrome(options=options)
        # self.driver.maximize_window()

    def policyinfo_flow(self):
        driver = self.driver
        driver.get("https://prism.prulifeuk.com.ph/")
        self.nav_login(driver)
        self.nav_policyinfo(driver)
        self.start_mine(driver)

    def handle_error_mining(self, driver, cond_str=''):
        try:
            driver.get("https://prism.prulifeuk.com.ph/")
            self.nav_login(driver)
            self.nav_policyinfo(driver)
        except:
            self.handle_error_mining(driver, cond_str)

        while True:
            elem = []
            try:
                elem = driver.find_elements('xpath', f'//a[text()={cond_str}]')
                if len(elem) > 0:
                    break
                else:
                    self.next_page_entry(driver)
            except:
                self.handle_error_mining(driver, cond_str)

    def nav_login(self, driver):
        try:
            wait = WebDriverWait(driver, 20)
            # set credentials
            with open(os.path.join(sys.path[0], "credentials.json"), "r") as f:
                data = json.load(f)
                prism_username = data['username']
                prism_password = data['password']
            # wait until login button is available
            login_btn = wait.until(EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="login-wrapper"]/div[2]/div[6]/input')))
            # input credentials
            username_txt = driver.find_element(
                'xpath', '//*[@id="username-textbox"]')
            username_txt.send_keys(prism_username)
            password_txt = driver.find_element(
                'xpath', '//*[@id="password-textbox"]')
            password_txt.send_keys(prism_password)
            # login
            login_btn.click()
            time.sleep(2)
        except:
            raise Exception('Error Log In')

    def nav_policyinfo(self, driver):
        # wait if multiple user message prompts
        wait = WebDriverWait(driver, 20)

        try:
            wait.until(EC.visibility_of_element_located(
                (By.XPATH, '//div/h1[text()="Policies issued"]')))
            wait.until(EC.visibility_of_element_located(
                (By.XPATH, '//label[text()="MULTIPLE USERS"]')))
            ok_btn = wait.until(EC.visibility_of_element_located(
                (By.XPATH, '//span[text()="OK"]')))
            ok_btn.click()
            wait.until(EC.invisibility_of_element_located(
                (By.XPATH, '//label[text()="MULTIPLE USERS"]')))
        except:
            pass
        # navigate to Policy Information > ALL
        parent_menu = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//span[text()="Servicing"]')))
        ActionChains(driver).move_to_element(parent_menu).perform()
        policyinfo_btn = wait.until(EC.visibility_of_element_located(
            (By.XPATH, '//span[text()="Policy information"]')))
        ActionChains(driver).move_to_element(
            policyinfo_btn).click(policyinfo_btn).perform()
        time.sleep(2)
        all_policy_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//label[text()="ALL"]')))
        driver.execute_script("arguments[0].click();", all_policy_btn)
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, '//*[contains(@id,"-record-") and contains(@id, "gridview-")]')))

    def start_mine(self, driver):
        xpath_grid = '//*[contains(@id,"-record-") and contains(@id, "gridview-")]/tbody/tr/td[1]/div/a'
        wait = WebDriverWait(driver, 20)
        policy_dict = {}

        while True:
            elems = [elem.text for elem in driver.find_elements(
                'xpath', xpath_grid)]
            for elem in elems:
                # print(f'Getting data for: {elem}')
                while True:
                    try:
                        clickable_elem = wait.until(
                            EC.visibility_of_element_located((By.LINK_TEXT, elem)))
                        clickable_elem.click()
                        time.sleep(2)
                        elem_info = self.scrape_info(driver)
                        policy_dict.update({elem: elem_info})
                        print(f'>>> {elem} --- {elem_info["GENERAL_INFORMATION"]["INSURED_NAME"]}')
                        # print(json.dumps({elem: elem_info}, indent=4))
                        all_policy_btn = wait.until(
                            EC.element_to_be_clickable((By.LINK_TEXT, 'ALL')))
                        driver.execute_script(
                            "arguments[0].click();", all_policy_btn)
                        time.sleep(2)
                        break
                    except Exception as e:
                        self.handle_error_mining(driver, elem)
                        pass

            wait.until(EC.visibility_of_element_located(
                (By.XPATH, xpath_grid)))

            try:
                next_page_stat = self.next_page_entry(driver)
                if next_page_stat == 'last_page':
                    break
            except:
                self.handle_error_mining(driver, elems[-1])

        with open(os.path.join(sys.path[0], "policy_data.json"), "w") as outfile:
            json.dump(policy_dict, outfile)

        self.create_excel()

        self.driver.close()

    def next_page_entry(self, driver):
        wait = WebDriverWait(driver, 20)
        next_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//span[@class="fa fa-angle-right"]/ancestor::a[contains(@class,"x-btn")]')))

        if next_btn.get_attribute('ariaDisabled') == "false":
            driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(2)
            wait.until(EC.visibility_of_element_located(
                (By.XPATH, "//label[contains(text(), 'Showing ') and contains(text(), 'entries')]")))
            xpath_grid = '//*[contains(@id,"-record-") and contains(@id, "gridview-")]/tbody/tr/td[1]/div/a'
            wait.until(EC.visibility_of_element_located(
                (By.XPATH, xpath_grid)))
            return 'has_next_page'
        else:
            return 'last_page'

    def scrape_info(self, driver):
        wait = WebDriverWait(driver, 20)

        ### GENERAL_INFORMATION ###
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, '//input[@name="agent_name"]')))

        tries = 0
        while True:
            tries = tries + 1
            agent_name = wait.until(EC.visibility_of_element_located(
                (By.XPATH, '//input[@name="agent_name"]'))).get_attribute('value')
            if len(agent_name.strip()) > 0:
                break
            else:
                time.sleep(1)

            if tries > 20:
                raise Exception("Timed Out")
            else:
                pass
        policy_number = driver.find_element(
            'xpath', '//*[@aria-labelledby="policyNumber-labelEl"]').get_attribute('innerText')
        branch_name = driver.find_element(
            'xpath', '//input[@name="branch_name"]').get_attribute('value')
        owner_name = driver.find_element(
            'xpath', '//input[@name="owner_name"]').get_attribute('value')
        insured_name = driver.find_element(
            'xpath', '//input[@name="insured_name"]').get_attribute('value')
        plan_description = driver.find_element(
            'xpath', '//input[@name="planCodeDescription"]').get_attribute('value')
        plan_currency = driver.find_element(
            'xpath', '//input[@name="currency"]').get_attribute('value')
        contract_status = driver.find_element(
            'xpath', '//input[@name="contract_status"]').get_attribute('value')
        premium_status = driver.find_element(
            'xpath', '//input[@name="premium_status"]').get_attribute('value')
        sum_assured = driver.find_element(
            'xpath', '//input[@name="face_amount"]').get_attribute('value')
        non_forfeiture_option = driver.find_element(
            'xpath', '//input[@name="non_forfeiture_option"]').get_attribute('value')
        dividend_option = driver.find_element(
            'xpath', '//input[@name="dividend_option"]').get_attribute('value')
        assigned_status = driver.find_element(
            'xpath', '//input[@name="assigned_status"]').get_attribute('value')
        effectivity_date = driver.find_element(
            'xpath', '//input[@name="effectivity_date"]').get_attribute('value')
        first_issue_date = driver.find_element(
            'xpath', '//input[@name="first_issue_date"]').get_attribute('value')
        mailing_address = driver.find_element(
            'xpath', '//input[@name="despatch_address"]').get_attribute('value')
        residence_address = driver.find_element(
            'xpath', '//input[@name="residence_address"]').get_attribute('value')
        general_information = {'POLICY_NUMBER': policy_number, 'AGENT_NAME': agent_name, 'BRANCH_NAME': branch_name, 'OWNER_NAME': owner_name,
                               'INSURED_NAME': insured_name, 'PLAN_DESCRIPTION': plan_description, 'PLAN_CURRENCY': plan_currency,
                               'CONTRACT_STATUS': contract_status, 'PREMIUM_STATUS': premium_status, 'SUM_ASSURED': sum_assured,
                               'NON_FORFEITURE_OPTION': non_forfeiture_option, 'DIVIDEND_OPTION': dividend_option,
                               'ASSIGNED_STATUS': assigned_status, 'EFFECTIVITY_DATE': effectivity_date, 'FIRST_ISSUE_DATE': first_issue_date,
                               'MAILING_ADDRESS': mailing_address, 'RESIDENCE_ADDRESS': residence_address}

        ### PAYMENT_INFORMATION ###
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//*[contains(text(), 'Payment Information')]"))).click()
        time.sleep(2)

        wait.until(EC.visibility_of_element_located(
            (By.XPATH, '//input[@name="payment_method"]')))

        tries = 0
        while True:
            tries = tries + 1
            payment_method = wait.until(EC.visibility_of_element_located(
                (By.XPATH, '//input[@name="payment_method"]'))).get_attribute('value').strip()
            if len(payment_method.strip()) > 0:
                break
            else:
                time.sleep(1)

            if tries > 20:
                raise Exception("Timed Out")
            else:
                pass
        due_date = driver.find_element(
            'xpath', '//input[@name="paid_to_date"]').get_attribute('value')
        billing_frequency = driver.find_element(
            'xpath', '//input[@name="billing_frequency"]').get_attribute('value')
        modal_premium = driver.find_element(
            'xpath', '//input[@name="modal_premium"]').get_attribute('value')
        single_premium = driver.find_element(
            'xpath', '//input[@name="single_premium"]').get_attribute('value')
        payment_information = {'PAYMENT_METHOD': payment_method,
                               'DUE_DATE': due_date, 'BILLING_FREQUENCY': billing_frequency,
                               'MODAL_PREMIUM': modal_premium, 'SINGLE_PREMIUM': single_premium}

        ### PLAN_DETAILS ###
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//*[contains(text(), 'Plan Details')]"))).click()
        time.sleep(2)

        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//*[contains(text(), 'COMPONENT DESCRIPTION')]")))

        first_row_col = ''
        xpath_row_col = '//*[contains(@id,"-record-") and contains(@id, "gridview-")]/tbody/tr/td[1]'
        tries = 0
        while True:
            tries = tries + 1
            first_row_col = wait.until(EC.visibility_of_element_located(
                (By.XPATH, xpath_row_col))).text.strip()
            if len(first_row_col) > 0:
                break
            else:
                time.sleep(1)

            if tries > 20:
                raise Exception("Timed Out")
            else:
                pass
        xpath_grid = '//*[contains(@id,"-record-") and contains(@id, "gridview-")]/tbody/tr'
        rows = driver.find_elements('xpath', xpath_grid)
        plan_details = []
        row_num = 0
        for row in rows:
            row_num = row_num + 1
            cols = row.find_elements('xpath', './/td')
            component_details = {'COMPONENT_DESCRIPTION': f'{" ".join([word.strip() for word in cols[0].text.split()])}',
                                 'SUM_ASSURED': f'{" ".join([word.strip() for word in cols[1].text.split()])}',
                                 'CONTRACT_STATUS': f'{" ".join([word.strip() for word in cols[2].text.split()])}',
                                 'PREMIUM_STATUS': f'{" ".join([word.strip() for word in cols[3].text.split()])}'}
            plan_details.append(component_details)

        ### FUND_DETAILS ###
        try:
            fund_details_exist = ''
            fund_details_exist = wait.until(EC.visibility_of_element_located(
                (By.XPATH, "//*[contains(text(), 'Fund Details')]"))).text.strip()
        except:
            fund_details_exist = ''

        fund_details = []

        if len(fund_details_exist) > 0:
            wait.until(EC.visibility_of_element_located(
                (By.XPATH, "//*[contains(text(), 'Fund Details')]"))).click()
            time.sleep(2)

            wait.until(EC.visibility_of_element_located(
                (By.XPATH, "//*[contains(text(), 'FUND TYPE')]")))

            first_row_col = ''
            xpath_row_col = '//*[contains(@id,"-record-") and contains(@id, "gridview-")]/tbody/tr/td[1]'
            tries = 0
            while True:
                tries = tries + 1
                first_row_col = wait.until(EC.visibility_of_element_located(
                    (By.XPATH, xpath_row_col))).text.strip()
                if len(first_row_col) > 0:
                    break
                else:
                    time.sleep(1)

                if tries > 20:
                    raise Exception("Timed Out")
                else:
                    pass
            xpath_grid = '//*[contains(@id,"-record-") and contains(@id, "gridview-")]/tbody/tr'
            rows = driver.find_elements('xpath', xpath_grid)
            row_num = 0
            for row in rows:
                row_num = row_num + 1
                cols = row.find_elements('xpath', './/td')
                fund_type_details = {'FUND_TYPE': f'{" ".join([word.strip() for word in cols[0].text.split()])}',
                                     'UNIT_BALANCE': f'{" ".join([word.strip() for word in cols[1].text.split()])}',
                                     'UNIT_PRICE': f'{" ".join([word.strip() for word in cols[2].text.split()])}',
                                     'PRICE_DATE': f'{" ".join([word.strip() for word in cols[3].text.split()])}',
                                     'FUND_VALUE': f'{" ".join([word.strip() for word in cols[4].text.split()])}'
                                     }
                fund_details.append(fund_type_details)
        else:
            fund_details = []

        ### BENEFICIARY_DETAILS ###
        try:
            beneficiary_exist = ''
            beneficiary_exist = wait.until(EC.visibility_of_element_located(
                (By.XPATH, "//*[contains(text(), 'Beneficiary Details')]"))).text.strip()
        except:
            beneficiary_exist = ''

        beneficiary_details = []

        if len(beneficiary_exist) > 0:
            wait.until(EC.visibility_of_element_located(
                (By.XPATH, "//*[contains(text(), 'Beneficiary Details')]"))).click()
            time.sleep(2)

            wait.until(EC.visibility_of_element_located(
                (By.XPATH, "//*[contains(text(), 'NAME')]")))

            first_row_col = ''
            xpath_row_col = '//*[contains(@id,"-record-") and contains(@id, "gridview-")]/tbody/tr/td[1]'
            tries = 0
            while True:
                tries = tries + 1
                first_row_col = wait.until(EC.visibility_of_element_located(
                    (By.XPATH, xpath_row_col))).text.strip()
                if len(first_row_col) > 0:
                    break
                else:
                    time.sleep(1)

                if tries > 20:
                    raise Exception("Timed Out")
                else:
                    pass
            xpath_grid = '//*[contains(@id,"-record-") and contains(@id, "gridview-")]/tbody/tr'
            rows = driver.find_elements('xpath', xpath_grid)

            row_num = 0
            for row in rows:
                row_num = row_num + 1
                cols = row.find_elements('xpath', './/td')
                beneficiary_name_details = {'NAME': f'{" ".join([word.strip() for word in cols[0].text.split()])}',
                                            'RELATIONSHIP': f'{" ".join([word.strip() for word in cols[1].text.split()])}',
                                            'BIRTHDATE': f'{" ".join([word.strip() for word in cols[2].text.split()])}',
                                            'PERCENTAGE': f'{" ".join([word.strip() for word in cols[3].text.split()])}',
                                            'DESIGNATION': f'{" ".join([word.strip() for word in cols[4].text.split()])}'
                                            }
                beneficiary_details.append(beneficiary_name_details)
        else:
            beneficiary_details = []

        inner_dict = {'GENERAL_INFORMATION': general_information,
                      'PAYMENT_INFORMATION': payment_information,
                      'PLAN_DETAILS': plan_details,
                      'FUND_DETAILS': fund_details,
                      'BENEFICIARY_DETAILS': beneficiary_details
                      }

        # print(json.dumps(inner_dict))

        return inner_dict

    def create_excel(self):
        with open(os.path.join(sys.path[0], "policy_data.json"), "r") as readfile:
            data_panda = pd.read_json(readfile).transpose()
            data_panda.to_excel(excel_writer=os.path.join(
                sys.path[0], "policy_data.xlsx"), index_label='POLICIES')


if __name__ == "__main__":

    prismscraper = PrismScraper()
    prismscraper.policyinfo_flow()
    # prismscraper.create_excel()
