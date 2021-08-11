import componentscraper

def run():
    v = componentscraper.Scraper("uris.txt", "variables.json")
    partList = v.getpartlist(v.partSources)
    getList = v.getListOfPrices(v.partSources, v.historic)
    listOfPrices = getList.listOfPrices
    if not getList.allGood:
        print("Scraping Failed")
        return
    priceCheck = v.priceCheck(partList, v.historic, listOfPrices)
    v.historic = priceCheck["historic"]
    v.writetorecord(v.historic)
    return {"listOfPrices": listOfPrices, "historic": v.historic, "partList": partList}

