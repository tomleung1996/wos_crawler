from model import get_engine, get_session
from model.wos_document import *
from sqlalchemy import MetaData, Table

def get_split_title_keyword_abstract(db_path=None, db_url=None, output_path='', foreground=False):
    assert (db_path is None and db_url is not None) or (db_path is not None and db_url is None)
    assert output_path is not None

    if db_path:
        engine = get_engine(db_path=db_path)
    else:
        engine = get_engine(db_url=db_url)
    session = get_session(engine)

    data = session.query(WosDocument).all()
    path = r'C:/Users/Tom/Desktop/bio_nature'
    if foreground:
        inner_path = path + '/foreground'
    else:
        inner_path = path + '/background'

    for document in data:
        title = document.title.strip() +'.'

        kw_str = ''
        # kw_str = ', '.join(document.keywords)
        for kw in document.keywords:
            kw_str += kw.keyword + '. '
        # kw_str = kw_str[:-2]

        kp_str = ''
        # kp_str = ', '.join(document.keyword_plus)
        for kp in document.keyword_plus:
            kp_str += kp.keyword_plus + '. '
        # kp_str = kp_str[:-2]

        if document.abs:
            abs_str = document.abs.replace('. ','.\n')
        else:
            abs_str = ''
        out_str = '\n'.join([title, kw_str, kp_str, abs_str])
        filename = inner_path + '/{}-{}.txt'.format(document.unique_id, document.pub_year)
        with open(filename, mode='w', encoding='utf-8') as file:
            file.write(out_str)

        with open(path+('/foreground.list' if foreground else '/background.list'), mode='a', encoding='utf-8') as l:
            l.write(('foreground' if foreground else 'background') + '/{}-{}.txt\n'.format(document.unique_id, document.pub_year))


def insert_terms(db_path=None, db_url=None, input_path=None):
    assert (db_path is None and db_url is not None) or (db_path is not None and db_url is None)
    assert input_path is not None

    if db_path:
        engine = get_engine(db_path=db_path)
    else:
        engine = get_engine(db_url=db_url)
    # session = get_session(engine)
    con = engine.connect()

    meta = MetaData(engine)
    term_table = Table('terms', meta, autoload=True)
    with open(input_path, mode='r', encoding='utf-8') as file:
        insert_list = []
        for line in file:
            line_split = line.strip().split('\t')
            term1 = line_split[0]
            if len(line_split) > 1:
                term2 = line_split[-1]
            else:
                term2 = None
            insert_list.append({'term':term1, 'term2':term2})

    con.execute(term_table.insert(), insert_list)
    con.close()





if __name__ == '__main__':
    # print('正在生成背景数据')
    # get_split_title_keyword_abstract(db_path=r'C:\Users\Tom\Desktop\advanced_query\2019-04-25-13.12.29\result.db',
    #                                  foreground=False)
    # print('正在生成前景数据')
    # get_split_title_keyword_abstract(db_path=r'C:\Users\Tom\Desktop\contest\contest.db',
    #                                  foreground=True)

    print('正在插入术语')
    insert_terms(db_url='mysql+pymysql://root:root@localhost/contest?charset=utf8',input_path=r'C:\Users\Tom\Desktop\gcp_result\bio_nature_fixed\bio_nature_fixed.out_term_list')
