'''check website via proxy and log the result per 30-40s'''
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager

class DESAdapter(HTTPAdapter):
    """
    A TransportAdapter that re-enables 3DES support in Requests.
    """
    def create_ssl_context(self):
        ctx = ssl.create_default_context()
        # disallow TLS_V1.3
        ctx.options |= ssl.OP_NO_TLSv1_3
        return ctx  
    def init_poolmanager(self, *args, **kwargs):
        #print(' ----------- DESAdapter.init_poolmanager -------------- ')
        kwargs['ssl_context'] = self.create_ssl_context()
        return super(DESAdapter, self).init_poolmanager(*args, **kwargs)
    def proxy_manager_for(self, *args, **kwargs):
        #print(' ----------- DESAdapter.proxy_manager_for -------------- ')
        kwargs['ssl_context'] = self.create_ssl_context()
        return super(DESAdapter, self).proxy_manager_for(*args, **kwargs)
        

from threading import Thread
from time import sleep
import datetime
import requests
import json
import ssl
import os.path
import os

urls = ['https://fed.rbi.org.in/FEDINTERLINK/login/Login.do',
'https://eportal.incometax.gov.in/',
'https://cyberpolice.nic.in/AdLogin.aspx',
'https://www.fpi.nsdl.co.in/',
'https://services.gst.gov.in/services/searchtp',
'https://www.mca.gov.in/content/mca/global/en/mca/master-data/MDS.html',
'https://cims.rbi.org.in/LOGIN/#/login',
'https://slbckerala.com/']


crawl_counter = {}
for url in urls:
    crawl_counter[url]={}
    
http_proxy = "http://10.132.2.231:8080"
https_proxy = "https://10.132.2.231:8080"

proxies = {
              "http": http_proxy,
              "https": https_proxy
            }    
      
session = requests.Session()
session.headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Encoding": "*",
    "Connection": "keep-alive",
}

cert_path = 'rootca.crt'
headers = {
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
"Accept-Encoding": "*",
"Connection": "keep-alive"
}

def check_api():
    now = datetime.datetime.now()
    timestamp = str(now.strftime("%Y%m%d_%H:%M:%S"))
    
    with open("/pythontest/urlcheck/log/query_status_log2.txt", "a") as f:
        f.write("crawl result at " + timestamp)
        f.write("\n") 
        for url in urls:
            try:
                s = requests.Session()
                s.mount('https://', DESAdapter())
                page = s.get(url, headers=headers, proxies=proxies, verify='rootca.crt')
                print(url+f" :resp - {page.status_code}")           
                f.write(url+" - resp "+str(page.status_code))
                f.write("\n")            
            except Exception as e:
                if "10054" in str(e):
                    page = session.get(url, timeout=1)
                    print(url+f" :resp - {page.status_code}")
                    crawl_log[url][timestamp]="resp code-"+str(page.status_code)
                    f.write(url+" - resp "+str(page.status_code))
                    f.write("\n")            
                else:
                    print(url+f" :resp NOT OK")
                    f.write(url+" - resp NOT OK")
                    f.write("\n") 


def schedule_api():
    while datetime.datetime.now().minute % 1 != 0:
        sleep(1)
    check_api()
    while True:
        sleep(30)
        check_api()
        
thread = Thread(target=schedule_api)
thread.start()
    