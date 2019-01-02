
import re
import string
from urllib import parse as urlparse

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import csv
# from selenium import TimeUnit
class ArchitectFinderScraper(object):
    def __init__(self):
        self.url = "https://www.samrakshane.karnataka.gov.in"
        
        options = webdriver.ChromeOptions()
        # options.add_argument('headless')

        self.driver = webdriver.Chrome(chrome_options=options)
        # self.driver.implicitly_wait(2)
    def scrape(self):
        self.driver.get(self.url)
        wait=WebDriverWait(self.driver,10)
        wait.until(lambda driver:driver.find_element_by_id('top')).is_displayed()
        self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_BtnGo').click()
        self.driver.get(self.url+"/Premium/Crops_You_Can_Insure.aspx")
        
        try:
            self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_btnAccept').click()
        except NoSuchElementException:
            pass

        select = Select(self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_DDLSeason'))
        option_indexes = range(1, len(select.options))
        
        districts=Select(self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_DDLDistrict'))
        
        district_option_indexes=range(1,len(districts.options))
        for index in option_indexes:
            try:
                if(index!=1):                        
                    select = Select(self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_DDLSeason'))  
                time.sleep(1)
                                
                select.select_by_index(index)
                for d_index in district_option_indexes:
                    try:
                        if(d_index!=1):                        
                                districts=Select(self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_DDLDistrict'))
                        time.sleep(1)                
                        districts.select_by_index(d_index)
                        wait=WebDriverWait(self.driver,15)
                        wait.until(EC.staleness_of(self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_DDLTaluk')))
                        taluks=Select(self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_DDLTaluk'))
                        taluk_option_indexes=range(1,len(taluks.options))
                        for taluk_index in taluk_option_indexes:
                            try:
                                if(taluk_index!=1):                        
                                    taluks=Select(self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_DDLTaluk'))
                                time.sleep(1.5)
                                taluks.select_by_index(taluk_index)
                                                
                                self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_btnShowPre').click()
                                pageno=2
                                while True:
                                    time.sleep(1)
                                    s=BeautifulSoup(self.driver.find_element_by_id('ctl00_ContentPlaceHolder1_gvCropYouCanInsure').get_attribute('innerHTML'),'html.parser')                                  
                                    table=s
                                    trs=s.find('tr').parent.find_all('tr',recursion=False)
                                    rows=[]
                                    for row in trs[:-2]:
                                        rows.append([val.text.encode('utf-8').decode('utf-8') for val in row.find_all('td')])
                                    with open('data.csv','a') as file_out:
                                        writer=csv.writer(file_out)
                                        writer.writerows(row for row in rows if len(row)>0)
                                    try:
                                        if(pageno%11!=0):
                                            next_page_elem = self.driver.find_element_by_xpath("//a[text()='%d']" % pageno)
                                            pageno+=1
                                        else:
                                            next_page_elem = self.driver.find_elements_by_xpath("//a[text()='...']")
                                            if(len(next_page_elem)==0 and pageno==11):
                                                break
                                            elif(len(next_page_elem)==1 and pageno==11):
                                                next_page_elem=next_page_elem[0]
                                                pageno+=1
                                            elif(len(next_page_elem)==2):
                                                next_page_elem=next_page_elem[1]
                                                pageno+=1
                                            else:
                                                break
                                        if(not isinstance(next_page_elem,list)):
                                            next_page_elem.click()
                                    except NoSuchElementException:
                                        pageno=2
                                        break # no more pages
                            except Exception:
                                continue
                    except Exception:
                        continue
            except Exception:
                continue           

        self.driver.quit()

if __name__ == '__main__':
    scraper = ArchitectFinderScraper()
    scraper.scrape()        
