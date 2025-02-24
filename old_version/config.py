import yaml

def open_yaml(yaml_file):
    '''
    Abre um arquivo com parâmetros de configuração do Streamlit.

    Args:
        yaml_file (str): Caminho e nome do arquivo .yaml.
    
    Returns:
        data (dict): Dicionário com os parâmetros de configuração.
    '''

    with open(yaml_file, 'r') as file:
        data = yaml.load(file, Loader = yaml.FullLoader)
    
    return data

def return_streamlit_config(data):
    '''
    Retornar uma formatação .css para configurar a página web Streamlit.

    Args:
        data (dict): Dicionário com as chaves `display`, `max-width` e `background-color`.
    
    Return:
        text (str): Bloco de código .css para formatação da página web Streamlit.
    '''

    return f"""
            <style>
                /* Ativando o wide mode */
                .streamlit-expanderHeader {{
                    display: {data['display']};
                }}
                .main {{
                    max-width: {data['max-width']};
                }}
                
                /* Definindo o fundo */
                body {{
                    background-color: {data['background-color']};
                }}
            </style>
            """

