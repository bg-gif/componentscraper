from bs4 import BeautifulSoup
import requests
import re
import json
import numpy as np
import time
import sendNotification

v = open('variables.json')
historic = json.load(v)
# print(historic)
with open("uris.txt") as f:
    partSources = f.readlines()

listOfParts = []
for part in partSources:
    if part.split("-")[0].strip() != "\n":
        listOfParts.append(part.split("-")[0].strip())
print(listOfParts)

def get_random_ua():
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


def getprice(part, listarg):
    random_ua = get_random_ua()
    partName = part.split("-")[0].strip()
    partUri = part.split("-")[1].strip()
    if partUri != "\n":
        r = requests.get(partUri, headers={"User-Agent": random_ua, "referer": "google.co.uk"})
    html = r.text
    responseCode = r.status_code
    print("Request: " + partUri + "\nResponse Code: " + str(responseCode))
    soup = BeautifulSoup(html, "html.parser")
    partdetail = {}
    if not soup.find_all("tbody"):
        print("No Price returned. Most likely due to bot detection")
        return
    tds = soup.find_all("tbody")[1].find("tr").find_all("td")
    for td in tds:
        price = td.find("a")
        if price is not None:
            cost = str(price.string)
            regex = "£\\d{1,3}\\.\\d{2}"
            if re.match(regex, cost):
                partdetail["price"] = cost.split("£")[1]
                partdetail["historicLow"] = cost.split("£")[1]
                partdetail["link"] = "https://uk.partpicker.com" + price["href"]
    partdetail["name"] = soup.head.find("meta", property="og:title")["content"]
    print(partdetail)
    listarg[partName] = partdetail
    delays = range(20)
    delay = np.random.choice(delays)
    time.sleep(delay)

# Create list of all component current details
listOfPrices = {}
for part in partSources:
    getprice(part, listOfPrices)
print(listOfPrices)

# Calculate total price of build and list components and prices
output = "\n\nPart List:\n\n"
total = 0
for partType in listOfParts:
    partName = listOfPrices[partType]["name"]
    partPrice = listOfPrices[partType]["price"]
    # print(partName + ": £" + partPrice)
    historicLow = historic["historicList"][partType]["historicLow"]
    output = output + partName + ": £" + partPrice
    if float(partPrice) < float(historicLow):
        output += ". New Historic Low!\n"
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


changedParts = False
for partType in listOfParts:
    historicList = historic["historicList"]
    if historicList[partType]["name"] != listOfPrices[partType]["name"]:
        changedParts = True
        print(f"\n{partType} has changed.\n")
        print(f"{historicList[partType]['name']} was changed to {listOfPrices[partType]['name']}\n")
        diff = round(float(historicList[partType]["price"]) - float(listOfPrices[partType]["price"]),2)
        if diff > 0:
            print(f"{listOfPrices[partType]['name']} is £{str(diff)} cheaper than {historicList[partType]['name']}\n")
        if diff < 0:
            print(f"{listOfPrices[partType]['name']} is £{str(abs(diff))} more expensive than {historicList[partType]['name']}\n")
        historicList.pop(partType)
        historicList[partType] = listOfPrices[partType]

if totalPrice != historic["historicPrice"]:
    print("New Total Price updated to include Changes\n")
    if changedParts:
        print("Price change due to changed parts")
    print(f"New Total Price is £{totalPrice}\n")
    totalDiff = round(float(totalPrice) - float(historic["historicPrice"]),2)
    # print(totalDiff)
    if totalDiff < 0:
        print(f"The new total is £{str(abs(totalDiff))} cheaper than {historic['historicPrice']}\n")
    if totalDiff > 0:
        print(f"The new total is £{str(totalDiff)} more expensive than previous.\n")
    historic["historicPrice"] = str(totalPrice)
if float(totalPrice) < float(historic["historicLow"]):
    print("New Historic Low Total Price!")
    sendNotification.send_notification_via_pushbullet("New Historic Low Price!", f"The current cost of the build is £{totalPrice}")
    historic["historicLow"] = totalPrice


with open("variables.json", "w") as stored:
    json.dump(historic, stored)
