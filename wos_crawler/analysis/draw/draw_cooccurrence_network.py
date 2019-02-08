import plotly
import plotly.graph_objs as go
import plotly.io as pio
import networkx as nx
import matplotlib.pyplot as plt


def draw_net(G: nx.Graph, title='co-occurrence', output_path=None):
    assert output_path is not None
    pos = nx.kamada_kawai_layout(G)
    # pos = nx.nx_pydot.graphviz_layout(G, prog='fdp')
    nx.set_node_attributes(G, pos, 'pos')

    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=0.8, color='#888'),
        hoverinfo='none',
        mode='lines')

    for edge in G.edges(data=True):
        x0, y0 = G.node[edge[0]]['pos']
        x1, y1 = G.node[edge[1]]['pos']
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])

    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        textfont=dict(
            size=[],
            family=['Times New Roman']
        ),
        mode='markers',
        hoverinfo='text',
        opacity=1,
        marker=dict(
            showscale=True,
            # colorscale options
            # 'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            # 'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            # 'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='Jet',
            opacity=0.9,
            reversescale=False,
            color=[],
            size=[],
            colorbar=dict(
                thickness=25,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line=dict(width=2)))

    for node in G.nodes():
        x, y = G.node[node]['pos']
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])

    for node, adjacencies in enumerate(G.adjacency()):
        node_trace['marker']['color'] += tuple([len(adjacencies[1])])
        node_trace['textfont']['size'] += tuple([len(adjacencies[1]) * 5 + 1])
        node_info = adjacencies[0].title()
        node_trace['text'] += tuple([node_info])
        node_trace['marker']['size'] += tuple([len(adjacencies[1]) * 5])

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='<br>' + title,
                        titlefont=dict(size=16),
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        # annotations=[dict(
                        #     text="Python code: <a href='https://plot.ly/ipython-notebooks/network-graphs/'> https://plot.ly/ipython-notebooks/network-graphs/</a>",
                        #     showarrow=False,
                        #     xref="paper", yref="paper",
                        #     x=0.005, y=-0.002)],
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

    plotly.offline.plot(fig, filename='{}.html'.format(output_path), auto_open=False, image_width=1600,
                        image_height=900, image='png')
