import os.path
import os
from urllib.request import Request, urlopen, FancyURLopener
from urllib.error import URLError
import urllib3
from requests.auth import HTTPProxyAuth
import cloudscraper
from bs4 import BeautifulSoup
from lxml import etree


def make_request(uri):
    # proxy_host = self.reset_proxy()
    proxy_host = "107.175.74.187:4444"
    proxy_key = '79c2db1481:Qeb5FIqx@'
    http_proxy = "http://" + proxy_key + proxy_host
    headers = {
        'User - Agent': 'Mozilla / 5.0(Windows NT 10.0; Win64; x64; rv: 91.0) Gecko / 20100101 Firefox / 91.0'
    }
    proxy_dict = {
        "http": http_proxy,
        "https": http_proxy
    }
    scraper = cloudscraper.create_scraper()
    print(proxy_host)
    # print(scraper.get('https://www.showmemyip.com/', headers=headers, proxies=proxy_dict).text)
    try:
        r = scraper.get(uri, headers=headers, proxies=proxy_dict)
    except cloudscraper.exceptions.CloudflareChallengeError as e:
        print(e)
        return "Failed"
    # r = requests.get(uri, headers=headers, proxies=proxy_dict)
    html = r.text
    soup = BeautifulSoup(html, "html.parser")
    print(soup)
    price = soup.find('div', {'class': 'price price-withsaving'})
    print(price)
    # dom = etree.HTML(str(soup))
    # print(dom.xpath('/html/body/div[6]/div[2]/div[1]/div/div/div[1]/div[1]/div[2]/div[2]/div[1]/div[2]')[0].text)
    return r.text


uri = "https://www.cclonline.com/product/324648/TU150WX/Cases/Lian-Li-PC-TU150X-Aluminium-ITX-Case-in-Black-with-Tempered-Glass/CAS4105/"

make_request(uri)
