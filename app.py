import streamlit as st 
import unicodedata
import yaml
import os
from utils.view_structure import plot_by_nodes_and_conexions_streamlit, plot_by_layers_streamlit
from utils.make_file import make_3dd
from utils.extract_model import dxf_extraction

yaml_file = 'parameters.yaml'
with open(yaml_file, 'r') as file:
    data = yaml.load(file, Loader = yaml.FullLoader)

def prepare_model(dxf_path: str, layers: list) -> tuple:
    '''
    Função que prepara o modelo para a simulação.

    Args:
        dxf_path (str): Caminho do arquivo dxf.
        layers (list): Lista de camadas a serem consideradas.
    
    Returns:
        tuple: Tupla contendo os nós e conexões do modelo.
    '''

    data = dxf_extraction(model_path = dxf_path)

    msp = data.get_modelspace()

    layers_name = data.get_layers_name()
    modelspace_list = data.extract_modelspace(msp = msp)
    normalized_data = data.normalize_data(modelspace_list = modelspace_list)
    layers_dict = data.separete_by_layers(modelspace_list = normalized_data)
    combination_layers_name = data.combine_layers_names(name_layers = layers_name, ignored_layers = ['0', 'Defpoints'])
    layers_dict_correct = data.combine_layers(layers_dict = layers_dict, new_layers_info = combination_layers_name)

    (nodes, conexions) = data.generate_frame3dd_data(layers_dict = layers_dict_correct, customize_layers = layers)

    return (nodes, conexions, layers_dict_correct)

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

if 'nodes' not in st.session_state or 'conexions' not in st.session_state or 'layers_dict' not in st.session_state:
    (nodes, conexions, layers_dict) = prepare_model(dxf_path = data['model_path'], layers = data['layers'])
    st.session_state['nodes'] = nodes
    st.session_state['conexions'] = conexions
    st.session_state['layers_dict'] = layers_dict
    st.session_state['plotter'] = plot_by_layers_streamlit(nodes_list = nodes, conexions_list = conexions, layers_dict = layers_dict)
else:
    nodes = st.session_state['nodes']
    conexions = st.session_state['conexions']
    layers_dict = st.session_state['layers_dict']
    plotter = st.session_state['plotter']

st.title('Simulador Vibra-torre [Trixel]')

# Renderização da estrutura usando Plotly
plot_by_layers_streamlit(nodes, conexions, layers_dict)

st.warning('A escolha de componentes de torre será adicionada em breve...')
with st.expander('Visualização da Estrutura', expanded = True):
    st.plotly_chart(st.session_state['plotter'], use_container_width=True, key="plotter_chart")

with st.expander('Configuração da Simulação', expanded = True):

    data = dict()

    st.markdown('### Unidades Métricas:')

    simulation_name = st.text_input('Nome da Simulação:', value = 'Simulação de Estrutura', help = 'Nome da simulação')
    force_unit = st.selectbox('Unidade de Força:', ['N'], index = 0, help = 'Unidade de força')
    length_unit = st.selectbox('Unidade de Comprimento:', ['m'], index = 0, help = 'Unidade de comprimento')
    mass_unit = st.selectbox('Unidade de Massa:', ['ton'], index = 0, help = 'Unidade de massa')

    units = {'simulation_name': simulation_name, 'force_unit': force_unit, 'length_unit': length_unit, 'mass_unit': mass_unit}
    data['units'] = units

    st.markdown('### Parâmetros das Barras:')

    Ax = st.text_input('Ax:', value = 0.06452, help = 'Área da seção transversal de um elemento de estrutura prismático')
    Asy = st.text_input('Asy:', value = 0.03871, help = 'Área de cisalhamento no eixo y local de um elemento de estrutura prismático')
    Asz = st.text_input('Asz:', value = 0.03871, help = 'Área de cisalhamento no eixo z local de um elemento de estrutura prismático')
    Jxx = st.text_input('Jxx:', value = 0.0002081, help = 'Momento de inércia torsional de um elemento de estrutura')
    Iyy = st.text_input('Iyy:', value = 0.0004162, help = 'Momento de inércia para flexão em torno do eixo y local')
    Izz = st.text_input('Izz:', value = 0.0004162, help = 'Momento de inércia para flexão em torno do eixo z local')
    e = st.text_input('E:', value = 68851.6, help = 'Módulo de elasticidade de um elemento de estrutura')
    g = st.text_input('G:', value = 26199.1, help = 'Módulo de elasticidade ao cisalhamento de um elemento de estrutura')
    p = st.text_input('p:', value = 0, help = 'O ângulo de rotação do elemento de estrutura, em graus')
    density = st.text_input('density:', value = 0.16, help = 'Densidade de massa de um elemento de estrutura (usando unidades consistentes)')
    
    conexions_parameters = {'Ax': Ax, 'Asy': Asy, 'Asz': Asz, 'Jxx': Jxx, 'Iyy': Iyy, 'Izz': Izz, 'E': e, 'G': g, 'p': p, 'density': density}
    data['conexions_parameters'] = conexions_parameters

    st.markdown('### Configuração da Renderização:')

    shear_deformation = st.selectbox('shear_deformation:', [0, 1], index = 1, help = '1: incluir deformação por cisalhamento')
    geometric_stiffness = st.selectbox('geometric_stiffness:', [0, 1], index = 1, help = '1: incluir rigidez geométrica')
    exaggerate_static_mesh_deformations = st.text_input('exaggerate_static_mesh_deformations:', value = 2.0, help = 'Exagerar deformações estáticas da malha')
    zoom_scale = st.text_input('zoom_scale:', value = 1.0, help = 'Escala de zoom para plotagem 3D')
    x_axis_increment = st.text_input('x_axis_increment:', value = 0.30, help = 'Incremento do eixo x para dados de força interna, em')

    render_parameters = {'shear_deformation': shear_deformation, 'geometric_stiffness': geometric_stiffness,
                         'exaggerate_static_mesh_deformations': exaggerate_static_mesh_deformations, 'zoom_scale': zoom_scale,
                         'x_axis_increment': x_axis_increment}
    data['render_parameters'] = render_parameters

    st.markdown('### Aceleração da Gravidade:')

    Gx = st.text_input('Gx:', value = 0, help = 'Aceleração gravitacional para carregamento próprio (local)')
    Gy = st.text_input('Gy:', value = 0, help = 'Aceleração gravitacional para carregamento próprio (local)')
    Gz = st.text_input('Gz:', value = -9.81, help = 'Aceleração gravitacional para carregamento próprio (local)')

    gravity = {'Gx': Gx, 'Gy': Gy, 'Gz': Gz}
    data['gravity'] = gravity

    st.markdown('### Configuração das Cargas Nodais:')

    loaded_nodes = st.multiselect('Nós Carregados:', [node[0] for node in nodes], help = 'Nós que receberão carga')
    X_load = st.text_input('X-load:', value = 0, help = 'Carga nodal no eixo x')
    Y_load = st.text_input('Y-load:', value = 200, help = 'Carga nodal no eixo y')
    Z_load = st.text_input('Z-load:', value = 0, help = 'Carga nodal no eixo z')
    X_mom = st.text_input('X-mom:', value = 0, help = 'Momento nodal no eixo x')
    Y_mom = st.text_input('Y-mom:', value = 0, help = 'Momento nodal no eixo y')
    Z_mom = st.text_input('Z-mom:', value = 0, help = 'Momento nodal no eixo z')

    nodal_loads = {'loaded_nodes': loaded_nodes, 'X_load': X_load, 'Y_load': Y_load, 'Z_load': Z_load, 'X_mom': X_mom, 'Y_mom': Y_mom, 'Z_mom': Z_mom}  
    data['nodal_loads'] = nodal_loads

    st.markdown('### Configuração das Cargas Distribuídas:')

    loaded_elements = st.multiselect('Elementos Carregados:', [i for i in range(1, len(conexions) + 1)], help = 'Elementos que receberão carga')
    Ux = st.text_input('Ux:', value = 0, help = 'Carga distribuída no eixo x')
    Uy = st.text_input('Uy:', value = 0, help = 'Carga distribuída no eixo y')
    Uz = st.text_input('Uz:', value = 0, help = 'Carga distribuída no eixo z')
    
    distributed_loads = {'loaded_elements': loaded_elements, 'Ux': Ux, 'Uy': Uy, 'Uz': Uz}
    data['distributed_loads'] = distributed_loads

    st.markdown('### Configuração da Análise:')

    desired_modes = st.text_input('desired_modes:', value = 4, help = 'Número de modos dinâmicos de vibração desejados')
    subspace_method = st.selectbox('subspace_method:', [1, 2], index = 0, help = '1: Jacobi de subespaço, 2: Stodola')
    mass_matrix = st.selectbox('mass_matrix:', [0, 1], index = 0, help = '0: matriz de massa consistente, 1: matriz de massa concentrada')
    mode_shape_tolerance = st.text_input('mode_shape_tolerance:', value = 1e-6, help = 'Tolerância da forma do modo')
    shift_value = st.text_input('shift_value:', value = 0.0, help = 'Valor de deslocamento para estruturas não restringidas')
    exaggerate_modal_mesh_deformations = st.text_input('exaggerate_modal_mesh_deformations:', value = 1.5, help = 'Exagerar deformações da malha modal')

    analysis_parameters = {'desired_modes': desired_modes, 'subspace_method': subspace_method, 'mass_matrix': mass_matrix,
                           'mode_shape_tolerance': mode_shape_tolerance, 'shift_value': shift_value, 
                           'exaggerate_modal_mesh_deformations': exaggerate_modal_mesh_deformations}
    data['analysis_parameters'] = analysis_parameters

    st.markdown('### Configuração do Pós-processamento:')

    nA = st.text_input('nA = derired_mode:', value = desired_modes, help = 'número de modos para animar', disabled = True)
    modes_to_animate = st.multiselect('modes_to_animate:', [i for i in range(1, int(nA) + 1)], help = 'modos para animar')
    pan_rate = st.text_input('pan_rate:', value = 5, help = 'taxa de panorâmica durante a animação')

    post_processing_parameters = {'nA': nA, 'modes_to_animate': modes_to_animate, 'pan_rate': pan_rate}
    data['post_processing_parameters'] = post_processing_parameters

    

    if not os.path.exists("data"):
        os.makedirs("data")

    simulation_file_path = "data/simulation.3dd"
    make_3dd(data, nodes, conexions)
    
    with open(simulation_file_path, "r") as file:
        simulation_file = file.read()

    st.download_button(
        label="Baixar Arquivo de Simulação",
        data=simulation_file,
        file_name="simulation.3dd",
        mime="text/plain",
        use_container_width = True
    )
