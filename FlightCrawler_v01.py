#!/usr/bin/env python
# coding: utf-8

# In[39]:


import argparse, os, time
import random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re
from datetime import datetime
import sys


# ## Aux

# In[40]:


def timestamp():
    # Take time stamp
    tm_stamp= datetime.now()
    date_string = datetime.strftime(tm_stamp,"%d/%m/%y")
    time_string = datetime.strftime(tm_stamp,"%H:%M:%S")
    return date_string, time_string


# # Ryanair

# In[41]:


def ryanair(browser):
    # open start page
    browser.get("https://www.ryanair.com/it/it/booking/home/STN/CIA/2019-09-20//1/0/0/0")
    time.sleep(20)
    # result page
    page = BeautifulSoup(browser.page_source)
    
    # find boxes with sets or results
    boxes = page.find_all("div", class_= ["flight-header","flight-header flight-header__notice"])
    last_box = boxes[len(boxes)-1]
    
    # extract flight data
    start_time = last_box.find_all("div", class_="start-time")[0].string
    end_time = last_box.find_all("div", class_="end-time")[0].string
    price_span = last_box.find_all("span", class_="flights-table-price__price")
    soldout_div = last_box.find_all("div", class_="flight-header__sold-out")

    # if flight available
    if price_span != []:
        price_string = price_span[0].string
        # change , to .
        price_string = re.sub(",",".",price_string)
        # split price and currency
        price, currency = re.split("\xa0",price_string)
        notice_tag = last_box.find_all("span", class_="flights-table-price__notice")
        if notice_tag == []:
            notice = ""
        else:
            notice = notice_tag[0].string

     # if sold out        
    if soldout_div != []:
        price = 'nan'
        currency = ''
        notice = 'Sold out'

    # Take time stamp
    date_string, time_string = timestamp()
    
    # add to csv file
    import csv
    with open('C:\\rob\\SVN\\Python\\FlightBot\\flight_data.csv', mode='a', newline='') as flight_data_file:
        flight_writer = csv.writer(flight_data_file)
        flight_writer.writerow            ([date_string, time_string,'Ryanair',start_time, end_time, price, currency, str(notice)])


# # Alitalia

# In[42]:


def alitaliaFillInForm(browser):
    browser.get("https://www.alitalia.com/it_it/homepage.html")
    time.sleep(5)
    # prenota button
    prenota = browser.find_element_by_class_name("cerca-volo__title")
    prenota.click()
    time.sleep(random.uniform(10,11))
    # aeroporto partenza form
    part= browser.find_elements_by_name("list_andata--prenota")
    part[0].clear()
    part[0].send_keys("Londra LHR")
    time.sleep(random.uniform(1,2))
    # aeroporto arrivo form
    arr = browser.find_elements_by_name("destination--prenota")
    arr[0].click()
    arr[0].send_keys("Roma FCO")
    time.sleep(random.uniform(1,2))
    # data andata
    date_andata = browser.find_element_by_name("date_andata")
    date_andata.send_keys("20/09/2019")
    time.sleep(random.uniform(1,2))
    date_andata.send_keys(Keys.RETURN)
    time.sleep(random.uniform(1,2))
    # data ritorno
    date_ritorno = browser.find_element_by_name("date_ritorno")
    date_ritorno.send_keys("25/09/2019")
    time.sleep(random.uniform(1,2))

    # bottoni
    page = BeautifulSoup(browser.page_source)
    # lists of all buttons
    inps = page.find_all(True, class_=["button"])
    k=0
    ix_button=[] # indice del bottone
    for inp in inps:
        dic=inp.attrs
        dk = list(dic.keys())
        if 'class' in dk and 'value' in dk and 'aria-label' in dk:
            ix_button.append(k)
        k=k+1
        # bottone 'cerca'
        val_but = browser.find_elements_by_class_name("button")
    cerca_button = val_but[ix_button[0]]
    cerca_button.click()
    time.sleep(random.uniform(1,2))
    # submit form
    butt = browser.find_element_by_id("submitHidden--prenota")
    butt.click()


# In[43]:


def alitaliaCollectResults(browser):
    page = BeautifulSoup(browser.page_source)
    # righe di risultati
    rows = page.find_all("div", class_="bookingTable__bodyRow j-bookTableRow")
    # pick the row with the right flight times
    for row in rows:
        times = row.find_all("span", class_="booking__fightPreviewDepArrCont__time")
        out = re.findall("\d\d:\d\d", str(times[0]))
        start_time = out[0]
        out = re.findall("\d\d:\d\d", str(times[1]))
        end_time = out[0]
        all_times = (start_time + " " + end_time)
        if all_times == "20:00 23:30":
            right_row = row
            break

    # all boxes in the right row
    boxes=right_row.find_all('a', class_="infoFlightWrapperBtn j-priceSelector")

    # alert in first box
    alert=boxes[0].find_all('span', class_='alert')
    if alert == []:
        notice = ''
    else:
        notice = alert[0].string
    notice
    
    # get price in first box
    qq=boxes[0].find_all("span", class_="price")
    price = re.findall('\d+,\d+', qq[0].string)[0]
    price = re.sub(',','.',price) # replace , with .

    #take time stamp
    date_string, time_string = timestamp()

    # add to csv file
    import csv
    with open('C:\\rob\\SVN\\Python\\FlightBot\\flight_data.csv', mode='a', newline='') as flight_data_file:
        flight_writer = csv.writer(flight_data_file)
        flight_writer.writerow            ([date_string, time_string,'Alitalia',start_time, end_time, price, 'Eur', str(notice)])


# In[44]:


def alitalia(browser):
    # riempi moduli e lancia search
    alitaliaFillInForm(browser)
    # wait for res load
    time.sleep(30)
    # collect results
    alitaliaCollectResults(browser)


# ## Easyjet

# In[45]:


def easyjetFillInForm(browser):
    # load page
    browser.get("https://www.easyjet.com/en")
    time.sleep(10)
    
    # one way checkbox
    time.sleep(random.uniform(1,2))
    inp_one_way = browser.find_element_by_class_name("checkbox")
    inp_one_way.click()
    # destinations
    time.sleep(random.uniform(1,2))
    origin = browser.find_element_by_name("origin")
    origin.clear()
    origin.send_keys("London Luton (LTN)", Keys.RETURN)
    
    time.sleep(random.uniform(1,2))
    dest = browser.find_element_by_name("destination")
    dest.clear()
    dest.send_keys("Rome Fiumicino (FCO)", Keys.RETURN)
    # date selection
    # click on calendar button
    time.sleep(random.uniform(1,2))
    chdate = browser.find_element_by_class_name("chosen-date")
    chdate.click()
    # pick right day
    time.sleep(random.uniform(4,5))
    
    
    page=BeautifulSoup(browser.page_source)
    # index with right date
    days = page.find_all(True, class_="day")
    k=0
    ix = []
    for day in days:
        if "2019-09-20" in str(day):
            ix.append(k)
        k = k+1
    # click on right date
    aselectable = browser.find_elements_by_class_name("day") # all days
    ixout = ix[0]
    aselectable[ixout].click()
    
    # search
    time.sleep(random.uniform(1,2))
    search_button = browser.find_element_by_xpath        ("//button[@class='ej-button rounded-corners arrow-button search-submit']")
    search_button.click()


# In[46]:


def easyjetCollectResults(browser):
    # switch to second page
    browser.switch_to.window(browser.window_handles[1])
    #
    page = BeautifulSoup(browser.page_source)
    # grid with results
    flight_grid = page.find_all("div", class_='flight-grid-day')
    # pick middle one
    right_grid =flight_grid[1]
    # flight times
    flight_times = right_grid.find_all('span', class_="flight-time")
    start_time = flight_times[0].string
    end_time = flight_times[1].string

    # check it's right date
    spans = right_grid.find_all('span')
    flight_date=spans[1]
    if '20 Sep' not in flight_date.string:
        iserror = True
    else:
        iserror = False
    # extract price
    xx=right_grid.find_all('span', class_='access-hidden')
    price_string = xx[2].string
    currency = price_string[0]
    price = price_string[1:]

    # no notice
    notice = ''
    
    #take time stamp
    date_string, time_string = timestamp()

    
    if iserror:
        print('ERROR!')
    else:
         # add to csv file
        import csv
        with open('flight_data.csv', mode='a', newline='') as flight_data_file:
            flight_writer = csv.writer(flight_data_file)
            flight_writer.writerow                ([date_string, time_string,'Easyjet',start_time, end_time, price, currency, str(notice)])


# In[47]:


def easyjet(browser):
    easyjetFillInForm(browser)
    
    time.sleep(20)
    
    easyjetCollectResults(browser)


# ## Main script

# In[50]:



# launch browser
browser = webdriver.Chrome()

# run ryanair
try:
	ryanair(browser)
except:
	print('ryanair failed - ', sys.exc_info()[1])

# run alitalia
try:
	alitalia(browser)
except:
	print('alitalia failed - ', sys.exc_info()[1])

# run easyjet
try:
	easyjet(browser)
except:
	print('easyjet failed - ', sys.exc_info()[1])


browser.quit()


# In[ ]:




