# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 19:07:48 2019

@author: pavan
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 19:59:05 2019

@author: pavan
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 01:49:07 2019

@author: pavan
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 20:53:03 2019

@author: pavan
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 20:22:40 2019

@author: pavan
"""

import time
import pandas as pd
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


#Static Args
DOMAIN = "https://www.capitaliq.com"
income_statement = "https://www.capitaliq.com/CIQDotNet/Financial/IncomeStatement.aspx?companyId="
USER_ID = "xyz"
PASSWORD = "xyz"
company_names = []
chrome_driver = webdriver.Chrome(executable_path = r"/c/Users/pavan/Downloads/Chrome/chromedriver.exe")
ltm_table_id = "ctl08_ctl08_Toggle"
run = 0

ipo_links = []
company_ipo_dict = {}
company_dict = {}
no_ipo_company = []
company_search_error = []
ltm_table_not_found = []
final_ipo_list = []
company_id_list = []

cid = [
"33414",
"36756",
"9249477",
"364700",
"13598362",
"13669587",
"11610157",
"6904040",
"109884",
"22298677",
"2381971",
"522765",
"12519035",
"3554517",
"27630454",
"26669504",
"7795259",
"986834",
"242224249",
"99080961"
]

ped = [
"Mar-26-2005",
"Jun-30-2004",
"Dec-31-2004",
"Dec-31-2004",
"Dec-31-2004",
"Dec-31-2004",
"Dec-31-2004",
"Jun-30-2005",
"Jun-30-2005",
"Jun-30-2005",
"Sep-30-2005",
"Sep-30-2005",
"Sep-30-2005",
"Sep-30-2006",
"Jun-30-2006",
"Jun-30-2006",
"Jun-30-2006",
"Sep-30-2013",
"Aug-03-2013",
"Jun-30-2013"  
]

fail = 0
def login_to_ciq(DOMAIN, userid, password, driver, company_id_list, pe_date_list, run):
    if run == 0 and fail == 0:
        driver.get(DOMAIN)
        driver.wait = WebDriverWait(driver, 10)
        box = driver.wait.until(EC.presence_of_element_located((By.ID, "username")))
        secondbox = driver.wait.until(EC.presence_of_element_located((By.ID, "password")))
        button = driver.wait.until(EC.element_to_be_clickable((By.ID, "myLoginButton")))
        box.send_keys(userid)
        time.sleep(1.5)
        secondbox.send_keys(password)
        time.sleep(1.5)
        button.click()
        time.sleep(1.5)
        links_to_ipo_links(company_id_list, pe_date_list, driver, run)
    else:
        links_to_ipo_links(company_id_list, pe_date_list, driver, run)


        
def links_to_ipo_links(company_id_list, pe_date_list, driver, run):
    final_df = pd.DataFrame()
    for company, pe_date in zip(company_id_list, pe_date_list):
        driver.get(income_statement+company)
        time.sleep(0.5)
        element = driver.wait.until(EC.element_to_be_clickable((By.ID, "_pageHeader_ShowMoreLink")))
        element.click()
        print("Clicked More Options")
        #click LTM
        if driver.find_element_by_xpath("//*[@id=\"_pageHeader_fin_dropdown_period\"]").find_element_by_tag_name('option').text != "LTM":
            driver.find_element_by_xpath("//*[@id=\"_pageHeader_fin_dropdown_period\"]").send_keys("LTM")
            print("Clicked LTM")
        #Click Original Fillings
        if driver.find_element_by_xpath("//*[@id=\"_pageHeader_fin_dropdown_restatement\"]").find_element_by_tag_name('option').text != "Original Filings":
            driver.find_element_by_xpath("//*[@id=\"_pageHeader_fin_dropdown_restatement\"]").send_keys("Original Filings")
            print("clicked original fillings")
        #click USD
        if driver.find_element_by_xpath("//*[@id=\"_pageHeader_fin_dropdown_currency\"]").find_element_by_tag_name('option').text != "US Dollar":
            driver.find_element_by_xpath("//*[@id=\"_pageHeader_fin_dropdown_currency\"]").send_keys("US Dollar")
            print("clicked USD")
        if driver.find_element_by_xpath("//*[@id=\"_pageHeader_fin_dropdown_template\"]").find_element_by_tag_name('option').text != "Standard":
            driver.find_element_by_xpath("//*[@id=\"_pageHeader_fin_dropdown_template\"]").send_keys("Standard")
            print("clicked standard")
        if driver.find_element_by_xpath("//*[@id=\"_pageHeader_fin_dropdown_conversion\"]").find_element_by_tag_name('option').text != "Historical":
            driver.find_element_by_xpath("//*[@id=\"_pageHeader_fin_dropdown_conversion\"]").send_keys("Historical")
            print("clicked historical")
        time.sleep(0.25)
        go_button = driver.find_element(by=By.ID, value="_pageHeader__goButtonRow5")
        go_button.click()
        element2 = driver.wait.until(EC.element_to_be_clickable((By.ID, "ctl03__rangeSlider_viewAll")))
        element2.click()
        print("clicked view all")
        html = driver.page_source
        soup = BeautifulSoup(html, features="html.parser")
        financial_table = soup.find('table', class_ = "FinancialGridView").find('tbody')
        print("found table")
        rnd_row = financial_table.find('span', text = "R & D Exp.").find_parent('tr')
        print("found row")
        all_entries = rnd_row.find_all('td', class_="dC")
        print("found all columns")
        flag1 = 0
        rnd_data = pd.DataFrame()
        for entry in all_entries:
            print("inside Loop")
            try:
                data = entry.find('div', class_ = "tCH").find('a')['title']
                flag1 = 1
                print("found proper entry in column")
            except:
                print("failed to find entry in column")
                continue
            print("checking entry")
            data_elements = data.split("\n")
            flag2 = 0
            if data_elements[2].split(":")[1].strip() == pe_date:
                flag2 = 1
                print("record matched")
                rnd_data['company_id'] = [company]
                rnd_data['data'] = data_elements[0]
                rnd_data['FY'] = [data_elements[1].split(":")[1].split(",")[0].strip()]
                rnd_data['period_ending_ciq'] = [data_elements[2].split(":")[1].strip()]
                rnd_data['filing_date_ciq'] = [data_elements[3].split(":")[1].strip()]
                rnd_data['period_type_ciq'] = [data_elements[4].split(":")[1].strip()]
                rnd_data['value_ciq'] = [data_elements[5].split(",")[0].split(":")[1].strip()]
                rnd_data['currency'] = [data_elements[5].split(",")[1].split(":")[1].strip()]
                break
        if flag1 == 0:
            rnd_data['company_id'] = [company]
            rnd_data['NOTE'] = ["DATA EMPTY"]
        elif flag2 == 0:
            rnd_data['company_id'] = [company]
            rnd_data['NOTE'] = ["No DATES Matched or Data Empty"]
        print(rnd_data)
        final_df = pd.concat([rnd_data, final_df])
    final_df.to_csv(f'/c/Users/pavan/Documents/Python_Environment/capital_iq/rnd/final_run4/capital_iq_{run}.csv', header = True)
    print(f"Dropped File {run} in location")

def divide_chunks(l,n):
    for i in range(0, len(l), n):  
        yield l[i:i + n]

    


n = 1
chunk_company_id = list(divide_chunks(cid, n))
chunk_pe_date_list = list(divide_chunks(ped, n))


start_time = time.time()
for company_id_list, pe_date_list in zip(chunk_company_id, chunk_pe_date_list):
    try:
        login_to_ciq(DOMAIN, USER_ID, PASSWORD, chrome_driver, company_id_list, pe_date_list, run)
    except:
        print(f"Run {run} failed...")
        print("Run failed for this")
        fail = 1
        continue
    run = run + 1


print(f"Total time of code execution for ALL companies {time.time() - start_time} ")
print(f"List of ALL IPOs scraped is:{final_ipo_list}")
print(f"No IPO Company : {no_ipo_company}")
