import random
import json
import sys
from pathlib import Path
from threading import Thread
from time import sleep
from selenium import webdriver

# read config file
root_dir = Path(sys.modules["__main__"].__file__).resolve().parent
PROXY_LINK, LINK, WEBDRIVER_LOCATION = None, None, None
with open(root_dir / "config.json") as f:
    data = json.load(f)
    PROXY_LINK = data["proxylink"]
    LINK = data["link"]
    WEBDRIVER_LOCATION = root_dir / data["driverlocation"]


# get list of proxies
def getProxyList(link):
    option = webdriver.ChromeOptions()
    option.add_argument("-incognito")
    option.add_argument("--headless")
    browser = webdriver.Chrome(WEBDRIVER_LOCATION, chrome_options=option)
    browser.get(link)

    proxy_elements = browser.find_elements_by_xpath("/html/body/div/div[2]/table/tbody/tr[@class='Odd']/td[1]/a")
    proxy_elements2 = browser.find_elements_by_xpath("/html/body/div/div[2]/table/tbody/tr[@class='Even']/td[1]/a")
    elements = proxy_elements + proxy_elements2
    proxy_ips = [x.text for x in elements]
    return proxy_ips

# port 80 proxies
proxyList = getProxyList(PROXY_LINK)

# load lists into memory
nameList = None
lastnameList = None
textList = None
with open(root_dir / "namelist.txt", encoding="utf-8") as f:
    nameList = f.readlines()
with open(root_dir / "lastnamelist.txt", encoding="utf-8") as f:
    lastnameList = f.readlines()
with open(root_dir / "textlist.txt", encoding="utf-8") as f:
    textList = f.readlines()

class Bot(Thread):
    def __init__(self, proxy, port=80):
        super(Bot, self).__init__()
        self.proxy = proxy
        self.port = port

    def run(self):
        option = webdriver.ChromeOptions()
        option.add_argument("-incognito")
        #option.add_argument("--headless")
        option.add_argument(f"--proxy-server={self.proxy}:{self.port}")
        print(f"{self.proxy}:{self.port}")
        browser = webdriver.Chrome(WEBDRIVER_LOCATION, chrome_options=option)
        while True:
            try:
                browser.get(LINK)
                sleep(1)
                name_box = browser.find_element_by_id("et_pb_contact_name_0")
                email_box = browser.find_element_by_id("et_pb_contact_email_0")
                text_box = browser.find_element_by_id("et_pb_contact_message_0")
                captcha_box = browser.find_element_by_xpath("//*[@id='et_pb_contact_form_0']/div[2]/form/div/div/p/input")

                # Solve captcha
                captcha_answer = int(captcha_box.get_attribute("data-first_digit")) + int(captcha_box.get_attribute("data-second_digit"))
                captcha_box.clear()
                captcha_box.send_keys(str(captcha_answer))

                # Get random details
                name = nameList[random.randint(0, len(nameList))].strip()
                lastname = lastnameList[random.randint(0, len(lastnameList))].strip()
                email = name + "." + lastname + str(random.randint(0, 99)) + "@gmail.com"
                text = textList[random.randint(0, len(textList))]
                text = text.replace("{eesnimi}", name)
                text = text.replace("{perekonnanimi}", lastname)
                # Fill in details
                name_box.clear()
                name_box.send_keys(name)
                email_box.clear()
                email_box.send_keys(email)
                text_box.clear()
                text_box.send_keys(text)
                text_box.submit()
            except:
                print(f"Bot with IP {self.proxy} failed.")
                runningBots.remove(self.proxy)
                browser.quit()
                break
runningBots = set()
for ip in proxyList:
    while len(runningBots) > 5:
        continue
    bot = Bot(ip)
    bot.start()
    runningBots.add(ip)

while len(runningBots) != 0:
    sleep(5)
    print(str(len(runningBots)) + " bots still running.")
    continue
print("All bots shut down.")