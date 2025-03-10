import ezdxf
import os

class configure_models():
    '''
    Extraction and preprocessing of models from a .dxf file.
    '''

    def __init__(self, models_path: str):
        '''
        Constructor of the class.

        Args:
            models_path (str): Path where the .dxf files are located.
        
        Returns:
            None
        '''

        self.models_path = models_path
    
    def __normalize_paths(self, files_path: list) -> list:
        '''
        Normalize the paths of the files.

        Args:
            files_path (list): List containing the paths of the files.

        Returns:
            files_path (list): List containing the normalized paths of the files.
        '''

        for index, file in enumerate(files_path):
            file = os.path.normpath(file)
            files_path[index] = file

        return files_path
    
    def __find_dxf_files(self) -> list:
        '''
        Returns a list with the names of all .dxf files in the specified directory.

        Args:
            None

        Returns:
            dxf_files (list): List containing the names of the .dxf files present in the directory.
        '''

        try:
            dxf_files = []
            for root, dirs, files in os.walk(self.models_path):
                for file in files:
                    if file.endswith('.dxf'):
                        dxf_files.append(os.path.join(root, file))
            return self.__normalize_paths(dxf_files)
        except Exception as e:
            print(f"Error processing DXF files: {e}")
            return list()
        
    def get_dxf_files(self) -> list:
        '''
        Returns a list with the names of all .dxf files in the specified directory.

        Args:
            None

        Returns:
            dxf_files (list): List containing the names of the .dxf files present in the directory.
        '''

        return self.__find_dxf_files()
    
    def __generate_modelspace(self, file: str) -> ezdxf.layouts.layout.Modelspace:
        '''
        Returns the object containing all the information of the structural model.
        
        Args:
            file (str): Path where the .dxf file is located.
        
        Returns:
            msp (Modelspace): Model loaded from the .dxf file.
        '''

        doc = ezdxf.readfile(file)
        msp = doc.modelspace()

        return msp

    def __generate_modelspaces(self) -> list:
        '''
        Returns the object containing all the information of the structural model.

        Args:  
            None
        
        Returns:
            modelspaces (list): List containing the models loaded from the .dxf files.
        '''

        files = self.get_dxf_files()

        modelspaces = list()
        for file in files:
            msp = self.__generate_modelspace(file)
            modelspaces.append(msp)
        
        return modelspaces
    
    def get_modelspaces(self) -> list:
        '''
        Returns the object containing all the information of the structural model.

        Args:  
            None
        
        Returns:
            modelspaces (list): List containing the models loaded from the .dxf files.
        '''

        return self.__generate_modelspaces()
    
    def __extract_modelspace(self, msp: ezdxf.layouts.layout.Modelspace) -> dict:
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
    
    def __extract_modelspaces(self, modelspaces: list) -> list:
        '''
        Returns the object containing all the information of the structural model.

        Args:  
            modelspaces (list): List containing the models loaded from the .dxf files.
        
        Returns:
            modelspace_list (list): List containing the information of the structure.
        '''

        modelspace_list = list()
        for msp in modelspaces:
            modelspace_list.append(self.__extract_modelspace(msp))
        
        return modelspace_list
    
    def get_modelspace_extraction(self) -> list:
        '''
        Returns the object containing all the information of the structural model.

        Args:  
            modelspaces (list): List containing the models loaded from the .dxf files.
        
        Returns:
            modelspace_list (list): List containing the information of the structure.
        '''

        return self.__extract_modelspaces(self.get_modelspaces())


def test():
    
    data = configure_models(models_path = 'models/dxf')

    files = data.get_dxf_files()
    print(f'Modelos Existentes: {len(files)}')

    for file in files:
        print(file)
    print('--\n')
    
    modelspaces = data.get_modelspace_extraction()

    print('Exemplos dos dados dos modelspaces:')
    for modelspace in modelspaces:
        for value in modelspace:
            print(value)
            break

if __name__ == '__main__':
    test()
