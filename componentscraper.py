from bs4 import BeautifulSoup
import requests
import re
import json
import numpy as np
import time
import sendNotification
import os.path


class Scraper:

    def __init__(self, uris, variables):
        self.partSources = self.getURIs(uris, variables)["partsources"]
        self.historic = self.getURIs(uris, variables)["historic"]


    def getURIs(self, uris, variables):
        variablesExists = os.path.exists('variables.json')
        if variablesExists:
            v = open(variables)
            historic = json.load(v)
        else:
            historic = {}
        # print(historic)
        with open(uris) as f:
            partSources = f.readlines()
        return {"partsources": partSources, "historic": historic }


    def getpartlist(self, partSources):
        listOfParts = []
        for part in partSources:
            if part.split("-")[0].strip() != "\n":
                listOfParts.append(part.split("-")[0].strip())
        # print(listOfParts)
        return listOfParts

    def get_random_ua(self):
        random_ua = ''
        ua_file = 'ua_file.txt'
        try:
            with open(ua_file) as f:
                lines = f.readlines()
                # print(lines)
            if len(lines) > 0:
                index = np.random.randint(len(lines) - 1)
                random_ua = lines[index]
        except Exception as ex:
            print('Exception in random_ua')
            print(str(ex))
        finally:
            return str(random_ua.strip())


    def getprice(self, part, listarg, historic):
        random_ua = self.get_random_ua()
        partName = part.split("-")[0].strip()
        partUri = part.split("-")[1].strip()
        if partUri != "\n":
            r = requests.get(partUri, headers={"User-Agent": random_ua, "referer": "google.co.uk"})
        html = r.text
        responseCode = r.status_code
        print("Request: " + partUri + "\nResponse Code: " + str(responseCode), end="\n")
        soup = BeautifulSoup(html, "html.parser")
        partdetail = {}
        if not soup.find_all("tbody"):
            print("No Price returned. Most likely due to bot detection", end="\n")
            return
        tds = soup.find_all("tbody")[1].find("tr").find_all("td")
        for td in tds:
            price = td.find("a")
            if price is not None:
                cost = str(price.string)
                regex = "£\\d{1,3}\\.\\d{2}"
                if re.match(regex, cost):
                    price_float = cost.split("£")[1]
                    partdetail["price"] = price_float
                    partdetail["link"] = "https://uk.partpicker.com" + price["href"]
                    if historic["historicList"][partName]:
                        historicPart = historic["historicList"][partName]
                        if float(historicPart["historicLow"]) < float(price_float):
                            partdetail["historicLow"] = historicPart["historicLow"]
                        else:
                            partdetail["historicLow"] = price_float
        partdetail["name"] = soup.head.find("meta", property="og:title")["content"]
        # print(partdetail)
        listarg[partName] = partdetail
        delays = range(20)
        delay = np.random.choice(delays)
        time.sleep(delay)
        return

    def getListOfPrices(self, partSources, historic):
        # Create list of all component current details
        listOfPrices = {}
        for part in partSources:
            self.getprice(part, listOfPrices, historic)
        if historic == {}:
            self['historic'] = listOfPrices
        # print(listOfPrices)
        print("\n")
        return listOfPrices

    def priceCheck(self, listOfParts, historic, listOfPrices):
        # Calculate total price of build and list components and prices
        output = "\n\nPart List:\n\n"
        total = 0
        for partType in listOfParts:
            partName = listOfPrices[partType]["name"]
            partPrice = listOfPrices[partType]["price"]
            # print(partName + ": £" + partPrice)
            historicLow = historic["historicList"][partType]["historicLow"]
            output = output + partName + ": £" + partPrice
            if float(partPrice) > float(historicLow):
                diff = str(round(float(partPrice) - float(historicLow)))
                print(f"{partType} is £{diff} more expensive than the historic low.")
            if float(partPrice) < float(historicLow):
                diff = str(round(float(historicLow) - float(partPrice),2))
                print(f"{partType} is £{diff} cheaper than the historic low. New Low Price added to historic record")
                output += ". New Historic Low!"
                sendNotification.send_notification_via_pushbullet(f"New {partType} Historic Low Price!", f"---{partType}---\n{listOfPrices[partType]['name']} has reached a historic low price of £{listOfPrices[partType]['price']}")
                historic["historicList"][partType]["historicLow"] = partPrice
            else:
                output += "\n"
            total = total + float(partPrice)

        noOfParts = str(len(listOfPrices))
        totalPrice = str(round(total, 2))

        print(output)
        print("Total Number of Parts: " + noOfParts)
        print("Total Price: £" + totalPrice)

        for partType in listOfParts:
            changed = False
            historicList = historic["historicList"]
            if historicList[partType]["name"] != listOfPrices[partType]["name"]:
                print(f"\n{partType} has changed.\n")
                print(f"{historicList[partType]['name']} was changed to {listOfPrices[partType]['name']}\n")
                diff = round(float(historicList[partType]["price"]) - float(listOfPrices[partType]["price"]),2)
                if diff > 0:
                    print(f"{listOfPrices[partType]['name']} is £{str(diff)} cheaper than {historicList[partType]['name']}\n")
                if diff < 0:
                    print(f"{listOfPrices[partType]['name']} is £{str(abs(diff))} more expensive than {historicList[partType]['name']}\n")
                historicList.pop(partType)
                historicList[partType] = listOfPrices[partType]
                changed = True


        if totalPrice != historic["historicPrice"]:
            print(f"Price Change! New Total Price is £{totalPrice}\nHistoric Low Price is £{historic['historicLow']}")
            totalDiff = round(float(totalPrice) - float(historic["historicPrice"]),2)
            # print(totalDiff)
            if totalDiff < 0:
                print(f"The new total is £{str(abs(totalDiff))} cheaper than previous.\n")
            if totalDiff > 0:
                print(f"The new total is £{str(totalDiff)} more expensive than previous.\n")
            historic["historicPrice"] = str(totalPrice)
        if float(totalPrice) < float(historic["historicLow"]):
            print("New Historic Low Total Price!")
            sendNotification.send_notification_via_pushbullet("New Historic Low Price!", f"The current cost of the build is £{totalPrice}\n{output}")
            historic["historicLow"] = totalPrice
        return {"output": output, "noOfParts": noOfParts, "totalPrice": totalPrice, "historic": historic}


    def writetorecord(self, historic):
        with open("variables.json", "w") as stored:
            json.dump(historic, stored)
        return
