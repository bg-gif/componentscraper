from bs4 import BeautifulSoup
import requests
import re
import json
import numpy as np
import time

v = open('variables.json')
historic = json.load(v)
uris = [
    "https://uk.pcpartpicker.com/product/vFhmP6/asus-rog-strix-b550-f-gaming-wi-fi-atx-am4-motherboard-rog-strix-b550-f-gaming-wi-fi",
    "https://uk.pcpartpicker.com/product/9nm323/amd-ryzen-53600-36-thz-6-core-processor-100-100000031box",
    "https://uk.pcpartpicker.com/product/29drxr/cooler-master-masterbox-nr200p-mini-itx-desktop-case-mcb-nr200p-kgnn-s00",
    "https://uk.pcpartpicker.com/product/BtsmP6/corsair-sf-600w-80-platinum-certified-fully-modular-sfx-power-supply-cp-9020182-na",
    "https://uk.pcpartpicker.com/product/p6RFf7/corsair-memory-cmk16gx4m2b3200c16",
    "https://uk.pcpartpicker.com/product/PVfFf7/nzxt-kraken-x53-7311-cfm-liquid-cpu-cooler-rl-krx53-01",
    "https://uk.pcpartpicker.com/product/Zxw7YJ/samsung-970-evo-plus-1-tb-m2-2280-nvme-solid-state-drive-mz-v7s1t0bam",
    "https://uk.pcpartpicker.com/product/ThhmP6/zotac-geforce-rtx-3070-8-gb-gaming-twin-edge-oc-video-card-zt-a30700h-10p"
    ]

def get_random_ua():
    random_ua = ''
    ua_file = 'ua_file.txt'
    try:
        with open(ua_file) as f:
            lines = f.readlines()
            # print(lines)
        if len(lines) > 0:
            index = np.random.randint(len(lines)-1)
            random_ua = lines[index]
    except Exception as ex:
        print('Exception in random_ua')
        print(str(ex))
    finally:
        return random_ua

def getprice(uri):
    random_ua = str(get_random_ua().strip())
    r = requests.get(uri, headers={
    "User-Agent": random_ua, "referer": "google.co.uk"})
    html = r.text
    responseCode = r.status_code
    print("Request: " + uri + "  Response Code: " + str(responseCode))
    soup = BeautifulSoup(html, "html.parser")
    partdetail = {}
    tds = soup.find_all("tbody")[1].find("tr").find_all("td")
    for td in tds:
        price = td.find("a")
        if price is not None:
            cost = str(price.string)
            regex = "£\\d{1,3}\\.\\d{2}"
            if re.match(regex, cost):
                partdetail["price"] = cost.split("£")[1]
                partdetail["link"] = "https://uk.partpicker.com" + price["href"]
    partdetail["name"] = soup.head.find("meta", property="og:title")["content"]
    print(partdetail)
    listOfPrices.append(partdetail)
    delays = [7, 4, 6, 2, 10, 19]
    delay = np.random.choice(delays)
    time.sleep(delay)

listOfPrices = []
for uri in uris:
    getprice(uri)
# print(listOfPrices)
output = ""
total = 0
for component in listOfPrices:
    output = output + component["name"] + ": " + component["price"] + "/n "
    cost = component["price"]
    total = total + float(cost)
print(output)
noOfParts = str(len(listOfPrices))
totalPrice = str(round(total, 2))
print("Total Number of Parts: " + noOfParts)
print("Total Price: £" + totalPrice)
for historicObj in historic["historicList"]:
    for currentObj in listOfPrices:
        # print(historicObj, currentObj)
        if historicObj == currentObj:
            if historicObj["price"] == currentObj["price"]:
                print(historicObj["name"] + ": Same Price")
            if historicObj["price"] > currentObj["price"]:
                print("New Low Price for " + historicObj["name"] + ".  Current Price: " + currentObj["price"] + ", Historic Price: " + historicObj["price"])

# with open("variables.json", "w") as stored:
#     update = {"historicPrice": totalPrice, "noOfParts": noOfParts, "historicList": listOfPrices}
#     json.dump(update, stored)

