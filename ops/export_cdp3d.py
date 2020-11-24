import bpy
import struct
import datetime
import mathutils

from ..crashday import p3d

if 'bpy' in locals():
    import importlib
    importlib.reload(p3d)


def color_to_int(value):
    return int('%02x%02x%02x' % (int(value[0]*255), int(value[1]*255), int(value[2]*255)), 16)

def error_no_main(self, context):
    self.layout.label(text='Every CD model must have a main mesh!')

def sanitise_mesh_name(name):
    return name.replace(' ', '_')

def get_textures_used(ob):
    textures = []

    m = None

    # Check if there are any materials on the mesh
    for mat in ob.data.materials:
        if mat is not None:
            m = mat
            break

    # if no material was found, add default colwhite.tga material to the object
    if m is None:
        col_white = bpy.data.materials.get('empty material')
        if col_white is None:
            col_white = bpy.data.materials.new('empty material')

            col_white.cdp3d.material_name = 'colwhite'
            col_white.cdp3d.material_type = 'FLAT'

        ob.data.materials.append(col_white)

    for mat in ob.data.materials:
        tn = ''
        if mat.cdp3d.use_texture:
            if mat.node_tree:
                img = mat.node_tree.nodes.get('Image Texture') # get texture used in the material
                if img and img.image: # if exists and has linked texture
                    tn = img.image.name.rsplit( ".", 1 )[ 0 ] # remove extension if present
                    mat.cdp3d.material_name = tn
                else:
                    tn = mat.cdp3d.material_name # otherwise use material preset in cdp3d material properties
            else:
                tn = mat.cdp3d.material_name
        else:
            tn = mat.cdp3d.material_name

        if tn not in textures:
            textures.append(tn)

    return textures

def save(operator,
         context, filepath='',
         use_selection=True,
         use_mesh_modifiers=True,
         use_empty_for_floor_level=True,
         bbox_mode='MAIN',
         force_main_mesh=False,
         export_log=True):

    # get the folder where file will be saved and add a log in that folder
    work_path = '\\'.join(filepath.split('\\')[0:-1])

    log_file = None
    if export_log:
        log_file = open(work_path + '//export-log.txt', 'a')
    date = datetime.datetime.now()
    if log_file:
        log_file.write('Started exporting on {}\nFile path: {}\n'.format(date.strftime('%d-%m-%Y %H:%M:%S'), filepath))
    print('\nExporting file to {}'.format(filepath))

    # create empty p3d model
    p = p3d.P3D()

    # exit edit mode
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')

    # get dependencies graph for applying modifiers
    dg = bpy.context.evaluated_depsgraph_get()

    col = bpy.context.scene.collection

    # stores the list of exported meshes - useful for modders to define in .cca
    exported_meshes_string = ''

    # store list oj objects to export
    objects = []
    for ob in col.all_objects:
         if ob.visible_get():
            if not use_selection:
                # apply modifiers if needed and store object
                objects.append(ob.evaluated_get(dg) if use_mesh_modifiers else ob)
            elif ob.select_get():
                objects.append(ob.evaluated_get(dg) if use_mesh_modifiers else ob)

    # store the list of all the used textures
    p.textures = []

    # store main, shadow and collision meshes
    main = None
    shad = None
    coll = None

    main_like = None
    any = None

    # find the main, sadow and coll mesh of the model
    for ob in objects:
        if ob.type == 'MESH':
            any = ob
            p.textures = list(set(p.textures + get_textures_used(ob)))
            if 'main' in ob.name:
                main_like = ob
            if ob.name == 'main':
                main = ob
                main_like = ob
                any = ob
            if ob.name == 'mainshad':
                shad = ob
            if ob.name == 'maincoll':
                coll = ob

    # save the amount of textures used in p3d model
    p.num_textures = len(p.textures)

    # p3d models must have a main mesh
    if main is None:
        if not force_main_mesh:
            bpy.context.window_manager.popup_menu(error_no_main, title='No main mesh', icon='ERROR')
            print('!!! Failed to export p3d. No main mesh found.')
            if log_file:
                log_file.write('!!! Failed to export p3d. No main mesh found.\n')
                log_file.close()
            return {'CANCELLED'}
        else:
            if main_like is not None:
                print('Found main like mesh: {}. Using as main'.format(main_like.name))
                main = main_like
            elif any is not None:
                print('Found some mesh: {}. Using as main'.format(any.name))
                main = any
            else:
                print('!!! Failed to export p3d. No meshes found.')
                if log_file:
                    log_file.write('!!! Failed to export p3d. No meshes found.\n')
                    log_file.close()
                return {'CANCELLED'}

    if shad is None:
        print('! Shadow mesh was not found, using main mesh for shadow.')
        if log_file:
            log_file.write('! Shadow mesh was not found, using main mesh for shadow.\n')
    if coll is None:
        print('! Collision mesh was not found, using main mesh for collisions.')
        if log_file:
            log_file.write('! Collision mesh was not found, using main mesh for collisions.\n')

    # the main mesh in p3d is always at 0.0.
    # this means we need to move all other models alongside main mesh
    main_center = main.location
    
    # iterate through all objects in the scene and save into p3d model
    p.meshes = []
    p.lights = []
    for ob in objects:
        if ob.type == 'LIGHT':
            p.num_lights += 1

            light = p3d.Light()
            light.name = sanitise_mesh_name(ob.name)
            light.pos = ob.location - main_center
            light.range = ob.data.energy
            light.color = color_to_int(ob.data.color)

            light.show_corona = ob.data.cdp3d.corona
            light.show_lens_flares = ob.data.cdp3d.lens_flares
            light.lightup_environment = ob.data.cdp3d.lightup_environment

            p.lights.append(light)

        if ob.type == 'MESH':
            m = p3d.Mesh()

            m.name = sanitise_mesh_name(ob.name)
            m.pos = ob.location - main_center

            mesh = ob.to_mesh()

            # save vertex positions
            scale = ob.scale

            lowx = 0.0
            highx = 0.0
            lowy = 0.0
            highy = 0.0
            lowz = 0.0
            highz = 0.0

            if len(m.vertices) > 0:
                lowx = highx = m.vertices[0].co[0]*scale[0]
                lowy = highy = m.vertices[0].co[1]*scale[1]
                lowz = highz = m.vertices[0].co[2]*scale[2]

            # save vertices and calculate mesh bounds
            m.vertices = []
            for v in mesh.vertices:
                pos = [a*b for a,b in zip(v.co,scale)]
                if lowx > pos[0]: lowx = pos[0]
                if highx < pos[0]: highx = pos[0]
                if lowy > pos[1]: lowy = pos[1]
                if highy < pos[1]: highy = pos[1]
                if lowz > pos[2]: lowz = pos[2]
                if highz < pos[2]: highz = pos[2]
                m.vertices.append(pos)

            m.num_vertices = len(m.vertices)

            m.length = highx - lowx
            m.height = highz - lowz
            m.depth = highy - lowy

            if bbox_mode == 'ALL':
                p.height = max(p.height, m.height)
                p.length = max(p.length, max(highx, -lowx) * 2)
                p.depth = max(p.depth, max(highy, -lowy) * 2)

            # save model bounds
            if ob == main:
                floor_level = bpy.data.objects.get('floor_level')

                m.name = sanitise_mesh_name('main')

                if floor_level is not None and use_empty_for_floor_level:
                    fl_pos = floor_level.location
                    m.height = -(fl_pos - main.location)[2]*2

                # this is size calculation which is done in original p3d
                # but this breaks collision for non-symmetrical tiles 
                if bbox_mode == 'MAIN':
                    p.length = m.length
                    p.height = m.height
                    p.depth = m.depth

                    # while this looks dumb, this is how original makep3d works
                    if p.length >= 19.95 and p.length <= 20.05: p.length = 20
                    if p.length >= 39.95 and p.length <= 40.05: p.length = 40
                    if p.depth >= 19.95 and p.depth <= 20.05: p.depth = 20
                    if p.depth >= 39.95 and p.depth <= 40.05: p.depth = 40

                # this would fix non-symmetrical tile bounding-box
                #p.height = m.height
                #p.length = max(highx, -lowx) * 2
                #p.depth = max(highy, -lowy) * 2

            items = mesh.cdp3d.bl_rna.properties['flags'].enum_items

            for flag in mesh.cdp3d.flags:
                m.flags |= items[flag].value

            # save the flags
            if ob == main:
                m.flags |= 1
                if shad is None:
                    m.flags |= 4
                if coll is None:
                    m.flags |= 8
            elif ob == shad:
                m.flags ^= 2
                m.flags |= 4
            elif ob == coll:
                m.flags ^= 2
                m.flags |= 8

            mesh.calc_loop_triangles()

            # save polys in blender order and texture infos
            m.texture_infos = [p3d.TextureInfo() for i in range(p.num_textures)]
            polys = []
            if len(mesh.uv_layers) == 0:
                mesh.uv_layers.new()
            for uv_layer in mesh.uv_layers:
                for tri in mesh.loop_triangles:
                    if len(tri.loops) != 3:
                        break
                    pol = p3d.Polygon()

                    # texture info
                    # TODO: if a polygon is assigned to a material which was deleted this will error
                    pol.texture = ob.data.materials[tri.material_index].cdp3d.material_name
                    pol.material = ob.data.materials[tri.material_index].cdp3d.material_type
                    
                    i = p.textures.index(pol.texture)
                    if pol.material == 'FLAT':
                        m.texture_infos[i].num_flat += 1
                    if pol.material == 'FLAT_METAL':
                        m.texture_infos[i].num_flat_metal += 1
                    if pol.material == 'GOURAUD':
                        m.texture_infos[i].num_gouraud += 1
                    if pol.material == 'GOURAUD_METAL':
                        m.texture_infos[i].num_gouraud_metal += 1
                    if pol.material == 'GOURAUD_METAL_ENV':
                        m.texture_infos[i].num_gouraud_metal_env += 1
                    if pol.material == 'SHINING':
                        m.texture_infos[i].num_shining += 1

                    # polygon info
                    pol.p1 = tri.vertices[0]
                    pol.u1, pol.v1 = uv_layer.data[tri.loops[0]].uv

                    pol.p2 = tri.vertices[1]
                    pol.u2, pol.v2 = uv_layer.data[tri.loops[1]].uv

                    pol.p3 = tri.vertices[2]
                    pol.u3, pol.v3 = uv_layer.data[tri.loops[2]].uv

                    polys.append(pol)

            # reorder polys into CD format, to align texture infos
            m.polys = []
            for t in range(len(p.textures)):
                if t > 0:
                    m.texture_infos[t].texture_start = m.texture_infos[t-1].texture_start 
                    m.texture_infos[t].texture_start += m.texture_infos[t-1].num_flat
                    m.texture_infos[t].texture_start += m.texture_infos[t-1].num_flat_metal
                    m.texture_infos[t].texture_start += m.texture_infos[t-1].num_gouraud
                    m.texture_infos[t].texture_start += m.texture_infos[t-1].num_gouraud_metal
                    m.texture_infos[t].texture_start += m.texture_infos[t-1].num_gouraud_metal_env
                    m.texture_infos[t].texture_start += m.texture_infos[t-1].num_shining

                for i, pol in enumerate(polys):
                    if pol.texture == p.textures[t] and pol.material == 'FLAT':
                        m.polys.append(pol)
                
                for i, pol in enumerate(polys):
                    if pol.texture == p.textures[t] and pol.material == 'FLAT_METAL':
                        m.polys.append(pol)

                for i, pol in enumerate(polys):
                    if pol.texture == p.textures[t] and pol.material == 'GOURAUD':
                        m.polys.append(pol)

                for i, pol in enumerate(polys):
                    if pol.texture == p.textures[t] and pol.material == 'GOURAUD_METAL':
                        m.polys.append(pol)

                for i, pol in enumerate(polys):
                    if pol.texture == p.textures[t] and pol.material == 'GOURAUD_METAL_ENV':
                        m.polys.append(pol)

                for i, pol in enumerate(polys):
                    if pol.texture == p.textures[t] and pol.material == 'SHINING':
                        m.polys.append(pol)


            m.num_polys = len(m.polys)

            if len(m.vertices) == 0 or len(m.polys) == 0:
                message = 'Can\'t export empty mesh: {}. {} vertices, {} polys. Ignoring'.format(m.name, len(m.vertices), len(m.polys))
                print(message)
                if log_file:
                    log_file.write(message)
            else:
                p.num_meshes += 1
                p.meshes.append(m)
                exported_meshes_string += ob.name + ' '

    # save p3d into file
    file = open(filepath, 'wb')
    print(p)
    p.write(file)
    file.close()

    print('p3d exported')
    if log_file:
        log_file.write('Meshes: {}\n'.format(exported_meshes_string))
        log_file.write('Finished p3d export.\n\n')
        log_file.close()

    return {'FINISHED'}

def save_pos(f, col, offset, name):
    obj = col.objects.get(name)
    pos = (0.0,0.0,0.0)
    if obj is not None:
        p = obj.location
        pos = (p[0] - offset[0], p[2] - offset[2], p[1] - offset[1])

    f.write('{:.4g} {:.4g} {:.4g} \t\t\t # {}{}\n'.format(pos[0], pos[1], pos[2], '!!!NOT FOUND ON EXPORT  ' if obj is None else '', name))

def save_pos2(f, col, offset, name):
    obj = col.objects.get(name)
    pos = (0.0,0.0,0.0)
    if obj is not None:
        p = obj.location
        pos = (p[0] - offset[0], p[2] - offset[2], p[1] - offset[1])

    f.write('{:.4g} \t\t\t # {}{}\n'.format(pos[2], '!!!NOT FOUND ON EXPORT  ' if obj is None else '', name))

def save_cca(operator,
         context, filepath=''):

    f = open(filepath, 'w')
    col = bpy.context.scene

    exported_meshes_string = ''

    # store main, shadow and collision meshes
    main = None
    mpos = (0.0,0.0,0.0)

    # find the main mesh of the model
    for ob in col.collection.all_objects:
        if ob.type == 'MESH':
            exported_meshes_string += ob.name + ' '
            if ob.name == 'main':
                main = ob
                mpos = main.location

    # p3d models must have a main mesh
    if main is None:
        print('!!! No main mesh found, .cca values might be wrong if main is not centered.')
        f.write('!!! No main mesh found, .cca values might be wrong if main is not centered.')   

    f.write('Meshes: {}\n\n'.format(exported_meshes_string))

    save_pos(f, col, mpos, 'center_of_gravity_pos')
    f.write('\n')
    save_pos(f, col, mpos, 'left_upper_wheel_pos')
    save_pos(f, col, mpos, 'right_lower_wheel_pos')
    save_pos(f, col, mpos, 'minigun_pos')
    f.write('0.0\t\t\t # Angle of minigun (negative values for downpointing)\n')
    save_pos(f, col, mpos, 'mines_pos')
    save_pos(f, col, mpos, 'missiles_pos')
    save_pos(f, col, mpos, 'driver_pos')
    save_pos(f, col, mpos, 'exhaust_pos')
    save_pos(f, col, mpos, 'exhaust2_pos')
    save_pos(f, col, mpos, 'flag_pos')
    save_pos(f, col, mpos, 'bomb_pos')
    save_pos(f, col, mpos, 'cockpit_cam_pos')
    save_pos(f, col, mpos, 'roof_cam_pos')
    save_pos(f, col, mpos, 'hood_cam_pos')
    save_pos(f, col, mpos, 'bumper_cam_pos')
    save_pos(f, col, mpos, 'rear_view_cam_pos')
    save_pos(f, col, mpos, 'left_side_cam_pos')
    save_pos(f, col, mpos, 'right_side_cam_pos')
    save_pos(f, col, mpos, 'driver1_cam_pos')
    save_pos(f, col, mpos, 'driver2_cam_pos')
    save_pos(f, col, mpos, 'driver3_cam_pos')
    save_pos(f, col, mpos, 'steering_wheel_pos')
    save_pos(f, col, mpos, 'car_cover_pos')
    save_pos2(f, col, mpos, 'engine_pos')

    f.close()
    return {'FINISHED'}