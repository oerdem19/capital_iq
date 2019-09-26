# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 01:49:07 2019

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
DOMAIN = "https://www.capitaliq.com/"
transactions = "/ciqdotnet/Transactions/"
USER_ID = "xyz"
PASSWORD = "xyz!"
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


links = ["https://www.capitaliq.com/ciqdotnet/Transactions/TransactionSummary.aspx?CompanyId=21766771&transactionViewType=2",
"https://www.capitaliq.com/ciqdotnet/Transactions/TransactionSummary.aspx?CompanyId=247573796&transactionViewType=2",
"https://www.capitaliq.com/ciqdotnet/Transactions/TransactionSummary.aspx?CompanyId=7756191&transactionViewType=2",
"https://www.capitaliq.com/ciqdotnet/Transactions/TransactionSummary.aspx?CompanyId=27169435&transactionViewType=2",
"https://www.capitaliq.com/ciqdotnet/Transactions/TransactionSummary.aspx?CompanyId=968960&transactionViewType=2",
"https://www.capitaliq.com/ciqdotnet/Transactions/TransactionSummary.aspx?CompanyId=7820161&transactionViewType=2",
"https://www.capitaliq.com/ciqdotnet/Transactions/TransactionSummary.aspx?CompanyId=35533642&transactionViewType=2",
"https://www.capitaliq.com/ciqdotnet/Transactions/TransactionSummary.aspx?CompanyId=25604401&transactionViewType=2",
"https://www.capitaliq.com/ciqdotnet/Transactions/TransactionSummary.aspx?CompanyId=859008&transactionViewType=2",
"https://www.capitaliq.com/ciqdotnet/Transactions/TransactionSummary.aspx?CompanyId=3554501&transactionViewType=2",
"https://www.capitaliq.com/ciqdotnet/Transactions/TransactionSummary.aspx?CompanyId=6628309&transactionViewType=2",
"https://www.capitaliq.com/ciqdotnet/Transactions/TransactionSummary.aspx?CompanyId=8610803&transactionViewType=2",
"https://www.capitaliq.com/ciqdotnet/Transactions/TransactionSummary.aspx?CompanyId=688540&transactionViewType=2",
"https://www.capitaliq.com/ciqdotnet/Transactions/TransactionSummary.aspx?CompanyId=38572588&transactionViewType=2",
"https://www.capitaliq.com/ciqdotnet/Transactions/TransactionSummary.aspx?CompanyId=318523&transactionViewType=2",
"https://www.capitaliq.com/ciqdotnet/Transactions/TransactionSummary.aspx?CompanyId=706277&transactionViewType=2",
"https://www.capitaliq.com/ciqdotnet/Transactions/TransactionSummary.aspx?CompanyId=110741&transactionViewType=2",
"https://www.capitaliq.com/ciqdotnet/Transactions/TransactionSummary.aspx?CompanyId=38442952&transactionViewType=2",
"https://www.capitaliq.com/ciqdotnet/Transactions/TransactionSummary.aspx?CompanyId=33509757&transactionViewType=2",
"https://www.capitaliq.com/ciqdotnet/Transactions/TransactionSummary.aspx?CompanyId=8285067&transactionViewType=2"
]

size = ["83.70",
"166.67",
"64.32",
"54.50",
"135.19",
"93.45",
"51.93",
"122.32",
"211.85",
"475.00",
"134.10",
"675.86",
"22.00",
"462.50",
"267.19",
"49.60",
"1,125.00",
"257.40",
"220.00",
"184.65",

]
def login_to_ciq(DOMAIN, userid, password, driver, chunk_links,chunk_size, run):
    if run == 0 :
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
        links_to_ipo_links(chunk_links, chunk_size, driver, run)
    else:
        links_to_ipo_links(chunk_links, chunk_size, driver, run)


        
def links_to_ipo_links(ch_links, ch_size, driver, run):
    ipo_table = []
    for link, size in zip(ch_links, ch_size):
        flag = 0
        driver.get(link)
        time.sleep(0.5)
        try:
            element = driver.find_element(by=By.ID, value="POTransactionGrid_viewall")
            element.click()
            print("Used View All")
        except:
            print("All elements Visible")
        html = driver.page_source
        soup = BeautifulSoup(html, features="html.parser")
        transaction_table = soup.find('table', class_ = "cTblListBody").find('tbody')
        all_rows = transaction_table.find_all('tr')
        for row in all_rows:
            all_columns = row.find_all('td')
            ipo_entry = []
            for column in all_columns:
                if column.text == 'IPO':
                    transaction_row = row.find_all('td')
                    transaction_table_page = transaction_row[1].a['href']
                    ipo_entry.append(transaction_table_page)
                    ipo_entry.append(size)
                    for column in transaction_row:
                        ipo_entry.append(column.text.replace('\n',''))
                    ipo_table.append(ipo_entry)
                    flag = 1
                else:
                    pass
        if flag == 0 :
            print(f"No IPO found for {link}")
            no_ipo_company.append(link)
    final_df = pd.DataFrame()
    print(ipo_table)
    for entry in ipo_table:
        driver.get(DOMAIN + transactions + entry[0])
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
            data['balance_sheet_date/as_of_date'] = [NOTE.split('as of:')[1].split('Period Ending:')[0].replace(u'Â', '').replace(u'\xa0', '')]
            data['period_ending'] = [NOTE.split('Period Ending:')[1].split('Exchange Rate')[0].replace(u'Â', '').replace(u'\xa0', '')]
            data['exchange_rate'] = [NOTE.split('=')[1].replace(u'Â', '').replace(u'\xa0', '')]
            data['link'] = DOMAIN + "CIQDotNet/Transactions/" + entry[0]
            data['manual_size'] = entry[1]
            data['Registration_Effective'] = entry[4]
            data['Offer_Date'] = entry[5]
            data['Company_name'] = entry[6] 
            data['size'] = entry[9]
            final_df = pd.concat([data, final_df])
        except:
            print("LTM Table not found")
            data['link'] = DOMAIN + "CIQDotNet/Transactions/" + entry[0]
            data['manual_size'] = entry[1]
            data['Registration_Effective'] = entry[4]
            data['Offer_Date'] = entry[5]
            data['Company_name'] = entry[6] 
            data['size'] = entry[9]
            data['NOTE'] = "LTM Table not found"
            final_df = pd.concat([data, final_df])
            ltm_table_not_found.append(entry[0])
            continue
    final_df.to_csv(f'/c/Users/pavan/Documents/Python_Environment/capital_iq/manual_17th_September/capital_iq_{run}.csv', header = True)
    final_ipo_list.append(ipo_table)
    print(f"Dropped File {run} in location")

def divide_chunks(l,n):
    for i in range(0, len(l), n):  
        yield l[i:i + n]

    


n = 10
chunk_links = list(divide_chunks(links, n))
chunk_size = list(divide_chunks(size, n))


start_time = time.time()
for link_chunks, size_chunks in zip(chunk_links, chunk_size):
    try:
        print(link_chunks)
        print(size_chunks)
        login_to_ciq(DOMAIN, USER_ID, PASSWORD, chrome_driver, link_chunks,size_chunks, run)
    except:
        print(f"Run {run} failed...")
        print("Run failed for this")
        continue
    run = run + 1


print(f"Total time of code execution for ALL companies {time.time() - start_time} ")
print(f"List of ALL IPOs scraped is:{final_ipo_list}")
print(f"No IPO Company : {no_ipo_company}")
