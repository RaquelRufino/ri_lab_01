# -*- coding: utf-8 -*-
import scrapy
import json
import datetime
from ri_lab_01.items import RiLab01Item
from ri_lab_01.items import RiLab01CommentItem


class OantagonistaSpider(scrapy.Spider):
    name = 'oantagonista'
    allowed_domains = ['oantagonista.com']
    start_urls = []
    n_page = 1
    limitDate = datetime.datetime(2018,1,1)

    def __init__(self, *a, **kw):
        super(OantagonistaSpider, self).__init__(*a, **kw)
        with open('seeds/oantagonista.json') as json_file:
                data = json.load(json_file)
        self.start_urls = list(data.values())

    def parse(self, response):
        

        def checkDateLimit(response, lowerLimit):
            currentDate = response.css('time.entry-date ::attr(datetime)').get()
            currentDate = currentDate.split(' ')[0].split('-')

            date =  datetime.datetime(int(currentDate[-3]), int(currentDate[-2]), int(currentDate[-1]))

            return date > lowerLimit


        if not checkDateLimit(response, self.limitDate) :
            return


        articles = response.css('article')

        for href in articles.css('a.article_link::attr(href)'):
            yield response.follow(href, callback= self.scrapeNewsPage)

        page = response.url.split("/")[-2]

        nextPage = self.start_urls[0] + 'pagina/' + str(self.n_page) +'/?ajax'
        self.n_page = self.n_page + 1

        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)

        
        yield scrapy.Request(nextPage, callback=self.parse)


    def scrapeNewsPage(self, response):

        encodeUTF8 = lambda target : target.encode('UTF-8')


        articleAuthor = response.css('header.entry-header div::text').get().replace('Por ','')


        articleText = ""

        for paragraph in response.css('div.entry-content p::text'):
            articleText = articleText + paragraph.get()
        
        reverseDate = lambda date : '/'.join(date.split('-')[::-1])

        date = response.css('time.entry-date ::attr(datetime)').get()
        year,time = date.split(' ')
        year = reverseDate(year)

        date =  year + " " + time

        yield {
            'title': encodeUTF8(response.css('h1.entry-title::text').get()),
            'subtitle': 'Nao tem subtitle',
            'author': encodeUTF8(articleAuthor) if articleAuthor.strip() else "Nao tem autor",
            'date': encodeUTF8(date),
            'section': encodeUTF8(response.css('header.entry-header span.postmeta span.categoria a::text').get()),
            'text': encodeUTF8(articleText),
            'url': response.request.url
        }
