# Web of Science 爬虫 / Web of Science Crawler
一个导出Web of Science题录数据的爬虫，支持以下两种方式：

- 给定所需的期刊名称列表，下载列表中所有期刊上的Article类型的文献
- 给定合法的WoS高级检索式，下载检索式得到的Article类型的结果
- PS:（因为WoS本身的限制，单个检索式超过10万个结果的话，10万条后面的结果无法导出，请通过年份限定的方式修改检索式进行分别爬取）

A crawler that downloads bibliographic data from Web of Science, given:

- A list of the desired journals' names, the crawler will download all bibliographic data of the articles (DocumentType = Article) in these journals.
- Or a legal Web of Science advanced query, the crawler will download the bibliographic data of the query result.
- PS: (Due to restrictions of Web of Science, users can only export the first 100K records, so if your query returns more than 100K results, please add a time constraint on it to split your query into serval parts. eg: add "PY=(year1-year2)")

## 使用方法 / Usage

给定期刊列表 / Given a list of journals' name


- 将你的期刊列表放到`input`文件夹中，命名为`journal_list.txt`， 取消`main.py`文件中`cmdline.execute('scrapy crawl wos_journal_spider'.split())`的注释，运行`main.py`


- Put your list of journals' name into the `input` folder and rename it to `journal_list.txt`, then uncomment `cmdline.execute('scrapy crawl wos_journal_spider'.split())` in `main.py`, run it.


给定高级检索式 / Given a advanced query

- 将你的检索式替换掉`spiders/wos_advanced_query_spider.py`第22行`query`后的内容，取消`main.py`文件中`cmdline.execute('scrapy crawl wos_advanced_query_spider'.split())`的注释，运行`main.py`

- Replace the content of `query` in `spiders/wos_advanced_query_spider.py`(line 22) by your own advanced query, then uncomment `cmdline.execute('scrapy crawl wos_advanced_query_spider'.split())` in `main.py`, run it.

## 输出格式 / Output format

输出格式为WoS导出的纯文本（全部字段，包含参考文献），保存于`output`文件夹。

- 如果使用的是期刊列表进行爬取，则输出文件存放的方式为每个期刊一个独立文件夹
- 如果使用的是高级检索式进行爬取，则输出文件的存放文件夹命名为爬虫启动的时间

The output format is WoS Plain Text, the same as the file you manually download from Web of Science. The files are stored in the `output` folder.

- If you run the crawler in the journal list mode, each journal will have its own folder
- If you run the crawler in the advanced query mode, the result folder will be named by current time.

