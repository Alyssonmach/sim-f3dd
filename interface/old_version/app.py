import matplotlib.pyplot as plt
import streamlit as st
import pyvista as pv
import numpy as np
import ezdxf
import config

data = config.open_yaml('page_config.yaml')
css_format = config.return_streamlit_config(data)
st.markdown(data, unsafe_allow_html = True)

# Configurando o Streamlit
st.title("SW - Vibra Torre Simulator")

doc = ezdxf.readfile('../models/dxf/ax3-345kv.dxf')
msp = doc.modelspace()

# Dicionários para categorizar nós e ligações por camada
nos_por_camada = {}
ligacoes_por_camada = {}

# Processamento das linhas do arquivo
for entity in msp.query('LINE'):
    # Obtém a camada da entidade
    layer = entity.dxf.layer
    
    # Obtém os pontos de início e fim
    start = (round(entity.dxf.start.x, 2), round(entity.dxf.start.y, 2), round(entity.dxf.start.z, 2))
    end = (round(entity.dxf.end.x, 2), round(entity.dxf.end.y, 2), round(entity.dxf.end.z, 2))
    
    # Inicializa as estruturas para a camada, se necessário
    if layer not in nos_por_camada:
        nos_por_camada[layer] = set()
        ligacoes_por_camada[layer] = []
    
    # Adiciona os nós e ligações à camada correspondente
    nos_por_camada[layer].update([start, end])
    ligacoes_por_camada[layer].append((start, end))

# Converte os conjuntos de nós para listas ordenadas por camada
nos_dict_por_camada = {}
ligacoes_indices_por_camada = {}


for layer, nos in nos_por_camada.items():
    nos = list(nos)
    nos_dict_por_camada[layer] = {n: i for i, n in enumerate(nos)}
    ligacoes_indices_por_camada[layer] = [
        (nos_dict_por_camada[layer][start], nos_dict_por_camada[layer][end])
        for start, end in ligacoes_por_camada[layer]
    ]
# Define cores para as camadas (ciclo de cores do Matplotlib)
colors = plt.cm.tab20(np.linspace(0, 1, len(nos_por_camada)))

layers_labels = {'Pés': ['PÉS_-_MONTANTES, EXTENSÃO_-_MONTANTES', 'PÉS_-_DIAGONAIS_HORIZONTAI', 'PÉS_-_DIAGONAIS_VERTICAIS'],
                 'Extensão': ['EXTENSÃO_-_DIAGONAIS_VERTI', 'EXTENSÃO_-_DIAGONAIS_VERTI', 'EXTENSÃO_-_DIAGONAIS_HORIZ'],
                 'Cabeça': ['CABEÇA_-_DIAGONAIS_HORIZON', 'CABEÇA_-_MONTANTES', 'CABEÇA_-_DIAGONAIS_VERTICA'],
                 'Braço': ['BRAÇO_-_MONTANTES', 'BRAÇO_-_DIAGONAIS_HORIZONT', 'BRAÇO_-_DIAGONAIS_VERTICAI'],
                 'Para Raio': ['PARA_RAIOS_-_MONTANTES','PARA_RAIOS_-_DIAGONAIS_VER'],
                 'Tronco': ['TRONCO_-_DIAGONAIS_HORIZON', 'TRONCO_-_DIAGONAIS_VERTICA', 'TRONCO_-_MONTANTES']}

col1, col2, col3 = st.columns(3)
with col1: para_raios_select = st.selectbox(label = 'Para Raios:', options = ['Nenhum', 'Para Raios 1'], index = 0)
with col2: cabeca_select = st.selectbox(label = 'Cabeças:', options = ['Nenhum', 'Cabeça 1'], index = 0)
with col3: tronco_select = st.selectbox(label = 'Troncos:', options = ['Nenhum', 'Tronco 1'], index = 0)

col1, col2, col3 = st.columns(3)
with col1: braco_select = st.selectbox(label = 'Braços:', options = ['Nenhum', 'Braço 1'],  index = 0)
with col2: extensao_select = st.selectbox(label = 'Extensões:', options = ['Nenhum', 'Extensão 1'], index = 0)
with col3: pes_select = st.selectbox(label = 'Pés:', options = ['Nenhum', 'Pés 1'],  index = 0)

active_labels = list()
if para_raios_select == 'Para Raios 1':
    active_labels.extend(layers_labels['Para Raio'])
if cabeca_select == 'Cabeça 1':
    active_labels.extend(layers_labels['Cabeça'])
if tronco_select == 'Tronco 1':
    active_labels.extend(layers_labels['Tronco'])
if braco_select == 'Braço 1':
    active_labels.extend(layers_labels['Braço'])
if extensao_select == 'Extensão 1':
    active_labels.extend(layers_labels['Extensão'])
if pes_select == 'Pés 1':
    active_labels.extend(layers_labels['Pés'])

# Cria um único plotter para todas as camadas
plotter = pv.Plotter()
for i, (layer, ligacoes) in enumerate(ligacoes_indices_por_camada.items()):
    if layer in active_labels:
        # Converte os dados no formato esperado pelo PyVista
        linhas_formato_pyvista = []
        for linha in ligacoes:
            linhas_formato_pyvista.extend([2, linha[0], linha[1]])  # "2" indica que cada linha conecta dois pontos
        linhas_formato_pyvista = np.array(linhas_formato_pyvista)
        
        # Cria a malha para visualização
        pontos = np.array(list(nos_dict_por_camada[layer].keys()))
        malha = pv.PolyData(pontos)
        malha.lines = linhas_formato_pyvista
        
        # Adiciona a malha ao plotter com cor única para a camada
        plotter.add_mesh(malha, color=colors[i, :3], line_width=2, label=f'Camada {layer}')
        

# Adiciona legenda e mostra o desenho
#plotter.add_legend()

# Renderizando como uma visualização interativa (HTML)
plotter.export_html("render.html")

# Exibindo o HTML no Streamlit
with open("render.html", "r") as f:
    html_content = f.read()

st.components.v1.html(html_content, height = 600, scrolling = True)

