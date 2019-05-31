from model import get_engine, get_session
from model.wos_document import *
import xml.etree.ElementTree as ET
import os


def parse_single(input_file=None, db_path=None, db_url=None):
    assert input_file is not None and (db_path is not None or db_url is not None)


    engine = get_engine(db_path, db_url)
    Base.metadata.create_all(engine)
    session = get_session(engine)

    print('正在解析{}……'.format(input_file))

    # TODO:被引数、利用数等实时指标在官方导出的格式里面没有。作者邮箱因为太过详细暂时不解析

    # 用ElementTree读取XML文件，其中root标签是records
    # 因为WOS的XML文件带有name_space，在查找节点时需要加进去
    tree = ET.parse(input_file)
    records = tree.getroot()
    name_space = records.tag[:records.tag.index('}')+1]
    wos_document_list = []

    for record in records:
        wos_document = WosDocument()

        wos_document.unique_id = get_unique_id(name_space, record)
        wos_document.title = get_title(name_space, record)
        wos_document.abs = get_abs(name_space, record)
        wos_document.journal = get_journal(name_space, record)
        wos_document.journal_iso = get_journal_iso(name_space, record)
        wos_document.journal_29 = get_journal_29(name_space, record)
        wos_document.publisher = get_publisher(name_space, record)
        wos_document.volume = get_volume(name_space, record)
        wos_document.issue = get_issue(name_space, record)
        wos_document.start_page = get_start_page(name_space, record)
        wos_document.end_page = get_end_page(name_space, record)
        wos_document.pub_year = get_pub_year(name_space, record)
        wos_document.pub_month_day = get_pub_month_day(name_space, record)
        wos_document.document_type = get_document_type(name_space, record)
        wos_document.doi = get_doi(name_space, record)
        wos_document.reference_num = get_reference_num(name_space, record)
        wos_document.funding_text = get_funding_text(name_space, record)
        wos_document.language = get_language(name_space, record)

        # print(wos_document)

        authors = record.find('./{0}static_data/{0}summary/{0}names'.format(name_space))
        wos_document.authors = get_authors(name_space, authors, record)

        # print(wos_document.authors)

        references = record.find('./{0}static_data/{0}fullrecord_metadata/{0}references'.format(name_space))
        wos_document.references = get_references(name_space, references)
        # print(wos_document.references)

        categories = record.findall('./{0}static_data/{0}fullrecord_metadata/{0}category_info/{0}subjects/{0}subject[@ascatype="traditional"]'.format(name_space))
        wos_document.categories = get_categories(name_space, categories)
        # print(wos_document.categories)

        areas = record.findall('./{0}static_data/{0}fullrecord_metadata/{0}category_info/{0}subjects/{0}subject[@ascatype="extended"]'.format(name_space))
        wos_document.research_areas = get_research_areas(name_space, areas)
        # print(wos_document.research_areas)

        keywords = record.find('./{0}static_data/{0}fullrecord_metadata/{0}keywords'.format(name_space))
        wos_document.keywords = get_keywords(name_space, keywords)
        # print(wos_document.keywords)

        keyword_plus = record.find('./{0}static_data/{0}item/{0}keywords_plus'.format(name_space))
        wos_document.keyword_plus = get_keyword_plus(name_space, keyword_plus)
        # print(wos_document.keyword_plus)

        fundings = record.find('./{0}static_data/{0}fullrecord_metadata/{0}fund_ack/{0}grants'.format(name_space))
        wos_document.fundings = get_fundings(name_space, fundings)
        # print(wos_document.fundings)

        wos_document_list.append(wos_document)

        # 及时写入清空队列
        if len(wos_document_list) > 499:
            print('缓存队列达到阈值，正在写入数据库……')
            session.add_all(wos_document_list)
            session.commit()
            wos_document_list.clear()
        # print()

    print('解析{}完成，正在写入数据库……'.format(input_file))
    session.add_all(wos_document_list)
    session.commit()
    session.close()
    print('插入{}完成\n'.format(input_file))


def get_unique_id(name_space, record):
    # 找到UID
    try:
        return record.find(name_space+'UID').text[4:].lower()
    except:
        return None

def get_title(name_space, record):
    # 找到标题
    try:
        return record.find('./{0}static_data/{0}summary/{0}titles/{0}title[@type="item"]'.format(name_space)).text.lower()
    except:
        return None

def get_abs(name_space, record):
    # 找到摘要
    try:
        return record.find('./{0}static_data/{0}fullrecord_metadata/{0}abstracts/{0}abstract/{0}abstract_text/{0}p'.format(name_space)).text.lower()
    except:
        return None

def get_journal(name_space, record):
    # 找到期刊
    try:
        return record.find('./{0}static_data/{0}summary/{0}titles/{0}title[@type="source"]'.format(name_space)).text.lower()
    except:
        return None

def get_journal_iso(name_space, record):
    # 找到期刊ISO缩写
    try:
        return record.find('./{0}static_data/{0}summary/{0}titles/{0}title[@type="abbrev_iso"]'.format(name_space)).text.lower()
    except:
        return None

def get_journal_29(record):
    # 找到期刊29字符缩写
    try:
        return record.find('./static_data/summary/titles/title[@type="abbrev_29"]').text.lower()
    except:
        return None

def get_publisher(name_space, record):
    # 找到出版商
    try:
        return record.find('./{0}static_data/{0}summary/{0}publishers/{0}publisher/{0}names/{0}name/{0}full_name'.format(name_space)).text.lower()
    except:
        return None

def get_volume(name_space, record):
    # 找到卷号
    try:
        return record.find('./{0}static_data/{0}summary/{0}pub_info'.format(name_space)).attrib['vol'].lower()
    except:
        return None

def get_issue(name_space, record):
    # 找到期号
    try:
        return record.find('./{0}static_data/{0}summary/{0}pub_info'.format(name_space)).attrib['issue'].lower()
    except:
        return None

def get_start_page(name_space, record):
    # 找到开始页码
    try:
        return record.find('./{0}static_data/{0}summary/{0}pub_info/{0}page'.format(name_space)).attrib['begin'].lower()
    except:
        return None

def get_end_page(name_space, record):
    # 找到结束页码
    try:
        return record.find('./{0}static_data/{0}summary/{0}pub_info/{0}page'.format(name_space)).attrib['end'].lower()
    except:
        return None

def get_pub_year(name_space, record):
    # 找到年份
    try:
        return record.find('./{0}static_data/{0}summary/{0}pub_info'.format(name_space)).attrib['pubyear'].lower()
    except:
        return None

def get_pub_month_day(name_space, record):
    # 找到月份
    try:
        return record.find('./{0}static_data/{0}summary/{0}pub_info'.format(name_space)).attrib['pubmonth'].lower()
    except:
        return None

def get_document_type(name_space, record):
    # 找到文档类型
    try:
        return record.find('./{0}static_data/{0}summary/{0}doctypes/{0}doctype'.format(name_space)).text.lower()
    except:
        return None

def get_doi(name_space, record):
    # 找到DOI
    try:
        return record.find('./{0}dynamic_data/{0}cluster_related/{0}identifiers/{0}identifier[@type="doi"]'.format(name_space)).attrib['value'].lower()
    except:
        return None

def get_reference_num(name_space, record):
    # 找到参考文献数量
    try:
        return record.find('./{0}static_data/{0}fullrecord_metadata/{0}references'.format(name_space)).attrib['count'].lower()
    except:
        return None

def get_funding_text(name_space, record):
    # 找到基金文本
    try:
        return record.find('./{0}static_data/{0}fullrecord_metadata/{0}fund_ack/{0}fund_text/{0}p'.format(name_space)).text.lower()
    except:
        return None

def get_language(name_space, record):
    # 找到语言
    try:
        return record.find('./{0}static_data/{0}fullrecord_metadata/{0}languages/{0}language'.format(name_space)).text.lower()
    except:
        return None

def get_authors(name_space, authors, record):
    author_list = []
    author_dict = {}
    if authors is not None:
        for author in authors:
            author_order = author.attrib['seq_no']
            is_reprint = 0
            try:
                # 判断是否为通讯作者
                author.attrib['reprint']
                is_reprint = 1
            except:
                pass

            try:
                # 有可能出现空作者（WoS的失误）
                full_name = author.find('./{}full_name'.format(name_space)).text.lower()
            except:
                continue

            try:
                first_name = author.find('./{}first_name'.format(name_space)).text.lower()
                last_name = author.find('./{}last_name'.format(name_space)).text.lower()
                abbr_name = author.find('./{}wos_standard'.format(name_space)).text.lower().replace(',','')

            except:
                # 团体作者只有fullname
                first_name = None
                last_name = full_name
                abbr_name = full_name

            wos_author = WosAuthor(first_name, last_name, abbr_name,author_order, is_reprint)
            author_dict[full_name] = wos_author

    if len(author_dict) > 0:
        addresses = record.find('./{0}static_data/{0}fullrecord_metadata/{0}addresses'.format(name_space))
        author_dict = get_affiliations(name_space, addresses, author_dict)
        author_list = list(author_dict.values())

    return author_list

def get_references(name_space, references):
    reference_list = []
    if references is not None:
        for reference in references:
            first_author = reference.find('./{}citedAuthor'.format(name_space))
            pub_year = reference.find('./{}year'.format(name_space))
            journal = reference.find('./{}citedWork'.format(name_space))
            volume = reference.find('./{}volume'.format(name_space))
            start_page = reference.find('./{}page'.format(name_space))
            doi = reference.find('./{}doi'.format(name_space))

            if first_author is not None:
                if first_author.text is not None:
                    first_author = first_author.text.replace(',', '').lower()
                else:
                    first_author = None
            else:
                first_author = '[anonymous]'
            if pub_year is not None:
                if pub_year.text is not None:
                    pub_year = pub_year.text.lower()
                    if len(pub_year) > 4:
                        pub_year = pub_year[:4]
                else:
                    pub_year = None
            if journal is not None:
                if journal.text is not None:
                    journal = journal.text.replace('.', '').lower()
                    if len(journal) > 254:
                        journal = journal[:254]
                else:
                    journal = None
            if volume is not None:
                if volume.text is not None:
                    volume = volume.text.lower()
                else:
                    volume = None
            if start_page is not None:
                if start_page.text is not None:
                    start_page = start_page.text.lower()
                else:
                    start_page = None
            if doi is not None:
                if doi.text is not None:
                    doi = doi.text.lower()
                else:
                    doi = None

            wos_reference = WosReference(first_author, pub_year, journal, volume, start_page, doi)
            reference_list.append(wos_reference)

    return reference_list

def get_categories(name_space, categories):
    category_list = []
    if categories is not None:
        for category in categories:
            wos_category = WosCategory(category.text.lower())
            category_list.append(wos_category)
    return category_list

def get_research_areas(name_space, areas):
    areas_list = []
    if areas is not None:
        for area in areas:
            wos_area = WosResearchArea(area.text.lower())
            areas_list.append(wos_area)
    return areas_list

def get_keywords(name_space, keywords):
    keyword_list = []
    if keywords is not None:
        for keyword in keywords:
            wos_keyword = WosKeyword(keyword.text.lower())
            keyword_list.append(wos_keyword)
    return keyword_list

def get_keyword_plus(name_space, keyword_plus):
    kp_list = []
    if keyword_plus is not None:
        for kp in keyword_plus:
            wos_kp = WosKeywordPlus(kp.text.lower())
            kp_list.append(wos_kp)
    return kp_list

def get_affiliations(name_space, addresses, author_dict):
    for address in addresses:
        address_name = address.find('./{0}address_spec/{0}full_address'.format(name_space)).text.lower()
        related_authors = address.find('./{0}names'.format(name_space))

        if related_authors is None:
            # print('地址{}没有对应作者，已抛弃'.format(address_name))
            continue

        for related_author in related_authors:
            full_name = related_author.find('./{0}full_name'.format(name_space)).text.lower()

            wos_affiliation = WosAffiliation(address_name)
            wos_affiliation.author = author_dict[full_name]

    return author_dict

def get_fundings(name_space, fundings):
    funding_list = []
    if fundings is not None:
        for funding in fundings:
            agent = None
            try:
                # 有可能基金只有一个编号没有机构
                agent = funding.find('./{0}grant_agency'.format(name_space)).text.lower()
            except:
                pass
            numbers = funding.find('./{0}grant_ids'.format(name_space))
            if numbers is not None:
                for number in numbers:
                    wos_funding = WosFunding(agent, number.text.lower())
                    funding_list.append(wos_funding)
            else:
                wos_funding = WosFunding(agent, None)
                funding_list.append(wos_funding)
    return funding_list


def parse(input_dir=None, db_path=None, db_url=None):
    assert input_dir is not None and (db_path is not None or db_url is not None)

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file[-4:] == '.xml':
                parse_single(os.path.join(root, file), db_path, db_url)

    print('全部解析完成')


if __name__ == '__main__':
    parse(input_dir=r'C:\Users\Tom\Desktop\test\3',
          db_url='mysql+pymysql://root:root@localhost/contest')
