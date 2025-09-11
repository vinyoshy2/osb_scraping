from pathlib import Path

import scrapy


class OSBSpider(scrapy.Spider):
    name = "OSB"
    BASE_URL = "https://www.oversightboard.com/decision/"
    start_urls = [BASE_URL + "?pg=1"]

    def parse_case(self, response, case_info):
        main_article = response.css("article.blocks")
        content = main_article.css("h2, p").getall()
        case_info["content"] = "\n".join(content)
        yield case_info

    def parse(self, response, page_number=1):
        decisions_block = response.css("div.wp-block-decisions-b")
        cases = decisions_block.css("a.detail-card")
        for case in cases:
            case_url = case.css("a.detail-card::attr(href)").get()
            case_info = {}
            type_info = case.css("div.card-labels h2.card-label::text").getall()
            case_info["case_type"], case_info["case_outcome"]  = type_info[0], type_info[1]
            card_body_p = case.css("div.card-body p::text").getall()
            case_info["case_id"] = card_body_p[0:-1]
            case_info["short_description"] = card_body_p[-1]
            case_info["case_title"] = case.css("div.card-body h3.title::text").get()
            meta = case.css("div.card-body dl.meta-list dd::text").getall()
            case_info["tags"], case_info["location"], case_info["date"] = meta[0:-2], meta[-2], meta[-1]
            yield scrapy.Request(case_url, callback=self.parse_case, cb_kwargs={"case_info": case_info})
        next_url = decisions_block.css("div a.btn::attr(href)").get()
        if next_url is not None:
            yield scrapy.Request(self.BASE_URL + next_url, callback=self.parse, cb_kwargs={"page_number": page_number+1})
