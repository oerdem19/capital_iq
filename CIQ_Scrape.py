# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 20:22:40 2019

@author: pavan
"""

import time
import datetime
import pandas as pd
import re
import urllib3
import requests
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup
from companies import companies_list

#Static Args
DOMAIN = "https://www.capitaliq.com/"
transactions = "/ciqdotnet/Transactions/"
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

def login_to_ciq(DOMAIN, userid, password, driver, company_names, run):
    if run == 0 :
        driver.get(DOMAIN)
        driver.wait = WebDriverWait(driver, 10)
        box = driver.wait.until(EC.presence_of_element_located((By.ID, "username")))
        secondbox = driver.wait.until(EC.presence_of_element_located((By.ID, "password")))
        button = driver.wait.until(EC.element_to_be_clickable((By.ID, "myLoginButton")))
        box.send_keys(userid)
        secondbox.send_keys(password)
        button.click()
        companies = search_company_ids(company_names, driver, run)
        companies_to_ipo_links(companies,driver, run)
    else:
        companies = search_company_ids(company_names, driver, run)
        companies_to_ipo_links(companies,driver, run)

def search_company_ids(company_names, driver, run):
    companies = []
    for company in company_names:
        driver.get(DOMAIN)
        logging.info("Trying to find search bar now")
        search_box = driver.wait.until(EC.presence_of_element_located((By.ID, "SearchTopBar")))
        logging.info("finding button now")
        button = driver.wait.until(EC.element_to_be_clickable((By.ID, "ciqSearchSearchButton")))
        search_box.send_keys(company.strip())
        button.click()
        html = driver.page_source
        soup = BeautifulSoup(html, features="html.parser")
        if driver.current_url == "https://www.capitaliq.com/CIQDotNet/Search/Search.aspx":
            result = soup.find('table', id = "ctl01__SearchGridView")
            if result is None:
                company_search_error.append(company)
                continue
            link = DOMAIN + result.find('tbody').tr.find('td', class_ = 'NameCell').div.span.a['href']
            cid = link.split("&pid=")[1]
            companies.append(cid)
            company_dict.update({company:cid})
        else:
            link = driver.current_url
            cid = link.split("=")[1]
            companies.append(cid)
            company_dict.update({company:cid})
    return companies
        
def companies_to_ipo_links(companies, driver, run):     
    ipo_links = []
    for cid in companies:
        flag = 0
        url = "https://www.capitaliq.com/ciqdotnet/Transactions/TransactionSummary.aspx?CompanyId={cid}&transactionViewType=2".format(cid = cid)
        print(url)
        driver.get(url)
        try:
            element = driver.find_element(by=By.ID, value="POTransactionGrid_viewall")
            element.click()
            print("Used View All")
        except:
            print("All elements Visible")
        html = driver.page_source
        soup = BeautifulSoup(html, features="html.parser")
        transaction_table = soup.find('table', class_ = "cTblListBody").find('tbody')
        #print(transaction_table)
        all_rows = transaction_table.find_all('tr')
        for row in all_rows:
            all_columns = row.find_all('td')
            for column in all_columns:
                if column.text == 'IPO':
                    transaction_table_page = row.find_all('td')[1].a['href']
                    ipo_links.append(transaction_table_page)
                    company_ipo_dict.update({cid:transaction_table_page})
                    flag = 1
                else:
                    pass
        if flag == 0 :
            print(f"No IPO for company with CompanyID={cid}")
            no_ipo_company.append(cid)
    final_df = pd.DataFrame()
    print(ipo_links)
    for link in ipo_links:
        driver.get(DOMAIN + transactions + link)
        try:    
            xpath = f"//*[@id=\"{ltm_table_id}\"]/span/table/tbody/tr/td/table"
            tbl = driver.find_element_by_xpath(xpath).get_attribute('outerHTML')
            df  = pd.read_html(tbl)[0]
            NOTE = df[0][0]
            print(NOTE)
            df1 = df.loc[:, 0:1].drop([0], axis = 0)
            df2 = df.loc[:, 2:3].drop([0], axis = 0)
            df2.columns = df1.columns
            data = pd.concat([df1,df2], axis = 0, ignore_index=True).dropna().set_index(0).T.reset_index()
            data['balance_sheet_date/as_of_date)'] = [NOTE.split('as of:')[1].split('Period Ending:')[0].replace(u'Â', '').replace(u'\xa0', '')]
            data['period_ending'] = [NOTE.split('Period Ending:')[1].split('Exchange Rate')[0].replace(u'Â', '').replace(u'\xa0', '')]
            data['exchange_rate'] = [NOTE.split('=')[1].replace(u'Â', '').replace(u'\xa0', '')]
            data['link'] = link
            final_df = pd.concat([data, final_df])
        except:
            print("LTM Table not found")
            ltm_table_not_found.append(link)
            continue
    final_df.to_csv(f'/c/Users/pavan/Documents/Python_Environment/capital_iq/rest/capital_iq_{run}.csv', header = True)
    print(f"Dropped File {run} in location")
    df = pd.DataFrame.from_dict(company_dict, orient="index")
    df.to_csv(f'/c/Users/pavan/Documents/Python_Environment/capital_iq/rest/capital_iq_company_dict.csv', header = False)
    df2 = pd.DataFrame.from_dict(company_ipo_dict, orient="index")
    df2.to_csv(f'/c/Users/pavan/Documents/Python_Environment/capital_iq/rest/capital_iq_company_ipo_dict.csv', header = False)
        
def divide_chunks(l,n):
    for i in range(0, len(l), n):  
        yield l[i:i + n]

def dictionary_to_csv():
    df = pd.DataFrame.from_dict(company_dict, orient="index")
    df.to_csv(f'/c/Users/pavan/Documents/Python_Environment/capital_iq/rest/capital_iq_company_dict.csv', header = False)
    print("Dropped File company_dict in location")
    df2 = pd.DataFrame.from_dict(company_ipo_dict, orient="index")
    df2.to_csv(f'/c/Users/pavan/Documents/Python_Environment/capital_iq/rest/capital_iq_company_ipo_dict.csv', header = False)
    print("Dropped File company_ipo_dict in location")
    print(f"""
          These files did not have a IPO page attached to them
          {no_ipo_company}
          """)
    print(f"""
          These companies faced errors on the search page:
          {company_search_error}
          """)
    print(f"""
          These links did not have an LTM table on its page.
          {ltm_table_not_found}
          """)
companies_list = companies_list()

n = 10
list_companies = list(divide_chunks(companies_list, n))
start_time = time.time()
for company_list in list_companies:
    try:
        login_to_ciq(DOMAIN, USER_ID, PASSWORD, chrome_driver, company_list, run)
    except:
        print(f"Run {run} failed...")
        continue
    run = run + 1

dictionary_to_csv()
print(f"Total time of code execution for 500 companies {time.time() - start_time} ")
