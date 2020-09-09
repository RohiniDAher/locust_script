from locust import HttpUser, task, between
#from locust.contrib.fasthttp import FastHttpUser
from bs4 import BeautifulSoup
import time
import json


class DemoUser(HttpUser):
    wait_time = between(1, 2)
    csrfmiddlewaretoken = ""
    host = "https://remotedesk.us"
    email = ""
    password = ""
    login_cred = [("rohini+1212191@verificient.com", "Verificient12!"),("rohini+090420201@verificient.com", "verificient12!"),("rohini+090420201@verificient.com","verificient12!") ]

    @task(1)
    def login_agent(self):
        if len(self.login_cred) > 0:
            self.email, self.password = self.login_cred.pop()
            self.client.cookies.clear()
            
            #--------------login---------------
            response = self.client.get("/")
            soup = BeautifulSoup(response.text, "html.parser")
            self.csrfmiddlewaretoken = soup.find('input', {'name': "csrfmiddlewaretoken"})
            self.csrfmiddlewaretoken = self.csrfmiddlewaretoken['value']
            print("csrf token --------", self.csrfmiddlewaretoken)
            print("home page title ---------------", soup.title)
            payload = {'email': self.email, 'password': self.password, "csrfmiddlewaretoken": self.csrfmiddlewaretoken}
            headers = {'content-type': 'application/x-www-form-urlencoded',
                   'connection': 'keep-alive',
                   'Referer': self.host,
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'
                   }
            resp = self.client.post("/account/login/", data=payload, headers=headers, name="best practice page")
            supr = BeautifulSoup(resp.text, "html.parser")
            heading2 = supr.find('h2', {'class': 'section-heading col-blue'})
            print("heading---------",heading2)
            print("best practice title-------------",supr.title)
            #time.sleep(2)
            
            
            #---------------------download page ---------------------
            download_page = supr.find('a',{'id':'next_step_button'})
            dw_link = download_page['href']+'#/download-connect/'
            print("download page link-----------",dw_link)
            
            
            dw_page = self.client.get(dw_link, name="download page")
            time.sleep(5)  
            print("download page status code---------------",dw_page.status_code)
            s1 = BeautifulSoup(dw_page.text, "html.parser")
            print("download page title-------------", s1.title)
            details = s1.find('h4',{'class', 'ng-binding'})
            print('script details --------------------',details)
            '''
            #script_data = s1.find_all('script')[21].text
            #print("script data------", script_data)
            #api = "/screencasts/session/self/config/?testsession_id="+session_uuid+"&fullTestConfig=true&appVersion=2.0.77.0211"
            #test_config = self.client.get(api)
            #print("test_config---------",test_config)
            
            begin_session_api = "/screencasts/session/self/set/preverification/done/"
            begin_sess = self.client.post(begin_session_api, data={"testsession_id":session_uuid})
            print("begin_session_api---------",begin_sess)
            
            time.sleep(5)
            
            resp = self.client.get("/account/logout", name='logging out')
            soup = BeautifulSoup(resp.text, "html.parser")
            logout_message = soup.find('p',{'class':'text-center'})
            print(logout_message)
            resp2 = self.client.post("/account/logout/", data={"csrfmiddlewaretoken": self.csrfmiddlewaretoken}, name="logout")
            print(resp2.history)
            soup = BeautifulSoup(resp2.text, "html.parser")
            logout_message2 = soup.find('h1',{'class':'brand-heading'})
            print(logout_message2)
            '''

#command --> locust -f demo_1.py --host="https://remotedesk.us" --headless -u 1 -r 5 -t 10 --stop-timeout 5 --csv=report_csv