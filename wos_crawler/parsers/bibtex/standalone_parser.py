import bibtexparser
from bibtexparser.bparser import BibTexParser
from parsers.bibtex.customization import *
from model import Base, engine, loadSession
from model.wos_document import *


def customizations(document):
    document = author(document)
    document = author_affiliation_v2(document)
    document = wos_category(document)
    document = keyword(document)
    document = keyword_plus(document)
    document = reference(document)
    return document


def run():
    bibtex_filename = r'C:\Users\Tom\PycharmProjects\wos_crawler\input\1501-2000.bib'

    with open(bibtex_filename, 'r', encoding='utf-8') as file:
        parser = BibTexParser()
        parser.customization = customizations
        bib_db = bibtexparser.load(file, parser=parser)

    Base.metadata.create_all(engine)
    session = loadSession()

    for i in range(len(bib_db.entries)):
        author_list = []
        category_list = []
        keyword_list = []
        keyword_plus_list = []
        reference_list = []

        # 解析文章基本信息 wos_document表的信息
        wos_document = WosDocument(bib_db.entries[i]['unique-id'][1:-1].lower()
                                   if 'unique-id' in bib_db.entries[i] else None,
                                   bib_db.entries[i]['title'][1:-1].lower().replace('\\', '')
                                   if 'title' in bib_db.entries[i] else None,
                                   bib_db.entries[i]['abstract'][1:-1].lower().replace('\n', ' ').replace('\\', '')
                                   if 'abstract' in bib_db.entries[i] else None,
                                   bib_db.entries[i]['journal'][1:-1].lower().replace('\\', '')
                                   if 'journal' in bib_db.entries[i] else None,
                                   bib_db.entries[i]['publisher'][1:-1].lower().replace('\\', '')
                                   if 'publisher' in bib_db.entries[i] else None,
                                   bib_db.entries[i]['volume'][1:-1].lower()
                                   if 'volume' in bib_db.entries[i] else None,
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
                                   bib_db.entries[i]['funding-acknowledgement'][1:-1].lower().replace('\n',
                                                                                                      ' ').replace('\\',
                                                                                                                   '')
                                   if 'funding-acknowledgement' in bib_db.entries[i] else None,
                                   bib_db.entries[i]['funding-text'][1:-1].lower().replace('\n', ' ').replace('\\', '')
                                   if 'funding-text' in bib_db.entries[i] else None,
                                   bib_db.entries[i]['language'][1:-1].lower()
                                   if 'language' in bib_db.entries[i] else None,
                                   bib_db.entries[i]['author-email'][1:-1].lower().replace('\n', ';').replace('\\', '')
                                   if 'author-email' in bib_db.entries[i] else None)

        # 解析作者及机构的信息
        for author_info, addresses in bib_db.entries[i]['affiliation'].items():

            affiliation_list = []
            author = WosAuthor(author_info[0], author_info[1], author_info[2], author_info[3])
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
        for category in bib_db.entries[i]['web-of-science-categories']:
            cat = WosCategory(category)
            category_list.append(cat)
        wos_document.categories = category_list

        # 解析作者关键词
        for keyword in bib_db.entries[i]['keywords']:
            key = WosKeyword(keyword)
            keyword_list.append(key)
        wos_document.keywords = keyword_list

        # 解析WoS KeywordPlus
        for keyword_plus in bib_db.entries[i]['keywords-plus']:
            kp = WosKeywordPlus(keyword_plus)
            keyword_plus_list.append(kp)
        wos_document.keyword_plus = keyword_plus_list

        session.add(wos_document)
    session.commit()
    session.close()


if __name__ == '__main__':
    run()
