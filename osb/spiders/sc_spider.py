from pathlib import Path
import string
import scrapy
from scrapy_playwright.page import PageMethod
from osb.items import SCItem

 #   states = ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]

states = ["california/court-of-appeal", "illinois/supreme-court", "ohio/seventh-district-court-of-appeals"]
BASE_URL = "https://law.justia.com/cases/{}/"
YEARS = [str(year) for year in range(2020,2026)]

def remove_punct(x):
    translator = str.maketrans('', '', string.punctuation)
    return x.translate(translator)

class SCSpider(scrapy.Spider):
    name = "SC"

    def start_requests(self):
        for state in states:
            yield scrapy.Request(
                BASE_URL.format(state),
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_load_state", "networkidle"),
                    ],
                },
            )

    def parse_case(self, response, source):
        name = response.css('span.col--three-fourths h1.heading-1::text').get()
        sub_name = name.split()[:3]
        case_id = "_".join([remove_punct(word.lower()) for word in sub_name])
        summary = "".join(response.css(
            'div.bg-wild-sand.has-padding-full-25.block.has-no-top-margin '
            'div#diminished-text p ::text'
        ).getall()).strip()
        pdf_url = response.urljoin(response.css('div#opinion a.pdf-icon::attr(href)').get())
        case = SCItem()
        case["case_id"] = case_id
        case["short_description"] = summary
        case["case_title"] = name
        case["file_urls"] = [pdf_url]
        case["source"] = source
        yield case

    def parse_case_list(self, response):
        split_url = response.url.split("/")
        src = "-".join(split_url[4:6])
        count = 0
        for href in response.css('div.has-padding-content-block-30 a.case-name::attr(href)').getall():
            full_url = response.urljoin(href)
            yield scrapy.Request(
                full_url,
                callback=self.parse_case,
                cb_kwargs={"source": src},
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_load_state", "networkidle"),
                    ],
                },
            )
            count += 1
            if count >= 5:
                return

    def parse(self, response):
 #       for link in response.css("div.indented ul li a"):
  #          text = link.css("::text").get()
   #         href = link.attrib["href"]
    #        full_url = response.urljoin(href)
     #       if "Supreme" in text or "Appeal" in text:
         full_url = response.url
         for year in YEARS:
             new_url = "{}{}".format(full_url, year)
             yield scrapy.Request(
                new_url,
                callback=self.parse_case_list,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_load_state", "networkidle"),
                    ],
                },
             )

