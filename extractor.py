#!/bin/env python
# -*- coding:utf8 -*-

import sys, os
import zlib
import base64
from lxml import etree
class BaseExtractorException(Exception):
    pass

class BaseExtractor(object):
    def __init__(self, params):
        self.extractor_name = params["name"]

    @staticmethod
    def decompress(content):
        return str(zlib.decompress(base64.b64decode(bytes(content, encoding="utf-8"))), encoding="utf-8")


    def extract(self, content):
        """
        :param doc: 输入的爬取结果，格式为{"result_data": "xxx",  "result_status": 200, "grab_time": 123,
                    "request_data": request_data}
        :return: 两个返回值，一个是抽取内容的dict，一个是待爬取的url 信息列表
                 url的信息格式类似 {"method": "get", "url": "xxx", "source": "pubmed", "post_data":"如果有"}
        """
        raise BaseExtractorException("{} extract not implement".format(self.extractor_name))

    @staticmethod
    def judge(doc):
        """
        :param doc: 输入的爬虫结果
        :return: 根据url、method等判断是否匹配该抽取器
        """
        return doc['request_data']['url'].find("cancer")


class UrlExtractor(BaseExtractor):
    def extract(self, doc):
        article_urls = []
        try:
            html_text = etree.HTML(doc)
            # 获取每篇文章的键接
            articles_url = html_text.xpath('//article//a[@class="docsum-title"]/@href')
            if articles_url:
                # 获取第二页的链接接
                for article_url in articles_url:
                    request_data = {"method": "get", "url": 'https://pubmed.ncbi.nlm.nih.gov'+article_url.strip(), "source": "pubmed", "post_data": "如果有"}
                    article_urls.append(request_data)
                return article_urls
        except Exception as e:
            print(str(e))

class DetailExtractor(BaseExtractor):
    def extract(self, doc):
        res = {}
        article_urls = []
        try:
            html_text = etree.HTML(doc)
            title = html_text.xpath('//div[@id="full-view-heading"]/h1/text()')[0].strip()
            cit = html_text.xpath('//div[@class="article-source"]/span[@class="cit"]/text()')[0].strip()
            doi = html_text.xpath('//div[@class="article-citation"]/span[@class="citation-doi"]/text()')
            res['title'] = title  # 文章标题
            res['cit'] = cit  # 时间
            res['doi'] = doi
            # 作者和链接
            authors_list = html_text.xpath('//div[@id="full-view-heading"]//a[@class="full-name"]/text()')[0].strip()
            author_url = html_text.xpath('//div[@id="full-view-heading"]//a[@class="full-name"]/@href')[0].strip()
            pm_id = html_text.xpath('//ul[@id="full-view-identifiers"]//strong[@class="current-id"]/text()')[0].strip()
            res['author_url'] = 'https://pubmed.ncbi.nlm.nih.gov' + author_url
            res['authors_list'] = authors_list
            res['pm_id'] = pm_id
            # 摘要
            abstract = html_text.xpath('//div[@id="enc-abstract"]/p/text()')[0].strip()
            res['abstract'] = abstract

            # similar articles
            similar_articles_li = html_text.xpath('//ul[@id="similar-articles-list"]/li')
            similar_list = []
            for li in similar_articles_li:
                smilar_dict = {}
                introduce = li.xpath('//div[@class="docsum-content"]//a[@class="docsum-title"]/text()')[0].strip()
                introduce_url_list = li.xpath('//div[@class="docsum-content"]//a[@class="docsum-title"]/@href')
                similar_authors = li.xpath('//span[@class="docsum-authors full-authors"]/text()')[0].strip()
                similar_time = li.xpath('//span[@class="docsum-journal-citation full-journal-citation"]/text()')[
                    0].strip()
                similar_pm_id = li.xpath('//span[@class="docsum-pmid"]/text()')[0].strip()
                smilar_dict['introduce'] = introduce
                smilar_dict['similar_authors'] = similar_authors
                smilar_dict['similar_pm_id'] = similar_pm_id
                smilar_dict['similar_time'] = similar_time

                for url in introduce_url_list:
                    introduce_url = 'https://pubmed.ncbi.nlm.nih.gov' + url
                    url = {"method": "get", "url": introduce_url,"source": "pubmed", "post_data": "如果有"}
                    article_urls.append(url)
                similar_list.append(smilar_dict)
            res['similar'] = similar_list
            # cited by
            cited_by = html_text.xpath('//ul[@id="citedby-articles-list"]/li')
            citeds_list = []
            for cited_list in cited_by:
                cited_dict = {}
                cited_url = cited_list.xpath('//a[@class="docsum-title"]/@href')[0].strip()
                cited_introduce = cited_list.xpath('//a[@class="docsum-title"]/text()')[0].strip()
                cited_authors = cited_list.xpath('//span[@class="docsum-authors full-authors"]/text()')[0].strip()
                cited_time = cited_list.xpath('//span[@class="docsum-journal-citation full-journal-citation"]/text()')[
                    0].strip()
                cited_pm_id = cited_list.xpath('//span[@class="docsum-pmid"]/text()')[0].strip()
                is_free = cited_list.xpath('//span[@class="free-resources spaced-citation-item citation-part"]/text()')

                cited_dict['cited_introduce'] = cited_introduce
                cited_url = 'https://pubmed.ncbi.nlm.nih.gov' + cited_url
                url = {"method": "get", "url": cited_url, "source": "pubmed"}
                article_urls.append(url)
                cited_dict['cited_authors'] = cited_authors
                cited_dict['cited_time'] = cited_time
                cited_dict['cited_pm_id'] = cited_pm_id
                cited_dict['is_free'] = is_free
                citeds_list.append(cited_dict)
            res['cited'] = citeds_list
            # Publication types
            publications_list = []
            publication_list = html_text.xpath('//div[@id="publication-types"]//ul/li//text()')
            for publication in publication_list:
                publication_dict = {}
                publication_dict['publication'] = publication.strip()
                publications_list.append(publication_dict)
            res['publication'] = publications_list
            # MeSH terms
            mesh_list = []
            mesh = html_text.xpath('//div[@id="mesh-terms"]//ul/li//text()')
            for m in mesh:
                mesh_dict = {}
                mesh_dict['mesh'] = m.strip()
                mesh_list.append(mesh_dict)
            res['mesh'] = mesh_list
            return res,article_urls
        except Exception as e:
            print(str(e))

class FakeExtractor(object):
    def __init__(self, params):
        self.extractor_name = params
    def extract(self, doc):
        res = {}
        article_urls = []
        try:
            html_text = etree.HTML(doc)
            # 获取每篇文章的键接
            articles_url = html_text.xpath('//article//a[@class="docsum-title"]/@href')
            if articles_url:
                # 获取第二页的链接接
                for article_url in articles_url:
                    request_data = {"method": "get", "url": 'https://pubmed.ncbi.nlm.nih.gov'+article_url.strip(), "source": "pubmed"}
                    article_urls.append(request_data)
                return res,article_urls
            title = html_text.xpath('//div[@id="full-view-heading"]/h1/text()')[0].strip()
            cit = html_text.xpath('//div[@class="article-source"]/span[@class="cit"]/text()')[0].strip()
            doi = html_text.xpath('//div[@class="article-citation"]/span[@class="citation-doi"]/text()')
            res['title'] = title  # 文章标题
            res['cit'] = cit  # 时间
            res['doi'] = doi
            # 作者和链接
            authors_list = html_text.xpath('//div[@id="full-view-heading"]//a[@class="full-name"]/text()')[0].strip()
            author_url = html_text.xpath('//div[@id="full-view-heading"]//a[@class="full-name"]/@href')[0].strip()
            pm_id = html_text.xpath('//ul[@id="full-view-identifiers"]//strong[@class="current-id"]/text()')[0].strip()
            res['author_url'] = 'https://pubmed.ncbi.nlm.nih.gov' + author_url
            res['authors_list'] = authors_list
            res['pm_id'] = pm_id
            # 摘要
            abstract = html_text.xpath('//div[@id="enc-abstract"]/p/text()')[0].strip()
            res['abstract'] = abstract

            # similar articles
            similar_articles_li = html_text.xpath('//ul[@id="similar-articles-list"]/li')
            similar_list = []
            for li in similar_articles_li:
                smilar_dict = {}
                introduce = li.xpath('//div[@class="docsum-content"]//a[@class="docsum-title"]/text()')[0].strip()
                introduce_url_list = li.xpath('//div[@class="docsum-content"]//a[@class="docsum-title"]/@href')
                similar_authors = li.xpath('//span[@class="docsum-authors full-authors"]/text()')[0].strip()
                similar_time = li.xpath('//span[@class="docsum-journal-citation full-journal-citation"]/text()')[
                    0].strip()
                similar_pm_id = li.xpath('//span[@class="docsum-pmid"]/text()')[0].strip()
                smilar_dict['introduce'] = introduce
                smilar_dict['similar_authors'] = similar_authors
                smilar_dict['similar_pm_id'] = similar_pm_id
                smilar_dict['similar_time'] = similar_time

                for url in introduce_url_list:
                    introduce_url = 'https://pubmed.ncbi.nlm.nih.gov' + url
                    url = {"method": "get", "url": introduce_url,"source": "pubmed", "post_data": "如果有"}
                    article_urls.append(url)
                similar_list.append(smilar_dict)
            res['similar'] = similar_list
            # cited by
            cited_by = html_text.xpath('//ul[@id="citedby-articles-list"]/li')
            citeds_list = []
            for cited_list in cited_by:
                cited_dict = {}
                cited_url = cited_list.xpath('//a[@class="docsum-title"]/@href')[0].strip()
                cited_introduce = cited_list.xpath('//a[@class="docsum-title"]/text()')[0].strip()
                cited_authors = cited_list.xpath('//span[@class="docsum-authors full-authors"]/text()')[0].strip()
                cited_time = cited_list.xpath('//span[@class="docsum-journal-citation full-journal-citation"]/text()')[
                    0].strip()
                cited_pm_id = cited_list.xpath('//span[@class="docsum-pmid"]/text()')[0].strip()
                is_free = cited_list.xpath('//span[@class="free-resources spaced-citation-item citation-part"]/text()')

                cited_dict['cited_introduce'] = cited_introduce
                cited_url = 'https://pubmed.ncbi.nlm.nih.gov' + cited_url
                url = {"method": "get", "url": cited_url, "source": "pubmed"}
                article_urls.append(url)
                cited_dict['cited_authors'] = cited_authors
                cited_dict['cited_time'] = cited_time
                cited_dict['cited_pm_id'] = cited_pm_id
                cited_dict['is_free'] = is_free
                citeds_list.append(cited_dict)
            res['cited'] = citeds_list
            # Publication types
            publications_list = []
            publication_list = html_text.xpath('//div[@id="publication-types"]//ul/li//text()')
            for publication in publication_list:
                publication_dict = {}
                publication_dict['publication'] = publication.strip()
                publications_list.append(publication_dict)
            res['publication'] = publications_list
            # MeSH terms
            mesh_list = []
            mesh = html_text.xpath('//div[@id="mesh-terms"]//ul/li//text()')
            for m in mesh:
                mesh_dict = {}
                mesh_dict['mesh'] = m.strip()
                mesh_list.append(mesh_dict)
            res['mesh'] = mesh_list
            return res,article_urls
        except Exception as e:
            print(str(e))

    @staticmethod
    def judge(doc):
        return doc['request_data']['url'].find("cancer")

def main(argv):
    pass

if __name__ == "__main__":
    main(sys.argv)