import streamlit as st 
import yaml
import sys

sys.path.append('dxf-extract/')
from extract_model import dxf_extraction
from view_structure import plot_by_nodes_and_conexions_streamlit
import os
import unicodedata

yaml_file = 'interface/parameters.yaml'
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

    return (nodes, conexions)

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

def make_3dd(data, nodes, conexions):
     
    with open('interface/data/simulation.3dd', 'w') as file:
        
        simulation_name = remove_accents(data['units']['simulation_name'])
        file.write(f'{simulation_name} ({data["units"]["force_unit"]}, {data["units"]["length_unit"]}, {data["units"]["mass_unit"]})\n\n')
        
        file.write('# node data ...\n\n')
        file.write(f'{len(nodes)}\t # number of nodes\n\n')
        file.write('#.node    x         y         z         r\n#.n       m         m         m         m\n\n')
        for node in nodes:
            file.write(f'{round(node[0], 2)}   {round(node[1], 2)}   {round(node[2], 2)}   {round(node[3], 2)}   0.00\n')
        file.write('\n')

        reaction_nodes = list()
        for node in nodes:
            if node[3] == 0: reaction_nodes.append(node[0])
        file.write(f'{len(reaction_nodes)}\t # number of nodes with reactions\n')
        file.write(f'#.n    x   y   z   xx  yy  zz      1=fixed, 0=free\n\n')
        for reaction in reaction_nodes:
            file.write(f'{reaction}\t 1\t 1\t 1\t 1\t 1\t 1\n')
        file.write('\n')

        file.write('# frame element data ...\n\n')
        count = 0
        for element in conexions:
            if element[1] != element[2]: count += 1
        file.write(f'{count}\t # number of frame elements\n')
        file.write('#.m   n1   n2   Ax   Asy   Asz   Jxx   Iyy   Izz   E   G   p   density\n')
        file.write('#     .    .    m^2  m^2   m^2   m^4   m^4   m^4   MPa MPa deg tonne/m^3\n\n')

        Ax = data['conexions_parameters']['Ax']
        Asy = data['conexions_parameters']['Asy']
        Asz = data['conexions_parameters']['Asz']
        Jxx = data['conexions_parameters']['Jxx']
        Iyy = data['conexions_parameters']['Iyy']   
        Izz = data['conexions_parameters']['Izz']
        E = data['conexions_parameters']['E']
        G = data['conexions_parameters']['G']
        p = data['conexions_parameters']['p']
        density = data['conexions_parameters']['density']
        
        count = 0
        for element in conexions:
            if element[1] != element[2]:
                count += 1
                file.write(f'{count} {element[1]} {element[2]} {Ax} {Asy} {Asz} {Jxx} {Iyy} {Izz} {E} {G} {p} {density}\n')
        file.write('\n')

        file.write(f'{data["render_parameters"]["shear_deformation"]}\t # 1: include shear deformation\n')
        file.write(f'{data["render_parameters"]["geometric_stiffness"]}\t # 1: include geometric stiffness\n')  
        file.write(f'{data["render_parameters"]["exaggerate_static_mesh_deformations"]}\t # exaggerate static mesh deformations\n')
        file.write(f'{data["render_parameters"]["zoom_scale"]}\t # zoom scale for 3D plotting\n')
        file.write(f'{data["render_parameters"]["x_axis_increment"]}\t # x-axis increment for internal force data, m\n\n')

        file.write('1                               # number of static load cases\n\n')
        file.write('# Begin Static Load Case 1 of 1\n\n')
        file.write('# gravitational acceleration for self-weight loading (global)\n')
        file.write('#   gX         gY         gZ\n')
        file.write('#   m/s^2     m/s^2     m/s^2\n\n')
        file.write(f'    {data["gravity"]["Gx"]}         {data["gravity"]["Gy"]}         {data["gravity"]["Gz"]}\n\n')

        file.write(f'{len(data["nodal_loads"]["loaded_nodes"])}\t # number of nodal loads\n')
        file.write('# .node  X-load   Y-load   Z-load   X-mom     Y-mom     Z-mom\n')
        file.write('#         N        N        N        N.m      N.m      N.m\n\n')
        if len(data["nodal_loads"]["loaded_nodes"]) > 0:
            for node in data["nodal_loads"]["loaded_nodes"]:
                file.write(f'{node}\t\t{data["nodal_loads"]["X_load"]}\t\t{data["nodal_loads"]["Y_load"]}\t\t{data["nodal_loads"]["Z_load"]}\t\t')
                file.write(f'{data["nodal_loads"]["X_mom"]}\t\t{data["nodal_loads"]["Y_mom"]}\t\t{data["nodal_loads"]["Z_mom"]}\n')
        file.write('\n')

        file.write(f'{len(data["distributed_loads"]["loaded_elements"])}\t # number of uniform distributed loads\n')
        file.write('#..j      Ux         Uy      Uz\n')
        file.write('#.frame   N/m       N/m    N/m\n')
        if len(data["distributed_loads"]["loaded_elements"]) > 0:
            for element in data["distributed_loads"]["loaded_elements"]:
                file.write(f'{element}\t\t{data["distributed_loads"]["Ux"]}\t\t{data["distributed_loads"]["Uy"]}\t\t{data["distributed_loads"]["Uz"]}\n')
        file.write('\n')

        file.write('0                       # number of trapezoidal distributed loads\n')
        file.write('0                               # number of internal concentrated loads\n')
        file.write('0                               # number of temperature loads\n')   
        file.write('0                               # number of nodes with prescribed displacements\n\n')
        file.write('# End   Static Load Case 1 of 1\n') 

        file.write(f'{data["analysis_parameters"]["desired_modes"]}\t # number of desired dynamic modes of vibration\n')    
        file.write(f'{data["analysis_parameters"]["subspace_method"]}\t # 1: subspace Jacobi, 2: Stodola\n')
        file.write(f'{data["analysis_parameters"]["mass_matrix"]}\t # 0: consistent mass, 1: lumped mass matrix\n')
        file.write(f'{data["analysis_parameters"]["mode_shape_tolerance"]}\t # mode shape tolerance\n')
        file.write(f'{data["analysis_parameters"]["shift_value"]}\t # shift value for unrestrained structures\n')
        file.write(f'{data["analysis_parameters"]["exaggerate_modal_mesh_deformations"]}\t # exaggerate modal mesh deformations\n\n')
        
        file.write('# concentrated mass inertia\n')
        file.write('0                # number of nodes with extra mass or inertia\n')
        file.write('#.n    M        Ixx   Iyy    Izz -  nodes and concentrated mass and inertia\n\n')

        file.write('0                               # frame elements with extra mass\n\n')

        file.write(f'{data["post_processing_parameters"]["nA"]}\t # number of modes to animate, nA\n')
        modes_animate = f'{data["post_processing_parameters"]["modes_to_animate"]}'.replace("[", "").replace("]", "").replace(",", "")
        if modes_animate != '':
            file.write(f'{modes_animate}\t # modes to animate, omit if nA == 0\n')
        else:
            file.write('0\t # modes to animate, omit if nA == 0\n')
        file.write(f'{data["post_processing_parameters"]["pan_rate"]}\t # pan rate during animation\n\n')

        file.write('# End of input data file for example I')

#################################

if 'nodes' not in st.session_state or 'conexions' not in st.session_state or 'plotter' not in st.session_state:
    (nodes, conexions) = prepare_model(dxf_path = data['model_path'], layers = data['layers'])
    st.session_state['nodes'] = nodes
    st.session_state['conexions'] = conexions
    #st.session_state['plotter'] = plot_by_nodes_and_conexions_streamlit(nodes_list = nodes, conexions_list = conexions)
else:
    nodes = st.session_state['nodes']
    conexions = st.session_state['conexions']
    #plotter = st.session_state['plotter']

st.title('Simulador Vibra-torre [Trixel]')

if not os.path.exists("interface/data/render.html"):
    #st.session_state['plotter'].export_html("interface/data/render.html")
    pass
   
# with open("interface/data/render.html", "r") as f:
#         html_content = f.read()

# st.warning('A escolha de componentes de torre será adicionada em breve...')
# with st.expander('Visualização da Estrutura', expanded = True):
#     st.components.v1.html(html_content, height = 700, scrolling = True)

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

    make_3dd(data, nodes, conexions)

    with open("interface/data/simulation.3dd", "r") as file:
        simulation_file = file.read()

    st.download_button(
        label="Baixar Arquivo de Simulação",
        data=simulation_file,
        file_name="simulation.3dd",
        mime="text/plain",
        use_container_width = True
    )
