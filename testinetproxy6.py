'''check websites via proxy and summarize the status quo'''
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
#import logging


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
#import ssl
#import certifi

def check_api():
    cert_path = 'DBSBank-Root-CA.pem'
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Encoding": "*",
    "Connection": "keep-alive"
    }
    now = datetime.datetime.now()
    timestamp = str(now.strftime("%Y%m%d_%H:%M:%S"))
    print(timestamp)

    for url in urls:
        try:
            s = requests.Session()
            s.mount('https://', DESAdapter())
            page = s.get(url, headers=headers, proxies=proxies, verify='DBSBank-Root-CA.crt')
            print(url+f" :response-{page.status_code}")
            crawl_log[url][timestamp]="resp code-"+str(page.status_code)
            if page.status_code in crawl_counter[url].keys():                
                crawl_counter[url][page.status_code] += 1
            else:
                crawl_counter[url][page.status_code]=1  
        except Exception as e:
            if "10054" in str(e):
                page = session.get(url, timeout=1)
                print(url+f" :response-{page.status_code}")
                crawl_log[url][timestamp]="resp code-"+str(page.status_code)
                if page.status_code in crawl_counter[url].keys():
                    crawl_counter[url][page.status_code] += 1
                else:
                    crawl_counter[url][page.status_code]=1                 
            else:
                print(url+f" :response-NOT OK")
                crawl_log[url][timestamp]="resp code-NOT OK"
                if "NOT OK" in crawl_counter[url].keys():
                    crawl_counter[url]["NOT OK"] += 1
                else:
                    crawl_counter[url]["NOT OK"]=1 
#    for keys, value in crawl_counter.items():
#        print(keys, value)
    with open("/home/lingduominl/pyfile/url_status_q.txt", "w") as f:
        for k, v in crawl_counter.items():
            f.write('%s:%s\n' % (k, v))
    pass
    with open("/home/lingduominl/pyfile/url_status_log.txt", "w") as f2:
        for k, v in crawl_log.items():
            f2.write('%s:%s\n' % (k, v))
    pass

def schedule_api():
    while datetime.datetime.now().minute % 1 != 0:
        sleep(1)
    check_api()
    while True:
        sleep(60)
        check_api()


urls = ['https://fed.rbi.org.in/FEDINTERLINK/login/Login.do',
'https://eportal.incometax.gov.in/',
'https://cyberpolice.nic.in/AdLogin.aspx',
'https://www.fpi.nsdl.co.in/',
'https://services.gst.gov.in/services/searchtp',
'https://www.mca.gov.in/content/mca/global/en/mca/master-data/MDS.html',
'https://cims.rbi.org.in/LOGIN/#/login',
'https://slbckerala.com/']


crawl_counter = {}
crawl_log = {}
for url in urls:
    crawl_counter[url]={}
for url in urls:
    crawl_log[url]={}
    
http_proxy = "http://10.91.79.179:8080"
https_proxy = "https://10.91.79.179:8080"

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

thread = Thread(target=schedule_api)
thread.start()
