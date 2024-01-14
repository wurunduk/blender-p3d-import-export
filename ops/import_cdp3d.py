import bpy, bmesh, os
import time
import struct

from pathlib import Path

from ..crashday import p3d

if 'bpy' in locals():
    import importlib
    importlib.reload(p3d)

def int_to_color(value):
    return (((value >> 16) & 255)/255.0, ((value >> 8) & 255)/255.0, (value & 255)/255.0)

def get_folders_array_from_path(filepath):
    drive, path_and_file = os.path.splitdrive(filepath)
    path, _ = os.path.split(path_and_file)
    folders = []
    while True:
        path, folder = os.path.split(path)

        if folder != "":
            folders.append(folder)
        elif path != "":
            folders.append(path)
            break

    return drive, folders

def shorten_path(path, ind):
    _, folders = get_folders_array_from_path(path)
    folders.reverse()
    out = os.path.join('..\\', *folders[ind:])
    return out

def find_texture_paths(filepath, search_path):
    drive, folders = get_folders_array_from_path(filepath)
    # crashday car models are always put into ../content/content_type/cars/*car_name*/
    # we can use this knowledge to accurately guess type of the model loaded and load additional textures in such cases
    is_car = folders[1] == 'cars'
    car_name = None
    if is_car:
        car_name = folders[0]
        print('Car model is being loaded, guessed name {}'.format(car_name))
    else:
        print('Non car model is being loaded')

    folders.reverse()

    # load textures of the mod
    try:
        ind = folders.index('models')
        textures_mod_path = os.path.join(drive, *folders[:ind], 'textures\\')
        if is_car and car_name is not None:
            # car specific textures
            textures_mod_car_path = os.path.join(textures_mod_path, 'cars\\', car_name)
            if os.path.isdir(textures_mod_car_path):
                search_path.append(textures_mod_car_path)
                print('Added {} local car textures path {}'.format(car_name, shorten_path(textures_mod_car_path, ind)))

        if os.path.isdir(textures_mod_path):
            search_path.append(textures_mod_path)
            print('Added local mod textures path {}'.format(shorten_path(textures_mod_path, ind)))

    except ValueError:
        print('Couldn\'t load local mod textures, model was not in models folder')

    # load unpacked original cd textures if present
    try:
        ind = folders.index('Crashday')
        textures_cd_path = os.path.join(drive, *folders[:ind+1], 'data\\content\\textures\\')
        if is_car and car_name is not None:
            # car specific textures
            textures_cd_car_path = os.path.join(textures_cd_path, 'cars\\', car_name)
            if os.path.isdir(textures_cd_car_path):
                search_path.append(textures_cd_car_path)
                print('Added {} crashday car textures path {}'.format(car_name, shorten_path(textures_cd_car_path, ind)))

        if os.path.isdir(textures_cd_path):
            search_path.append(textures_cd_path)
            print('Added general crashday textures path {}'.format(shorten_path(textures_cd_path, ind)))
    except ValueError:
        print('Couldn\'t find Crashday folder, no general textures loaded')

def texture_exists(full_path, file_name):
    #remove extension and add to path
    p = os.path.join(full_path, os.path.splitext(file_name)[0])
    tga_path = p + '.tga'
    dds_path = p + '.dds'
    if os.path.isfile(tga_path):
        print('Loaded tga in {}'.format(tga_path))
        return tga_path
    elif os.path.isfile(dds_path):
        print('Loaded dds in {}'.format(dds_path))
        return dds_path
    else:
        return None

def add_textures(p3d_model, paths):
    for tex in p3d_model.textures:
        texture = bpy.data.textures.get(tex)

        if texture is None:
            texture = bpy.data.textures.new(tex, type='IMAGE')

        img = None
        for p in paths:
            path = texture_exists(p, tex)
            if path is not None:
                img = bpy.data.images.load(path)
                texture.image = img
                break
        if img is None:
            print('Failed to load {}'.format(tex))

def get_material_name(material_name):
    return material_name[1] + ' ' + material_name[0].lower()

def add_material(obj, material_name):
    material = bpy.data.materials.get(get_material_name(material_name))

    if material is None:
        material = bpy.data.materials.new(get_material_name(material_name))

        material.cdp3d.material_name = material_name[1]
        material.cdp3d.material_type = material_name[0]

        material.use_nodes = True
        principled_bsdf = material.node_tree.nodes.get('Principled BSDF')

        texImage = material.node_tree.nodes.new('ShaderNodeTexImage')
        texImage.image = bpy.data.textures.get( material_name[1]).image

        # blender 4.0 renamed 'Specular' node input to 'Specular IOR Level'
        if bpy.app.version[0] >= 4:
            def set_material_params(metalness, specularity, roughness):
                principled_bsdf.inputs['Metallic'].default_value = metalness
                principled_bsdf.inputs['Specular IOR Level'].default_value = specularity
                principled_bsdf.inputs['Roughness'].default_value = roughness
        else:
            def set_material_params(metalness, specularity, roughness):
                principled_bsdf.inputs['Metallic'].default_value = metalness
                principled_bsdf.inputs['Specular'].default_value = specularity
                principled_bsdf.inputs['Roughness'].default_value = roughness

        inputs_by_material_name = {
            'FLAT' : (0.0, 1.0, 1.0),
            'FLAT_METAL' : (1.0, 0.9, 0.9),
            'GOURAUD' : (0.0, 0.1, 0.8),
            'GOURAUD_METAL' : (0.8, 0.5, 0.2),
            'GOURAUD_METAL_ENV' : (0.5, 0.3, 0.05),
            'SHINING' : (1.0, .2, 0.0),
        }

        material_inputs = inputs_by_material_name[material_name[0]]
        if material_inputs != None:
            set_material_params(material_inputs[0], material_inputs[1], material_inputs[2])

        material.node_tree.links.new(principled_bsdf.inputs['Base Color'], texImage.outputs['Color'])

    obj.data.materials.append(material)

def create_meshes(p3d_model, col, use_edge_split_modifier, remove_doubles_distance):
    for m in p3d_model.meshes:
        mesh = bpy.data.meshes.new(name=m.name)
        obj = bpy.data.objects.new(mesh.name, mesh)
        obj.location = m.pos

        col.objects.link(obj)

        # if 'coll' in m.name or 'shad' in m.name or 'lod' in m.name or '.' in m.name:
        #     obj.hide_set(True)

        items = mesh.cdp3d.bl_rna.properties['flags'].enum_items

        flags = set()
        for flag in items:
            # print(flag.value)
            if m.flags & flag.value:
                flags.add(flag.identifier)

        mesh.cdp3d.flags = flags

        for t in m.materials_used:
            add_material(obj, t)

        faces = []
        uvs = []

        for i in range(m.num_polys):
            faces.append([m.polys[i].p1, m.polys[i].p2, m.polys[i].p3])
            uvs.append((m.polys[i].u1, m.polys[i].v1))
            uvs.append((m.polys[i].u2, m.polys[i].v2))
            uvs.append((m.polys[i].u3, m.polys[i].v3))

        mesh.from_pydata(m.vertices, [], faces)

        for i, f in enumerate(mesh.polygons):
            mat_ind = [(j, item) for j, item in enumerate(m.materials_used) if item[1] == m.polys[i].texture and item[0] == m.polys[i].material]
            f.material_index = mat_ind[0][0]
            if  mat_ind[0][1][0] == 'GOURAUD' or mat_ind[0][1][0] == 'GOURAUD_METAL' or mat_ind[0][1][0] == 'GOURAUD_METAL_ENV':
                f.use_smooth = True

        uv_layer = mesh.uv_layers.new(do_init=False)
        mesh.uv_layers.active = uv_layer

        uv_layer.data.foreach_set('uv', [uv for pair in [uvs[i] for i, l in enumerate(mesh.loops)] for uv in pair])

        if use_edge_split_modifier:
            bm = bmesh.new()
            bm.from_mesh(mesh)

            for edge in bm.edges:
                if len(edge.link_loops) == 1:
                    edge.smooth = False

            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=remove_doubles_distance)
            mod = obj.modifiers.new('EdgeSplit', 'EDGE_SPLIT')
            mod.use_edge_angle = False
            bm.to_mesh(mesh)
            bm.free()


def create_lights(p3d_model, col):
    for l in p3d_model.lights:
        new_light = bpy.data.lights.new(name=l.name, type='POINT')
        new_light.color = int_to_color(l.color)
        new_light.energy = l.range

        new_light.cdp3d.corona = l.show_corona
        new_light.cdp3d.lens_flares = l.show_lens_flares
        new_light.cdp3d.lightup_environment = l.lightup_environment

        light_object = bpy.data.objects.new(new_light.name, new_light)
        light_object.location = l.pos

        col.objects.link(light_object)

def create_pos(col, pos, name):
    obj = bpy.data.objects.new(name, None)
    col.objects.link(obj)

    obj.location = pos
    obj.empty_display_type = 'PLAIN_AXES'

def load(operator,
         context,
         use_edge_split_modifier=True,
         remove_doubles_distance=0.00001,
         filepath='',
         search_textures=True):

    file_name = filepath.split('\\')[-1]

    print('\nImporting file {} from {}'.format(file_name, filepath))

    search_path = []
    if search_textures:
        find_texture_paths(filepath, search_path)

    p = p3d.P3D()

    file = open(filepath, 'rb')
    p.read(file)
    file.close()

    print(p)

    col = bpy.data.collections.new(file_name)
    bpy.context.scene.collection.children.link(col)

    add_textures(p, search_path)
    create_lights(p, col)
    create_meshes(p, col, use_edge_split_modifier, remove_doubles_distance)

    create_pos(col, (0.0, 0.0, - p.height/2.0), 'floor_level')

    print('Done importing .p3d file')

    return {'FINISHED'}

def add_position(line, col, name):
    line = line.split('#')[0]
    line = line.strip()
    pos = [float(i) for i in line.split(' ')]

    if len(pos) != 3:
        return

    temp = pos[1]
    pos[1] = pos[2]
    pos[2] = temp

    create_pos(col, pos, name)

# thanks CD for storing a position as one float yes
def add_position2(line, col, name):
    line = line.split('#')[0]
    line = line.strip()
    pos = float(line)

    create_pos(col, (0.0, pos, 0.0), name)


def load_cca(operator, context, filepath=''):
    file = open(filepath, 'r')
    content = file.readlines()

    col = bpy.data.collections.new('Positions')
    bpy.context.scene.collection.children.link(col)

    add_position(content[6], col, 'center_of_gravity_pos')

    p = content.index('--- Positions ---\n')

    add_position(content[p+2], col, 'left_upper_wheel_pos')
    add_position(content[p+3], col, 'right_lower_wheel_pos')
    add_position(content[p+4], col, 'minigun_pos')
    add_position(content[p+6], col, 'mines_pos')
    add_position(content[p+7], col, 'missiles_pos')
    add_position(content[p+8], col, 'driver_pos')
    add_position(content[p+9], col, 'exhaust_pos')
    add_position(content[p+10], col, 'exhaust2_pos')
    add_position(content[p+11], col, 'flag_pos')
    add_position(content[p+12], col, 'bomb_pos')
    add_position(content[p+13], col, 'cockpit_cam_pos')
    add_position(content[p+14], col, 'roof_cam_pos')
    add_position(content[p+15], col, 'hood_cam_pos')
    add_position(content[p+16], col, 'bumper_cam_pos')
    add_position(content[p+17], col, 'rear_view_cam_pos')
    add_position(content[p+18], col, 'left_side_cam_pos')
    add_position(content[p+19], col, 'right_side_cam_pos')
    add_position(content[p+20], col, 'driver1_cam_pos')
    add_position(content[p+21], col, 'driver2_cam_pos')
    add_position(content[p+22], col, 'driver3_cam_pos')
    add_position(content[p+23], col, 'steering_wheel_pos')
    add_position(content[p+24], col, 'car_cover_pos')
    add_position2(content[p+25], col, 'engine_pos')

    file.close()

    return {'FINISHED'}
