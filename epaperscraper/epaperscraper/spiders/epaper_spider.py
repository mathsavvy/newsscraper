import scrapy
import re
import datetime as dt
# from scrapy.linkextractors import LinkExtractor #
# from scrapy.spiders import CrawlSpider, Rule #
# from scrapy.selector import Selector #
# from scrapy.http import FormRequest #
from bs4 import BeautifulSoup #

# from scrapy.utils.markup import remove_tags
# import newspaper
import json
# from scrapy_selenium import SeleniumRequest #


class Epaper(scrapy.Spider):
    name = "epaper"

    start_urls = ["https://epaper.thehindu.com/Login"]

    

    # def parse(self, response):
    #     request_token = response.xpath(
    #         '//*[@id="sectiNionA"]/div[1]/div/form/input[1]/@value'
    #     ).extract_first()
    #     print("here", request_token)
    #     return FormRequest.from_response(
    #         response,
    #         formdata={
    #             "Email": "shivam.jaiswal.18001@iitgoa.ac.in",
    #             "Password": "84662f",
    #             "__RequestVerificationToken": request_token,
    #             "hiddenTab": "https://epaper.thehindu.com/Login/LandingPage",
    #         },
    #         callback=self.get_all_page,
    #     )
    def parse(self, response):
        # for date in ['%s/09/2020'%(i) for i in range(29, 30)] :
        if getattr(self, 'date', ''):
            date = getattr(self,'date','')
        else:
            date = dt.datetime.today().strftime('%d/%m/%Y')
        yield scrapy.Request(
        url= "http://epaper.thehindu.com/Home/GetAllpages?editionid=115&editiondate=%s" % date,
        callback=self.after_login,
            cb_kwargs={
                "date": date,
            },
        )
        # scrapy.fetch('http://epaper.thehindu.com/Home/GetAllpages?editionid=1&editiondate=07%2F09%2F2020')

    def after_login(self, response, date):
        print("hii shivam ", response)
        for i in json.loads(response.text):
            new_url = (
                "https://epaper.thehindu.com/Home/getStoriesOnPage?pageid=%s"
                % i["PageId"]
            )
            yield scrapy.Request(url=new_url,
                                 callback=self.get_all_stories,
                                 cb_kwargs={
                                     "date": date,
                                 },
                                 )

    def get_all_stories(self, response, date):
        for i in json.loads(response.text):
            complete_url = (
                "https://epaper.thehindu.com/User/ShowArticleView?OrgId=%s" % i["OrgId"]
            )
            full_article_url = (
                "https://epaper.thehindu.com/Home/ShareArticle?OrgId=%s&imageview=0"
                % i["OrgId"]
            )
            yield scrapy.Request(
                url=complete_url,
                callback=self.in_each_stories,
                cb_kwargs={
                    "storyid": i["storyid"],
                    "orgid": i["OrgId"],
                    "date": date,
                    "title": i["storyTitle"],
                    "link": full_article_url,
                    "summary": i["Summary"],
                },
            )

    def in_each_stories(self, response, storyid, date, orgid, title, link, summary):

        # print(
        #     "response = ",
        #     response,
        #     "storyid = ",
        #     storyid,
        #     "date = ",
        #     date,
        #     "orgid = ",
        #     orgid,
        #     "title = ",
        #     title,
        #     "summary = ",
        #     summary,
        # )

        x = json.loads(response.text)
        # print()

        yield {
            "response = ": response,
            "storyid = ": storyid,
            "date = ": date,
            "orgid = ": orgid,
            "title = ": title,
            "link = ": link,
            "page Number = ": x["PageNumber"],
            "summary = ": summary,
            "total news": BeautifulSoup(x["StoryContent"][0]["Body"]).getText(),
        }