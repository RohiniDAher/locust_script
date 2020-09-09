import requests
import json
from bs4 import BeautifulSoup

url = "https://remotedesk.us/downloads/session/0032bf86100c4fc492a32840344680ae/#/download-connect"

r = requests.get(url)

soup = BeautifulSoup(r.text, "html.parser")
print(soup.title)