from scrapy import cmdline

#按期刊下载
# cmdline.execute('scrapy crawl wos_journal_spider'.split())

#按检索式下载
cmdline.execute('scrapy crawl wos_advanced_query_spider'.split())