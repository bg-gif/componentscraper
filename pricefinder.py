import componentscraper

def run():
    v = componentscraper.Scraper("uris.txt", "variables.json")
    partList = v.getpartlist(v.partSources)
    listOfPrices = v.getListOfPrices(v.partSources, v.historic)
    priceCheck = v.priceCheck(partList, v.historic, listOfPrices)
    v.historic = priceCheck["historic"]
    v.writetorecord(v.historic)
    return {"listOfPrices":listOfPrices, "historic": v.historic, "partList": partList}

