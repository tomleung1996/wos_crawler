import bibtexparser
from bibtexparser.bparser import BibTexParser
from parsers.bibtex.wos.customization import *
from model import get_engine, get_session
from model.wos_document import *
import os


def customizations(document):
    document = author(document)
    document = author_affiliation_v2(document)
    document = wos_category(document)
    document = research_area(document)
    document = keyword(document)
    document = keyword_plus(document)
    document = reference(document)
    document = funding(document)
    return document


def parse_single(input_file=None, db_path=None, db_url=None):
    assert input_file is not None and (db_path is not None or db_url is not None)

    print('正在解析{}……'.format(input_file))

    bibtex_filename = input_file

    with open(bibtex_filename, 'r', encoding='utf-8') as file:
        parser = BibTexParser()
        parser.customization = customizations
        bib_db = bibtexparser.load(file, parser=parser)

    # print(len(bib_db.entries))
    # exit(-1)

    # for k,v in bib_db.entries[0].items():
    #     print(k,v)
    #     print('======\n')
    # exit(0)

    # if len(bib_db.entries) != 500:
    #     exit(-1)

    engine = get_engine(db_path, db_url)
    Base.metadata.create_all(engine)
    session = get_session(engine)

    for i in range(len(bib_db.entries)):
        author_list = []
        category_list = []
        area_list = []
        keyword_list = []
        keyword_plus_list = []
        reference_list = []
        funding_list = []

        # 解析文章基本信息 wos_document表的信息
        try:
            wos_document = WosDocument(bib_db.entries[i]['unique-id'][5:-1].lower()
                                       if 'unique-id' in bib_db.entries[i] else None,
                                       bib_db.entries[i]['title'][1:-1].lower().replace('\n', ' ').replace('\\', '')
                                       if 'title' in bib_db.entries[i] else None,
                                       bib_db.entries[i]['abstract'][1:-1].lower().replace('\n', ' ').replace('\\', '')
                                       if 'abstract' in bib_db.entries[i] else None,
                                       bib_db.entries[i]['journal'][1:-1].lower().replace('\\', '')
                                       if 'journal' in bib_db.entries[i] else
                                       bib_db.entries[i]['booktitle'][1:-1].lower().replace('\n', ' ').replace('\\', '')
                                       if 'booktitle' in bib_db.entries[i] else None,
                                       bib_db.entries[i]['journal-iso'][1:-1].lower().replace('\\', '')
                                       if 'journal-iso' in bib_db.entries[i] else None,
                                       # bibtex格式不存在29字符格式的期刊缩写
                                       None,
                                       bib_db.entries[i]['publisher'][1:-1].lower().replace('\\', '')
                                       if 'publisher' in bib_db.entries[i] else None,
                                       bib_db.entries[i]['volume'][1:-1].lower()
                                       if 'volume' in bib_db.entries[i] else None,
                                       bib_db.entries[i]['number'][1:-1].lower()
                                       if 'number' in bib_db.entries[i] else None,
                                       bib_db.entries[i]['pages'][1:-1].lower().split('-')[0]
                                       if 'pages' in bib_db.entries[i] and len(bib_db.entries[i]['pages'][1:-1].lower().split('-')) > 1 else
                                       bib_db.entries[i]['pages'][1:-1].lower().split('+')[0]
                                       if 'pages' in bib_db.entries[i] else None,
                                       bib_db.entries[i]['pages'][1:-1].lower().split('-')[1]
                                       if 'pages' in bib_db.entries[i] and len(bib_db.entries[i]['pages'][1:-1].lower().split('-')) > 1 else
                                       '+' if 'pages' in bib_db.entries[i] else None,
                                       bib_db.entries[i]['year'][1:-1].lower()
                                       if 'year' in bib_db.entries[i] else None,
                                       bib_db.entries[i]['month'][1:-1].lower()
                                       if 'month' in bib_db.entries[i] else None,
                                       bib_db.entries[i]['type'][1:-1].lower()
                                       if 'type' in bib_db.entries[i] else None,
                                       bib_db.entries[i]['doi'][1:-1].lower()
                                       if 'doi' in bib_db.entries[i] else None,
                                       bib_db.entries[i]['times-cited'][1:-1].lower()
                                       if 'times-cited' in bib_db.entries[i] else None,
                                       bib_db.entries[i]['number-of-cited-references'][1:-1].lower()
                                       if 'number-of-cited-references' in bib_db.entries[i] else None,
                                       bib_db.entries[i]['usage-count-last-180-days'][1:-1].lower()
                                       if 'usage-count-last-180-days' in bib_db.entries[i] else None,
                                       bib_db.entries[i]['usage-count-since-2013'][1:-1].lower()
                                       if 'usage-count-since-2013' in bib_db.entries[i] else None,
                                       bib_db.entries[i]['funding-text'][1:-1].lower().replace('\n', ' ').replace('\\','')
                                       if 'funding-text' in bib_db.entries[i] else None,
                                       bib_db.entries[i]['language'][1:-1].lower()
                                       if 'language' in bib_db.entries[i] else None,
                                       bib_db.entries[i]['author-email'][1:-1].lower().replace('\n', ';').replace('\\','')
                                       if 'author-email' in bib_db.entries[i] else None)
        except Exception as e:
            print(bib_db.entries[i])
            print('该行出现故障', e)
            exit(-1)
        # TODO: 暂时把格式错误的文章删去
        if wos_document.unique_id is None:
            print('{} 文件存在格式不正确的记录，已跳过该记录'.format(input_file))
            continue

        # 解析作者及机构的信息
        if bib_db.entries[i]['affiliation'] is not None:
            for author_info, addresses in bib_db.entries[i]['affiliation'].items():

                affiliation_list = []
                # bibtex格式无法找到规范缩写
                author = WosAuthor(author_info[0], author_info[1], None,author_info[2], author_info[3])
                session.add(author)
                session.flush()

                if addresses is None:
                    no_affiliation = WosAffiliation(None)
                    affiliation_list.append(no_affiliation)
                else:
                    for address in addresses:
                        affiliation = WosAffiliation(address)
                        affiliation_list.append(affiliation)

                author.affiliations = affiliation_list

                author_list.append(author)
            wos_document.authors = author_list

        # 解析WoS分类信息
        if bib_db.entries[i]['web-of-science-categories'] is not None:
            for category in bib_db.entries[i]['web-of-science-categories']:
                cat = WosCategory(category)
                category_list.append(cat)
            wos_document.categories = category_list

        # 解析研究领域信息
        if bib_db.entries[i]['research-areas'] is not None:
            for area in bib_db.entries[i]['research-areas']:
                a = WosResearchArea(area)
                area_list.append(a)
            wos_document.research_areas = area_list

        # 解析作者关键词
        if bib_db.entries[i]['keywords'] is not None:
            for keyword in bib_db.entries[i]['keywords']:
                key = WosKeyword(keyword)
                keyword_list.append(key)
            wos_document.keywords = keyword_list

        # 解析WoS KeywordPlus
        if bib_db.entries[i]['keywords-plus'] is not None:
            for keyword_plus in bib_db.entries[i]['keywords-plus']:
                kp = WosKeywordPlus(keyword_plus)
                keyword_plus_list.append(kp)
            wos_document.keyword_plus = keyword_plus_list

        # 解析基金信息
        if bib_db.entries[i]['funding-acknowledgement'] is not None:
            for agent, numbers in bib_db.entries[i]['funding-acknowledgement'].items():
                for number in numbers:
                    fund = WosFunding(agent, number)
                    funding_list.append(fund)
            wos_document.fundings = funding_list

        # 解析参考文献信息
        if bib_db.entries[i]['cited-references'] is not None:
            for reference in bib_db.entries[i]['cited-references']:
                ref = WosReference(reference[0].replace('.','').replace('. ','').replace(',',''),
                                   reference[1], reference[2], reference[3], reference[4], reference[5])
                reference_list.append(ref)
            wos_document.references = reference_list

        session.add(wos_document)

    print('解析{}完成，正在插入……'.format(input_file))

    session.commit()
    session.close()

    print('插入{}完成\n'.format(input_file))


def parse(input_dir=None, db_path=None, db_url=None):
    assert input_dir is not None and (db_path is not None or db_url is not None)

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file[-4:] == '.bib':
                parse_single(os.path.join(root, file), db_path, db_url)

    print('全部解析完成')


if __name__ == '__main__':
    parse(r'C:\Users\Tom\PycharmProjects\wos_crawler\output\advanced_query\2019-01-31-10.32.08',
          'C:/Users/Tom/Desktop/test.db')
