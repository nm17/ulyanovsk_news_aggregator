# -*- coding: utf-8 -*-
import re
from datetime import datetime, timedelta, tzinfo

import pytz

import scrapy
from scrapy import Request
from scrapy.http import Response

TZ = pytz.timezone("Europe/Ulyanovsk")


def cleanhtml(raw_html):
    cleanr = re.compile("<.*?>")
    cleantext = re.sub(cleanr, "", raw_html)
    return cleantext.replace("\xa0", "")


class A73onlineSpider(scrapy.Spider):
    name = "73online"
    allowed_domains = ["73online.ru"]
    start_urls = ["https://73online.ru/news/"]

    def parse_news(self, response):
        dt = datetime.strptime(
            response.css("div.gray:nth-child(1)::text").extract()[0], "%d.%m.%Y, %H:%M"
        )
        dt = TZ.localize(dt)
        yield {
            "img": response.css("#readnews img")[1].attrib.get("src", None),
            "date": dt.isoformat(),
            "text": cleanhtml(
                "\n".join(response.css("p , #readnews b::text").extract())
            ),
            **response.meta["data"],
        }

    def parse_page(self, response):
        for news in response.css(".idx-newslist"):
            header = news.css(".header::text").extract()[0]

            yield Request(
                "https://73online.ru/" + news.css(".header").attrib["href"],
                callback=self.parse_news,
                meta={"data": {"header": header}},
            )
        yield Request(
            "https://73online.ru/news/"
            + response.css("#idx-mainnews .main")[0].attrib["href"].lstrip("news/"),
            callback=self.parse_page,
        )

    def parse(self, response):
        yield self.parse_page(response)
        last = int(response.css(".main:nth-child(7)").attrib["href"].lstrip("news/"))
        for page_n in range(2, last + 1):
            yield Request(
                "https://73online.ru/news/" + str(page_n), callback=self.parse_page
            )
