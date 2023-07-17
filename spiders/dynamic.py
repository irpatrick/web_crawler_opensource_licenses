# UNDER DEVELOPMENT

from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
# url = 'https://data.un.org/Search.aspx?q=kenya'
url = 'https://data.europa.eu/data/datasets?locale=en&query=rwanda&page=1&limit=20'

driver = webdriver.Chrome()

driver.get(url=url)

sleep(5)
#ctl00_main_pnlResults > div.Results > div.ResultSet > div:nth-child(1)
# next = driver.find_element(By.ID, "ctl00_main_results_linkNext")
# next = driver.find_element(By.CLASS_NAME, "next-button")
accept = driver.find_element(By.CSS_SELECTOR, "#cookie-btn-accept")
last_page = driver.find_element(By.CSS_SELECTOR, "body > div > div.site-wrapper > div.mt-0.d-flex.flex-column.p-0.bg-transparent.content > div > div:nth-child(3) > div > div > ul > li:nth-child(3) > button").text
try:
    accept.click()
    sleep(2)
except:
    pass
# ctl00_main_results_linkNext
c = 0
for i in range(int(last_page)):
    sleep(9) 
    c+=1
    print(i)
    try:
        results = driver.find_elements(By.CLASS_NAME, "dataset-info-box-body")
        #  print(results[0].find_element(By.TAG_NAME,"a").text)
        for a in results:
            print(a.find_element(By.TAG_NAME,"h2").text)
    except Exception:
        pass   
    next = driver.find_element(By.CLASS_NAME, "next-button")
    if i < int(last_page)-1:
        next.click()
