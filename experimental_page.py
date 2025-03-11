from utils.view_structure import plot_by_layers_streamlit
from structure_compose import prepare_model
from utils.make_file import make_3dd
import streamlit as st
import os

def page2():

    UPLOAD_FOLDER = "uploads"
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    st.title('Simulador Vibra-torre [Trixel]')

    uploaded_file = st.file_uploader("Faça o upload de um arquivo DXF", type=["dxf"])

    if uploaded_file is not None:
        # Definir o caminho para salvar o arquivo
        file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
        
        # Salvar o arquivo no diretório
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"Arquivo salvo em: {file_path}")

        if 'nodes_exp' not in st.session_state or 'conexions_exp' not in st.session_state or 'layers_dict_exp' not in st.session_state:
            (nodes, conexions, layers_dict) = prepare_model(dxf_path = f'{file_path}', apply_scale = True)
            st.session_state['nodes_exp'] = nodes
            st.session_state['conexions_exp'] = conexions
            st.session_state['layers_dict_exp'] = layers_dict
            st.session_state['plotter_exp'] = plot_by_layers_streamlit(nodes_list = nodes, conexions_list = conexions, layers_dict = layers_dict, visualize_IDs = True)
        else:
            nodes = st.session_state['nodes_exp']
            conexions = st.session_state['conexions_exp']
            layers_dict = st.session_state['layers_dict_exp']
            plotter = st.session_state['plotter_exp']

        st.title('Simulador Vibra-torre [Trixel]')

       
        with st.expander('Visualização da Estrutura', expanded = True):
            st.plotly_chart(st.session_state['plotter_exp'], use_container_width=True, key="plotter_chart")
        
        with st.expander('Configuração da Simulação', expanded = True):

            data = dict()

            st.markdown('### Unidades Métricas:')
            simulation_name_help = 'Título da simulação a ser ilustrado nos arquivos gerados do Frame3DD'
            simulation_name = st.text_input('Nome da Simulação:', value = 'Simulação de Estrutura', help = simulation_name_help)
            force_unit, length_unit, mass_unit = 'N', 'mm', 'ton'
            st.markdown(body = '**Força**: `Newton [N]` | **Comprimento**: `Milímetros [mm]` | **Massa**: `Tonelada [ton]`')
            
            units = {'simulation_name': simulation_name, 'force_unit': force_unit, 'length_unit': length_unit, 'mass_unit': mass_unit}
            data['units'] = units

            st.markdown('### Parâmetros das Barras:')

            Ax = st.text_input('Ax: $[mm^2]$', value = 606, help = 'Área da seção transversal de um elemento de estrutura prismático')
            Asy = st.text_input('Asy $[mm^2]$:', value = 282, help = 'Área de cisalhamento no eixo y local de um elemento de estrutura prismático')
            Asz = st.text_input('Asz $[mm^2]$:', value = 282, help = 'Área de cisalhamento no eixo z local de um elemento de estrutura prismático')
            Jxx = st.text_input('Jxx $[mm^4]$:', value = 8100, help = 'Momento de inércia torsional de um elemento de estrutura')
            Iyy = st.text_input('Iyy $[mm^4]$:', value = 14600, help = 'Momento de inércia para flexão em torno do eixo y local')
            Izz = st.text_input('Izz $[mm^4]$:', value = 14600, help = 'Momento de inércia para flexão em torno do eixo z local')
            e = st.text_input('E $[MPa]$:', value = 200000, help = 'Módulo de elasticidade de um elemento de estrutura')
            g = st.text_input('G $[MPa]$:', value = 70000, help = 'Módulo de elasticidade ao cisalhamento de um elemento de estrutura')
            p = st.text_input('p $[deg]$:', value = 0, help = 'O ângulo de rotação do elemento de estrutura, em graus')
            density = st.text_input('Densidade $[\\frac{ton}{mm^3}]$:', value = 7.85e-9, help = 'Densidade de massa de um elemento de estrutura (usando unidades consistentes)')
            
            conexions_parameters = {'Ax': Ax, 'Asy': Asy, 'Asz': Asz, 'Jxx': Jxx, 'Iyy': Iyy, 'Izz': Izz, 'E': e, 'G': g, 'p': p, 'density': density}
            data['conexions_parameters'] = conexions_parameters

            st.markdown('### Configuração da Renderização:')

            shear_deformation = st.selectbox('Deformação de Cisalhamento:', options = ['Não', 'Sim'], index = 1, help = '1: incluir deformação por cisalhamento')
            shear_deformation = 1 if shear_deformation == 'Sim' else 0
            geometric_stiffness = st.selectbox('Rigidez Geométrica:', ['Não', 'Sim'], index = 1, help = '1: incluir rigidez geométrica')
            geometric_stiffness = 1 if geometric_stiffness == 'Sim' else 0
            exaggerate_static_mesh_deformations = st.text_input('Taxa de exagero de deformação estática na malha:', value = 0.1, help = 'Exagerar deformações estáticas da malha')
            zoom_scale = st.text_input('Escala de Zoom:', value = 1.0, help = 'Escala de zoom para plotagem 3D')
            x_axis_increment = st.text_input('Incremento do Eixo X $[mm]$:', value = 0.30, help = 'Incremento do eixo x para dados de força interna')

            render_parameters = {'shear_deformation': shear_deformation, 'geometric_stiffness': geometric_stiffness,
                                'exaggerate_static_mesh_deformations': exaggerate_static_mesh_deformations, 'zoom_scale': zoom_scale,
                                'x_axis_increment': x_axis_increment}
            data['render_parameters'] = render_parameters

            st.markdown('### Aceleração da Gravidade:')

            Gx = st.text_input('Gx $[\\frac{mm}{s^2}]$:', value = 0, help = 'Aceleração gravitacional para carregamento próprio (local)')
            Gy = st.text_input('Gy $[\\frac{mm}{s^2}]$:', value = 0, help = 'Aceleração gravitacional para carregamento próprio (local)')
            Gz = st.text_input('Gz $[\\frac{mm}{s^2}]$:', value = -9810, help = 'Aceleração gravitacional para carregamento próprio (local)')

            gravity = {'Gx': Gx, 'Gy': Gy, 'Gz': Gz}
            data['gravity'] = gravity

            st.markdown('### Configuração das Cargas Nodais:')

            loaded_nodes = st.multiselect('Nós Carregados:', [node[0] for node in nodes], help = 'Nós que receberão carga')
            X_load = st.text_input('X-carga $[N]$:', value = 20000, help = 'Carga nodal no eixo x')
            Y_load = st.text_input('Y-carga $[N]$:', value = 0, help = 'Carga nodal no eixo y')
            Z_load = st.text_input('Z-carga $[N]$:', value = 0, help = 'Carga nodal no eixo z')
            X_mom = st.text_input('X-momento $[N.mm]$:', value = 0, help = 'Momento nodal no eixo x')
            Y_mom = st.text_input('Y-momento: $[N.mm]$', value = 0, help = 'Momento nodal no eixo y')
            Z_mom = st.text_input('Z-momento: $[N.mm]$', value = 0, help = 'Momento nodal no eixo z')

            nodal_loads = {'loaded_nodes': loaded_nodes, 'X_load': X_load, 'Y_load': Y_load, 'Z_load': Z_load, 'X_mom': X_mom, 'Y_mom': Y_mom, 'Z_mom': Z_mom}  
            data['nodal_loads'] = nodal_loads

            st.markdown('### Configuração das Cargas Distribuídas:')

            loaded_elements = st.multiselect('Elementos Carregados:', [i for i in range(1, len(conexions) + 1)], help = 'Elementos que receberão carga')
            Ux = st.text_input('Ux $[\\frac{N}{mm}]$:', value = 0, help = 'Carga distribuída no eixo x')
            Uy = st.text_input('Uy $[\\frac{N}{mm}]$:', value = 0, help = 'Carga distribuída no eixo y')
            Uz = st.text_input('Uz $[\\frac{N}{mm}]$:', value = 0, help = 'Carga distribuída no eixo z')
            
            distributed_loads = {'loaded_elements': loaded_elements, 'Ux': Ux, 'Uy': Uy, 'Uz': Uz}
            data['distributed_loads'] = distributed_loads

            st.markdown('### Configuração da Análise:')

            desired_modes = st.text_input('Modos Dinâmicos:', value = 8, help = 'Número de modos dinâmicos de vibração desejados')
            subspace_method = st.selectbox('Método de Subespaços:', ['Jacobini', 'Stodola'], index = 0, help = 'Métodos de subespaço matricial Jacobi ou Stodola')
            subspace_method = 1 if subspace_method == 'Jacobini' else 2
            mass_matrix = st.selectbox('Matriz de Massa Concentrada:', ['Massa Consistente', 'Massa Concentrada'], index = 0, help = 'Matriz de massa consistente, ou de massa concentrada')
            mass_matrix = 0 if mass_matrix == 'Massa Consistente' else 1
            mode_shape_tolerance = st.text_input('Tolerância da Forma de Modo:', value = 1e-6, help = 'Tolerância da forma do modo')
            shift_value = st.text_input('Deslocamento para estruturas não restringidas:', value = 0.0, help = 'Valor de deslocamento para estruturas não restringidas')
            exaggerate_modal_mesh_deformations = st.text_input('Exagero na deformação da malha modal:', value = 0.1, help = 'Exagerar deformações da malha modal')

            analysis_parameters = {'desired_modes': desired_modes, 'subspace_method': subspace_method, 'mass_matrix': mass_matrix,
                                'mode_shape_tolerance': mode_shape_tolerance, 'shift_value': shift_value, 
                                'exaggerate_modal_mesh_deformations': exaggerate_modal_mesh_deformations}
            data['analysis_parameters'] = analysis_parameters

            st.markdown('### Configuração do Pós-processamento:')

            nA = st.text_input('Modos para animar:', value = desired_modes, help = 'número de modos para animar', disabled = True)
            modes_to_animate = st.multiselect('Modos para animar:', [i for i in range(1, int(nA) + 1)], default = [i for i in range(1, int(nA) + 1)], help = 'modos para animar')
            pan_rate = st.text_input('Taxa panorâmica da animação:', value = 5, help = 'taxa de panorâmica durante a animação')

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

