import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog

app = QApplication(sys.argv)

import qt5reactor

qt5reactor.install()

from twisted.internet import reactor
from gui.gui_crawler import *
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerRunner
from spiders.wos_advanced_query_spider import WosAdvancedQuerySpiderSpider
from spiders.wos_journal_spider import WosJournalSpiderSpider


# TS=INFORMATION SCIENCE AND PY=2018

class GuiCrawler(QMainWindow):

    # 初始化GUI及绑定signal和slot
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.radioButtonJournal.toggled.connect(self.choose_input_format)
        self.ui.pushButtonJournal.clicked.connect(self.choose_journal_list_path)
        self.ui.pushButtonOutputPath.clicked.connect(self.choose_output_path)
        self.ui.lineEditJournal.textChanged.connect(self.change_start_crawler_button_state)
        self.ui.textEditQuery.textChanged.connect(self.change_start_crawler_button_state)
        self.ui.lineEditOutputPath.textChanged.connect(self.change_start_crawler_button_state)
        self.ui.pushButtonStartCrawler.clicked.connect(self.start_crawler)

    # 改变“选择期刊列表”以及两个文本输入框的状态
    def choose_input_format(self):
        if self.ui.radioButtonJournal.isChecked():
            self.ui.lineEditJournal.setEnabled(True)
            self.ui.textEditQuery.setEnabled(False)
            self.ui.pushButtonJournal.setEnabled(True)
        else:
            self.ui.lineEditJournal.setEnabled(False)
            self.ui.textEditQuery.setEnabled(True)
            self.ui.pushButtonJournal.setEnabled(False)
        self.change_start_crawler_button_state()

    # 得到期刊列表路径
    def choose_journal_list_path(self):
        dir_name = QFileDialog.getOpenFileName(self, '选择期刊列表文件：', '/')
        self.ui.lineEditJournal.setText(dir_name[0])
        if self.ui.lineEditJournal.text() != '' and self.ui.lineEditOutputPath.text() != '':
            self.ui.pushButtonStartCrawler.setEnabled(True)

    # 得到下载存放路径
    def choose_output_path(self):
        dir_name = QFileDialog.getExistingDirectory(self, '选择导出文件存放路径：', '/')
        self.ui.lineEditOutputPath.setText(dir_name)
        if self.ui.lineEditOutputPath.text() != '':
            self.ui.pushButtonStartCrawler.setEnabled(True)

    # 更改爬取按钮的状态（只有选中某种方式并且该方式文本框不为空才显示可用）
    def change_start_crawler_button_state(self):
        if (
                self.ui.lineEditJournal.text() != '' and self.ui.radioButtonJournal.isChecked() and self.ui.lineEditOutputPath.text() != '') \
                or (
                self.ui.textEditQuery.toPlainText() != '' and self.ui.radioButtonQuery.isChecked() and self.ui.lineEditOutputPath.text() != ''):
            self.ui.pushButtonStartCrawler.setEnabled(True)
        else:
            self.ui.pushButtonStartCrawler.setEnabled(False)

    # 将全部按钮禁用
    def disable_all_ui(self):
        self.ui.pushButtonStartCrawler.setEnabled(False)
        self.ui.comboBoxOutputFormat.setEnabled(False)
        self.ui.comboBoxDocumentType.setEnabled(False)
        self.ui.lineEditOutputPath.setEnabled(False)
        self.ui.lineEditJournal.setEnabled(False)
        self.ui.pushButtonOutputPath.setEnabled(False)
        self.ui.pushButtonJournal.setEnabled(False)
        self.ui.radioButtonQuery.setEnabled(False)
        self.ui.radioButtonJournal.setEnabled(False)
        self.ui.textEditQuery.setEnabled(False)


    # 开始爬取
    def start_crawler(self):

        self.disable_all_ui()

        output_path = self.ui.lineEditOutputPath.text()
        print('保存路径为：' + output_path)

        document_type = self.ui.comboBoxDocumentType.currentText()
        print('爬取文献类型：' + document_type)
        if document_type == 'All document types':
            document_type = ''
        document_type = document_type.lower()

        output_format = self.ui.comboBoxOutputFormat.currentText()
        print('保存格式：' + output_format)
        if output_format == 'Plain Text':
            output_format = 'fieldtagged'
        elif output_format == 'Tab-delimited (Win)':
            output_format = 'tabWinUnicode'
        elif output_format == 'Tab-delimited (Mac)':
            output_format = 'tabMacUnicode'
        elif output_format == 'Tab-delimited (Win, UTF-8)':
            output_format = 'tabWinUTF8'
        elif output_format == 'Tab-delimited (Mac, UTF-8)':
            output_format = 'tabMacUTF8'
        output_format = output_format.lower()

        # 需要注意，此处使用了CrawlerRunner，以便scrapy与GUI在同一个进程中异步进行
        crawler = CrawlerRunner(get_project_settings())
        d = None
        if self.ui.radioButtonJournal.isChecked():
            journal_list_path = self.ui.lineEditJournal.text()
            print('期刊列表存放路径为：' + journal_list_path)
            print('正在调用WosJournalSpider进行爬取……')
            d = crawler.crawl(WosJournalSpiderSpider, journal_list_path, output_path, document_type, output_format, self)

        elif self.ui.radioButtonQuery.isChecked():
            query = self.ui.textEditQuery.toPlainText()
            print('检索式为：' + query)
            print('正在调用WosAdvancedQuerySpider进行爬取……')
            d = crawler.crawl(WosAdvancedQuerySpiderSpider, query, output_path, document_type, output_format, self)

        d.addBoth(lambda _: print('爬取完成！'))

    def closeEvent(self, e):
        print('关闭程序……')
        try:
            reactor.callFromThread(reactor.stop)
        except Exception as exception:
            pass
        e.accept()


if __name__ == '__main__':
    # 需要使用reactor来执行，而不是app.exec_()
    gui_crawler = GuiCrawler()
    gui_crawler.show()
    reactor.run()
