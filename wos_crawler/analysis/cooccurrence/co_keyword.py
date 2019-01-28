from model import get_engine, get_session
from model.wos_document import *
from itertools import combinations
from netUtil.build_network import get_network
import networkx as nx
import operator
from analysis.draw.draw_cooccurrence_network import draw_net
import os

def draw_cooccurrence_network(net_type=None, db_path=None, output_path=None, top_n=30):
    assert net_type is not None and output_path is not None and db_path is not None

    engine = get_engine(db_path)
    session = get_session(engine)

    print('正在处理共现数据')
    graph_data = []
    data = []
    title = None
    for doc in session.query(WosDocument).order_by(WosDocument.unique_id.asc()).all():
        if net_type == 'keyword':
            title = 'Author Keyword Co-occurrence Network'
            data = [i.keyword for i in doc.keywords]
        elif net_type == 'keyword_plus':
            title = 'WoS Keyword Co-occurrence Network'
            data = [i.keyword_plus for i in doc.keyword_plus]
        elif net_type == 'keyword_all':
            title = 'All Keyword Co-occurrence Network'
            data1 = set([i.keyword for i in doc.keywords if i.keyword is not None])
            data2 = set([i.keyword_plus for i in doc.keyword_plus if i.keyword_plus is not None])
            data = list(data1.union(data2))
        elif net_type == 'author':
            title = 'Author Co-authorship Network'
            for author in doc.authors:
                if author.first_name is not None:
                    data.append(author.last_name + ', ' + author.first_name)
                else:
                    data.append(author.last_name)
        else:
            data = None
            print('未考虑到的作图情况：', net_type)
            exit(-1)
        if len(data) > 1:
            graph_data += list(combinations(data, 2))

        data.clear()
    session.close()

    print('正在生成共现网络')
    network = get_network(graph_data, directed=False)

    filter_nodes = [i[0] for i in sorted(dict(network.degree).items(), key=operator.itemgetter(1), reverse=True)[top_n:]]

    sub = nx.restricted_view(network, filter_nodes, [])

    print('正在绘图')
    draw_net(sub, title=title, output_path=os.path.join(output_path, net_type))

if __name__ == '__main__':
    draw_cooccurrence_network(net_type='keyword',
                              db_path=r'C:\Users\Tom\PycharmProjects\wos_crawler\output\advanced_query\2019-01-27-17.15.27\result.db',
                              output_path=r'C:\Users\Tom\Desktop',
                              top_n=100)

