from utils.extract_model import dxf_extraction

def prepare_model(dxf_path: str, layers = '', apply_scale = False) -> tuple:
    '''
    Function that prepares the model for simulation.

    Arguments:
        dxf_path (str): Path of the dxf file.
        layers (list): List of layers to be considered.

    Returns:
        tuple: Tuple containing nodes and connections of the model.
    '''

    data = dxf_extraction(model_path = dxf_path)

    msp = data.get_modelspace()

    layers_name = data.get_layers_name()
    modelspace_list = data.extract_modelspace(msp = msp)
    if apply_scale:
        modelspace_list = data.convert_m_to_mm(modelspace_list = modelspace_list)
    normalized_data = data.normalize_data(modelspace_list = modelspace_list)
    layers_dict = data.separete_by_layers(modelspace_list = normalized_data)
    if layers != '':
        combination_layers_name = data.combine_layers_names(name_layers = layers_name, ignored_layers = ['0', 'Defpoints'])
        layers_dict = data.combine_layers(layers_dict = layers_dict, new_layers_info = combination_layers_name)
        (nodes, conexions) = data.generate_frame3dd_data(layers_dict = layers_dict, customize_layers = layers)
    else:
        layers_dict = data.unite_by_layers(modelspace_list = normalized_data)
        (nodes, conexions) = data.generate_frame3dd_data(layers_dict = layers_dict)

    return (nodes, conexions, layers_dict)