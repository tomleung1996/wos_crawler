# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from parsers.bibtex.wos import bibtex_parser
from items import WosBibtexItem

class ParseAndStorePipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, WosBibtexItem):
            bibtex_parser.parse_single(item['filename'], item['output_path'])
        else:
            print('未考虑到的管道情况：', type(item))
            exit(-1)
        return item
