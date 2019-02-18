from model import get_engine, get_session
from model.wos_document import *
from itertools import combinations
from netUtil.build_network import get_network
import networkx as nx
from analysis.draw.draw_cooccurrence_network import draw_net
import matplotlib.pyplot as plt
from sqlalchemy import func, desc
import os

def draw_cooccurrence_network(net_type=None, db_path=None, output_path=None, top_n=30):
    assert net_type is not None and output_path is not None and db_path is not None

    engine = get_engine(db_path)
    session = get_session(engine)

    print('正在处理共现数据')
    graph_data = []
    data = []
    title = None
    if net_type == 'keyword':
        title = 'Author Keyword Co-occurrence Network'
        data = session.query(WosDocument.unique_id,
                             func.group_concat(WosKeyword.keyword, ';'))\
                                .join(WosKeyword).group_by(WosDocument.unique_id)
        filter_data = session.query(WosKeyword.keyword, func.count('*').label('num')) \
            .group_by(WosKeyword.keyword).order_by(desc('num'))
    elif net_type == 'keyword_plus':
        title = 'WoS Keyword Co-occurrence Network'
        data = session.query(WosDocument.unique_id,
                             func.group_concat(WosKeywordPlus.keyword_plus, ';'))\
                                .join(WosKeywordPlus).group_by(WosDocument.unique_id)
        filter_data = session.query(WosKeywordPlus.keyword_plus, func.count('*').label('num')) \
            .group_by(WosKeywordPlus.keyword_plus).order_by(desc('num'))
    elif net_type == 'author':
        title = 'Author Co-authorship Network'
        data = session.query(WosDocument.unique_id,
                             func.group_concat(WosAuthor.last_name +','+ WosAuthor.first_name, ';'))\
                                .join(WosAuthor).group_by(WosDocument.unique_id)
        filter_data = session.query(WosAuthor.last_name + ',' + WosAuthor.first_name, func.count('*').label('num')) \
            .group_by(WosAuthor.last_name + ',' + WosAuthor.first_name).order_by(desc('num'))

    else:
        print('未考虑到的作图情况：', net_type)
        exit(-1)

    for row in data:
        row_split = row[1].split(';')
        if len(row_split) > 1:
            graph_data += list(combinations(row_split, 2))

    # network是包含了全部关键词的共现网络
    print('正在生成共现网络')
    network = get_network(graph_data, directed=False)

    session.close()

    nx.write_graphml(network, 'test.gml')

    filter_nodes = [i[0] for i in filter_data[top_n:]]
    sub = nx.restricted_view(network, filter_nodes, [])



    # 最大联通子图
    # sub = sorted(nx.connected_component_subgraphs(sub), key = len, reverse=True)[0]

    # print('正在绘图')
    draw_net(sub, title=title, output_path=os.path.join(output_path, net_type))

if __name__ == '__main__':
    draw_cooccurrence_network(net_type='author',
                              db_path=r'C:\Users\Tom\PycharmProjects\wos_crawler\output\advanced_query\2019-01-31-10.21.19\result.db',
                              output_path=r'C:\Users\Tom\Desktop',
                              top_n=50)

