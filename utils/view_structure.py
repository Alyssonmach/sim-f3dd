import streamlit as st
import plotly.graph_objects as go
import numpy as np
import random
import pyvista as pv

def generate_color():
    '''
    Gera uma cor RGB aleatória para representar uma camada.

    Args:
        None
    
    Returns:
        list: Lista com valores RGB normalizados (0-1)
    '''
    return [random.randint(50, 255) / 255 for _ in range(3)]  # Valores normalizados (0-1)

def plot_structure(modelspace_list: list) -> list:
    '''
    Plota as ligações das estruturas.

    Args:
            modelspace_list (list): Lista contendo as informações da estrutura.
    
    Returns:
        None
    '''
    
    plotter = pv.Plotter()
    
    
    points, lines = list(), list()

    ponto_to_index = dict()
    index = 0

    for element in modelspace_list:
        for ponto in [element['start_point'], element['end_point']]:
            ponto_tuple = tuple(ponto)  # Garantir que seja um hashable
            if ponto_tuple not in ponto_to_index:
                ponto_to_index[ponto_tuple] = index
                points.append(ponto)
                index += 1
    
    for element in modelspace_list:
        start_idx = ponto_to_index[tuple(element['start_point'])]
        end_idx = ponto_to_index[tuple(element['end_point'])]
        lines.append([2, start_idx, end_idx])  # '2' significa linha entre dois pontos

    points = np.array(points)
    lines = np.array(lines)

    poly_data = pv.PolyData(points)
    poly_data.lines = lines

    plotter.add_mesh(poly_data, color = 'blue', line_width = 2)
    plotter.add_points(points, color = 'red', point_size = 10)

    plotter.show()

def plot_conexions_by_layers(layers_dict: dict):
    '''
    Plota os pontos e ligações em 3D usando PyVista, separando por camada com cores distintas.

    Args:
        layers_dict (dict): Dicionário com as ligações da estrutura separadas por camadas.

    Returns:
        None
    '''
    
    plotter = pv.Plotter()
    layer_colors = {layer: generate_color() for layer in layers_dict}

    for layer, conexions in layers_dict.items():
        points, lines = list(), list()
        point_to_index = dict()
        index = 0

        for conexion in conexions:
            for ponto in [conexion['start_point'], conexion['end_point']]:
                point_tuple = tuple(ponto)
                if point_tuple not in point_to_index:
                    point_to_index[point_tuple] = index
                    points.append(ponto)
                    index += 1
        
        for conexion in conexions:
            start_idx = point_to_index[tuple(conexion['start_point'])]
            end_idx = point_to_index[tuple(conexion['end_point'])]
            lines.append([2, start_idx, end_idx])  # '2' indica uma linha entre dois pontos

        points = np.array(points)
        lines = np.array(lines)

        poly_data = pv.PolyData(points)
        poly_data.lines = lines

        color = layer_colors[layer]

        plotter.add_mesh(poly_data, color = color, line_width = 3, label = layer)
        plotter.add_points(points, color = color, point_size = 10)

    plotter.add_legend()
    plotter.show()

def plot_by_nodes_and_conexions(nodes_list, conexions_list):
    '''
    Visualiza a estrutura em 3D com PyVista, com base na lista de nós e conexões.

    Args:
        nodes_list (list): Lista de nós no formato [[ID, X, Y, Z], ...]
        conexions_list (list): Lista de ligações no formato [[ID_NO, ID1, ID2], ...]
    '''

    plotter = pv.Plotter()
    
    points = np.array([no[1:] for no in nodes_list])  # Apenas coordenadas X, Y, Z
    structure = pv.PolyData(points)

    lines = []
    for ligacao in conexions_list:
        _, id1, id2 = ligacao  # Ignorar ID da ligação, pegar apenas os nós
        lines.extend([2, id1 - 1, id2 - 1])  # "2" indica uma linha conectando dois pontos

    structure.lines = lines

    plotter.add_mesh(structure, color = 'black', line_width = 2)

    for node in nodes_list:
        id_node, x, y, z = node
        sphere = pv.Sphere(radius = 0.05, center = (x, y, z))
        plotter.add_mesh(sphere, color = 'red')
        #plotter.add_point_labels(points=[[x, y, z]], labels=[str(id_node)], point_size=20, text_color='black')

    plotter.show_grid()
    plotter.view_xy()  # Vista superior
    plotter.show()

def plot_by_nodes_and_conexions_streamlit(nodes_list, conexions_list):
    '''
    Visualiza a estrutura em 3D com Plotly e Streamlit, com base na lista de nós e conexões.

    Args:
        nodes_list (list): Lista de nós no formato [[ID, X, Y, Z], ...]
        conexions_list (list): Lista de ligações no formato [[ID_NO, ID1, ID2], ...]
    
    Returns:
        fig (go.Figure): Figura com a estrutura visualizada.
    '''

    # Extraindo coordenadas dos nós
    points = np.array([no[1:] for no in nodes_list])  # Apenas coordenadas X, Y, Z

    # Criando a figura
    fig = go.Figure()

    # Adicionando nós como esferas vermelhas
    fig.add_trace(go.Scatter3d(
        x=points[:, 0], y=points[:, 1], z=points[:, 2],
        mode='markers',
        marker=dict(size=3, color='red'),  # Reduzindo o tamanho dos marcadores
        name='Nós'
    ))

    # Adicionando conexões como linhas pretas
    x_lines, y_lines, z_lines = [], [], []
    for ligacao in conexions_list:
        _, id1, id2 = ligacao  # Ignorar ID da ligação, pegar apenas os nós
        x_lines.extend([points[id1 - 1, 0], points[id2 - 1, 0], None])
        y_lines.extend([points[id1 - 1, 1], points[id2 - 1, 1], None])
        z_lines.extend([points[id1 - 1, 2], points[id2 - 1, 2], None])

    fig.add_trace(go.Scatter3d(
        x=x_lines, y=y_lines, z=z_lines,
        mode='lines',
        line=dict(color='black', width=1),  # Reduzindo a largura das linhas
        name='Conexões'
    ))

    # Configurando a visualização
    fig.update_layout(
        scene=dict(
            xaxis=dict(title='X', showgrid=False),
            yaxis=dict(title='Y', showgrid=False),
            zaxis=dict(title='Z', showgrid=False),
            aspectmode='data',
            camera=dict(
                eye=dict(x=0, y=3.5, z=0)  # Configurando a câmera para visualização frontal (eixos X e Z)
            )
        ),
        title='Visualização da Estrutura',
        showlegend=False,
        margin=dict(l=0, r=0, b=0, t=40),  # Reduzindo as margens
        width=1200,  # Aumentando a largura da figura
        height=800   # Aumentando a altura da figura
    )

    return fig

def plot_by_layers_streamlit(nodes_list, conexions_list, layers_dict):
    '''
    Visualiza a estrutura em 3D com Plotly e Streamlit, separando os elementos por camadas.

    Args:
        nodes_list (list): Lista de nós no formato [[ID, X, Y, Z], ...]
        conexions_list (list): Lista de ligações no formato [[ID_NO, ID1, ID2], ...]
        layers_dict (dict): Dicionário com as ligações da estrutura separadas por camadas.
    
    Returns:
        fig (go.Figure): Figura com a estrutura visualizada.
    '''

    # Extraindo coordenadas dos nós
    points = np.array([no[1:] for no in nodes_list])  # Apenas coordenadas X, Y, Z
    node_labels = [str(no[0]) for no in nodes_list]  # IDs dos nós como texto
    # Criando a figura
    fig = go.Figure()

    # Adicionando nós como esferas vermelhas
    fig.add_trace(go.Scatter3d(
        x=points[:, 0], y=points[:, 1], z=points[:, 2],
        mode='markers',
        marker=dict(size=2, color='black'),
        name='Nós'
    ))

    # Adicionando conexões por camada
    layer_colors = {layer: generate_color() for layer in layers_dict}
    for layer, conexions in layers_dict.items():
        x_lines, y_lines, z_lines = [], [], []
        for conexion in conexions:
            start_point = conexion['start_point']
            end_point = conexion['end_point']
            x_lines.extend([start_point[0], end_point[0], None])
            y_lines.extend([start_point[1], end_point[1], None])
            z_lines.extend([start_point[2], end_point[2], None])
        
        fig.add_trace(go.Scatter3d(
            x=x_lines, y=y_lines, z=z_lines,
            mode='lines',
            line=dict(color=f'rgb({layer_colors[layer][0]*255}, {layer_colors[layer][1]*255}, {layer_colors[layer][2]*255})', width=2),
            name=f'Conexões {layer}'
        ))


    # Configurando a visualização
    fig.update_layout(
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z',
            aspectmode='data',
            camera=dict(
                eye=dict(x=0, y=3.5, z=0)  # Configurando a câmera para visualização frontal (eixos X e Z)
            )
        ),
        title='Visualização da Estrutura por Camadas',
        showlegend=True,
        margin=dict(l=0, r=0, b=0, t=40),  # Reduzindo as margens
        width=1200,  # Aumentando a largura da figura
        height=800   # Aumentando a altura da figura
    )

    return fig

