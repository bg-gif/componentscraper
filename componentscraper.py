import logging
from bs4 import BeautifulSoup
import requests
import re
import json
import numpy as np
import time
import send_notification
import os.path
import os
from urllib.request import Request, urlopen, FancyURLopener
from urllib.error import URLError
import urllib3
from requests.auth import HTTPProxyAuth
import cloudscraper
from selenium import webdriver


def write_to_record(historic):
    os.environ['HISTORIC'] = str(historic)
    print("history\n" + os.environ['HISTORIC'])
    print('fuuuuuuck')
    return 'Historic Updated'


def price_check(list_of_parts, historic, list_of_prices):
    # Calculate total price of build and list components and prices
    output = "\n\nPart List:\n\n"
    total = 0
    print(list_of_parts, historic, list_of_prices)
    for part_type in list_of_parts:
        part_name = list_of_prices[part_type]["name"]
        part_price = list_of_prices[part_type]["price"]
        if historic != list_of_prices:
            # print(part_name + ": £" + part_price)
            historic_low = historic["historic_list"][part_type]["historic_low"]
            output = output + part_name + ": £" + part_price
            if float(part_price) > float(historic_low):
                diff = str(round(float(part_price) - float(historic_low)))
                print(f"{part_type} is £{diff} more expensive than the historic low.")
            if float(part_price) < float(historic_low):
                diff = str(round(float(historic_low) - float(part_price), 2))
                print(f"{part_type} is £{diff} cheaper than the historic low. New Low Price added to historic record")
                output += ". New Historic Low!\n"
                send_notification.send_notification_via_pushbullet(f"New {part_type} Historic Low Price!",
                                                                   f"---{part_type}---\n{list_of_prices[part_type]['name']} has reached a historic low price of £{list_of_prices[part_type]['price']}")
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
        if historic != list_of_prices:
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
                print(
                    f"Price Change! New Total Price is £{total_price}\nHistoric Low Price is £{historic['historic_low']}")
                total_diff = round(float(total_price) - float(historic["historic_price"]), 2)
                # print(total_diff)
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
        else:
            historic = {"historic_list": list_of_prices, "historic_low": total_price, "historic_price": total_price, "historic_no_of_parts": no_of_parts}
    return {"output": output, "no_of_parts": no_of_parts, "total_price": total_price, "historic": historic}


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


def get_part_list(part_sources):
    list_of_parts = []
    for part in part_sources:
        if part.split("-")[0].strip() != "\n":
            list_of_parts.append(part.split("-")[0].strip())
    # print(list_of_parts)
    return list_of_parts


def get_variables(uris):
    historic = json.loads(os.getenv('HISTORIC'))
    print(type(historic))
    with open(uris) as f:
        part_sources = f.readlines()
    return {"part_sources": part_sources, "historic": historic}


def get_proxy_list():
    proxy_str = os.getenv('PROXY_LIST')
    proxy_list = proxy_str.split(',')
    return proxy_list


class Scraper:

    def __init__(self, uris):
        self.part_sources = get_variables(uris)["part_sources"]
        self.historic = get_variables(uris)["historic"]
        self.proxy_list = get_proxy_list()

    def reset_proxy(self):
        index = np.random.randint(len(self.proxy_list) - 1)
        proxy_host = self.proxy_list[index]
        return proxy_host

    def make_request(self, uri):
        proxy_host = self.reset_proxy()
        proxy_key = os.getenv('PROXY_KEY')
        http_proxy = "http://" + "127.0.0.1:24000"
        https_proxy = "http://" + proxy_key + proxy_host
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Cookie": "xcsrftoken=JmV23GDbuy3k5sFBMYFUlAPheEIJ2gjJTajRBKG9LmMhHTEO0LmJsw5VWH1XhhO3; xsessionid=c9rdy88zkouwbq9pp6n3dglyfa7142jm; xgdpr-consent=deny; cf_clearance=0d2ecd2bffdefba61e10c54a134b854419a58cbd-1628982253-0-250"}
        proxy_dict = {
            "http": http_proxy,
            "https": http_proxy
        }
        # scraper = cloudscraper.create_scraper()
        # print(proxy_host)
        # print(scraper.get('https://www.showmemyip.com/', headers=headers, proxies=proxy_dict).text)
        # try:
        #     r = scraper.get(uri, proxies=proxy_dict)
        # except cloudscraper.exceptions.CloudflareChallengeError as e:
        #     print(e)
        #     return "Failed"
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        r = requests.get(uri, proxies=proxy_dict, verify=False)
        return r

    def get_price(self, part, part_list, historic):
        part_name = part.split("-")[0].strip()
        part_uri = part.split("-")[1].strip()
        if part_uri != "\n":
            try:
                r = self.make_request(part_uri)
                if r.status_code != 200:
                    print("Request: " + part_uri + "\nResponse Code: " + str(r.status_code) + "\nRetrying....", end="\n")
                    self.get_price(part, part_list, historic)
                if r.status_code == 200:
                    response_code = r.status_code
                    print("Request: " + part_uri + "\nResponse Code: " + str(r.status_code), end="\n")
                    html = r.text
                    soup = BeautifulSoup(html, "html.parser")
                    part_detail = {}
                    if not soup.find_all("tbody"):
                        # print("No Price returned. Most likely due to bot detection", end="\n")
                        # return 400
                        print("Request: " + part_uri + "\nResponse Code: " + str(r.status_code) + "\nRetrying....",
                              end="\n")
                        self.get_price(part, part_list, historic)
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
                                if historic != {}:
                                    if historic.historic_list[part_name]:
                                        historicPart = historic["historic_list"][part_name]
                                        if float(historicPart["historic_low"]) < float(price_float):
                                            part_detail["historic_low"] = historicPart["historic_low"]
                                        else:
                                            part_detail["historic_low"] = price_float
                    part_detail["name"] = soup.head.find("meta", property="og:title")["content"]
                    part_list[part_name] = part_detail
                    delays = range(5)
                    delay = np.random.choice(delays)
                    time.sleep(delay)
                    return response_code
                if r.status_code == 503:
                    return 503
                else:
                    return 666
            except URLError as e:
                print(e)
                self.get_price(part, part_list, historic)


    def get_list_of_prices(self, part_sources, historic):
        # Create list of all component current details
        print("HISTORIC: " + str(historic))
        list_of_prices = {}
        all_good = True
        response_list = []
        for part in part_sources:
            rc = self.get_price(part, list_of_prices, historic)
            response_list.append({part: rc})
            if rc != 200:
                all_good = False
        if historic == {}:
            self.historic = list_of_prices
        print("\n")
        return {"list_of_prices": list_of_prices, "all_good": all_good, 'response_list': response_list}


class AppURLopener(FancyURLopener):
    # random_ua = get_random_ua()
    version = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0"

    def http_error_default(self, url, fp, errcode, errmsg, headers):
        if errcode == 403:
            raise ValueError("403")
        return super(FixFancyURLOpener, self).http_error_default(
            url, fp, errcode, errmsg, headers
        )
