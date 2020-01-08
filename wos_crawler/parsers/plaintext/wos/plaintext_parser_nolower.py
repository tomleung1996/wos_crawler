from model import get_engine, get_session
from model.wos_document import *
from parsers.bibtex.wos.customization import find_nth
from sqlalchemy import or_, MetaData
import re
import os
import hashlib


def parse_single(input_file=None, db_path=None, db_url=None, exist_set=None):
    assert input_file is not None and (db_path is not None or db_url is not None) and exist_set is not None

    engine = get_engine(db_path, db_url)
    Base.metadata.create_all(engine)
    session = get_session(engine)

    volume_pattern = re.compile(r'^[Vv]\d+$')
    page_pattern = re.compile(r'^[Pp]\w*\d+$')
    doi_pattern = re.compile(r'^DOI \d+.+$')
    year_pattern = re.compile(r'^\d{4}$')

    print('正在解析{}……'.format(input_file))

    with open(input_file, 'r', encoding='utf-8') as file:
        cur_field = None
        author_dict = {}
        initials_list = []
        author_order = 1
        wos_document = WosDocument()
        wos_document_list = []

        # 有些换行了的字段先暂存，等到最后再处理
        journal_line = None
        wos_category_line = None
        research_area_line = None
        keyword_line = None
        keyword_plus_line = None
        funding_line = None

        for line in file.readlines():
            # line = line[:-1].lower()
            line = line[:-1]

            # 通过每一行的前三个字符来识别行的状态
            tmp = line[:3]
            if tmp != '   ':
                cur_field = tmp

            if cur_field == 'PT ':
                del wos_document
                wos_document = WosDocument()
            # 获得作者的缩写
            elif cur_field == 'AU ':
                if tmp == cur_field:
                    initials_list.clear()
                full_name = line[3:]
                initials_list.append(full_name)
            # 解析作者得到作者顺序，此时尚未绑定通讯作者和地址
            # 需要处理用空格分割的特殊情况
            # 还需要处理匿名作者等无分割情况
            # 还需要处理团体作者单独放在CA字段的情况
            elif cur_field == 'AF ':
                if tmp == cur_field:
                    author_dict.clear()
                    author_order = 1
                full_name = line[3:]
                try:
                    pos = full_name.index(',')
                except:
                    try:
                        pos = full_name.index(' ')
                    except:
                        pos = len(full_name)
                author = WosAuthor(full_name[pos + 1:], full_name[:pos].strip(), initials_list[author_order-1].replace(',',''),author_order, 0)
                author.document = wos_document
                author_dict[full_name] = author

                if author_order == 1:
                    wos_document.first_author = initials_list[author_order-1].replace(',','')

                author_order += 1
            elif cur_field == 'CA ':
                group_author = line[3:]
                initials_list.append(group_author)
                author = WosAuthor(group_author, None, initials_list[author_order-1].replace(',',''), author_order, 0)
                author_dict[group_author] = author

                if author_order == 1:
                    wos_document.first_author = initials_list[author_order-1].replace(',','')

                author_order += 1
            elif cur_field == 'C1 ':
                # 将机构地址绑定到前面提取到的作者上
                author_affiliation = line[3:]
                try:
                    pos = author_affiliation.index(']')
                except:
                    # print('存在没有作者的机构{}，已抛弃'.format(author_affiliation))
                    continue
                authors = author_affiliation[1:pos].split('; ')
                for author in authors:
                    affiliation = WosAffiliation(author_affiliation[pos + 2:-1])
                    affiliation.author = author_dict[author]
            elif cur_field == 'RP ':
                # 确定通讯作者
                rp_author_affiliations = line[3:].split('; ')
                for rp_author_affiliation in rp_author_affiliations:
                    try:
                        pos = rp_author_affiliation.index(' (')
                        rp_author = rp_author_affiliation[:pos]
                    except:
                        rp_author = rp_author_affiliation
                    try:
                        rp_index = initials_list.index(rp_author) + 1
                    except:
                        rp_index = 1
                    for author in author_dict.keys():
                        if author_dict[author].author_order == rp_index:
                            author_dict[author].is_reprint_author = 1
            elif cur_field == 'TI ':
                title = line[3:]
                if wos_document.title is not None:
                    wos_document.title += ' ' + title
                else:
                    wos_document.title = title
            elif cur_field == 'SO ':
                if journal_line is not None:
                    journal_line += ' ' + line[3:]
                else:
                    journal_line = line[3:]
            elif cur_field == 'LA ':
                wos_document.language = line[3:]
            elif cur_field == 'DT ':
                wos_document.document_type = line[3:]
            elif cur_field == 'DE ':
                if keyword_line is not None:
                    keyword_line += ' ' + line[3:]
                else:
                    keyword_line = line[3:]
            elif cur_field == 'ID ':
                if keyword_plus_line is not None:
                    keyword_plus_line += ' ' + line[3:]
                else:
                    keyword_plus_line = line[3:]
            elif cur_field == 'AB ':
                if wos_document.abs is not None:
                    wos_document.abs += ' ' + line[3:]
                else:
                    wos_document.abs = line[3:]
            elif cur_field == 'EM ':
                wos_document.author_email = line[3:].replace(' ', '')
            elif cur_field == 'FU ':
                if funding_line is not None:
                    funding_line += ' ' + line[3:]
                else:
                    funding_line = line[3:]
            elif cur_field == 'FX ':
                if wos_document.funding_text is not None:
                    wos_document.funding_text += ' ' + line[3:]
                else:
                    wos_document.funding_text = line[3:]
            elif cur_field == 'CR ':
                # 解析参考文献

                reference = line[3:]
                ref_split = reference.split(', ')
                first_author = None
                pub_year = None
                journal = None
                volume = None
                start_page = None
                doi = None

                year_flag = False

                if len(ref_split) < 2:
                    journal = ref_split[0]
                else:
                    i_list = []
                    for i_part in range(len(ref_split)):
                        volume_match = volume_pattern.match(ref_split[i_part])
                        page_match = page_pattern.match(ref_split[i_part])
                        doi_match = doi_pattern.match(ref_split[i_part])
                        if not year_flag:
                            year_match = year_pattern.match(ref_split[i_part])
                        else:
                            year_match = None

                        if year_match:
                            pub_year = ref_split[i_part]
                            i_list.append(i_part)
                            year_flag = True
                        elif volume_match:
                            volume = ref_split[i_part][1:]
                            i_list.append(i_part)
                        elif page_match:
                            start_page = ref_split[i_part][1:]
                            i_list.append(i_part)
                        elif doi_match:
                            doi = ref_split[i_part].lower().replace('doi ', '').replace('[', '').replace(']', '')
                            i_list.append(i_part)

                    i_list.sort()
                    if len(i_list) > 0:
                        if min(i_list) > 0:
                            first_author = ref_split[0]
                        start_pos = None
                        end_pos = None
                        pos = 0
                        while pos < len(i_list) - 1:
                            if i_list[pos + 1] - i_list[pos] > 1:
                                start_pos = i_list[pos] + 1
                            if start_pos is not None and i_list[pos + 1] - i_list[pos] == 1:
                                end_pos = i_list[pos]
                                break
                            pos += 1
                        if start_pos is not None or end_pos is not None:
                            if start_pos == end_pos:
                                journal = ref_split[start_pos]
                            elif end_pos is None:
                                journal = ', '.join(ref_split[start_pos:i_list[-1]])
                            else:
                                journal = ', '.join(ref_split[start_pos:end_pos])

                        else:
                            if year_flag:
                                try:
                                    journal = ref_split[i_list[-1] + 1]
                                except:
                                    journal = None
                            else:
                                journal = ref_split[i_list[0] - 1]
                    else:
                        first_author = ref_split[0]
                        journal = ref_split[1]

                # 由于参考文献字段非常不规范，经常超长，所以使用截断
                if first_author is not None and len(first_author) > 254:
                    first_author = first_author[:254]
                if journal is not None and len(journal) > 254:
                    journal = journal[:254]

                ref = WosReference(first_author.replace('.','').replace('. ','').replace(',','') if first_author else first_author,
                                   pub_year, journal, volume, start_page, doi)
                ref.document = wos_document

            elif cur_field == 'NR ':
                wos_document.reference_num = int(line[3:])
            elif cur_field == 'TC ':
                wos_document.cited_times = int(line[3:])
            elif cur_field == 'U1 ':
                wos_document.usage_180 = int(line[3:])
            elif cur_field == 'U2':
                wos_document.usage_since_2013 = int(line[3:])
            elif cur_field == 'PU ':
                wos_document.publisher = line[3:]
            elif cur_field == 'JI ':
                wos_document.journal_iso = line[3:]
            elif cur_field == 'J9 ':
                wos_document.journal_29 = line[3:]
            elif cur_field == 'PD ':
                wos_document.pub_month_day = line[3:]
            elif cur_field == 'PY ':
                wos_document.pub_year = line[3:]
            elif cur_field == 'VL ':
                wos_document.volume = line[3:]
            elif cur_field == 'IS ':
                wos_document.issue = line[3:]
            elif cur_field == 'BP ':
                wos_document.start_page = line[3:]
            elif cur_field == 'EP ':
                wos_document.end_page = line[3:]
            elif cur_field == 'DI ':
                wos_document.doi = line[3:]
            elif cur_field == 'WC ':
                if wos_category_line is not None:
                    wos_category_line += ' ' + line[3:]
                else:
                    wos_category_line = line[3:]
            elif cur_field == 'SC ':
                if research_area_line is not None:
                    research_area_line += ' ' + line[3:]
                else:
                    research_area_line = line[3:]
            elif cur_field == 'UT ':
                wos_document.unique_id = line[7:]
            elif cur_field == 'ER':
                # 在最后一行处理多行字段的问题
                if journal_line is not None:
                    wos_document.journal = journal_line
                    journal_line = None

                if keyword_line is not None:
                    keywords = keyword_line.split('; ')
                    for keyword in keywords:
                        if len(keyword) > 254:
                            keyword = keyword[:254]
                        key = WosKeyword(keyword)
                        key.document = wos_document
                    keyword_line = None

                if keyword_plus_line is not None:
                    keyword_plus = keyword_plus_line.split('; ')
                    for kp in keyword_plus:
                        if len(kp) > 254:
                            kp = kp[:254]
                        keyp = WosKeywordPlus(kp)
                        keyp.document = wos_document
                    keyword_plus_line = None

                if wos_category_line is not None:
                    categories = wos_category_line.split('; ')
                    for category in categories:
                        if len(category) > 254:
                            category = category[:254]
                        cat = WosCategory(category)
                        cat.document = wos_document
                    wos_category_line = None

                if research_area_line is not None:
                    areas = research_area_line.split('; ')
                    for area in areas:
                        if len(area) > 254:
                            area = area[:254]
                        a = WosResearchArea(area)
                        a.document = wos_document
                    research_area_line = None

                if funding_line is not None:
                    fundings = funding_line.split('; ')
                    for fund in fundings:
                        pos = find_nth(fund, '[', -1)
                        if pos != -1:
                            funding = [fund[:pos], fund[pos:]]
                            agent = funding[0]
                            numbers = funding[1].replace('[', '').replace(']', '').split(', ')
                            for number in numbers:
                                f = WosFunding(agent, number)
                                f.document = wos_document
                        else:
                            agent = fund
                            f = WosFunding(agent, None)
                            f.document = wos_document
                    funding_line = None
                wos_document.document_md5 = document_hash(wos_document)

                # TODO:排除非article和review文献，用完记得删除
                # if (not 'article' in wos_document.document_type and not 'review' in wos_document.document_type) \
                #         or 'early access' in wos_document.document_type or 'retracted' in wos_document.document_type\
                #         or 'software' in wos_document.document_type or 'hardware' in wos_document.document_type\
                #         or 'exhibit' in wos_document.document_type or 'database' in wos_document.document_type\
                #         or 'book' in wos_document.document_type:
                #     continue

                # 统一处理一下超长截断问题
                if len(wos_document.title) > 499:
                    wos_document.title = wos_document.title[:499]
                if wos_document.unique_id in exist_set:
                    continue
                else:
                    exist_set.add(wos_document.unique_id)
                    wos_document_list.append(wos_document)


    print('解析{}完成，正在写入数据库……'.format(input_file))
    session.add_all(wos_document_list)
    session.commit()
    session.close()
    print('插入{}完成\n'.format(input_file))
    return exist_set

def document_hash(doc:WosDocument):
    first_author = doc.first_author
    journal_29 = doc.journal_29
    volume = doc.volume
    start_page = doc.start_page
    pub_year = doc.pub_year
    doi = doc.doi

    if not first_author:
        first_author = ''
    if not journal_29:
        journal_29 = ''
    if not volume:
        volume = ''
    if not start_page:
        start_page = ''
    if not pub_year:
        pub_year = ''
    if not doi:
        doi = ''
    return hashlib.md5(
        (','.join([first_author.lower(), journal_29.lower(), volume.lower(), start_page.lower(), pub_year.lower()])).encode('utf-8')).hexdigest()


def parse(input_dir=None, db_path=None, db_url=None):
    assert input_dir is not None and (db_path is not None or db_url is not None)

    init_set = set()

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file[-4:] == '.txt':
                exist_set = parse_single(os.path.join(root, file), db_path, db_url, init_set)
                init_set = init_set.union(exist_set)

    # 最后处理内部引证关系
    print('开始处理内部引证关系……')
    engine = get_engine(db_path, db_url)
    Base.metadata.create_all(engine)
    session = get_session(engine)

    session.execute('REPLACE INTO wos_inner_reference '
                    'SELECT DISTINCT t1.document_unique_id AS citing_paper_id, t2.unique_id AS cited_paper_id '
                    'FROM wos_reference t1 INNER JOIN wos_document t2 '
                    'ON t1.document_md5 = t2.document_md5 OR t1.doi = t2.doi '
                    'ORDER BY citing_paper_id, cited_paper_id')
    session.commit()
    session.execute('DELETE FROM wos_inner_reference WHERE citing_paper_id = cited_paper_id')
    session.commit()
    session.close()

    print('全部解析完成')


if __name__ == '__main__':
    parse(input_dir=r'C:\Users\Tom\Desktop\genome editing related',
          db_path=r'C:\Users\Tom\Desktop\tresult')
    pass
