# -*- coding: utf-8 -*-

import scrapy
import requests
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
import json
import urllib
from urllib import parse
import csv

with open('ZillowSpiderMan.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Zip Code", "Price", "Status", "Zestimate", "Address", "City", "State", "Bedrooms",
                     "Bathrooms", "Size", "Type", "Year Built", "Heating", "Cooling", "Parking", "Lot Size",
                     "Price/sqft", "URL"])


class ZillowSpiderMan(scrapy.Spider):
    # --------------------------SetUp--------------------------
    name = 'SpiderZillow'
    base_url = 'https://www.zillow.com/homes/Schenectady,-NY_rb/?'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
    }
    # Get param from using urllib.parse.unquote the url of page
    params = {
        'searchQueryState': '{"pagination":{"currentPage":1},"usersSearchTerm":"Schenectady, NY","mapBounds":{"west":-74.21919025585936,"east":-73.71656574414061,"south":42.62679258938623,"north":43.030660149479566},"regionSelection":[{"regionId":40779,"regionType":6}],"isMapVisible":false,"mapZoom":11,"filterState":{},"isListVisible":true}'
    }
    page_amount = 16
    page_urls = []

    # ------------------------Functions------------------------

    def start_requests(self):
        for page in range(1, self.page_amount + 1):
            json_params = json.loads(self.params['searchQueryState'])
            json_params['pagination']['currentPage'] = page
            self.params['searchQueryState'] = json.dumps(json_params, separators=(",", ":"))
            # Create the url by adding the base and encoding back params using urllib.parse.urlencode
            next_page = self.base_url + urllib.parse.urlencode(self.params)
            self.page_urls.append(str(next_page))
        for url in self.page_urls:
            print(url)
            yield scrapy.Request(url=url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        cards_on_page = response.css('ul[class="photo-cards photo-cards_wow photo-cards_short"]')
        card_li = cards_on_page.css('li')
        list = card_li.css('a.list-card-link::attr(href)').extract()

        for card in list:
            print(card)
            yield response.follow(url=card, headers=self.headers, callback=self.formatter)

    def formatter(self, response):

        # main_data
        main_data_list = response.css('div[class="ds-home-details-chip"]')
        main_data_labels = main_data_list.css('span')
        print(main_data_labels)

        #PRICE
        price = main_data_labels.css('span[class="ds-value"]::text').get()
        print(price)
        urlnow = response.url

        #BD/BA/SQFT
        try:
            test = main_data_list.css('span[class="ds-bed-bath-living-area"]')
            bddata = test.css('span::text').getall()
            bedrooms = bddata[0] + bddata[1] + bddata[2]
            bathrooms = bddata[3] + bddata[4] + bddata[5]
            size_of = bddata[6] + bddata[7] + bddata[8]
            print(bddata)
        except IndexError:
            bedrooms = 'No Data'
            bathrooms = 'No Data'
            size_of = 'No Data'

        #ADDY
        try:
            street = main_data_list.css('div[class="ds-price-change-address-row"]')
            addy = street.css('span::text').getall()
            print(addy)
            street_addy = addy[0].replace(',', '')
            city_state_zip = addy[-1].split(' ')
            city = city_state_zip[0].replace(',', '')
            state = city_state_zip[1].replace(',', '')
            zip_code = city_state_zip[2].replace(',', '')
            print(street_addy)
            print(city)
            print(state)
            print(zip_code)
        except IndexError:
            street_addy = 'No Data'
            city = 'No Data'
            state = 'No Data'
            zip_code = 'No Data'

        #STATS
        try:
            stats = main_data_list.css('div:nth-child(3)')
            stass = stats.css('span::text').getall()
            status = stass[0]
            print(status)
            zestimate = stass[-1]
            print(zestimate)
        except IndexError:
            status = 'No Data'
            zestimate = 'No Data'

        #FACTSANDFEATURES
        fact_feature_list = response.css('ul[class="ds-home-fact-list"]')

        #TYPE
        try:
            type_ = fact_feature_list.css('li:nth-child(1)')
            type_ = type_.css('span:nth-child(3)::text').get()
            print(type_)
        except:
            type_ = 'No Data'

        #YEAR BUILT
        try:
            year_built = fact_feature_list.css('li:nth-child(2)')
            year_built = year_built.css('span:nth-child(3)::text').get()
            print(year_built)
        except:
            year_built = 'No Data'

        #HEATING
        try:
            heating = fact_feature_list.css('li:nth-child(3)')
            heating = heating.css('span:nth-child(3)::text').get()
            print(heating)
        except:
            heating = 'No Data'

        #COOLING
        try:
            cooling = fact_feature_list.css('li:nth-child(4)')
            cooling = cooling.css('span:nth-child(3)::text').get()
            print(cooling)
        except:
            cooling = 'No Data'

        #PARKING
        try:
            parking = fact_feature_list.css('li:nth-child(5)')
            parking = parking.css('span:nth-child(3)::text').get()
            print(parking)
        except:
            parking = 'No Data'

        #LOT
        try:
            lot = fact_feature_list.css('li:nth-child(6)')
            lot = lot.css('span:nth-child(3)::text').get()
            print(lot)
        except:
            lot = 'No Data'

        #PRICE/PER/SQFT
        try:
            price_per_sqft = fact_feature_list.css('li:nth-child(7)')
            price_per_sqft = price_per_sqft.css('span:nth-child(3)::text').get()
            print(price_per_sqft)
        except:
            price_per_sqft = 'No Data'

        with open('ZillowSpiderMan.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(
                [zip_code, price, status, zestimate, street_addy, city, state, bedrooms, bathrooms, size_of,
                 type_, year_built, heating, cooling, parking, lot, price_per_sqft, urlnow])


# main driver
if __name__ == '__main__':
    # run scraper
    process = CrawlerProcess()
    process.crawl(ZillowSpiderMan)
    process.start()

# debug data extraction logic
# ZillowScraper.parse_listing(ZillowScraper, '')


