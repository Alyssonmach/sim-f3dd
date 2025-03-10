import numpy as np
import unicodedata
import ezdxf

class dxf_extraction():
    '''
    Classe para extrair a estrutura de modelo de um arquivo .dxf.
    '''

    def __init__(self, model_path: str):
        '''
        Construtor da classe.

        Args:
            model_path (str): Caminho onde o arquivo .dxf está localizado.
        
        Returns:
            None
        '''

        self.model_path = model_path
    
    def get_modelspace(self) -> ezdxf.layouts.layout.Modelspace:
        '''
        Retorna o objeto contendo todas as informações do modelo estrutural.
        Args:
            None
        Returns:
            msp (Modelspace): Modelo carregado a partir do arquivo .dxf.
        '''

        doc = ezdxf.readfile(self.model_path)
        msp = doc.modelspace()

        return msp

    def get_layers_name(self) -> list:
        '''
        Retorna uma lista com os nomes de todas as camadas existentes no arquivo .dxf.

        Args:
            None

        Returns:
            name_list (list): Lista contendo os nomes das camadas (layers) presentes no DXF.
        '''

        try:
            doc = ezdxf.readfile(self.model_path)  
            layers = [layer.dxf.name for layer in doc.layers]  
            return layers
        except Exception as e:
            print(f"Erro ao processar o arquivo DXF: {e}")
            return list()

    def normalize_texts(self, text: str) -> str:
        '''
        Remove acentos e converte para maiúsculas.

        Args:
            text (str): Texto a ser normalizado.

        Returns:
            text (str): Texto normalizado.
        '''

        text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
        
        return text.upper()

    def combine_layers_names(self, name_layers, ignored_layers):
        '''
        Agrupa as camadas do DXF por prefixo, ignorando '0' e 'Defpoints'.
        
        Args:
            name_layers (list): Lista de nomes das camadas.
            ignored_layers (list): Lista com o nome das camadas a serem ignoradas.
        
        Returns:
            combination_dict: Dicionário onde a chave é o prefixo e o valor é uma lista das camadas correspondentes.
        '''

        layers_dict = {}

        for layer in name_layers:
            layer_norm = self.normalize_texts(layer)  
            if layer in ignored_layers:
                continue  # Ignorar camadas indesejadas
            
            prefix = layer_norm.split("_")[0]  # Pega a primeira palavra como chave
            if prefix not in layers_dict:
                layers_dict[prefix] = list()
            
            layers_dict[prefix].append(layer)

        return layers_dict

    def extract_modelspace(self, msp: ezdxf.layouts.layout.Modelspace) -> dict:
        '''
        Retorna o Modelspace do ezdxf para uma lista em Python.

        Args:
            msp (Modelspace): Modelo carregado a partir do arquivo .dxf.

        Returns:
            modelspace_list (list): Lista contendo as informações da estrutura.
        '''
        
        modelspace_list = list()

        for entity in msp.query('LINE'):
            layer = entity.dxf.layer
            start = (round(entity.dxf.start.x, 4), round(entity.dxf.start.y, 4), round(entity.dxf.start.z, 4))
            end = (round(entity.dxf.end.x, 4), round(entity.dxf.end.y, 4), round(entity.dxf.end.z, 4))
            
            element = {'layer': layer, 'start_point': start, 'end_point': end}
            modelspace_list.append(element)
        
        return modelspace_list
    
    def convert_m_to_mm(self, modelspace_list: list) -> list:
        '''
        Modifica a escala da nuvem de pontos de metros para milímetros.

        Args:
            modelspace_list (list): Lista contendo as informações da estrutura na escala de metros.
        
        Returns:
            modelspace_list_mm (list): Lista contendo as informações da estrutura na escala de milímetros.
        '''

        modelspace_list_mm = list()

        for element in modelspace_list:
            modelspace_list_mm.append({
                'layer': element['layer'],
                'start_point': tuple(np.array(element['start_point']) * 1000),
                'end_point': tuple(np.array(element['end_point']) * 1000)
            })
        
        return modelspace_list_mm
    
    def normalize_data(self, modelspace_list: list) -> list:
        '''
        Retorna os dados normalizados.

        Args:
            modelspace_list (list): Lista contendo as informações da estrutura.
        
        Returns:
            normalized_data (list): Lista com as informações da estrutrua normalizada.
        '''

        all_coords = [np.array(d['start_point']) for d in modelspace_list] + [np.array(d['end_point']) for d in modelspace_list]
        # utiliza o valor mais próximo de 0
        # ref_coord = np.min(all_coords, axis = 0)
        # Calcula a média das coordenadas x, y
        # ref_coord = np.mean([coord[0] for coord in all_coords])  
        # Calcula a média das coordenadas x, y, z
        ref_coord = np.mean(all_coords, axis=0)

        normalized_data = list()
        for element in modelspace_list:
            normalized_data.append({
                'layer': element['layer'],
                'start_point': tuple(np.array(element['start_point']) - ref_coord),
                'end_point': tuple(np.array(element['end_point']) - ref_coord)
            })

        return normalized_data

    def separete_by_layers(self, modelspace_list: list) -> dict:
        '''
        Separa as informações da estrutura em diferentes camadas.

        Args:
            modelspace_list (list): Lista contendo as informações da estrutura.
        
        Returns:

        '''

        layers_dict = dict()

        for element in modelspace_list:
            layer = element['layer']
            if layer not in layers_dict:
                layers_dict[layer] = list() 
        
            layers_dict[layer].append({
                'start_point': element['start_point'],
                'end_point': element['end_point']
            })
        
        return layers_dict
    
    def combine_layers(self, layers_dict: dict, new_layers_info: dict) -> dict:
        '''
        Combina múltiplas camadas em uma única camada renomeada.

        Args:
            layers_dict (dict): Dicionário com as ligações separadas por camadas.
            new_layers_info (dict): Dicionário com a chave sendo o novo nome e o valor sendo uma lista de camadas a unir.
        
        Returns:
            new_layers_dict (dict): Dicionário com as ligações separadas por camadas. (dict): Dicionário com as ligações separadas por camadas após a realização das combinações.
        '''

        new_layers_dict = dict()

        for layer in layers_dict: 
            if not any(layer in layers for layers in new_layers_info.values()):
                new_layers_info[layer] = layers_dict[layer] # Adiciona as camadas que não serão combinadas

        for new_name, layers in new_layers_info.items():
            new_conexions = list()
            
            for layer in layers:
                if layer in layers_dict:
                    new_conexions.extend(layers_dict[layer])  # Adiciona as ligações dessa camada
            
            if new_conexions:
                new_layers_dict[new_name] = new_conexions

        return new_layers_dict

    def generate_frame3dd_data(self, layers_dict: dict, customize_layers: list) -> tuple:
        '''
        Gera dados do modelo para o Frame3DD.

        Args:
            layers_dict (dict): Dicionário com as ligações separadas por camadas.
            customize_layers (list): Lista com as camadas a serem consideradas.
        
        Returns:
            tuple_values (tuple): Informação de nós e ligações do modelo.
        '''

        id_counter = 1  
        id_conexion = 1  
        nodes_dict = dict()

        nodes_list, conexions_list = list(), list()

        for layer, conexions in layers_dict.items():
            if layer in customize_layers:
                for conexion in conexions:
                    start = conexion["start_point"]
                    end = conexion["end_point"]

                    if start not in nodes_dict:
                        nodes_dict[start] = id_counter
                        nodes_list.append([id_counter, *start])
                        id_counter += 1

                    if end not in nodes_dict:
                        nodes_dict[end] = id_counter
                        nodes_list.append([id_counter, *end])
                        id_counter += 1

                    conexions_list.append([id_conexion, nodes_dict[start], nodes_dict[end]])
                    id_conexion += 1

        return (nodes_list, conexions_list)

    def filter_connections_same_z(self, conexions_list: list, nodes_list: list) -> list:
        '''
        Filtra as conexões cujos pontos de ligação estão no mesmo eixo z.

        Args:
            conexions_list (list): Lista de conexões com IDs dos nós.
            nodes_list (list): Lista de nós com IDs e coordenadas x, y, z.

        Returns:
            same_z_connections (list): Lista contendo os IDs das conexões cujos pontos de ligação estão no mesmo eixo z.
        '''

        # Cria um dicionário para mapear IDs de nós para suas coordenadas
        nodes_dict = {node[0]: node[1:] for node in nodes_list}

        same_z_connections = []

        for conexion in conexions_list:
            id_conexion, start_id, end_id = conexion
            start_node = nodes_dict[start_id]
            end_node = nodes_dict[end_id]

            # Verifica se os pontos de ligação estão no mesmo eixo z
            if start_node[2] == end_node[2]:
                same_z_connections.append(id_conexion)

        return same_z_connections
