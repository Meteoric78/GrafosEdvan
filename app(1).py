# app.py

import dash
import dash_cytoscape as cyto
from dash import html, dcc
from dash.dependencies import Input, Output, State
from dash import callback_context
import networkx as nx
import graph_manager
import copy
import json

# Load the graph data from JSON
with open('cytoscape_elements(2).json') as f:
    graph_data = json.load(f)

# Load the graph using graph_manager
G = graph_manager.load_graph()
elements = graph_manager.networkx_to_cytoscape(G)
is_directed = G.is_directed()


nodes = [item for item in graph_data if 'source' not in item['data']]
edges = [item for item in graph_data if 'source' in item['data']]
elements = nodes + edges
#elements = []

# Create the Dash application
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Visualização Interativa de Grafo com Dash Cytoscape'),

    # Main Div with flex display for two columns
    html.Div([
        # Left Column: Contains all controls
        html.Div([
            # Section to add nodes
            html.Div([
                dcc.Input(
                    id='input-node-name',
                    type='text',
                    placeholder='Nome do novo nó',
                    style={'marginRight': '10px'}
                ),
                html.Button('Adicionar Nó', id='btn-add-node', n_clicks=0)
            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '20px'}),

            # Section to add edges manually
            html.Div([
                dcc.Input(
                    id='input-source-node',
                    type='text',
                    placeholder='Nó de origem',
                    style={'marginRight': '10px'}
                ),
                dcc.Input(
                    id='input-target-node',
                    type='text',
                    placeholder='Nó de destino',
                    style={'marginRight': '10px'}
                ),
                html.Button('Adicionar Aresta', id='btn-add-edge', n_clicks=0)
            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '20px'}),

            # Section to add edges from selection
            html.Div([
                html.Button('Adicionar Arestas da Seleção', id='btn-add-edges-from-selection', n_clicks=0, style={'marginRight': '10px'}),
                html.Button('Limpar Seleção', id='btn-clear-selection', n_clicks=0)
            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '20px'}),

            # Section to remove a specific node
            html.Div([
                dcc.Input(
                    id='input-node-remove',
                    type='text',
                    placeholder='ID do nó a remover',
                    style={'marginRight': '10px'}
                ),
                html.Button('Remover Nó', id='btn-remove-node', n_clicks=0)
            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '20px'}),

            # Section to remove selected nodes
            html.Div([
                html.Button('Remover Nós Selecionados', id='btn-remove-selected-nodes', n_clicks=0, style={'marginRight': '10px'})
            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '20px'}),

            # Section to remove edges by text
            html.Div([
                html.H3('Remover Arestas por Texto'),
                dcc.Input(
                    id='input-edge-source-remove',
                    type='text',
                    placeholder='Nó de origem',
                    style={'marginRight': '10px', 'marginBottom': '5px'}
                ),
                dcc.Input(
                    id='input-edge-target-remove',
                    type='text',
                    placeholder='Nó de destino',
                    style={'marginRight': '10px', 'marginBottom': '5px'}
                ),
                html.Button('Remover Aresta', id='btn-remove-edge', n_clicks=0)
            ], style={'marginBottom': '20px'}),

            # Section to remove selected edges
            html.Div([
                html.Button('Remover Arestas Selecionadas', id='btn-remove-selected-edges', n_clicks=0, style={'marginRight': '10px'})
            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '20px'}),

            # Section to remove all selected elements
            html.Div([
                html.Button('Remover Todos os Selecionados', id='btn-remove-all-selected', n_clicks=0, style={'marginRight': '10px', 'backgroundColor': '#FF4136', 'color': 'white'})
            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '20px'}),

            # Section to modify colors
            html.H3('Modificar Cores'),
            # Color selection via Dropdown
            html.Div([
                html.Label('Escolha a cor:'),
                dcc.Dropdown(
                    id='dropdown-color',
                    options=[
                        {'label': 'Vermelho', 'value': '#FF0000'},
                        {'label': 'Verde', 'value': '#00FF00'},
                        {'label': 'Azul', 'value': '#0000FF'},
                        {'label': 'Amarelo', 'value': '#FFFF00'},
                        {'label': 'Roxo', 'value': '#800080'},
                        {'label': 'Laranja', 'value': '#FFA500'},
                        {'label': 'Preto', 'value': '#000000'},
                        {'label': 'Cinza', 'value': '#808080'},
                        # Add more colors as needed
                    ],
                    value='#FF5733',  # Default color
                    clearable=False,
                    style={'marginTop': '5px', 'marginBottom': '10px', 'width': '150px'}
                ),
            ], style={'marginBottom': '10px'}),

            # Buttons to modify colors
            html.Div([
                html.Button('Modificar Cor de Nós Selecionados', id='btn-change-color-nodes', n_clicks=0, style={'marginBottom': '10px'}),
                html.Button('Modificar Cor de Arestas Selecionadas', id='btn-change-color-edges', n_clicks=0, style={'marginBottom': '10px'}),
                html.Button('Modificar Cor de Todos Itens Selecionados', id='btn-change-color-items', n_clicks=0, style={'marginBottom': '10px'}),
            ], style={'display': 'flex', 'flexDirection': 'column'}),

            # Section to display graph information
            html.H3('Informações do Grafo'),
            html.Div([
                html.P(id='graph-info-nodes', children='Número de Vértices: 0'),
                html.P(id='graph-info-edges', children='Número de Arestas: 0'),
                html.P(id='graph-info-directed', children='Orientado: Não'),
                html.P(id='graph-info-weighted', children='Ponderado: Não'),
            ], style={'marginTop': '20px'}),

            # Button to toggle graph type
            html.Div([
                html.Button('Alternar Tipo de Grafo', id='btn-toggle-directedness', n_clicks=0, style={'width': '100%', 'padding': '10px', 'backgroundColor': '#0074D9', 'color': 'white'})
            ], style={'marginTop': '30px'}),

            # Add this within the left column Div in app.layout

            # Button to toggle weightedness
            html.Div([
                html.Button(
                    'Alternar Grafos Ponderados',
                    id='btn-toggle-weighted',
                    n_clicks=0,
                    style={
                        'width': '100%',
                        'padding': '10px',
                        'backgroundColor': '#FF851B',
                        'color': 'white',
                        'marginTop': '10px'
                    }
                )
            ], style={'marginTop': '20px'}),
            html.Div([
                html.Button(
                    'Exportar como Json',
                    id='btn-export',
                    n_clicks=0,
                    style={
                        'width': '100%',
                        'padding': '10px',
                        'backgroundColor': '#000000',
                        'color': 'white',
                        'marginTop': '10px'
                    }
                )
            ], style={'marginTop': '20px'})


        ], style={
            'width': '30%',              # Set left column width
            'padding': '20px',           # Internal padding
            'boxSizing': 'border-box'    # Include padding in width
        }),
        dcc.Download(id='download-json'),
        # Right Column: Contains the graph with border
        html.Div([
            cyto.Cytoscape(
                id='cytoscape-grafo',
                elements=elements,
                layout={'name': 'preset'},
                style={'width': '100%', 'height': '800px'},
                stylesheet=[
                    # Node styles
                    {
                        'selector': 'node',
                        'style': {
                            'content': 'data(label)',
                            'text-valign': 'center',
                            'text-halign': 'center',
                            'width': '70px',
                            'height': '70px',
                            'font-size': '20px',
                            'background-color': 'data(color)',  # Use color from data
                            'color': 'white',
                            'border-width': '2px',
                            'border-color': '#001f3f',
                            'shape': 'ellipse',
                            'selectable': 'True',
                        }
                    },
                    {
                        'selector': 'node:selected',
                        'style': {
                            'border-width': '4px',
                            'border-color': 'yellow'
                        }
                    },
                    # Edge styles (initially undirected)
                    {
                        'selector': 'edge',
                        'style': {
                            'curve-style': 'bezier',
                            'width': 2,
                            'line-color': 'data(color)',  # Use color from data
                            'target-arrow-shape': 'none',  # No arrow initially
                            'target-arrow-color': 'data(color)',
                            'arrow-scale': 1,
                            'selectable': 'True',
                            'content': 'data(label)',       # Display edge labels for weights
                            'font-size': '12px',            # Adjust font size for readability
                            'text-rotation': 'autorotate',  # Rotate text to align with edge direction
                            'text-margin-y': '-10px',        # Position label above the edge
                            'text-background-color': '#ffffff',  # Optional: Add background to text for better visibility
                            'text-background-opacity': 0.7,      # Optional: Set background opacity
                            'text-background-padding': '3px',    # Optional: Add padding around text
                        }
                    },
                    {
                        'selector': 'edge:selected',
                        'style': {
                            'line-color': 'red',
                            'target-arrow-color': 'red'
                        }
                    }
                ]
            )
            
        ], style={
            'width': '70%',                # Set right column width
            'border': '2px solid #001f3f',# Add border to the graph div
            'padding': '20px',             # Internal padding
            'boxSizing': 'border-box'      # Include padding in width
        })
    ], style={
        'display': 'flex',                 # Set flex layout
        'flexDirection': 'row',            # Horizontal layout for columns
        'height': '100vh'                   # Full viewport height
    }),

    # Store component for selected items (nodes and edges)
    dcc.Store(id='store-selected-items', data={'nodes': [], 'edges': []}),

    # Store component for graph type (directed or undirected)
    dcc.Store(id='store-graph-type', data={'directed': is_directed}),

    # Add this alongside other Store components in app.layout

    # Store component for graph weightedness
    dcc.Store(id='store-graph-weighted', data={'weighted': False}),


    # Error dialog to display messages
    dcc.ConfirmDialog(
        id='error-dialog',
        message=''
    ),

])

# Helper function to reconstruct the NetworkX graph from Cytoscape elements
def reconstruct_graph_from_elements(elements_data, directed=False):
    """
    Reconstructs a NetworkX graph from Cytoscape elements.
    
    Parameters:
    - elements_data (list): List of Cytoscape elements.
    - directed (bool): If True, creates a DiGraph. Otherwise, Graph.
    
    Returns:
    - G (networkx.Graph or networkx.DiGraph): Reconstructed graph.
    """
    if directed:
        G = nx.DiGraph()
    else:
        G = nx.Graph()

    # Reconstruct nodes
    for element in elements_data:
        if 'source' not in element['data']:
            node_id = element['data']['id']
            label = element['data'].get('label', node_id)
            group = element['data'].get('group', 0)
            color = element['data'].get('color', '#0074D9')  # Default color
            G.add_node(node_id, label=label, group=group, color=color)

    # Reconstruct edges
    for element in elements_data:
        if 'source' in element['data']:
            source = element['data']['source']
            target = element['data']['target']
            color = element['data'].get('color', '#ccc')  # Default color
            weight = element['data'].get('weight', None)  # Optional weight
            if weight is not None:
                G.add_edge(source, target, color=color, weight=weight)
            else:
                G.add_edge(source, target, color=color)

    return G

# Callback to update the selection list (nodes and edges)
@app.callback(
    Output('store-selected-items', 'data'),
    [Input('cytoscape-grafo', 'selectedNodeData'),
     Input('cytoscape-grafo', 'selectedEdgeData'),
     Input('btn-clear-selection', 'n_clicks')],
    [State('store-selected-items', 'data'),
     State('cytoscape-grafo', 'elements'),
     State('store-graph-type', 'data')]
)
def update_selection_list(selectedNodeData, selectedEdgeData, n_clicks_clear, selection_data, elements_data, graph_type):
    """
    Updates the list of selected items (nodes and edges) based on user interactions.
    """
    directed = graph_type['directed']
    ctx = callback_context
    if not ctx.triggered:
        return selection_data

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'btn-clear-selection':
        return {'nodes': [], 'edges': []}

    # Reconstruct the graph to get current nodes and edges
    G = reconstruct_graph_from_elements(elements_data, directed=directed)
    existing_nodes = set(G.nodes)
    existing_edges = set(G.edges())

    # Update selection by removing items that no longer exist
    selection_nodes = [node_id for node_id in selection_data['nodes'] if node_id in existing_nodes]
    selection_edges = [edge_id for edge_id in selection_data['edges'] if edge_id in existing_edges]

    if triggered_id == 'cytoscape-grafo':
        # Current list of selected node IDs
        new_selected_nodes = [node['id'] for node in selectedNodeData] if selectedNodeData else []
        # Current list of selected edge IDs
        new_selected_edges = [edge['id'] for edge in selectedEdgeData] if selectedEdgeData else []

        # Nodes added to selection
        added_nodes = [node_id for node_id in new_selected_nodes if node_id not in selection_nodes]
        # Nodes removed from selection
        removed_nodes = [node_id for node_id in selection_nodes if node_id not in new_selected_nodes]

        # Edges added to selection
        added_edges = [edge_id for edge_id in new_selected_edges if edge_id not in selection_edges]
        # Edges removed from selection
        removed_edges = [edge_id for edge_id in selection_edges if edge_id not in new_selected_edges]

        # Update the selection lists
        for node_id in added_nodes:
            selection_nodes.append(node_id)
        for node_id in removed_nodes:
            selection_nodes.remove(node_id)

        for edge_id in added_edges:
            selection_edges.append(edge_id)
        for edge_id in removed_edges:
            selection_edges.remove(edge_id)

    # Update the selection with nodes and edges
    return {'nodes': selection_nodes, 'edges': selection_edges}
@app.callback(
    Output("download-json", "data"),
    Input("btn-export", "n_clicks"),
    State("cytoscape-grafo", "elements"),
    prevent_initial_call=True  # Prevents the callback from firing when the app loads
)
def display_elements_as_json(n_clicks, elements):
    if n_clicks:
        try:
            # Attempt to serialize the elements to JSON
            elements_json = json.dumps(elements, indent=3)
            # Return the JSON content with the specified filename
            return dict(content=elements_json, filename="cytoscape_elements.json")
        except Exception as e:
            # Handle any exceptions that occur during serialization
            error_message = {"error": str(e)}
            error_json = json.dumps(error_message, indent=3)
            return dict(content=error_json, filename="error.json")
# Combined callback to handle adding, removing, and modifying colors of nodes and edges
# Callback to handle adding, removing, modifying, and toggling weightedness of nodes and edges
@app.callback(
    Output('cytoscape-grafo', 'elements'),
    Output('error-dialog', 'displayed'),
    Output('error-dialog', 'message'),
    [
        Input('btn-add-node', 'n_clicks'),
        Input('btn-add-edge', 'n_clicks'),
        Input('btn-add-edges-from-selection', 'n_clicks'),
        Input('btn-remove-node', 'n_clicks'),
        Input('btn-remove-selected-nodes', 'n_clicks'),
        Input('btn-remove-edge', 'n_clicks'),
        Input('btn-remove-selected-edges', 'n_clicks'),
        Input('btn-remove-all-selected', 'n_clicks'),
        Input('btn-change-color-nodes', 'n_clicks'),
        Input('btn-change-color-edges', 'n_clicks'),
        Input('btn-change-color-items', 'n_clicks'),
        Input('btn-toggle-directedness', 'n_clicks'),
        Input('btn-toggle-weighted', 'n_clicks'),

    ],
    [
        State('cytoscape-grafo', 'elements'),
        State('input-node-name', 'value'),
        State('input-source-node', 'value'),
        State('input-target-node', 'value'),
        State('input-node-remove', 'value'),
        State('input-edge-source-remove', 'value'),
        State('input-edge-target-remove', 'value'),
        State('dropdown-color', 'value'),
        State('store-selected-items', 'data'),
        State('store-graph-type', 'data'),
        State('store-graph-weighted', 'data'),
    ],
    prevent_initial_call=True
)
def update_graph(
    btn_add_node_clicks, btn_add_edge_clicks, btn_add_edges_selection_clicks,
    btn_remove_node_clicks, btn_remove_selected_nodes_clicks,
    btn_remove_edge_clicks, btn_remove_selected_edges_clicks,
    btn_remove_all_selected_clicks,
    btn_change_color_nodes_clicks, btn_change_color_edges_clicks,
    btn_change_color_items_clicks, btn_toggle_directedness_clicks,
    btn_toggle_weighted_clicks,
    elements_data, node_label, source_node, target_node, node_to_remove,
    edge_source_remove, edge_target_remove,
    selected_color, selection_data, graph_type, graph_weighted
):
    """
    Updates the graph based on user interactions, including toggling weightedness.
    """
    directed = graph_type['directed']
    weighted = graph_weighted.get('weighted', False)  # Current weighted state
    ctx = callback_context

    if not ctx.triggered:
        return elements_data, False, ''

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Reconstruct the NetworkX graph from current elements
    G = reconstruct_graph_from_elements(elements_data, directed=directed)

    try:
        if triggered_id == 'btn-add-node':
            if node_label:
                node_label = node_label.strip()
                G = graph_manager.add_node(G, node_label)
                elements = graph_manager.networkx_to_cytoscape(G)
                return elements, False, ''
            else:
                return elements_data, True, 'Por favor, insira o nome do nó.'

        elif triggered_id == 'btn-add-edge':
            if source_node and target_node:
                source_node = source_node.strip()
                target_node = target_node.strip()
                G = graph_manager.add_edge(G, source_node, target_node)
                elements = graph_manager.networkx_to_cytoscape(G)
                return elements, False, ''
            else:
                return elements_data, True, 'Por favor, insira os IDs dos nós de origem e destino.'

        elif triggered_id == 'btn-add-edges-from-selection':
            if not selection_data['nodes'] or len(selection_data['nodes']) < 2:
                return elements_data, True, 'Por favor, selecione pelo menos dois nós.'
            error_messages = []
            for i in range(len(selection_data['nodes']) - 1):
                source = selection_data['nodes'][i]
                target = selection_data['nodes'][i + 1]
                try:
                    G = graph_manager.add_edge(G, source, target)
                except nx.NetworkXError as e:
                    error_messages.append(str(e))
            elements = graph_manager.networkx_to_cytoscape(G)
            if error_messages:
                return elements, True, '\n'.join(error_messages)
            else:
                return elements, False, ''

        elif triggered_id == 'btn-remove-node':
            if node_to_remove:
                node_to_remove = node_to_remove.strip()
                G = graph_manager.remove_node(G, node_to_remove)
                elements = graph_manager.networkx_to_cytoscape(G)
                return elements, False, ''
            else:
                return elements_data, True, 'Por favor, insira o ID do nó a ser removido.'

        elif triggered_id == 'btn-remove-selected-nodes':
            if selection_data['nodes']:
                error_messages = []
                for node_id in selection_data['nodes'].copy():
                    try:
                        G = graph_manager.remove_node(G, node_id)
                    except nx.NetworkXError as e:
                        error_messages.append(str(e))
                elements = graph_manager.networkx_to_cytoscape(G)
                if error_messages:
                    return elements, True, '\n'.join(error_messages)
                else:
                    return elements, False, ''
            else:
                return elements_data, True, 'Nenhum nó selecionado para remover.'

        elif triggered_id == 'btn-remove-edge':
            if edge_source_remove and edge_target_remove:
                edge_source_remove = edge_source_remove.strip()
                edge_target_remove = edge_target_remove.strip()
                if directed:
                    edge_id = f"{edge_source_remove}->{edge_target_remove}"
                else:
                    sorted_nodes = sorted([edge_source_remove, edge_target_remove])
                    edge_id = f"{sorted_nodes[0]}-{sorted_nodes[1]}"
                try:
                    G = graph_manager.remove_edge(G, edge_source_remove, edge_target_remove)
                    elements = graph_manager.networkx_to_cytoscape(G)
                    return elements, False, ''
                except nx.NetworkXError as e:
                    return elements_data, True, str(e)
            else:
                return elements_data, True, 'Por favor, insira os IDs dos nós de origem e destino da aresta a remover.'

        elif triggered_id == 'btn-remove-selected-edges':
            if selection_data['edges']:
                error_messages = []
                for edge_id in selection_data['edges'].copy():
                    try:
                        if directed:
                            source, target = edge_id.split('->')
                        else:
                            source, target = edge_id.split('-')
                        G = graph_manager.remove_edge(G, source, target)
                    except nx.NetworkXError as e:
                        error_messages.append(str(e))
                elements = graph_manager.networkx_to_cytoscape(G)
                if error_messages:
                    return elements, True, '\n'.join(error_messages)
                else:
                    return elements, False, ''
            else:
                return elements_data, True, 'Nenhuma aresta selecionada para remover.'

        elif triggered_id == 'btn-remove-all-selected':
            error_messages = []
            # Remove selected nodes
            if selection_data['nodes']:
                for node_id in selection_data['nodes'].copy():
                    try:
                        G = graph_manager.remove_node(G, node_id)
                    except nx.NetworkXError as e:
                        error_messages.append(str(e))
            # Remove selected edges
            if selection_data['edges']:
                for edge_id in selection_data['edges'].copy():
                    try:
                        if directed:
                            source, target = edge_id.split('->')
                        else:
                            source, target = edge_id.split('-')
                        G = graph_manager.remove_edge(G, source, target)
                    except nx.NetworkXError as e:
                        error_messages.append(str(e))
            elements = graph_manager.networkx_to_cytoscape(G)
            if error_messages:
                return elements, True, '\n'.join(error_messages)
            else:
                return elements, False, ''

        elif triggered_id == 'btn-change-color-nodes':
            if selected_color:
                # Create a deep copy to ensure Dash detects the changes
                new_elements = copy.deepcopy(elements_data)
                for element in new_elements:
                    if 'source' not in element['data']:
                        node_id = element['data']['id']
                        if node_id in selection_data['nodes']:
                            element['data']['color'] = selected_color
                return new_elements, False, ''
            else:
                return elements_data, True, 'Por favor, selecione uma cor.'

        elif triggered_id == 'btn-change-color-edges':
            if selected_color:
                # Create a deep copy to ensure Dash detects the changes
                new_elements = copy.deepcopy(elements_data)
                for element in new_elements:
                    if 'source' in element['data']:
                        edge_id = element['data']['id']
                        if edge_id in selection_data['edges']:
                            element['data']['color'] = selected_color
                return new_elements, False, ''
            else:
                return elements_data, True, 'Por favor, selecione uma cor.'

        elif triggered_id == 'btn-change-color-items':
            if selected_color:
                # Create a deep copy to ensure Dash detects the changes
                new_elements = copy.deepcopy(elements_data)
                for element in new_elements:
                    if 'source' not in element['data']:
                        node_id = element['data']['id']
                        if node_id in selection_data['nodes']:
                            element['data']['color'] = selected_color
                    else:
                        edge_id = element['data']['id']
                        if edge_id in selection_data['edges']:
                            element['data']['color'] = selected_color
                return new_elements, False, ''
            else:
                return elements_data, True, 'Por favor, selecione uma cor.'

        elif triggered_id == 'btn-toggle-directedness':
            # Toggle the graph type
            new_directed = not directed
            if new_directed:
                G = G.to_directed()
            else:
                G = G.to_undirected()
            elements = graph_manager.networkx_to_cytoscape(G)
            return elements, False, ''

        elif triggered_id == 'btn-toggle-weighted':
            # Toggle the weightedness
            weighted = not weighted
            if weighted:
                # Assign a default weight to all edges if not already weighted
                for u, v, data in G.edges(data=True):
                    if 'weight' not in data:
                        data['weight'] = 1.0  
            else:
                # Remove weights from all edges
                for u, v in G.edges():
                    if 'weight' in G.edges[u, v]:
                        del G.edges[u, v]['weight']
            # Convert the graph back to Cytoscape elements
            elements = graph_manager.networkx_to_cytoscape(G)
            return elements, False, ''


        else:
            return elements_data, False, ''

    except nx.NetworkXError as e:
        # In case of error, display the error message
        return elements_data, True, str(e)

    # For any other case, return the elements unchanged
    return elements_data, False, ''


# Callback to toggle the graph type in the store
@app.callback(
    Output('store-graph-type', 'data'),
    Input('btn-toggle-directedness', 'n_clicks'),
    State('store-graph-type', 'data'),
    prevent_initial_call=True
)
def toggle_graph_type(n_clicks, graph_type):
    if n_clicks:
        graph_type['directed'] = not graph_type['directed']
    return graph_type

# Add this new callback to handle updating the weighted store

@app.callback(
    Output('store-graph-weighted', 'data'),
    Input('btn-toggle-weighted', 'n_clicks'),
    State('store-graph-weighted', 'data'),
    prevent_initial_call=True
)
def toggle_weighted(n_clicks, graph_weighted):
    """
    Toggles the weightedness of the graph and updates the store.
    """
    if n_clicks:
        graph_weighted['weighted'] = not graph_weighted['weighted']
    return graph_weighted


# Callback to update the Cytoscape stylesheet based on graph type
@app.callback(
    Output('cytoscape-grafo', 'stylesheet'),
    Input('store-graph-type', 'data')
)
def update_stylesheet(graph_type):
    """
    Updates the Cytoscape stylesheet to show arrows if the graph is directed.
    """
    directed = graph_type['directed']
    if directed:
        stylesheet = [
            # Node styles
            {
                'selector': 'node',
                'style': {
                    'content': 'data(label)',
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'width': '70px',
                    'height': '70px',
                    'font-size': '20px',
                    'background-color': 'data(color)',
                    'color': 'white',
                    'border-width': '2px',
                    'border-color': '#001f3f',
                    'shape': 'ellipse',
                    'selectable': 'True',
                }
            },
            {
                'selector': 'node:selected',
                'style': {
                    'border-width': '4px',
                    'border-color': 'yellow'
                }
            },
            # Directed edge styles
            {
                'selector': 'edge',
                'style': {
                    'curve-style': 'bezier',
                    'width': 2,
                    'line-color': 'data(color)',
                    'target-arrow-shape': 'triangle',
                    'target-arrow-color': 'data(color)',
                    'arrow-scale': 1,
                    'selectable': 'True',
                    'content': 'data(label)',       # Display edge labels for weights
                    'font-size': '12px',            # Adjust font size for readability
                    'text-rotation': 'autorotate',  # Rotate text to align with edge direction
                    'text-margin-y': '-10px',        # Position label above the edge
                    'text-background-color': '#ffffff',  # Optional: Add background to text for better visibility
                    'text-background-opacity': 0.7,      # Optional: Set background opacity
                    'text-background-padding': '3px',    # Optional: Add padding around text
                }
            },
            {
                'selector': 'edge:selected',
                'style': {
                    'line-color': 'red',
                    'target-arrow-color': 'red'
                }
            }
        ]
    else:
        stylesheet = [
            # Node styles
            {
                'selector': 'node',
                'style': {
                    'content': 'data(label)',
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'width': '70px',
                    'height': '70px',
                    'font-size': '20px',
                    'background-color': 'data(color)',
                    'color': 'white',
                    'border-width': '2px',
                    'border-color': '#001f3f',
                    'shape': 'ellipse',
                    'selectable': 'True',
                }
            },
            {
                'selector': 'node:selected',
                'style': {
                    'border-width': '4px',
                    'border-color': 'yellow'
                }
            },
            # Undirected edge styles
            {
                'selector': 'edge',
                'style': {
                    'curve-style': 'bezier',
                    'width': 2,
                    'line-color': 'data(color)',
                    'target-arrow-shape': 'none',
                    'target-arrow-color': 'data(color)',
                    'arrow-scale': 1,
                    'selectable': 'True',
                    'content': 'data(label)',       # Display edge labels for weights
                    'font-size': '12px',            # Adjust font size for readability
                    'text-rotation': 'autorotate',  # Rotate text to align with edge direction
                    'text-margin-y': '-10px',        # Position label above the edge
                    'text-background-color': '#ffffff',  # Optional: Add background to text for better visibility
                    'text-background-opacity': 0.7,      # Optional: Set background opacity
                    'text-background-padding': '3px',    # Optional: Add padding around text
                }
            },
            {
                'selector': 'edge:selected',
                'style': {
                    'line-color': 'red',
                    'target-arrow-color': 'red'
                }
            }
        ]
    return stylesheet


# Callback to update graph information
@app.callback(
    [Output('graph-info-nodes', 'children'),
     Output('graph-info-edges', 'children'),
     Output('graph-info-directed', 'children'),
     Output('graph-info-weighted', 'children')],
    [Input('cytoscape-grafo', 'elements'),
     Input('store-graph-type', 'data'),
     Input('store-graph-weighted', 'data')]  # Adicionado
)
def update_graph_info(elements_data, graph_type, graph_weighted):
    """
    Updates the graph information displayed in the interface, incluindo o estado ponderado.
    """
    directed = graph_type['directed']
    weighted = graph_weighted.get('weighted', False)
    G = reconstruct_graph_from_elements(elements_data, directed=directed)

    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    is_directed = G.is_directed()
    has_weights = weighted and any('weight' in data for _, _, data in G.edges(data=True))

    directed_text = 'Sim' if is_directed else 'Não'
    weighted_text = 'Sim' if has_weights else 'Não'

    return (
        f"Número de Vértices: {num_nodes}",
        f"Número de Arestas: {num_edges}",
        f"Orientado: {directed_text}",
        f"Ponderado: {weighted_text}"
    )



if __name__ == '__main__':
    app.run_server(debug=True)
