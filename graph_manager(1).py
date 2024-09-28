# graph_manager.py

import networkx as nx

def create_graph(directed=False):
    """
    Creates an empty graph (directed or undirected) and saves it to a GraphML file.
    
    Parameters:
    - directed (bool): If True, creates a directed graph. Otherwise, undirected.
    """
    if directed:
        G = nx.DiGraph()
    else:
        G = nx.Graph()
    # Saving the graph in GraphML format
    nx.write_graphml(G, 'grafo.graphml')
    print(f"Grafo {'direcionado' if directed else 'não direcionado'} criado e salvo em 'grafo.graphml'.")

def load_graph():
    """
    Loads the graph from a GraphML file, preserving its directedness.
    
    Returns:
    - G (networkx.Graph or networkx.DiGraph): The loaded graph.
    """
    G = nx.read_graphml('grafo.graphml')
    # Convert to DiGraph if necessary
    if G.is_directed():
        G = G.to_directed()
    else:
        G = G.to_undirected()
    return G

def add_node(G, new_node_id):
    """
    Adds a new node to the existing graph.
    """
    if new_node_id in G.nodes:
        raise nx.NetworkXError(f"O nó '{new_node_id}' já existe.")
    else:
        G.add_node(new_node_id, label=new_node_id, group=int(len(G.nodes())) % 3, color='#0074D9')
    return G

def remove_node(G, node_id):
    """
    Removes a node from the existing graph.
    """
    if node_id in G.nodes:
        G.remove_node(node_id)
    else:
        raise nx.NetworkXError(f"O nó '{node_id}' não existe.")
    return G

def add_edge(G, source_id, target_id, weight=1.0):
    """
    Adds a new edge between two nodes in the existing graph.
    """
    if source_id not in G.nodes or target_id not in G.nodes:
        missing_nodes = [node for node in [source_id, target_id] if node not in G.nodes]
        raise nx.NetworkXError(f"Nós não encontrados no grafo: {', '.join(missing_nodes)}")
    if G.has_edge(source_id, target_id):
        raise nx.NetworkXError(f"Aresta já existe entre '{source_id}' e '{target_id}'.")
    else:
        G.add_edge(source_id, target_id, color='#ccc')
    return G

def remove_edge(G, source_id, target_id):
    """
    Removes an edge between two nodes in the existing graph.
    """
    if G.has_edge(source_id, target_id):
        G.remove_edge(source_id, target_id)
    else:
        raise nx.NetworkXError(f"A aresta entre '{source_id}' e '{target_id}' não existe.")
    return G

# graph_manager.py

def networkx_to_cytoscape(G):
    """
    Converts a NetworkX graph to Cytoscape elements with unique edge IDs and labels for weights.
    
    Parameters:
    - G (networkx.Graph or networkx.DiGraph): The graph.
    
    Returns:
    - elements (list): List of elements for Cytoscape.
    """
    elements = []

    # Adding nodes
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

    # Adding edges with unique IDs and labels for weights
    for source, target, data in G.edges(data=True):
        if G.is_directed():
            edge_id = f"{source}->{target}"
        else:
            # Sort the node IDs to ensure consistency in undirected graphs
            sorted_nodes = sorted([source, target])
            edge_id = f"{sorted_nodes[0]}-{sorted_nodes[1]}"
        
        # Set the label to the weight if it exists, else leave it empty
        edge_label = str(data['weight']) if 'weight' in data else ''

        element = {
            'data': {
                'id': edge_id,
                'source': source,
                'target': target,
                'color': data.get('color', '#ccc'),
                'label': edge_label,               # Add label for the edge
                'weight': data.get('weight', None) # Include weight if it exists
            }
        }
        elements.append(element)

    return elements

def reconstruct_graph_from_elements(elements, directed=False):
    """
    Reconstrói um grafo NetworkX a partir dos elementos do Cytoscape.
    
    Parâmetros:
    - elements (list): Lista de elementos do Cytoscape (nós e arestas).
    - directed (bool): Define se o grafo será direcionado.
    
    Retorna:
    - G (networkx.Graph ou networkx.DiGraph): O grafo reconstruído.
    """
    G = nx.DiGraph() if directed else nx.Graph()
    
    for element in elements:
        data = element.get('data', {})
        if 'source' in data and 'target' in data:
            # É uma aresta
            source = data['source']
            target = data['target']
            edge_attrs = {}
            if 'color' in data:
                edge_attrs['color'] = data['color']
            if 'weight' in data and data['weight'] != '':
                try:
                    edge_attrs['weight'] = float(data['weight'])
                except ValueError:
                    edge_attrs['weight'] = 1.0  # Valor padrão em caso de erro
            G.add_edge(source, target, **edge_attrs)
        else:
            # É um nó
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
                    node_attrs['group'] = 0  # Valor padrão em caso de erro
            position = element.get('position', {})
            if 'x' in position and 'y' in position:
                node_attrs['position'] = {
                    'x': float(position['x']),
                    'y': float(position['y'])
                }
            G.add_node(node_id, **node_attrs)
    
    return G

if __name__ == '__main__':
    # By default, create an undirected graph
    create_graph(directed=False)
