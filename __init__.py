import bpy
from .gui import gui
from .ops import ops
from .props import props

if 'bpy' in locals():
    import importlib
    importlib.reload(gui)
    importlib.reload(ops)
    importlib.reload(props)

bl_info = {
    'name': 'Crashday p3d Exporter',
    'author': 'Wurunduk',
    'blender': (2, 83, 0),
    'location': 'File > Import-Export',
    'version': (1, 6, 1),
    'support': 'COMMUNITY',
    'category': 'Import-Export'}

classes = [
    ops.IMPORT_OT_cdcca,
    ops.IMPORT_OT_cdp3d,
    ops.EXPORT_OT_cdcca,
    ops.EXPORT_OT_cdp3d,
    gui.MATERIAL_PT_p3d_material,
    gui.DATA_PT_p3d_light,
    gui.DATA_PT_p3d_mesh,
    props.CDP3DMaterialProps,
    props.CDP3DLightProps,
    props.CDP3DMeshProps
]

# Add to a menu
def menu_func_export(self, context):
    self.layout.operator(ops.EXPORT_OT_cdp3d.bl_idname, text='Crashday Model (.p3d)')
    self.layout.operator(ops.EXPORT_OT_cdcca.bl_idname, text='Crashday Carinfo Pos (.txt)')


def menu_func_import(self, context):
    self.layout.operator(ops.IMPORT_OT_cdp3d.bl_idname, text='Crashday Model (.p3d)')
    self.layout.operator(ops.IMPORT_OT_cdcca.bl_idname, text='Crashday Carinfo (.cca)')


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_export)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_import)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == '__main__':
    register()