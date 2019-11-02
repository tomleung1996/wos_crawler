# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from scrapy.http import FormRequest
import time
from bs4 import BeautifulSoup
import os
import sys
from parsers.bibtex.wos import bibtex_parser
from parsers.plaintext.wos import plaintext_parser


class WosJournalSpiderV2Spider(scrapy.Spider):
    name = 'wos_journal_10k_spider'
    allowed_domains = ['webofknowledge.com']
    start_urls = ['http://www.webofknowledge.com/']
    timestamp = str(time.strftime('%Y-%m-%d-%H.%M.%S', time.localtime(time.time())))

    # 提取URL中的SID和QID所需要的正则表达式
    sid_pattern = r'SID=(\w+)&'
    qid_pattern = r'qid=(\d+)&'

    # 提取已购买数据库的正则表达式
    db_pattern = r'WOS\.(\w+)'
    db_list = []

    # 目标文献类型
    document_type = 'Article'

    # 导出文献格式
    output_format = 'bibtex'

    # 待爬取期刊列表和列表存放的位置
    JOURNAL_LIST = []
    # JOURNAL_LIST_PATH = r'C:\Users\Tom\PycharmProjects\wos_crawler\wos_crawler\input\journal_list.txt'
    JOURNAL_LIST_PATH = None
    output_path_prefix = ''

    def __init__(self, journal_list_path=None, output_path='../output', document_type='Article',
                 output_format='fieldtagged', gui=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.JOURNAL_LIST_PATH = journal_list_path
        self.output_path_prefix = output_path
        self.document_type = document_type
        self.output_format = output_format
        self.gui = gui

        if journal_list_path is None:
            print('请指定期刊列表')
            sys.exit(-1)
        if output_path is None:
            print('请指定有效的输出路径')
            sys.exit(-1)

        with open(self.JOURNAL_LIST_PATH) as file:
            for row in file:
                # 策略一，手动分年份（对plos one可能需要逐年爬取）
                # self.JOURNAL_LIST.append((row.strip().replace('\n', '').upper(), '1900-1950'))
                # self.JOURNAL_LIST.append((row.strip().replace('\n', '').upper(), '1951-1970'))
                # self.JOURNAL_LIST.append((row.strip().replace('\n', '').upper(), '1971-1990'))
                # self.JOURNAL_LIST.append((row.strip().replace('\n', '').upper(), '1991-2000'))
                self.JOURNAL_LIST.append((row.strip().replace('\n', '').upper(), '2001-2010'))
                self.JOURNAL_LIST.append((row.strip().replace('\n', '').upper(), '2011-2013'))
                self.JOURNAL_LIST.append((row.strip().replace('\n', '').upper(), '2014-2016'))
                self.JOURNAL_LIST.append((row.strip().replace('\n', '').upper(), '2017-2018'))

        self.JOURNAL_LIST.sort()
        self.total_paper_num = 0
        self.downloaded = 0

        self.JOURNAL_LIST = (n for n in self.JOURNAL_LIST)

    # 在爬虫运行后进行一次期刊列表的初始化工作，将文件中的期刊名读入
    # def start_requests(self):
    #     with open(self.JOURNAL_LIST_PATH) as file:
    #         for row in file:
    #             self.JOURNAL_LIST.append(row.strip().replace('\n',''))
    #     self.JOURNAL_LIST.sort()
    #     self.total_paper_num = 0
    #     self.downloaded = 0
    #
    #     for url in self.start_urls:
    #         yield Request(url, dont_filter=True)

    def parse(self, response):
        """
        获取SID并提交高级搜索请求，将高级搜索请求返回给parse_result_entry处理
        每次搜索都更换一次SID

        :param response:
        :return:
        """
        # if len(self.JOURNAL_LIST) <= 0:
        #     print('**待爬取期刊已全部加入队列，不再产生新的异步请求，请等待现有的请求执行完成**')
        #     return

        # 获得当前要爬取的期刊名称
        # journal_name = self.JOURNAL_LIST.pop(0)
        for journal_name, year in self.JOURNAL_LIST:
            i = int(time.time())
            # 获取SID
            pattern = re.compile(self.sid_pattern)
            result = re.search(pattern, response.url)
            if result is not None:
                sid = result.group(1)
                print('\033[1;30;47m {} \033[0m 提取得到SID：'.format(journal_name + ' ' + year), result.group(1))
            else:
                print('\033[1;30;47m {} \033[0m SID提取失败'.format(journal_name + ' ' + year))
                sid = None
                exit(-1)

            # 获取已购买的WOS核心数据库信息
            soup = BeautifulSoup(response.text, 'lxml')
            db_str = str(soup.find('select', attrs={'id': 'ss_showsuggestions'}).get('onchange'))
            pattern = re.compile(self.db_pattern)
            result = pattern.findall(db_str)
            if result is not None:
                print('已购买的数据库为：', result)
                self.db_list = result

            # 提交post高级搜索请求
            adv_search_url = 'http://apps.webofknowledge.com/WOS_AdvancedSearch.do'
            # 检索式，目前设定为期刊，稍作修改可以爬取任意检索式
            query = 'SO="{}" AND PY=({})'.format(journal_name.upper(), year)

            query_form = {
                "product": "WOS",
                "search_mode": "AdvancedSearch",
                "SID": sid,
                "input_invalid_notice": "Search Error: Please enter a search term.",
                "input_invalid_notice_limits": " <br/>Note: Fields displayed in scrolling boxes must be combined with at least one other search field.",
                "action": "search",
                "replaceSetId": "",
                "goToPageLoc": "SearchHistoryTableBanner",
                "value(input1)": query,
                "value(searchOp)": "search",
                "value(select2)": "LA",
                "value(input2)": "",
                "value(select3)": "DT",
                "value(input3)": self.document_type,
                "value(limitCount)": "14",
                "limitStatus": "collapsed",
                "ss_lemmatization": "On",
                "ss_spellchecking": "Suggest",
                "SinceLastVisit_UTC": "",
                "SinceLastVisit_DATE": "",
                "period": "Range Selection",
                "range": "ALL",
                "startYear": "1900",
                "endYear": time.strftime('%Y'),
                "editions": self.db_list,
                # "editions": ["SCI", "SSCI", "AHCI", "ISTP", "ISSHP", "ESCI", "CCR", "IC"],
                "update_back2search_link_param": "yes",
                "ss_query_language": "",
                "rs_sort_by": "PY.D;LD.D;SO.A;VL.D;PG.A;AU.A",
            }

            # 将这一个高级搜索请求yield给parse_result_entry，内容为检索历史记录，包含检索结果的入口
            # 同时通过meta参数为下一个处理函数传递sid、journal_name等有用信息
            return FormRequest(adv_search_url, method='POST', formdata=query_form, dont_filter=True,
                               callback=self.parse_result_entry,
                               meta={'sid': sid, 'journal_name': journal_name, 'query': query, 'year':year})

        # 一个检索式爬取完成后，yield一个新的Request，相当于一个尾递归实现的循环功能，
        # 好处是每个检索式都是用不同的SID来爬取的
        # yield Request(self.start_urls[0], callback=self.parse, dont_filter=True, meta={})

    def parse_result_entry(self, response):
        """
        找到高级检索结果入口链接，交给parse_results处理
        同时还要记录下QID
        :param response:
        :return:
        """
        sid = response.meta['sid']
        journal_name = response.meta['journal_name']
        year = response.meta['year']
        query = response.meta['query']
        # cookiejar = response.meta['cookiejar']

        # filename = 'test/result-entry' + str(time.time()) + '-' + sid + '.html'
        # os.makedirs(os.path.dirname(filename), exist_ok=True)
        # with open(filename, 'w', encoding='utf-8') as file:
        #     file.write(response.text)

        # 通过bs4解析html找到检索结果的入口
        soup = BeautifulSoup(response.text, 'lxml')
        entry_url = soup.find('a', attrs={'title': 'Click to view the results'}).get('href')
        entry_url = 'http://apps.webofknowledge.com' + entry_url

        # 找到入口url中的QID，存放起来以供下一步处理函数使用
        pattern = re.compile(self.qid_pattern)
        result = re.search(pattern, entry_url)
        if result is not None:
            qid = result.group(1)
            print('\033[1;30;47m {} \033[0m 提取得到qid：'.format(journal_name + ' ' + year), result.group(1))
        else:
            print('\033[1;30;47m {} \033[0m qid提取失败'.format(journal_name + ' ' + year))
            exit(-1)

        # yield一个Request给parse_result，让它去处理搜索结果页面，同时用meta传递有用参数
        return Request(entry_url, callback=self.parse_results,
                       meta={'sid': sid, 'journal_name': journal_name, 'query': query, 'qid': qid, 'year':year})

    def parse_results(self, response):
        sid = response.meta['sid']
        journal_name = response.meta['journal_name']
        year = response.meta['year']
        query = response.meta['query']
        qid = response.meta['qid']
        # cookiejar = response.meta['cookiejar']

        # filename = 'test/results-' + str(time.time()) + '-' + sid + '.html'
        # os.makedirs(os.path.dirname(filename), exist_ok=True)
        # with open(filename, 'w', encoding='utf-8') as file:
        #     file.write(response.text)

        # 通过bs4获取页面结果数字，得到需要分批爬取的批次数
        soup = BeautifulSoup(response.text, 'lxml')
        paper_num = int(soup.find('span', attrs={'id': 'footer_formatted_count'}).get_text().replace(',', ''))

        # 处理超过10万文献的期刊
        if paper_num >= 100000:
            print('{}文献数量超过10万（{}），跳过爬取\n'.format(journal_name, paper_num))
            filename = self.output_path_prefix + '/journal/{}-{}/'.format('100K-' + journal_name + ' ' + year, paper_num)
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            yield Request(self.start_urls[0], method='GET', callback=self.parse, dont_filter=True)
            return

        span = 500
        iter_num = paper_num // span + (1 if paper_num % span != 0 else 0)
        self.COUNT = 0

        # 对每一批次的结果进行导出（500一批）
        print('{} 有{}条文献需要下载'.format(journal_name + ' ' + year, paper_num))
        self.total_paper_num += paper_num
        for i in range(1, iter_num + 1):
            end = i * span
            start = (i - 1) * span + 1
            if end > paper_num:
                end = paper_num
            print('\t正在下载 {} 的第 {} 到第 {} 条文献'.format(journal_name + ' ' + year, start, end))
            output_form = {
                "selectedIds": "",
                "displayCitedRefs": "true",
                "displayTimesCited": "true",
                "displayUsageInfo": "true",
                "viewType": "summary",
                "product": "WOS",
                "rurl": response.url,
                "mark_id": "WOS",
                "colName": "WOS",
                "search_mode": "AdvancedSearch",
                "locale": "en_US",
                "view_name": "WOS-summary",
                "sortBy": "PY.D;LD.D;SO.A;VL.D;PG.A;AU.A",
                "mode": "OpenOutputService",
                "qid": str(qid),
                "SID": str(sid),
                "format": "saveToFile",
                "filters": "HIGHLY_CITED HOT_PAPER OPEN_ACCESS PMID USAGEIND AUTHORSIDENTIFIERS ACCESSION_NUM FUNDING SUBJECT_CATEGORY JCR_CATEGORY LANG IDS PAGEC SABBR CITREFC ISSN PUBINFO KEYWORDS CITTIMES ADDRS CONFERENCE_SPONSORS DOCTYPE CITREF ABSTRACT CONFERENCE_INFO SOURCE TITLE AUTHORS  ",
                "mark_to": str(end),
                "mark_from": str(start),
                "queryNatural": str(query),
                "count_new_items_marked": "0",
                "use_two_ets": "false",
                "IncitesEntitled": "no",
                "value(record_select_type)": "range",
                "markFrom": str(start),
                "markTo": str(end),
                "fields_selection": "HIGHLY_CITED HOT_PAPER OPEN_ACCESS PMID USAGEIND AUTHORSIDENTIFIERS ACCESSION_NUM FUNDING SUBJECT_CATEGORY JCR_CATEGORY LANG IDS PAGEC SABBR CITREFC ISSN PUBINFO KEYWORDS CITTIMES ADDRS CONFERENCE_SPONSORS DOCTYPE CITREF ABSTRACT CONFERENCE_INFO SOURCE TITLE AUTHORS  ",
                "save_options": self.output_format
            }

            # 将下载地址yield一个FormRequest给download_result函数，传递有用参数
            output_url = 'http://apps.webofknowledge.com//OutboundService.do?action=go&&'
            yield FormRequest(output_url, method='POST', formdata=output_form, dont_filter=True,
                              callback=self.download_result,
                              meta={'sid': sid, 'journal_name': journal_name, 'query': query, 'qid': qid,
                                    'start': start, 'end': end, 'iter_num': iter_num,
                                    'paper_num':paper_num, 'year':year},
                              priority=paper_num - start)

    def download_result(self, response):

        file_postfix_pattern = re.compile(r'filename=\w+\.(\w+)$')
        file_postfix = re.search(file_postfix_pattern, response.headers[b'Content-Disposition'].decode())
        if file_postfix is not None:
            file_postfix = file_postfix.group(1)
        else:
            print('\t找不到文件原始后缀，使用txt后缀保存')
            file_postfix = 'txt'

        sid = response.meta['sid']
        journal_name = response.meta['journal_name']
        year = response.meta['year']
        query = response.meta['query']
        qid = response.meta['qid']
        start = response.meta['start']
        end = response.meta['end']
        # cookiejar = response.meta['cookiejar']
        iter_num = response.meta['iter_num']
        paper_num = response.meta['paper_num']

        # 按期刊名称保存文件

        # filename = self.output_path_prefix + '/journal/{}/{}/{}.{}'.format(self.timestamp,
        #                                                                    journal_name + '-' + str(paper_num),
        #                                                                    journal_name + '-' + str(start) + '-' + str(
        #                                                                        end),
        #                                                                    file_postfix)
        filename = self.output_path_prefix + '/journal/{}/{}.{}'.format(journal_name + ' ' + year + '-' + str(paper_num),
                                                                           journal_name + '-' + str(start) + '-' + str(
                                                                               end),
                                                                           file_postfix)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        text = response.text

        # WoS的bibtex格式不规范，需要特别处理一下
        if self.output_format == 'bibtex':
            text = text.replace('Early Access Date', 'Early-Access-Date').replace('Early Access Year',
                                                                                  'Early-Access-Year')

        with open(filename, 'w', encoding='utf-8') as file:
            file.write(text)

        print('\t--成功下载 {} 的第 {} 到第 {} 条文献--'.format(journal_name, start, end))

        self.downloaded += end - start + 1
        if self.gui is not None:
            self.gui.ui.progressBarDownload.setValue(self.downloaded / self.total_paper_num * 100)

        self.COUNT += 1

        if self.COUNT == iter_num:
            print('\033[1;30;47m {} \033[0m 最后一个文件下载完成，开始爬取下一本期刊\n'.format(journal_name))
            return Request(self.start_urls[0], method='GET', callback=self.parse, dont_filter=True)

    # def close(spider, reason):
    #     # 等到全部爬取完成后再解析并导入数据库
    #     if spider.output_format == 'bibtex':
    #         print('爬取完成，开始导入数据库(bibtex)')
    #         bibtex_parser.parse(input_dir=spider.output_path_prefix + '/journal/{}'.format(spider.timestamp),
    #                             db_path=spider.output_path_prefix + '/journal/{}/result.db'.format(
    #                                 spider.timestamp))
    #     elif spider.output_format == 'fieldtagged':
    #         print('爬取完成，开始导入数据库(fieldtagged/plaintext)')
    #         plaintex_parser.parse(input_dir=spider.output_path_prefix + '/journal/{}'.format(spider.timestamp),
    #                               db_path=spider.output_path_prefix + '/journal/{}/result.db'.format(
    #                                   spider.timestamp))
