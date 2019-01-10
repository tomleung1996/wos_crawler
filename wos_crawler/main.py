from wos_crawler.gui.main_gui import *
import wos_crawler.settings
from scrapy import cmdline

def crawl_by_journal(journal_list_path, output_path='../output'):
    cmdline.execute(r'scrapy crawl wos_journal_spider -a journal_list_path={} -a output_path={}'.format(journal_list_path, output_path).split())

def crawl_by_query(query, output_path='../output'):
    cmdline.execute(r'scrapy crawl wos_advanced_query_spider -a output_path={}'.format(output_path).split() +
                    ['-a','query={}'.format(query)])

def crawl_by_gui():
    app = QApplication(sys.argv)
    gui_crawler = GuiCrawler()
    gui_crawler.show()
    sys.exit(app.exec_())



if __name__ ==  '__main__':
    #按期刊下载
    # crawl_by_journal(journal_list_path=r'C:\Users\Tom\PycharmProjects\wos_crawler\wos_crawler\input\journal_list.txt',
    #                  output_path='../output')

    #按检索式下载
    # crawl_by_query(query='TS=information science AND PY=2018',
    #                output_path='../output')

    #使用GUI下载
    # crawl_by_gui()
    pass
