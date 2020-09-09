from locust import HttpUser, TaskSet, task, between
from locust import events
from bs4 import BeautifulSoup
import time
from constants import Constants as c
import os
import re
from datetime import timedelta

@events.init_command_line_parser.add_listener
def _(parser):
    parser.add_argument("--server", type=str, env_var="LOCUST_SERVER", default="preprod", help="prod, preprod, dev")
    
@events.init.add_listener
def _(environment, **kw):
    print("Custom argument supplied: %s" % environment.parsed_options.server)

class UserTasks(TaskSet):
    csrfmiddlewaretoken = ""
    #if server == "preprod":
    host = "https://remotedesk.us"
    email = ""
    password = ""
    login_cred=c.login_cred
    best_practice_page_title = re.compile(c.BEST_PRACTISE_PAGE_TITLE)

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
            #print("csrf token --------", self.csrfmiddlewaretoken)
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
            best_practice_url = resp.url
            print("best practice url---------------------", best_practice_url)
            #assert self.best_practice_page_title.search(str(supr.title)) is not None, "expected title not found"
            assert resp.status_code is 200, "Unexpected response code"
            assert resp.elapsed < timedelta(seconds = 3), "Request took more than 3 sec"
            
            #---------------------download page --------------------
            
            download_page = supr.find('a',{'id':'next_step_button'})
            dw_link = download_page['href']+ '#/download-connect/'
            #print("download page link-----------",dw_link)
            dw_header = {
                   'connection': 'keep-alive',
                   'Referer': best_practice_url,
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'
                   }
            
            dw_page = self.client.get(dw_link, name="download page", headers=dw_header)
            time.sleep(5)  
            #print("download page status code---------------",dw_page.status_code)
            s1 = BeautifulSoup(dw_page.text, "html.parser")
            print("download page title-------------", s1.title)
                        
            script_data = str(s1.find_all('script')[20].text)
            #print("-------------------------------------------")
            #print(script_data)
            session_id = script_data.rfind('sessionId')
            id = script_data[session_id+12: session_id+17]
            access_token = script_data.rfind('accessToken')
            token = script_data[access_token+14: access_token+44]
            print("script data------{}------------{}".format(id, token))
            
            #id = "73269"
            #token = "YyBDtiuEuiM7xdPjwJSWS6P64HovNX"
            api = "/screencasts/session/self/config/?testsession_id="+id+"&fullTestConfig=true&appVersion=2.0.77.0211"
            config_header = {
                    'Authorization': "Bearer "+token
            }
            test_config = self.client.get(api, headers=config_header, name="test_config")
            config = BeautifulSoup(test_config.text, "html.parser")
            print("test_config---------", test_config.status_code)
            assert test_config.status_code is 200, "Unexpected response code"
            
            begin_session_api = "/screencasts/session/self/set/preverification/done/"
            begin_sess = self.client.post(begin_session_api, data={"testsession_id":id}, headers = config_header, name ="begin session")
            #begin_session = BeautifulSoup(begin_sess.text, "html.parser")
            print("begin session status---------------------", begin_sess.status_code)
            #print("begin_session_api---------",begin_session)
            assert begin_sess.status_code is 200, "Unexpected response code"
            
            open_session_api = "/screencasts/session/self/startsession/"
            open_sess = self.client.post(open_session_api, data={"testsession_id":id, "app_version":"2.76.0.0211"}, headers=config_header, name="open session")
            print("open session ----------------", open_sess.status_code)
            assert open_sess.status_code is 200, "Unexpected response code"
            
            mac_address_api = "/screencasts/session/"+id+"/store/mac/"
            mac_add = self.client.post(mac_address_api, data={"mac_hash":"127.0.0.1"}, headers=config_header, name="MAC address")
            print("MAC address ----------------", mac_add.status_code)
            assert mac_add.status_code is 200, "Unexpected response code"
            
            close_session_api = "/screencasts/session/self/closesession/?duration=395"
            close_sess = self.client.post(close_session_api, data={"testsession_id":id, "app_version":"2.76.0.0211"}, headers=config_header, name="close session")
            print("close session --------------", close_sess.status_code)
            assert close_sess.status_code is 200, "Unexpected response code"
            
            '''
            chunk_upload_done_api = "/screencasts/session/self/chunkupload/done/"
            chunk_upload = self.client.post(chunk_upload_done_api, data={"testsession_id":id, "app_version":"2.76.0.0211"}, headers=config_header, name="chunk upload done")
            print("chunk upload done --------------", chunk_upload.status_code)
            assert chunk_upload.status_code is 200, "Unexpected response code"
            
            
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
    
    
class WebSiteUser(HttpUser):
    wait_time = between(1, 5)
    tasks = [UserTasks]


#command --> locust -f .\demo_2.py --host="https://remotedesk.us" --headless -u 1 -r 1 -t 15 --print-stats --only-summary 