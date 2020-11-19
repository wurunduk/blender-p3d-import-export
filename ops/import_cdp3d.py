import bpy, bmesh, os
import time
import struct

from ..crashday import p3d

if 'bpy' in locals():
    import importlib
    importlib.reload(p3d)

def int_to_color(value):
    return (((value >> 16) & 255)/255.0, ((value >> 8) & 255)/255.0, (value & 255)/255.0)

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
        print('Could not load texture {}'.format(p))
        return None

def add_textures(p3d_model, paths):
    for tex in p3d_model.textures:
        texture = bpy.data.textures.get(tex)

        if texture is None:
            texture = bpy.data.textures.new(tex, type='IMAGE')

        for p in paths:
            path = texture_exists(p, tex)
            if path is not None:
                img = bpy.data.images.load(path)
                texture.image = img
                break

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

        if(material_name[0] == 'FLAT'):
            principled_bsdf.inputs['Metallic'].default_value  = 0.0
            principled_bsdf.inputs['Specular'].default_value = 1.0
            principled_bsdf.inputs['Roughness'].default_value = 1.0
        elif(material_name[0] == 'FLAT_METAL'):
            principled_bsdf.inputs['Metallic'].default_value = 1.0
            principled_bsdf.inputs['Specular'].default_value = .9
            principled_bsdf.inputs['Roughness'].default_value = .9
        elif(material_name[0] == 'GOURAUD'):
            principled_bsdf.inputs['Metallic'].default_value = 0.0
            principled_bsdf.inputs['Specular'].default_value = 0.1
            principled_bsdf.inputs['Roughness'].default_value = 0.8
        elif(material_name[0] == 'GOURAUD_METAL'):
            principled_bsdf.inputs['Metallic'].default_value = .8
            principled_bsdf.inputs['Specular'].default_value = .5
            principled_bsdf.inputs['Roughness'].default_value = .2
        elif(material_name[0] == 'GOURAUD_METAL_ENV'):
            principled_bsdf.inputs['Metallic'].default_value = .5
            principled_bsdf.inputs['Specular'].default_value = .3
            principled_bsdf.inputs['Roughness'].default_value = .05
        elif(material_name[0] == 'SHINING'):
            principled_bsdf.inputs['Metallic'].default_value = 1.0
            principled_bsdf.inputs['Specular'].default_value = .2
            principled_bsdf.inputs['Roughness'].default_value = .0

        material.node_tree.links.new(principled_bsdf.inputs['Base Color'], texImage.outputs['Color'])

    obj.data.materials.append(material)

def create_meshes(p3d_model, col, use_edge_split_modifier, remove_doubles_distance):
    for m in p3d_model.meshes:
        mesh = bpy.data.meshes.new(name=m.name)
        obj = bpy.data.objects.new(mesh.name, mesh)
        obj.location = m.pos

        col.objects.link(obj)

        # if "coll" in m.name or "shad" in m.name or "lod" in m.name or "." in m.name:
        #     obj.hide_set(True)

        mesh.cdp3d.collisions = m.flags & 2

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
            mod = obj.modifiers.new("EdgeSplit", 'EDGE_SPLIT')
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
         cd_path='', car_path='',
         cd_path_mod='', car_path_mod=''):

    file_name = filepath.split('\\')[-1]

    print('\nImporting file {} from {}'.format(file_name, filepath))

    search_path = []
    if os.path.exists(cd_path):
        search_path.append(cd_path)
    if os.path.exists(car_path):
        search_path.append(car_path)
    if os.path.exists(cd_path_mod):
        search_path.append(cd_path_mod)
    if os.path.exists(car_path_mod):
        search_path.append(car_path_mod)

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
    
    

