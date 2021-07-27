from bs4 import BeautifulSoup
import requests
import re

uris = [
    "https://uk.pcpartpicker.com/product/vFhmP6/asus-rog-strix-b550-f-gaming-wi-fi-atx-am4-motherboard-rog-strix-b550-f-gaming-wi-fi",
    "https://uk.pcpartpicker.com/product/9nm323/amd-ryzen-53600-36-thz-6-core-processor-100-100000031box"
    ]


def getprice(uri):
    r = requests.get(uri, headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"})
    html = r.text
    soup = BeautifulSoup(html, "html.parser")
    output = {}
    tds = soup.find_all("tbody")[1].find("tr").find_all("td")
    for td in tds:
        price = td.find("a")
        if price != None:
            shit = str(price.string)
            regex = "£\\d{1,3}\\.\\d{2}"
            if re.match(regex, shit):
                output["price"] = shit
                output["link"] = "https://uk.partpicker.com" + price["href"]
    output["name"] = soup.title.string.split('-')[0]
    listOfPrices.append(output)

listOfPrices = []
for uri in uris:
    getprice(uri)
print(listOfPrices)

