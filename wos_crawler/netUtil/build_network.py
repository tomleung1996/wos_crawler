import networkx as nx

def get_network(data, directed=False):
    assert data is not None

    if directed:
        graph = nx.DiGraph()
    else:
        graph = nx.Graph()

    for edge in data:
        if graph.has_edge(str(edge[0]), str(edge[1])):
            graph.edges[str(edge[0]), str(edge[1])]['weight'] += 1
        else:
            graph.add_edge(str(edge[0]), str(edge[1]), weight=1)
    return graph