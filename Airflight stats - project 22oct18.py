#!/usr/bin/env python
# coding: utf-8

# In[1]:


from bs4 import BeautifulSoup
import requests
import json
from pathlib import Path


# In[2]:


html_page = "downloaded_page_for_list_extraction.html"


# In[3]:


# extract carrier list values

def extract_data(page):
    data = []
    
    with open(page, "r") as html:
        soup = BeautifulSoup(html, "lxml")
        carr = soup.find(id = "CarrierList")
        for rows in carr.find_all('option'):
            val = (rows['value'])
            if(len(val) == 2): #Not selecting carrier grouped values like 'all'
                data.append(val)
                
    return data


# extract airport list values

def extract_airports(page):
    data = []
    
    with open(page, "r") as html: 
        soup = BeautifulSoup(html, "lxml")
        select = soup.find(id = "AirportList")
        for row in select.find_all("option"):
            val = row['value']
            if(val[0:3].lower() != 'all'): #Not selecting airport grouped values like 'all'
                data.append(val)
            
    return data
        
        


# In[4]:


carrier_list = extract_data(html_page)

airport_list = extract_airports(html_page)


# In[5]:


# Total number of carrier-airport combinations
print(len(airport_list) * len(carrier_list))


# In[ ]:


URL = "https://www.transtats.bts.gov/Data_Elements.aspx?Data=2"
s = requests.Session() 
resp = s.get(URL)
soup = BeautifulSoup(resp.text, "lxml")

#Finding header values for the requests
viewstate = soup.find(id = "__VIEWSTATE")['value']
eventvalidation = soup.find(id = "__EVENTVALIDATION")['value']
viewstategenerator = soup.find(id = "__VIEWSTATEGENERATOR")['value']


# In[10]:


def new_session():
    URL = "https://www.transtats.bts.gov/Data_Elements.aspx?Data=2"
    s = requests.Session()
    resp = s.get(URL)
    soup = BeautifulSoup(resp.text, "lxml")

    viewstate = soup.find(id = "__VIEWSTATE")['value']
    eventvalidation = soup.find(id = "__EVENTVALIDATION")['value']
    viewstategenerator = soup.find(id = "__VIEWSTATEGENERATOR")['value']
    print(viewstate)


# In[17]:


#Keeping count of carrier-airport combinations with no data
exists_counter = 0
does_not_exist_counter = 0

#Sending requests and HTML response into file
for carrier in carrier_list:
    for airport in airport_list:
        
        body = {
            "__EVENTTARGET" : "",
            "__EVENTARGUMENT" : "",
            "__VIEWSTATE" : viewstate,
            "__VIEWSTATEGENERATOR" : viewstategenerator,
            "CarrierList" : carrier,
            "AirportList" : airport,
            "Submit" : "submit",
            "__EVENTVALIDATION" : eventvalidation
        }

        resp = s.post(URL, data = body)
        f = open("./flight_data/"+carrier+"_"+airport+".html", "w")
        (f.write(resp.text))
        f.close()
        output_file_name = "./flight_data/"+carrier+"_"+airport+".html"
        html_response_file = Path(output_file_name)
        
        
        if html_response_file.is_file():
            exists_counter +=1
            pass
        else:
            does_not_exist_counter +=1
            while True:
                try:
                    resp = s.post(URL, data = body)
                except Exception as e:
                    print(e)
                    print('renewing session', '\n') #If session times out. Renewing it
                    new_session()
                    continue
                break
                
            f = open(output_file_name, "w")
            (f.write(resp.text))
            f.close()

  


# In[13]:


print(exists_counter)
print(does_not_exist_counter)

