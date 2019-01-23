import re

def author(document):
    if 'author' in document:
        if document['author']:
            # document['author'] = document['author'].lower().replace('\n', ' ').replace('jr., ', '').replace('sr., ', '') \
            #     .replace('\\', '').split(' and ')
            document['author'] = document['author'].lower().replace('\n', ' ').replace('\\', '').split(' and ')
        else:
            document['author'] = [None]
    else:
        document['author'] = [None]
    return document


# def author_affiliation(document):
#     """
#     提取作者和机构的规则有点复杂，需要稍作说明：
#     首先去掉不合适的字符，并以换行符断开
#     每一行都包含了一个机构及一个或多个作者
#     如果句子中不存在分号，则说明只有一个作者，此时只需要找到第二个逗号并分开，就是作者和机构的对应关系
#     如果存在，则按分号分割，前面几个作者都能顺利提取，最后一个作者与机构在同一元素中，处理方法同上
#
#     其中，通讯作者（reprint author）会在前面几位出现，不用管，只需要标记该作者为通讯作者即可（用全名）
#     因为通讯作者的机构会在后面以正常顺序显示
#
#     并且，通讯作者如果有多个单位，则会显示多行
#     通讯作者可能有多个
#
#     总结一下情况：
#     1. 普通情况，一个通讯作者，每个人一个地址
#     2. 一个通讯作者，有些人有多个地址
#     3. 多个通讯作者，每人一个地址
#     4. 多个通讯作者，有些人多个地址
#     5. 匿名作者，啥都没有（设置NULL）
#     6. 没有归属作者的机构（删除掉）
#     7. 作者名字带有sr或者jr（目前的操作是删除jr和sr）
#     8. 某些时候狗血的名字不用逗号分割而是用了空格（连同8、9情况一起考虑）
#     9. 某些更狗血的名字姓和名都带有空格（巴西人）
#     10. 有些人只有姓没名字（荷兰人）
#     11. 有的人名字里面有逗号（夏威夷人，不是中间名）
#     12. 有的作者没有机构地址
#
#     select a.author_order, a.last_name, a.first_name, b.address from wos_author as a
#     left join wos_affiliation as b on a.author_id = b.author_id order by a.author_order
#
#     :param document:
#     :return:
#     """
#
#     if 'affiliation' in document:
#         if document['affiliation']:
#             result = {}
#             reprint_author_name = []
#             all_author = set()
#             ordered_author_list = document['author']
#             affiliations = document['affiliation'][1:-1].lower().replace(', jr.', '').replace(', sr.', '').replace('\\',
#                                                                                                                    '').split(
#                 '\n')
#             for affiliation in affiliations:
#                 space_flag = False
#                 author_list = []
#                 tmp = affiliation.split('; ')
#                 if len(tmp) > 1:
#                     # 处理空格情况
#                     pos = find_nth(tmp[-1], ',', 2)
#                     if tmp[-1][:pos] not in ordered_author_list:
#                         pos = tmp[-1].index(',')
#                         space_flag = True
#
#                     author_list += tmp[:-1]
#
#                     if 'reprint author' in tmp[-1]:
#                         pos2 = tmp[-1].index(',')
#                         reprint_author_name += tmp[:-1]
#
#                         # 处理没有名字只有姓的情况
#                         reprint_name = tmp[-1][:pos2 + 3]
#                         if 'reprint author' in reprint_name:
#                             reprint_name = tmp[-1][:tmp[-1].index('(') - 1]
#                         reprint_author_name.append(reprint_name)
#                         continue
#
#                     author_list.append(tmp[-1][:pos])
#                     # tmp[-1] = tmp[-1][pos + 2:]
#                     # address = tmp[-1]
#                     address = tmp[-1][pos + 2:]
#                 else:
#                     # 处理空格情况
#                     pos = find_nth(tmp[0], ',', 2)
#                     if tmp[0][:pos] not in ordered_author_list:
#                         pos = tmp[0].index(',')
#                         space_flag = True
#
#                     address = tmp[0][pos + 2:]
#
#                     if 'reprint author' in tmp[0]:
#                         pos2 = tmp[0].index(',')
#                         # 处理没有名字只有姓的情况
#                         reprint_name = tmp[0][:pos2 + 3]
#                         if 'reprint author' in reprint_name:
#                             reprint_name = tmp[0][:tmp[0].index('(') - 1]
#                         reprint_author_name.append(reprint_name)
#                         continue
#
#                     author_list.append(tmp[0][:pos])
#                 # print(author_list)
#                 for author in author_list:
#                     is_reprint = 0
#                     for name in reprint_author_name:
#                         if space_flag:
#                             name = name.replace(',', '')
#                         if name in author:
#                             is_reprint = 1
#                     try:
#                         last_name, first_name = author.split(',')
#                     except:
#                         try:
#                             last_name, first_name = author.split(' ')
#                         except:
#                             last_name, first_name = author, None
#                         address = tmp[-1][tmp[-1].index(',') + 2:]
#
#                     try:
#
#                         # 处理名字中有逗号的情况（需要调换顺序）
#                         name_split = author.split(', ')
#                         if len(name_split) == 3:
#                             new_name = '{}, {}, {}'.format(name_split[0], name_split[2], name_split[1])
#                             author_order = ordered_author_list.index(new_name) + 1
#                         else:
#                             author_order = ordered_author_list.index(author) + 1
#                     except ValueError as e:
#                         print(document['unique-id'], '文献存在没有作者归属的机构，该机构将被舍弃', author)
#                         continue
#
#                     if (first_name, last_name, author_order, is_reprint) in result:
#                         result[(first_name, last_name, author_order, is_reprint)] \
#                             .append(address)
#                     else:
#                         result[(first_name, last_name, author_order, is_reprint)] = [address]
#
#                     all_author.add(author)
#
#             # 处理作者没有机构的情况（不处理会导致作者缺失）
#             if len(all_author) < len(ordered_author_list):
#                 # print(len(all_author), all_author)
#                 # print(len(ordered_author_list), ordered_author_list)
#                 print('{} 文献有{}个作者没有机构，设NULL'.format(document['unique-id'], len(ordered_author_list) - len(all_author)))
#                 for add_author in ordered_author_list:
#                     if add_author not in all_author:
#                         try:
#                             last_name, first_name = add_author.split(', ')
#                         except:
#                             try:
#                                 last_name, first_name = add_author.split(', ')[0], ', '.join(add_author.split(', ')[1:])
#                             except:
#                                 try:
#                                     last_name, first_name = add_author.split(' ')
#                                 except:
#                                     last_name, first_name = add_author, None
#                         result[(first_name, last_name, ordered_author_list.index(add_author) + 1, 0)] = [None]
#
#             document['affiliation'] = result
#         else:
#             document['affiliation'] = {(None, None, None, None): None}
#     else:
#         document['affiliation'] = {(None, None, None, None): None}
#     return document


def author_affiliation_v2(document):
    # select a.document_unique_id, a.author_order, a.last_name, a.first_name, a.is_reprint_author, b.address from wos_author as a
    #          left join wos_affiliation as b on a.author_id = b.author_id order by a.document_unique_id,a.author_order
    # 调用本函数之前请先调用author函数
    if 'affiliation' in document:
        if document['affiliation']:
            ordered_author_list = document['author']
            assert type(ordered_author_list) == type([])

            # 首先处理名字中有逗号的情况（即除了分割姓名的逗号以外，还有第第二个逗号，此时需要交换第二、三部分的位置）
            for i_author in range(len(ordered_author_list)):
                name_split = ordered_author_list[i_author].split(', ')
                if len(name_split) == 3:
                    ordered_author_list[i_author] = '{}, {}, {}'.format(name_split[0], name_split[2], name_split[1])
                # 如果遇到其他情况，则报错，保证完备性
                elif len(name_split) > 3:
                    print(name_split)
                    print('未考虑的情况：name_split长度大于3')
                    exit(-1)

            result = {}
            reprint_author_list = []

            # 确保每个作者都出现了
            appeared_author = set()

            affiliations = document['affiliation'][1:-1].lower().replace('\\', '').split('\n')

            for affiliation in affiliations:
                # 首先要抽取出每一行包含的作者名字
                author_in_this_line = []

                # 在新的变量中操作字符串
                bak_affiliation = affiliation.replace(';', '')

                # 标志这一行是否是通讯作者行，通讯作者的名字是缩写，要特殊处理
                reprint_author_line = 0

                if 'reprint author' in bak_affiliation:
                    reprint_author_line = 1
                    bak_affiliation = bak_affiliation.replace(' (reprint author)', '')

                    for author_name in ordered_author_list:
                        # 将正常的全称处理为reprint作者的表示格式
                        name_split = author_name.split(', ')
                        reprint_name = ''
                        if len(name_split) >= 2:
                            for i_part in range(len(name_split)):
                                if i_part == 0:
                                    reprint_name += (name_split[i_part] + ', ')
                                else:
                                    if ' ' in name_split[i_part]:
                                        reprint_name += (name_split[i_part][0] + name_split[i_part].split(' ')[1][0])
                                    else:
                                        reprint_name += name_split[i_part][0]

                        # 处理名称以空格分割的情况
                        elif len(author_name.split(' ')) == 2:
                            tmp = author_name.split(' ')
                            reprint_name = ', '.join([tmp[0], tmp[1][0]])
                        elif len(name_split) == 1:
                            # 对于只有姓没有名的就直接保留
                            reprint_name = author_name
                        else:
                            print('出现未考虑到的情况：', author_name)
                            exit(-1)

                        if reprint_name in bak_affiliation:
                            author_in_this_line.append(author_name)
                            reprint_author_list.append(author_name)
                            appeared_author.add(author_name)
                            bak_affiliation = bak_affiliation.replace(reprint_name, '')
                else:
                    for author_name in ordered_author_list:
                        if author_name in bak_affiliation:
                            author_in_this_line.append(author_name)
                            appeared_author.add(author_name)
                            bak_affiliation = bak_affiliation.replace(author_name, '')

                # 将作者从机构字段中提取并删除后，处理地址
                pos = bak_affiliation.index(',') + 2
                address = bak_affiliation[pos:]

                # 将结果写入result
                for author_inline in author_in_this_line:
                    try:
                        last_name, first_name = author_inline.split(', ')
                    except:
                        try:
                            last_name, first_name = author_inline.split(' ')
                        except:
                            try:
                                last_name, first_name = author_inline.split(', ')[0], ', '.join(
                                    author_inline.split(', ')[1:])
                            except:
                                last_name, first_name = author_inline, None

                    author_order = ordered_author_list.index(author_inline) + 1
                    is_reprint = 1 if author_inline in reprint_author_list else 0

                    if (first_name, last_name, author_order, is_reprint) in result:
                        result[(first_name, last_name, author_order, is_reprint)].add(address)
                    else:
                        result[(first_name, last_name, author_order, is_reprint)] = {address}

            # 如果有的作者没有机构，会在这里进行最后的补充检查
            if len(appeared_author) < len(ordered_author_list):
                for author_name in ordered_author_list:
                    if author_name not in appeared_author:
                        try:
                            last_name, first_name = author_name.split(', ')
                        except:
                            try:
                                last_name, first_name = author_name.split(' ')
                            except:
                                try:
                                    last_name, first_name = author_name.split(', ')[0], ', '.join(
                                        author_name.split(', ')[1:])
                                except:
                                    last_name, first_name = author_name, None

                        author_order = ordered_author_list.index(author_name) + 1
                        result[(first_name, last_name, author_order, 0)] = {None}

            document['affiliation'] = result
        else:
            document['affiliation'] = {(None, None, None, None): None}
    else:
        document['affiliation'] = {(None, None, None, None): None}
    return document


def wos_category(document):
    if 'web-of-science-categories' in document:
        if document['web-of-science-categories']:
            document['web-of-science-categories'] = document['web-of-science-categories'][1:-1] \
                .lower().replace('\n', '').replace('\\', '').split('; ')
        else:
            document['web-of-science-categories'] = [None]
    else:
        document['web-of-science-categories'] = [None]
    return document

def research_area(document):
    if 'research-areas' in document:
        if document['research-areas']:
            document['research-areas'] = document['research-areas'][1:-1] \
                .lower().replace('\n', '').replace('\\', '').split('; ')
        else:
            document['research-areas'] = [None]
    else:
        document['research-areas'] = [None]
    return document

def keyword(document):
    if 'keywords' in document:
        if document['keywords']:
            document['keywords'] = document['keywords'][1:-1].lower().replace('\n', ' ').replace('\\', '').split('; ')
        else:
            document['keywords'] = [None]
    else:
        document['keywords'] = [None]
    return document


def keyword_plus(document):
    if 'keywords-plus' in document:
        if document['keywords-plus']:
            document['keywords-plus'] = document['keywords-plus'][1:-1] \
                .lower().replace('\n', ' ').replace('\\', '').split('; ')
        else:
            document['keywords-plus'] = [None]
    else:
        document['keywords-plus'] = [None]
    return document


def reference(document):
    if 'cited-references' in document:
        if document['cited-references']:
            volume_pattern = re.compile(r'v\d+')
            page_pattern = re.compile(r'p\d+')
            doi_pattern = re.compile(r'doi .+')


            result = []
            references = document['cited-references'][1:-1].lower().replace('{[}', '[').replace('\\', '').split('\n')

            for reference in references:
                ref_split = reference[:-1].split(', ')

                first_author = ref_split[0]
                pub_year = ref_split[1]
                journal = None
                volume = None
                start_page = None
                doi = None

                min_i = 999
                for i_part in range(2, len(ref_split)):
                    volume_match = volume_pattern.match(ref_split[i_part])
                    page_match = page_pattern.match(ref_split[i_part])
                    doi_match = doi_pattern.match(ref_split[i_part])

                    if volume_match:
                        volume = ref_split[i_part][1:]
                        if i_part < min_i:
                            min_i = i_part
                    elif page_match:
                        start_page = ref_split[i_part][1:]
                        if i_part < min_i:
                            min_i = i_part
                    elif doi_match:
                        doi = ref_split[i_part].replace('doi ','').replace('[','').replace(']','')
                        if i_part < min_i:
                            min_i = i_part

                if min_i > 2:
                    journal = ', '.join(ref_split[2:min_i])

                result.append((first_author, pub_year, journal, volume, start_page, doi))

            document['cited-references'] = result
        else:
            document['cited-references'] = [(None,None,None,None,None,None)]
    else:
        document['cited-references'] = [(None,None,None,None,None,None)]
    return document


def funding(document):
    if 'funding-acknowledgement' in document:
        if document['funding-acknowledgement']:
            result = {}
            fundings = document['funding-acknowledgement'][1:-1].lower().replace('\\', '').replace('\n', ' ') \
                .replace('{[}', '[').split('; ')

            for fund in fundings:
                tmp = fund.split(' [')
                if len(tmp) == 2:
                    agent, numbers = tmp[0], tmp[1]
                    numbers = numbers.replace(']', '').split(', ')
                elif len(tmp) == 1:
                    agent, numbers = tmp[0], [None]
                elif len(tmp) == 3:
                    agent, numbers = tmp[0] + ' [' + tmp[1], tmp[2]
                    numbers = numbers.replace(']', '').split(', ')
                else:
                    print('未考虑到的情况：', tmp)
                    exit(-1)

                result[agent] = numbers
            document['funding-acknowledgement'] = result
        else:
            document['funding-acknowledgement'] = {None: [None]}
    else:
        document['funding-acknowledgement'] = {None: [None]}
    return document


def find_nth(haystack, needle, n):
    n -= 1
    parts = haystack.split(needle, n + 1)
    if len(parts) <= n + 1:
        return -1
    return len(haystack) - len(parts[-1]) - len(needle)


if __name__ == '__main__':
    print(find_nth('abcabc', 'a', 1))
