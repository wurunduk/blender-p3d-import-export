import bpy

if "bpy" in locals():
    import importlib
    if "gui" in locals():
        importlib.reload(gui)

from . import gui

bl_info = {
    "name": "Crashday p3d format",
    "author": "Wurunduk",
    "blender": (2, 83, 0),
    "location": "File > Import-Export",
    "version": (1, 5, 0),
    "support": 'COMMUNITY',
    "category": "Import-Export"}

classes = [
    gui.IMPORT_OT_cdcca,
    gui.IMPORT_OT_cdp3d,
    gui.EXPORT_OT_cdcca,
    gui.EXPORT_OT_cdp3d,
    gui.MATERIAL_PT_p3d_materials,
    gui.DATA_PT_p3d_lights,
    gui.CDP3DMaterialProps,
    gui.CDP3DLightProps
]

# Add to a menu
def menu_func_export(self, context):
    self.layout.operator(gui.EXPORT_OT_cdp3d.bl_idname, text="Crashday Model (.p3d)")
    self.layout.operator(gui.EXPORT_OT_cdcca.bl_idname, text="Crashday Carinfo Pos (.txt)")


def menu_func_import(self, context):
    self.layout.operator(gui.IMPORT_OT_cdp3d.bl_idname, text="Crashday Model (.p3d)")
    self.layout.operator(gui.IMPORT_OT_cdcca.bl_idname, text="Crashday Carinfo (.cca)")


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

if __name__ == "__main__":
    register()