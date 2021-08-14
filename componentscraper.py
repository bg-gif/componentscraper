import logging
from typing import Optional
from bs4 import BeautifulSoup
import requests
import re
import json
import numpy as np
import time
import send_notification
import os.path
import os
from decouple import config


def price_check(list_of_parts, historic, list_of_prices):
    # Calculate total price of build and list components and prices
    output = "\n\nPart List:\n\n"
    total = 0
    for part_type in list_of_parts:
        part_name = list_of_prices[part_type]["name"]
        part_price = list_of_prices[partType]["price"]
        # print(partName + ": £" + partPrice)
        historic_low = historic["historic_list"][partType]["historic_low"]
        output = output + part_name + ": £" + part_price
        if float(part_price) > float(historic_low):
            diff = str(round(float(part_price) - float(historic_low)))
            print(f"{part_type} is £{diff} more expensive than the historic low.")
        if float(part_price) < float(historic_low):
            diff = str(round(float(historic_low) - float(part_price), 2))
            print(f"{part_type} is £{diff} cheaper than the historic low. New Low Price added to historic record")
            output += ". New Historic Low!\n"
            send_notification.send_notification_via_pushbullet(f"New {partType} Historic Low Price!",
                                                              f"---{partType}---\n{list_of_prices[part_type]['name']} has reached a historic low price of £{list_of_prices[part_type]['price']}")
            historic["historic_list"][part_type]["historic_low"] = part_price
        else:
            output += "\n"
        total = total + float(part_price)

    no_of_parts = str(len(list_of_prices))
    total_price = str(round(total, 2))

    print(output)
    print("Total Number of Parts: " + no_of_parts)
    print("Total Price: £" + total_price)
    logging.debug(output + "\nTotal Number of Parts: " + no_of_parts + "\nTotal Price: £" + total_price)

    for part_type in list_of_parts:
        historic_list = historic["historic_list"]
        if historic_list[part_type]["name"] != list_of_prices[part_type]["name"]:
            print(f"\n{part_type} has changed.\n")
            print(f"{historic_list[part_type]['name']} was changed to {list_of_prices[part_type]['name']}\n")
            diff = round(float(historic_list[part_type]["price"]) - float(list_of_prices[part_type]["price"]), 2)
            if diff > 0:
                print(
                    f"{list_of_prices[part_type]['name']} is £{str(diff)} cheaper than {historic_list[part_type]['name']}\n")
            if diff < 0:
                print(
                    f"{list_of_prices[part_type]['name']} is £{str(abs(diff))} more expensive than {historic_list[part_type]['name']}\n")
            historic_list.pop(part_type)
            historic_list[part_type] = list_of_prices[part_type]
            changed = True

    if total_price != historic["historic_price"]:
        print(f"Price Change! New Total Price is £{total_price}\nHistoric Low Price is £{historic['historic_low']}")
        total_diff = round(float(total_price) - float(historic["historic_price"]), 2)
        # print(totalDiff)
        if total_diff < 0:
            print(f"The new total is £{str(abs(total_diff))} cheaper than previous.\n")
        if total_diff > 0:
            print(f"The new total is £{str(total_diff)} more expensive than previous.\n")
        historic["historic_price"] = str(total_price)
    if float(total_price) < float(historic["historic_low"]):
        print("New Historic Low Total Price!")
        send_notification.send_notification_via_pushbullet("New Historic Low Price!",
                                                          f"The current cost of the build is £{total_price}\n{output}")
        historic["historic_low"] = total_price
    return {"output": output, "no_of_parts": no_of_parts, "total_price": total_price, "historic": historic}


def get_part_list(part_sources):
    list_of_parts = []
    for part in part_sources:
        if part.split("-")[0].strip() != "\n":
            list_of_parts.append(part.split("-")[0].strip())
    # print(listOfParts)
    return list_of_parts


def get_variables(uris):
    historic = os.getenv('HISTORIC')
    if not historic:
        historic = {}
    with open(uris) as f:
        part_sources = f.readlines()
    return {"part_sources": part_sources, "historic": historic}


def write_to_record(historic):
    os.environ['HISTORIC'] = historic
    return 'Historic Updated'


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


def get_price(part, listarg, historic):
    random_ua = get_random_ua()
    part_name = part.split("-")[0].strip()
    part_uri = part.split("-")[1].strip()
    if part_uri != "\n":
        r = requests.get(part_uri, headers={"User-Agent": random_ua, "referer": "google.co.uk"})
    html = r.text
    response_code = r.status_code
    print("Request: " + part_uri + "\nResponse Code: " + str(response_code), end="\n")
    soup = BeautifulSoup(html, "html.parser")
    part_detail = {}
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
                part_detail["price"] = price_float
                part_detail["link"] = "https://uk.partpicker.com" + price["href"]
                if historic["historic_list"][part_name]:
                    historic_part = historic["historic_list"][part_name]
                    if float(historic_part["historic_low"]) < float(price_float):
                        part_detail["historic_low"] = historic_part["historic_low"]
                    else:
                        part_detail["historic_low"] = price_float
    part_detail["name"] = soup.head.find("meta", property="og:title")["content"]
    # print(part_detail)
    listarg[partName] = part_detail
    delays = range(20)
    delay = np.random.choice(delays)
    time.sleep(delay)
    return "All Prices Collected"


class Scraper:

    def __init__(self, uris):
        self.part_sources = get_variables(uris)["part_sources"]
        self.historic = get_variables(uris)["historic"]

    def get_list_of_prices(self, part_sources, historic):
        # Create list of all component current details
        list_of_prices = {}
        for part in part_sources:
            get_price(part, list_of_prices, historic)
        if historic == {}:
            self['historic'] = list_of_prices
        # print(listOfPrices)
        print("\n")
        return list_of_prices
