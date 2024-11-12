import dash
import dash_cytoscape as cyto
from dash import html, dcc
from dash.dependencies import Input, Output, State
from dash import callback_context
import networkx as nx
import graph_manager
import copy
import json
from graph_manager import reconstruct_graph_from_elements

with open('cytoscape_elements(2).json') as f:
    graph_data = json.load(f)

is_directed = False


nodes = [item for item in graph_data if 'source' not in item['data']]
edges = [item for item in graph_data if 'source' in item['data']]
elements = nodes + edges
elements = []

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Visualização Interativa de Grafo com Dash Cytoscape'),
    # Main Div
    html.Div([
        # Left Column
        html.Div([
            html.Div([
                dcc.Input(
                    id='input-node-name',
                    type='text',
                    placeholder='Nome do novo nó',
                    style={'marginRight': '10px'}
                ),
                html.Button('Adicionar Nó', id='btn-add-node', n_clicks=0),
                html.Button('Remover Nó', id='btn-remove-node', n_clicks=0),
                html.Button('BFS', id='btn-bfs', n_clicks=0),
                html.Button('DFS', id='btn-dfs', n_clicks=0)
            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '20px'}),

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
                html.Button('Adicionar Aresta', id='btn-add-edge', n_clicks=0),
                html.Button('Remover Aresta', id='btn-remove-edge', n_clicks=0),
                html.Button('Dijkstra', id='btn-dijkstra', n_clicks=0),
                html.Button('Bellman Ford', id='btn-bellman-ford', n_clicks=0),
            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '20px'}),

            html.Div([
                html.Button('Adicionar Arestas da Seleção', id='btn-add-edges-from-selection', n_clicks=0, style={'marginRight': '10px'}),
                html.Button('Remover Todos os Selecionados', id='btn-remove-all-selected', n_clicks=0, style={'marginRight': '10px', 'backgroundColor': '#FF4136', 'color': 'white'})
            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '20px'}),

            html.Div([
                dcc.Input(
                    id='input-weight',
                    type='number',
                    placeholder='Peso da aresta',
                    style={'marginRight': '10px'}
                ),
                html.Button('Alterar Peso das Arestas Selecionadas', id='btn-change-weight-edges', n_clicks=0)
            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '20px'}),

            html.H3('Modificar Cores'),
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
                    ],
                    value='#FF5733',
                    clearable=False,
                    style={'marginTop': '5px', 'marginBottom': '10px', 'width': '150px'}
                ),
            ], style={'marginBottom': '10px'}),

            html.Div([
                html.Button('Modificar Cor de Todos Itens Selecionados', id='btn-change-color-items', n_clicks=0, style={'marginBottom': '10px'})
            ], style={'display': 'flex', 'flexDirection': 'column'}),

            html.H3('Informações do Grafo'),
            html.Div([
                html.P(id='graph-info-nodes', children='Número de Vértices: 0'),
                html.P(id='graph-info-edges', children='Número de Arestas: 0'),
                html.P(id='graph-info-directed', children='Orientado: Não'),
                html.P(id='graph-info-weighted', children='Ponderado: Não'),
            ], style={'marginTop': '20px'}),

            html.Div([
                html.Button('Alternar Tipo de Grafo', id='btn-toggle-directedness', n_clicks=0, style={'width': '100%', 'padding': '10px', 'backgroundColor': '#0074D9', 'color': 'white'})
            ], style={'marginTop': '30px'}),

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
            ], style={'marginTop': '0px'}),
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
            ], style={'marginTop': '0px'})


        ], style={
            'width': '30%',       
            'padding': '20px',          
            'boxSizing': 'border-box'   
        }),
        dcc.Download(id='download-json'),

        # Right Column
        html.Div([
            cyto.Cytoscape(
                id='cytoscape-grafo',
                elements=elements,
                layout={'name': 'preset'},
                style={'width': '100%', 'height': '800px'},
                stylesheet=[
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
                            'content': 'data(label)',       
                            'font-size': '12px',           
                            'text-rotation': 'autorotate',  
                            'text-margin-y': '-10px',        
                            'text-background-color': '#ffffff', 
                            'text-background-opacity': 0.7, 
                            'text-background-padding': '3px',
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
            'width': '70%',            
            'border': '2px solid #001f3f',
            'padding': '20px',            
            'boxSizing': 'border-box'     
        })
    ], style={
        'display': 'flex',               
        'flexDirection': 'row',          
        'height': '90vh'                  
    }),


    dcc.Store(id='store-selected-items', data={'nodes': [], 'edges': []}),

    dcc.Store(id='store-graph-type', data={'directed': is_directed}),

    dcc.Store(id='store-graph-weighted', data={'weighted': False}),

    dcc.Store(id='state-graph', data=elements),

    dcc.Store(id='dijkstra-paths-store'),

    dcc.ConfirmDialog(
        id='error-dialog',
        message=''
    ),
])

@app.callback(
    Output('store-selected-items', 'data'),
    [Input('cytoscape-grafo', 'selectedNodeData'),
     Input('cytoscape-grafo', 'selectedEdgeData')],
    [State('store-selected-items', 'data'),
     State('cytoscape-grafo', 'elements'),
     State('store-graph-type', 'data')]
)
def update_selection_list(selectedNodeData, selectedEdgeData, selection_data, elements_data, graph_type):
    directed = graph_type['directed']
    ctx = callback_context
    if not ctx.triggered:
        return selection_data

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'btn-clear-selection':
        return {'nodes': [], 'edges': []}

    G = reconstruct_graph_from_elements(elements_data, directed=directed)
    existing_nodes = set(G.nodes)
    existing_edges = set(G.edges())

    selection_nodes = [node_id for node_id in selection_data['nodes'] if node_id in existing_nodes]
    selection_edges = [edge_id for edge_id in selection_data['edges'] if edge_id in existing_edges]

    if triggered_id == 'cytoscape-grafo':

        new_selected_nodes = [node['id'] for node in selectedNodeData] if selectedNodeData else []

        new_selected_edges = [edge['id'] for edge in selectedEdgeData] if selectedEdgeData else []

        added_nodes = [node_id for node_id in new_selected_nodes if node_id not in selection_nodes]

        removed_nodes = [node_id for node_id in selection_nodes if node_id not in new_selected_nodes]

        added_edges = [edge_id for edge_id in new_selected_edges if edge_id not in selection_edges]

        removed_edges = [edge_id for edge_id in selection_edges if edge_id not in new_selected_edges]

        for node_id in added_nodes:
            selection_nodes.append(node_id)
        for node_id in removed_nodes:
            selection_nodes.remove(node_id)

        for edge_id in added_edges:
            selection_edges.append(edge_id)
        for edge_id in removed_edges:
            selection_edges.remove(edge_id)

    return {'nodes': selection_nodes, 'edges': selection_edges}


@app.callback(
    Output("download-json", "data"),
    Input("btn-export", "n_clicks"),
    State("cytoscape-grafo", "elements"),
    prevent_initial_call=True
)
def display_elements_as_json(n_clicks, elements):
    if n_clicks:
        try:

            elements_json = json.dumps(elements, indent=3)

            return dict(content=elements_json, filename="cytoscape_elements.json")
        except Exception as e:

            error_message = {"error": str(e)}
            error_json = json.dumps(error_message, indent=3)
            return dict(content=error_json, filename="error.json")

@app.callback(
    Output('cytoscape-grafo', 'elements'),
    Output('error-dialog', 'displayed'),
    Output('error-dialog', 'message'),
    [
        Input('btn-add-node', 'n_clicks'),
        Input('btn-add-edge', 'n_clicks'),
        Input('btn-bfs', 'n_clicks'),
        Input('btn-dfs', 'n_clicks'),
        Input('btn-dijkstra', 'n_clicks'),
        Input('btn-bellman-ford', 'n_clicks'),
        Input('btn-add-edges-from-selection', 'n_clicks'),
        Input('btn-change-weight-edges', 'n_clicks'),
        Input('btn-remove-all-selected', 'n_clicks'),
        Input('btn-change-color-items', 'n_clicks'),
        Input('btn-toggle-directedness', 'n_clicks'),
        Input('btn-toggle-weighted', 'n_clicks'),

    ],
    [
        State('cytoscape-grafo', 'elements'),
        State('input-node-name', 'value'),
        State('input-source-node', 'value'),
        State('input-target-node', 'value'),
        State('input-weight', 'value'),
        State('dropdown-color', 'value'),
        State('store-selected-items', 'data'),
        State('store-graph-type', 'data'),
        State('store-graph-weighted', 'data')
    ],
    prevent_initial_call=True
)
def update_graph(
    btn_add_node_clicks, btn_add_edge_clicks, btn_bfs_clicks, btn_dfs_clicks, btn_dijkstra_clicks, btn_bellman_ford_clicks,
    btn_add_edges_selection_clicks, btn_change_weight_edges,
    btn_remove_all_selected_clicks,
    btn_change_color_items_clicks, btn_toggle_directedness_clicks,
    btn_toggle_weighted_clicks,
    elements_data, node_label, source_node, target_node, input_weight,
    selected_color, selection_data, graph_type, graph_weighted
):
    directed = graph_type['directed']
    weighted = graph_weighted.get('weighted', False)
    ctx = callback_context
    resultado_busca = ""

    if not ctx.triggered:
        return elements_data, False, ''

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    G = reconstruct_graph_from_elements(elements_data, directed=directed)

    try:
        if triggered_id == 'btn-add-node':
            if node_label:
                node_label = node_label.strip()
                G = graph_manager.cyto_add_node(G, node_label)
                
                elements = graph_manager.networkx_to_cytoscape(G)

                return elements, False, ''
            else:
                return elements_data, True, 'Por favor, insira o nome do nó.'

        elif triggered_id == 'btn-remove-node':
            if node_label:
                node_label = node_label.strip()
                G = graph_manager.cyto_remove_node(G, node_label)
                elements = graph_manager.networkx_to_cytoscape(G)
                return elements, False, ''
            else:
                return elements_data, True, 'Por favor, insira o nome do nó a ser removido.'

        elif triggered_id == 'btn-add-edge':
            if source_node and target_node:
                source_node = source_node.strip()
                target_node = target_node.strip()
                G = graph_manager.cyto_add_edge(G, source_node, target_node)
                elements = graph_manager.networkx_to_cytoscape(G)
                return elements, False, ''
            else:
                return elements_data, True, 'Por favor, insira os IDs dos nós de origem e destino.'

        elif triggered_id == 'btn-remove-edge':
            if source_node and target_node:
                source_node = source_node.strip()
                target_node = target_node.strip()
                try:
                    G = graph_manager.cyto_remove_edge(G, source_node, target_node)
                    elements = graph_manager.networkx_to_cytoscape(G)
                    return elements, False, ''
                except nx.NetworkXError as e:
                    return elements_data, True, str(e)
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
                    G = graph_manager.cyto_add_edge(G, source, target)
                except nx.NetworkXError as e:
                    error_messages.append(str(e))
            elements = graph_manager.networkx_to_cytoscape(G)
            if error_messages:
                return elements, True, '\n'.join(error_messages)
            else:
                return elements, False, ''

        elif triggered_id == 'btn-change-weight-edges':
            if selection_data['edges']:
                new_elements = copy.deepcopy(elements_data)
                for element in new_elements:
                    if 'source' in element['data']:
                        edge_id = element['data']['id']
                        if edge_id in selection_data['edges']:
                            element['data']['weight'] = input_weight
                return new_elements, False, ''
            else:
                return elements_data, True, 'Por favor, selecione um peso para alterar.'

        elif triggered_id == 'btn-remove-all-selected':
            error_messages = []

            if selection_data['nodes']:
                for node_id in selection_data['nodes'].copy():
                    try:
                        G = graph_manager.cyto_remove_node(G, node_id)
                    except nx.NetworkXError as e:
                        error_messages.append(str(e))

            if selection_data['edges']:
                for edge_id in selection_data['edges'].copy():
                    try:
                        if directed:
                            source, target = edge_id.split('->')
                        else:
                            source, target = edge_id.split('-')
                        G = graph_manager.cyto_remove_edge(G, source, target)
                    except nx.NetworkXError as e:
                        error_messages.append(str(e))
            elements = graph_manager.networkx_to_cytoscape(G)
            if error_messages:
                return elements, True, '\n'.join(error_messages)
            else:
                return elements, False, ''

        elif triggered_id == 'btn-change-color-items':
            if selected_color:

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

            new_directed = not directed
            if new_directed:
                G = G.to_directed()
            else:
                G = G.to_undirected()
            elements = graph_manager.networkx_to_cytoscape(G)
            return elements, False, ''

        elif triggered_id == 'btn-toggle-weighted':

            weighted = not weighted
            if weighted:

                for u, v, data in G.edges(data=True):
                    if 'weight' not in data:
                        data['weight'] = 1.0
                    data['label'] = str(data['weight'])
            else:

                for u, v, data in G.edges(data=True):
                    data['label'] = '' 

            elements = graph_manager.networkx_to_cytoscape(G)
            return elements, False, ''


        elif triggered_id == 'btn-bfs':
            if node_label:
                node_label = node_label.strip()
                bfs_result = nx.bfs_tree(G, node_label)
                resultado_busca = f"BFS a partir de {node_label}: {list(bfs_result)}"

                bfs_edges = list(bfs_result.edges())
                print(bfs_edges)

                new_elements = copy.deepcopy(elements_data)
                for element in new_elements:
                    if 'source' in element['data'] and 'target' in element['data']:
                        edge = (element['data']['source'], element['data']['target'])
                        if edge in bfs_edges:
                            element['data']['color'] = '#000000'
                        else:
                            element['data']['color'] = "#ccc"
                return new_elements, False, ''
    
        elif triggered_id == 'btn-dfs':
            if node_label:
                node_label = node_label.strip()

                dfs_edges = []
                visited = set()

                is_directed = G.is_directed()

                def add_edges(dfs_edge_list):
                    for edge in dfs_edge_list:
                        if not is_directed:
                            dfs_edges.append(tuple(sorted(edge)))
                        else:
                            dfs_edges.append(edge)

                if node_label in G:
                    edges = list(nx.dfs_edges(G, node_label))
                    add_edges(edges)
                    visited.update([node_label] + [v for _, v in edges])
                else:
                    resultado_busca = f"Node '{node_label}' not found in the graph."
                    return elements_data, False, resultado_busca

                for node in G.nodes():
                    if node not in visited:
                        edges = list(nx.dfs_edges(G, node))
                        add_edges(edges)
                        visited.update([node] + [v for _, v in edges])

                resultado_busca = f"DFS completed. Total DFS edges: {len(dfs_edges)}"

                new_elements = copy.deepcopy(elements_data)
                for element in new_elements:
                    if 'source' in element['data'] and 'target' in element['data']:
                        edge = (element['data']['source'], element['data']['target'])
                        if not is_directed:
                            edge_sorted = tuple(sorted(edge))
                            if edge_sorted in dfs_edges:
                                element['data']['color'] = '#123456'
                            else:
                                element['data']['color'] = "#ccc"
                        else:
                            if edge in dfs_edges:
                                element['data']['color'] = '#123456'
                            else:
                                element['data']['color'] = "#ccc"
            return new_elements, False, ''

        elif triggered_id == 'btn-dijkstra':
            if source_node and target_node:
                source = source_node.strip()
                finish = target_node.strip()

                if source not in G.nodes:
                    return elements_data, True, f"Source node '{source}' does not exist in the graph."

                if finish not in G.nodes:
                    return elements_data, True, f"Finish node '{finish}' does not exist in the graph."

                try:
                    path = nx.dijkstra_path(G, source, finish, weight='weight')
                    length = nx.dijkstra_path_length(G, source, finish, weight='weight')
                    resultado_busca = f"Dijkstra's shortest path from {source} to {finish}: {' -> '.join(path)}\nTotal length: {length}"

                    dijkstra_edges = list(zip(path[:-1], path[1:]))
                    print(f"Dijkstra Edges: {dijkstra_edges}")

                    new_elements = copy.deepcopy(elements_data)

                    for element in new_elements:
                        if 'source' in element['data'] and 'target' in element['data']:
                            element['data']['color'] = '#ccc'

                    for element in new_elements:
                        if 'source' in element['data'] and 'target' in element['data']:
                            edge = (element['data']['source'], element['data']['target'])
                            if edge in dijkstra_edges or (edge[1], edge[0]) in dijkstra_edges:
                                element['data']['color'] = '#AA6600'
                    
                    return new_elements, False, ''
                except nx.NetworkXNoPath:
                    return elements_data, True, f"No path found from {source} to {finish}."
            return elements_data, False, ''

        elif triggered_id == 'btn-bellman-ford':
            if source_node and target_node:
                source = source_node.strip()
                finish = target_node.strip()

                if source not in G.nodes:
                    return elements_data, True, f"Source node '{source}' does not exist in the graph."

                if finish not in G.nodes:
                    return elements_data, True, f"Finish node '{finish}' does not exist in the graph."

                try:
                    path = nx.bellman_ford_path(G, source, finish, weight='weight')
                    length = nx.bellman_ford_path_length(G, source, finish, weight='weight')
                    resultado_busca = f"Dijkstra's shortest path from {source} to {finish}: {' -> '.join(path)}\nTotal length: {length}"

                    bellman_ford_edges = list(zip(path[:-1], path[1:]))
                    print(f"Bellman-Ford Edges: {bellman_ford_edges}")

                    new_elements = copy.deepcopy(elements_data)

                    for element in new_elements:
                        if 'source' in element['data'] and 'target' in element['data']:
                            element['data']['color'] = '#ccc'

                    for element in new_elements:
                        if 'source' in element['data'] and 'target' in element['data']:
                            edge = (element['data']['source'], element['data']['target'])
                            if edge in bellman_ford_edges or (edge[1], edge[0]) in bellman_ford_edges:
                                element['data']['color'] = '#AA6600'
                    
                    return new_elements, False, ''
                except nx.NetworkXNoPath:
                    return elements_data, True, f"No path found from {source} to {finish}."
            return elements_data, False, ''

        if resultado_busca: 
            print(resultado_busca)
        else:
            return elements_data, False, ''

    except nx.NetworkXError as e:
        return elements_data, True, str(e)

    return elements_data, False, ''

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

@app.callback(
    Output('cytoscape-grafo', 'stylesheet'),
    Input('store-graph-type', 'data')
)
def update_stylesheet(graph_type):
    directed = graph_type['directed']
    if directed:
        stylesheet = [
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
                    'content': 'data(label)',     
                    'font-size': '12px',           
                    'text-rotation': 'autorotate',  
                    'text-margin-y': '-10px',       
                    'text-background-color': '#ffffff',  
                    'text-background-opacity': 0.7,      
                    'text-background-padding': '3px',    
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
                    'content': 'data(label)',      
                    'font-size': '12px',           
                    'text-rotation': 'autorotate',  
                    'text-margin-y': '-10px',        
                    'text-background-color': '#ffffff',  
                    'text-background-opacity': 0.7,     
                    'text-background-padding': '3px',   
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

@app.callback(
    [Output('graph-info-nodes', 'children'),
     Output('graph-info-edges', 'children'),
     Output('graph-info-directed', 'children'),
     Output('graph-info-weighted', 'children')],
    [Input('cytoscape-grafo', 'elements'),
     Input('store-graph-type', 'data'),
     Input('store-graph-weighted', 'data')]
)
def update_graph_info(elements_data, graph_type, graph_weighted):
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
