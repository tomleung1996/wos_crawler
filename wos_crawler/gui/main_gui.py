import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog

app = QApplication(sys.argv)

import qt5reactor

qt5reactor.install()

from twisted.internet import reactor
from gui.tab_gui_crawler import *
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerRunner
from spiders.wos_advanced_query_spider import WosAdvancedQuerySpiderSpider
from spiders.wos_journal_spider_v2 import WosJournalSpiderV2Spider
import parsers.plaintext.wos.plaintext_parser
import parsers.bibtex.wos.bibtex_parser
import parsers.xml.wos.xml_parser_v3
import time


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

        # tab2功能
        self.ui.pushButtonParserInput.clicked.connect(self.choose_raw_data_path)
        self.ui.pushButtonParserSQLiteOutput.clicked.connect(self.choose_sqlite_output_path)
        self.ui.radioButtonSQLite.toggled.connect(self.choose_sql_output_format)
        self.ui.lineEditParsrSQLiteOutput.textChanged.connect(self.change_start_parser_button_state)
        self.ui.lineEditParsrMySQLDBAddress.textChanged.connect(self.change_start_parser_button_state)
        self.ui.lineEditParsrMySQLDBName.textChanged.connect(self.change_start_parser_button_state)
        self.ui.lineEditParsrMySQLUsername.textChanged.connect(self.change_start_parser_button_state)
        self.ui.lineEditParsrMySQLPassword.textChanged.connect(self.change_start_parser_button_state)
        self.ui.lineEditParsrInputPath.textChanged.connect(self.change_start_parser_button_state)
        self.ui.pushButtonParserStart.clicked.connect(self.start_parser)

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
        elif output_format == 'Bibtex':
            output_format = 'bibtex'
        elif output_format == 'HTML':
            output_format = 'html'
        elif output_format == 'Tab-delimited (Win)':
            output_format = 'tabWinUnicode'
        elif output_format == 'Tab-delimited (Mac)':
            output_format = 'tabMacUnicode'
        elif output_format == 'Tab-delimited (Win, UTF-8)':
            output_format = 'tabWinUTF8'
        elif output_format == 'Tab-delimited (Mac, UTF-8)':
            output_format = 'tabMacUTF8'
        # output_format = output_format.lower()

        # 需要注意，此处使用了CrawlerRunner，以便scrapy与GUI在同一个进程中异步进行
        crawler = CrawlerRunner(get_project_settings())
        d = None
        if self.ui.radioButtonJournal.isChecked():
            journal_list_path = self.ui.lineEditJournal.text()
            print('期刊列表存放路径为：' + journal_list_path)
            print('正在调用WosJournalSpider进行爬取……')
            d = crawler.crawl(WosJournalSpiderV2Spider, journal_list_path, output_path, document_type, output_format,
                              self)

        elif self.ui.radioButtonQuery.isChecked():
            query = self.ui.textEditQuery.toPlainText()
            print('检索式为：' + query)
            print('正在调用WosAdvancedQuerySpider进行爬取……')
            d = crawler.crawl(WosAdvancedQuerySpiderSpider, query, output_path, document_type, output_format, self)

        d.addBoth(lambda _: print('爬取完成！'))

    # tab2功能
    def choose_raw_data_path(self):
        dir_name = QFileDialog.getExistingDirectory(self, '选择待解析文件的存放路径：', '/')
        self.ui.lineEditParsrInputPath.setText(dir_name)

    # tab2功能
    def choose_sqlite_output_path(self):
        dir_name = QFileDialog.getExistingDirectory(self, '选择SQLite数据库文件的存放路径：', '/')
        self.ui.lineEditParsrSQLiteOutput.setText(dir_name)

    # tab2功能
    def choose_sql_output_format(self):
        if self.ui.radioButtonMySQL.isChecked():
            self.ui.lineEditParsrMySQLDBAddress.setEnabled(True)
            self.ui.lineEditParsrMySQLDBName.setEnabled(True)
            self.ui.lineEditParsrMySQLUsername.setEnabled(True)
            self.ui.lineEditParsrMySQLPassword.setEnabled(True)
            self.ui.lineEditParsrSQLiteOutput.setEnabled(False)
            self.ui.pushButtonParserSQLiteOutput.setEnabled(False)
        else:
            self.ui.lineEditParsrMySQLDBAddress.setEnabled(False)
            self.ui.lineEditParsrMySQLDBName.setEnabled(False)
            self.ui.lineEditParsrMySQLUsername.setEnabled(False)
            self.ui.lineEditParsrMySQLPassword.setEnabled(False)
            self.ui.lineEditParsrSQLiteOutput.setEnabled(True)
            self.ui.pushButtonParserSQLiteOutput.setEnabled(True)

    # tab2功能
    def change_start_parser_button_state(self):
        if self.ui.lineEditParsrInputPath.text() != '' and \
                ((self.ui.radioButtonSQLite.isChecked() and self.ui.lineEditParsrSQLiteOutput.text() != '') or
                 (self.ui.radioButtonMySQL.isChecked() and self.ui.lineEditParsrMySQLDBAddress.text() != '' and
                  self.ui.lineEditParsrMySQLDBName.text() != '' and self.ui.lineEditParsrMySQLUsername.text() != '' and
                  self.ui.lineEditParsrMySQLPassword.text() != '')):
            self.ui.pushButtonParserStart.setEnabled(True)
        else:
            self.ui.pushButtonParserStart.setEnabled(False)

    # tab2功能
    def disable_all_tab2(self):
        self.ui.radioButtonMySQL.setEnabled(False)
        self.ui.radioButtonSQLite.setEnabled(False)
        self.ui.radioButtonPlaintext.setEnabled(False)
        self.ui.radioButtonXML.setEnabled(False)
        self.ui.radioButtonBibtex.setEnabled(False)
        self.ui.lineEditParsrInputPath.setEnabled(False)
        self.ui.lineEditParsrSQLiteOutput.setEnabled(False)
        self.ui.lineEditParsrMySQLPassword.setEnabled(False)
        self.ui.lineEditParsrMySQLUsername.setEnabled(False)
        self.ui.lineEditParsrMySQLDBName.setEnabled(False)
        self.ui.lineEditParsrMySQLDBAddress.setEnabled(False)
        self.ui.pushButtonParserSQLiteOutput.setEnabled(False)
        self.ui.pushButtonParserInput.setEnabled(False)
        self.ui.pushButtonParserStart.setEnabled(False)

    # tab2功能
    def reset_default(self):
        self.ui.radioButtonPlaintext.setEnabled(True)
        self.ui.radioButtonBibtex.setEnabled(True)
        self.ui.radioButtonXML.setEnabled(True)
        self.ui.radioButtonSQLite.setEnabled(True)
        self.ui.radioButtonMySQL.setEnabled(True)
        self.ui.lineEditParsrInputPath.setEnabled(True)
        self.ui.pushButtonParserInput.setEnabled(True)

        if self.ui.radioButtonSQLite.isChecked():
            self.ui.lineEditParsrSQLiteOutput.setEnabled(True)
            self.ui.pushButtonParserSQLiteOutput.setEnabled(True)
        else:
            self.ui.lineEditParsrMySQLDBAddress.setEnabled(True)
            self.ui.lineEditParsrMySQLDBName.setEnabled(True)
            self.ui.lineEditParsrMySQLUsername.setEnabled(True)
            self.ui.lineEditParsrMySQLPassword.setEnabled(True)

        self.ui.pushButtonParserStart.setEnabled(True)

    # tab2功能
    def start_parser(self):
        self.disable_all_tab2()
        timestamp = str(time.strftime('%Y-%m-%d-%H.%M.%S', time.localtime(time.time())))

        input_path = self.ui.lineEditParsrInputPath.text()
        print('待解析文件路径：{}'.format(input_path))

        if self.ui.radioButtonPlaintext.isChecked():
            file_format = 'Plaintext'
            parser = parsers.plaintext.wos.plaintext_parser
        elif self.ui.radioButtonBibtex.isChecked():
            file_format = 'Bibtex'
            parser = parsers.bibtex.wos.bibtex_parser
        else:
            file_format = 'XML'
            parser = parsers.xml.wos.xml_parser_v3
        print('待解析文件格式：{}'.format(file_format))

        if self.ui.radioButtonSQLite.isChecked():
            output_path = self.ui.lineEditParsrSQLiteOutput.text() + r'\{}-result.db'.format(timestamp)
            print('SQLite输出路径为：{}'.format(output_path))
            print('开始解析……')
            parser.parse(input_dir=input_path, db_path=output_path)
        else:
            db_address = self.ui.lineEditParsrMySQLDBAddress.text()
            db_name = self.ui.lineEditParsrMySQLDBName.text()
            db_username = self.ui.lineEditParsrMySQLUsername.text()
            db_password = self.ui.lineEditParsrMySQLPassword.text()

            mysql_url = 'mysql+pymysql://{}:{}@{}:3306/{}?charset=utf8' \
                .format(db_username, db_password, db_address, db_name)

            print('MySQL连接信息：{}'.format(mysql_url))
            print('开始解析……')
            parser.parse(input_dir=input_path, db_url=mysql_url)

        print('解析完成！')
        self.reset_default()

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
