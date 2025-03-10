from extract_model import dxf_extraction
import view_structure

def test():
    '''
    Módulo de teste.

    Args:
        None
    
    Returns:
        None
    '''

    #data = dxf_extraction('../models/dxf/generico_400kv.dxf')
    data = dxf_extraction('../models/dxf/Montagem - AX3.dxf')

    msp = data.get_modelspace()
    print(f'Objeto com as Ligações:{msp}\n\n')

    layers_name = data.get_layers_name()

    print('Nomes das Camadas:')
    for name in layers_name:
        print(name)
    print('\n\n')

    modelspace_list = data.extract_modelspace(msp = msp)
    for space in modelspace_list:
        print(f'Exemplo sem normalização:\n {space}\n\n')
        break

    #modelspace_mm = data.convert_m_to_mm(modelspace_list = modelspace_list)
    normalized_data = data.normalize_data(modelspace_list = modelspace_list)
    
    for space in normalized_data:
        print(f'\nExemplo com normalização:\n {space}\n\n')
        break

    print('Exemplo da Estrutura de Dicionário:')
    layers_dict = data.separete_by_layers(modelspace_list = normalized_data)
    for keys, elements in layers_dict.items():
        print(f'Chave: {keys} e Quantidade de Ligações: {len(elements)}')
    print('\n\n')

    print('Exemplo da Estrutura de Dicionário Corrigida:')
    combination_layers_name = data.combine_layers_names(name_layers = layers_name, ignored_layers = ['0', 'Defpoints'])
    layers_dict_correct = data.combine_layers(layers_dict = layers_dict, new_layers_info = combination_layers_name)
    for keys, elements in layers_dict_correct.items():
        print(f'Chave: {keys} e Quantidade de Ligações: {len(elements)}')
    print('\n\n')

    layers = ['PES', 'EXTENSAO', 'TRONCO', 'CABECA', 'BRACO', 'PARA']
    #layers = ['FRAMES']
    (nodes, conexions) = data.generate_frame3dd_data(layers_dict = layers_dict_correct, customize_layers = layers)

    # for node in nodes:
    #     print(f'{round(node[0], 2)}   {round(node[1], 2)}   {round(node[2], 2)}   {round(node[3], 2)}   0.00')

    # for node in nodes:
    #     if node[3] == 0:
    #         print(f'{node[0]}\t 1\t 1\t 1\t 1\t 1\t 1')
    
    count = 0
    for element in conexions:
        if element[1] != element[2]:
            count += 1
            print(f'{count} {element[1]} {element[2]} 0.06452 0.03871 0.03871 0.0002081 0.0004162 0.0004162 68851.6 26199.1 0 0.16')
        
    # same_z_connections = data.filter_connections_same_z(conexions_list = conexions, nodes_list = nodes)
    # count = 0
    # for conexion in same_z_connections:
    #     count += 1
    #     print(f'{conexion}   0   0   -414.282')
    # print('Quantidade:', count)

    #view_structure.plot_structure(modelspace_list = normalized_data)
    #view_structure.plot_conexions_by_layers(layers_dict = layers_dict)
    #view_structure.plot_conexions_by_layers(layers_dict = layers_dict_correct)
    view_structure.plot_by_nodes_and_conexions(nodes_list = nodes, conexions_list = conexions)

if __name__ == test():
    test()