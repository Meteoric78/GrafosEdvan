import networkx as nx

def create_graph(directed=False):
    if directed:
        G = nx.DiGraph()
    else:
        G = nx.Graph()
    nx.write_graphml(G, 'grafo.graphml')
    print(f"Grafo {'direcionado' if directed else 'não direcionado'} criado e salvo em 'grafo.graphml'.")

def load_graph():
    G = nx.read_graphml('grafo.graphml')
    if G.is_directed():
        G = G.to_directed()
    else:
        G = G.to_undirected()
    return G

def cyto_add_node(G, new_node_id, position={'x': 0, 'y': 0}):
    if new_node_id in G.nodes:
        raise nx.NetworkXError(f"O nó '{new_node_id}' já existe.")
    else:
        G.add_node(new_node_id, label=new_node_id, group=int(len(G.nodes())) % 3, color='#0074D9', position=position)
    return G

def cyto_remove_node(G, node_id):
    if node_id in G.nodes:
        G.remove_node(node_id)
    else:
        raise nx.NetworkXError(f"O nó '{node_id}' não existe.")
    return G

def cyto_add_edge(G, source_id, target_id, weight=1.0):
    if source_id not in G.nodes or target_id not in G.nodes:
        missing_nodes = [node for node in [source_id, target_id] if node not in G.nodes]
        raise nx.NetworkXError(f"Nós não encontrados no grafo: {', '.join(missing_nodes)}")
    if G.has_edge(source_id, target_id):
        raise nx.NetworkXError(f"Aresta já existe entre '{source_id}' e '{target_id}'.")
    else:
        G.add_edge(source_id, target_id, color='#ccc', weight=weight)
    return G

def cyto_remove_edge(G, source_id, target_id):
    if G.has_edge(source_id, target_id):
        G.remove_edge(source_id, target_id)
    else:
        raise nx.NetworkXError(f"A aresta entre '{source_id}' e '{target_id}' não existe.")
    return G

def networkx_to_cytoscape(G):
    elements = []
    for node_id, data in G.nodes(data=True):
        position = data.get('position', {'x': 0, 'y': 0})  # Default position if not set
        element = {
            'data': {
                'id': node_id,
                'label': data.get('label', node_id),
                'group': data.get('group', 0),
                'color': data.get('color', '#0074D9')
            },
            'position': {
                'x': position.get('x', 0),
                'y': position.get('y', 0)
            },
            'classes': 'grupo-' + str(data.get('group', 0))
        }
        elements.append(element)

    for source, target, data in G.edges(data=True):
        if G.is_directed():
            edge_id = f"{source}->{target}"
        else:
            sorted_nodes = sorted([source, target])
            edge_id = f"{sorted_nodes[0]}-{sorted_nodes[1]}"
        edge_label = data.get('label', '')

        element = {
            'data': {
                'id': edge_id,
                'source': source,
                'target': target,
                'color': data.get('color', '#ccc'),
                'label': edge_label,
                'weight': data.get('weight', 1.0)
            }
        }
        elements.append(element)

    return elements
def reconstruct_graph_from_elements(elements, directed=False):
    G = nx.DiGraph() if directed else nx.Graph()
    for element in elements:
        data = element.get('data', {})
        if 'source' in data and 'target' in data:
            source = data['source']
            target = data['target']
            edge_attrs = {}
            if 'color' in data:
                edge_attrs['color'] = data['color']
            if 'weight' in data and data['weight'] != '':
                try:
                    edge_attrs['weight'] = float(data['weight'])
                except ValueError:
                    edge_attrs['weight'] = 1.0 
            else:
                edge_attrs['weight'] = 1.0 

            G.add_edge(source, target, **edge_attrs)
        else:
            node_id = data.get('id')
            node_attrs = {}
            if 'label' in data:
                node_attrs['label'] = data['label']
            if 'color' in data:
                node_attrs['color'] = data['color']
            if 'group' in data:
                try:
                    node_attrs['group'] = int(data['group'])
                except ValueError:
                    node_attrs['group'] = 0
            position = element.get('position', {'x': 0, 'y': 0})
            node_attrs['position'] = position
            G.add_node(node_id, **node_attrs)
    return G

if __name__ == '__main__':
    create_graph(directed=False)
