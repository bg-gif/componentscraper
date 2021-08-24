import componentscraper as cs


def run():
    v = cs.Scraper("uris.txt")
    part_list = cs.get_part_list(v.part_sources)
    get_list = v.get_list_of_prices(v.part_sources, v.historic)
    list_of_prices = get_list['list_of_prices']
    print(list_of_prices)
    # if not get_list['all_good']:
    #     print("Scraping Failed")
    #     return {'message': 'Something fucked up', 'responses': get_list['response_list']}
    price_check = cs.price_check(part_list, v.historic, list_of_prices)
    v.historic = price_check["historic"]
    print("HISTORIC: " + str(v.historic))
    cs.write_to_record(v.historic)
    return {"list_of_prices": list_of_prices, "historic": v.historic, "part_list": part_list}
