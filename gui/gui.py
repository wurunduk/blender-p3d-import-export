import bpy


class MATERIAL_PT_p3d_material(bpy.types.Panel):
    bl_idname      = 'MATERIAL_PT_p3d_material'
    bl_label       = 'Crashday - Material'
    bl_space_type  = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context     = 'material'

    def draw(self, context):
        if not context.material or not context.material.cdp3d:
            return

        def get_texture_name():
            img = context.material.node_tree.nodes.get('Image Texture')
            if img and img.image:
                return img.image.name
            else:
                return None

        layout = self.layout
        col = layout.column()
        settings = context.material.cdp3d

        col.prop(settings, 'use_texture')
        if settings.use_texture:
            found_texture = get_texture_name()
            if found_texture:
                col.label(text='Found texture: {}'.format(found_texture))
            else:
                col.label(text='Texture not found, using {}'.format(settings.material_name), icon='ERROR')

        sub = col.row()
        sub.enabled = not settings.use_texture or found_texture is None
        sub.prop(settings, 'material_name')
        col.prop(settings, 'material_type', text='Material Type')

class DATA_PT_p3d_light(bpy.types.Panel):
    bl_idname      = 'DATA_PT_p3d_light'
    bl_label       = 'Crashday - Light'
    bl_space_type  = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context     = 'data'

    @classmethod
    def poll(cls, context):
        light = context.light
        return (light and light.type in {'POINT', 'SUN', 'SPOT', 'AREA'})
        

    def draw(self, context):
        if not context.light or not context.light.cdp3d:
            return
        
        layout = self.layout
        settings = context.light.cdp3d

        layout.prop(context.light, 'color')
        layout.prop(context.light, 'energy', text='Range')

        layout.prop(settings, 'corona')
        layout.prop(settings, 'lens_flares')
        layout.prop(settings, 'lightup_environment')

class DATA_PT_p3d_mesh(bpy.types.Panel):
    bl_idname      = 'DATA_PT_p3d_mesh'
    bl_label       = 'Crashday - Mesh'
    bl_space_type  = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context     = 'data'

    @classmethod
    def poll(cls, context):
        mesh = context.mesh
        return mesh

    def draw(self, context):
        if not context.mesh or not context.mesh.cdp3d:
            return

        layout = self.layout
        settings = context.mesh.cdp3d

        layout.prop(settings, 'collisions')