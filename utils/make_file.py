import unicodedata

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

def make_3dd(data, nodes, conexions):
     
    with open('data/simulation.3dd', 'w') as file:
        
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