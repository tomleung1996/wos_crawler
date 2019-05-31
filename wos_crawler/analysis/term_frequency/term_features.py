from model import get_engine, get_session
from model.wos_document import *
from sqlalchemy import MetaData, Table
from sqlalchemy.sql import select, asc
import csv
import re
import numpy as np


def term_feature_extraction(db_path=None, db_url=None, output_path=''):
    assert (db_path is None and db_url is not None) or (db_path is not None and db_url is None)
    assert output_path is not None

    if db_path:
        engine = get_engine(db_path=db_path)
    else:
        engine = get_engine(db_url=db_url)

    meta = MetaData(engine)
    con = engine.connect()
    session = get_session(engine)
    term_table = Table('terms', meta, autoload=True)

    dataframe = []
    abbr = {}

    query_terms = select([term_table.c.tid, term_table.c.term, term_table.c.term2]).where(
        term_table.c.tid > 9281).order_by(asc(term_table.c.tid))
    result = con.execute(query_terms)
    terms = list(result)
    result.close()

    # with open('terms.csv', mode='w', encoding='utf-8') as _:
    #     _.write('"' + '","'.join(
    #         ['term', 'year', 'document_count', 'document_increment_ratio', 'author_count', 'citation_count',
    #          'funding_count',
    #          'reference_count', 'acc_document_count', 'acc_author_count', 'acc_citation_count',
    #          'acc_funding_count', 'acc_reference_count']) + '"\n')

    with open(r'abbreviations.txt', mode='r', encoding='utf-8') as abbr_file:
        for line in abbr_file:
            line_split = line.strip().split('\t')
            abbr[line_split[2].lower()] = line_split[1].lower()

    for term in terms:
        if len(term[1]) < 6:
            new_term = abbr.get(term[1], term[1])
        else:
            new_term = term[1]
        print(term[0], ':', new_term)

        acc_document_count = 0
        acc_author_count = 0
        acc_reference_count = 0
        acc_funding_count = 0
        acc_citation_count = 0

        last_document_count = 0

        for year in range(2003, 2013):
            document_count = 0
            author_count = 0
            reference_count = 0
            funding_count = 0
            citation_count = 0

            documents = session.query(WosDocument).filter(WosDocument.pub_year == year).all()
            for document in documents:
                keyword_plus = ', '.join(
                    [kp.keyword_plus for kp in document.keyword_plus]) if document.keyword_plus else ''
                keyword = ', '.join([kw.keyword for kw in document.keywords]) if document.keywords else ''
                title = document.title if document.title else ''
                abstract = document.abs if document.abs else ''
                string = ' '.join([keyword_plus, keyword, title, abstract])

                term_pattern = re.compile(r'\b{}s*\b'.format(re.escape(new_term)))
                if term[2]:
                    term2_pattern = re.compile(r'\b{}s*\b'.format(re.escape(term[2])))
                else:
                    term2_pattern = re.compile(r'nothing')
                if term_pattern.search(string) or term2_pattern.search(string):
                    # if new_term in keyword_plus or new_term in keyword or new_term in title or new_term in abstract:
                    document_count += 1
                    author_count += len(document.authors)
                    reference_count += len(document.references)
                    funding_count += len(document.fundings)
                    citation_count += document.cited_times

            acc_document_count += document_count
            acc_author_count += author_count
            acc_reference_count += reference_count
            acc_funding_count += funding_count
            acc_citation_count += citation_count
            document_increment_ratio = (document_count / last_document_count) if last_document_count != 0 else 0
            last_document_count = document_count

            # dataframe.append((new_term, year, document_count,document_increment_ratio, author_count, citation_count, funding_count,
            #                   reference_count, acc_document_count, acc_author_count, acc_citation_count, acc_funding_count, acc_reference_count))

            with open('terms.csv', mode='a', encoding='utf-8') as file:
                file.write('"' + '","'.join(map(str,
                                                [new_term, year, document_count, document_increment_ratio, author_count,
                                                 citation_count, funding_count,
                                                 reference_count, acc_document_count, acc_author_count,
                                                 acc_citation_count, acc_funding_count, acc_reference_count])) + '"\n')

    # df = pd.DataFrame(dataframe, columns=['term','year','document_count','document_increment_ratio','author_count', 'citation_count','funding_count',
    #                                     'reference_count','acc_document_count','acc_author_count','acc_citation_count',
    #                                     'acc_funding_count','acc_reference_count'])
    # df.to_csv('terms.csv', index=None)

    session.close()
    con.close()


def score_calculation(input_path=None, output_path=None):
    assert input_path is not None and output_path is not None

    mean_dict = {
        2000: 0.118055,
        2001: 0.118055,
        2002: 0.118055,
        2003: 0.118055,
        2004: 0.152416,
        2005: 0.132724,
        2006: 0.744399,
        2007: 0.162363,
        2008: 0.747614,
        2009: 0.200141,
        2010: 0.233296,
        2011: 0.267959,
        2012: 0.916608
    }

    with open(input_path, mode='r', encoding='utf-8') as instream, \
            open(output_path, mode='w', encoding='utf-8') as outstream:

        outstream.write(
            '"term","year","score","document_growth","document_count","document_increment_ratio","author_count","citation_count",'
            '"funding_count","reference_count","acc_document_count","acc_author_count","acc_citation_count",'
            '"acc_funding_count","acc_reference_count"\n')

        lines = csv.reader(instream)
        last_term = None
        last_1_df = 0
        last_2_df = 0
        last_3_df = 0

        for line in lines:
            if line[0] != last_term:
                last_term = line[0]
                cur_df = int(line[2])
                last_1_df = 0
                last_2_df = 0
                last_3_df = 0
                cur_mean = mean_dict[int(line[1])]
                last_1_mean = mean_dict[int(line[1])-1]
                last_2_mean = mean_dict[int(line[1])-2]
                last_3_mean = mean_dict[int(line[1])-3]

                # score = np.log2((cur_df + last_1_df) if (cur_df + last_1_df) > 0 else 1) * ((cur_df + last_1_df + 2 * cur_mean) / (last_2_df + last_3_df + 2 * cur_mean))
                score = np.log(last_2_df + last_3_df + 1) * \
                        ((cur_df + last_1_df + 1) / (last_2_df + last_3_df + 1))
                growth = (cur_df + last_1_df + 1) / (last_2_df + last_3_df + 1)
                last_1_df = cur_df
            else:
                cur_mean = mean_dict[int(line[1])]
                cur_df = int(line[2])
                last_1_mean = mean_dict[int(line[1]) - 1]
                last_2_mean = mean_dict[int(line[1]) - 2]
                last_3_mean = mean_dict[int(line[1]) - 3]

                # if line[0] == 'cell-free' and (line[1] == '2012' or line[1] == '2011'):
                #     print(cur_mean, cur_df, last_1_df, last_2_df, last_3_df)

                score = np.log(last_2_df + last_3_df + 1) * \
                        ((cur_df + last_1_df + 1) / (last_2_df + last_3_df + 1))
                growth = (cur_df + last_1_df + 1) / (last_2_df + last_3_df + 1)
                last_3_df = last_2_df
                last_2_df = last_1_df
                last_1_df = cur_df



            result = line[:]
            result.insert(2, str(score))
            result.insert(3, str(growth))
            outstream.write('"' + '","'.join(result) + '"\n')


if __name__ == '__main__':
    # term_feature_extraction(db_url='mysql+pymysql://root:root@localhost/contest?charset=utf8')
    score_calculation(
        input_path=r'C:\Users\Tom\PycharmProjects\wos_crawler\wos_crawler\analysis\term_frequency\terms.csv',
        output_path=r'escore_0.5_new.csv')
