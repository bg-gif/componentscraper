from bs4 import BeautifulSoup
import requests
import re
import json

v = open('variables.json')
# print(json.load(v))
historic = json.load(v)
# print(historic["historicList"])
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


def getprice(uri):
    r = requests.get(uri, headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"})
    html = r.text
    soup = BeautifulSoup(html, "html.parser")
    partdetail = {}
    x = print(soup.find_all("tbody"))
    print(type(x)
    if type(x) is not None or len(x) != 0:
        tds = x[0].find("tr").find_all("td")
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
# with open("variables.json", "w") as stored:
#     update = {"historicPrice": totalPrice, "noOfParts": noOfParts, "historicList": listOfPrices}
#     json.dump(update, stored)

