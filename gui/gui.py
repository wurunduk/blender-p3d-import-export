import bpy

class MATERIAL_PT_p3d_material(bpy.types.Panel):
    bl_idname      = "MATERIAL_PT_p3d_material"
    bl_label       = "CDRE - Material"
    bl_space_type  = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context     = "material"

    def draw(self, context):
        if not context.material or not context.material.cdp3d:
            return

        layout = self.layout
        settings = context.material.cdp3d

        layout.prop(settings, "material_name")
        layout.prop(settings, "material_type", text="Material Type")

class DATA_PT_p3d_light(bpy.types.Panel):
    bl_idname      = "DATA_PT_p3d_light"
    bl_label       = "CDRE - Light"
    bl_space_type  = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context     = "data"

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
    bl_idname      = "DATA_PT_p3d_mesh"
    bl_label       = "CDRE - Mesh"
    bl_space_type  = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context     = "data"

    def draw(self, context):
        if not context.mesh or not context.mesh.cdp3d:
            return

        layout = self.layout
        settings = context.mesh.cdp3d

        layout.prop(settings, "collisions")