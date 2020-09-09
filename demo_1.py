from locust import HttpUser, task, between
from bs4 import BeautifulSoup
import time
import json


class DemoUser(HttpUser):
    wait_time = between(1, 2)
    csrfmiddlewaretoken = ""
    host = "https://remotedesk.us"
    email = ""
    password = ""
    login_cred = [("rohini+1212191@verificient.com", "Verificient12!") ]

    def on_start(self):
        if len(self.login_cred) > 0:
            self.email, self.password = self.login_cred.pop()
            self.client.cookies.clear()
            response = self.client.get("/")
            soup = BeautifulSoup(response.text, "html.parser")
            self.csrfmiddlewaretoken = soup.find('input', {'name': "csrfmiddlewaretoken"})
            self.csrfmiddlewaretoken = self.csrfmiddlewaretoken['value']
            print("csrf token --------", self.csrfmiddlewaretoken)
            #print("login         *****************************************************************")
            
    def on_stop(self):
        resp = self.client.get("/account/logout", name='logging out')
        soup = BeautifulSoup(resp.text, "html.parser")
        logout_message = soup.find('p',{'class':'text-center'})
        print(logout_message)
        resp2 = self.client.post("/account/logout/", data={"csrfmiddlewaretoken": self.csrfmiddlewaretoken}, name="logout")
        print(resp2.history)
        soup = BeautifulSoup(resp2.text, "html.parser")
        logout_message2 = soup.find('h1',{'class':'brand-heading'})
        print(logout_message2)

    @task
    def login_page(self):
        payload = {'email': self.email, 'password': self.password, "csrfmiddlewaretoken": self.csrfmiddlewaretoken}
        headers = {'content-type': 'application/x-www-form-urlencoded',
                   'connection': 'keep-alive',
                   'Referer': self.host,
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'
                   }
        resp = self.client.post("/account/login/", data=payload, headers=headers, name="best practice page")
        supr = BeautifulSoup(resp.text, "html.parser")
        print("login history------",resp.history)
        heading2 = supr.find('h2', {'class': 'section-heading col-blue'})
        print("heading---------",heading2)
        time.sleep(2)
        download_page = supr.find('a',{'id':'next_step_button'})
        dw_link = download_page['href']
        print("download page link-----------",dw_link)
        self.client.get(dw_link, name="download page")
        time.sleep(2)
        raise StopUser()
        
        

#command --> locust -f demo_1.py --host="https://remotedesk.us" --headless -u 1 -r 5 -t 10 --stop-timeout 5 --csv=report_csv