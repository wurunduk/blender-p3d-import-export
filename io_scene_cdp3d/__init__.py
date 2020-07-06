# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Crashday p3d format",
    "author": "Wurunduk",
    "blender": (2, 83, 0),
    "location": "File > Import-Export",
    "version": (1, 4, 2),
    "support": 'COMMUNITY',
    "category": "Import-Export"}

if "bpy" in locals():
    import importlib
    if "import_cdp3d" in locals():
        importlib.reload(import_cdp3d)
    if "export_cdp3d" in locals():
        importlib.reload(export_cdp3d)


import bpy
from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        StringProperty,
        )
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        )

class ImportCDCCA(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.crashday_cca"
    bl_label = 'Import CCA'
    bl_options = {'UNDO'}

    filename_ext = ".cca"
    filter_glob: StringProperty(default="*.cca", options={'HIDDEN'})

    def execute(self, context):
        from . import import_cdp3d
        keywords = self.as_keywords(ignore=("filter_glob",
                                            ))

        return import_cdp3d.load_cca(self, context, **keywords)

class ImportCDP3D(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.crashday_p3d"
    bl_label = 'Import P3D'
    bl_options = {'UNDO'}

    filename_ext = ".p3d"
    filter_glob: StringProperty(default="*.p3d", options={'HIDDEN'})

    use_edge_split_modifier: BoolProperty(
        name="Use EdgeSplit modifier for hard edges, remove doubles",
        default=True,
    )

    cd_path: StringProperty(
        name="Path to general texture folder",
        description="If provided plugin will auto load textures from this folder"
    )

    car_path: StringProperty(
        name="Path to a car texture folder",
        description="If provided plugin will auto load textures from this folder"
    )

    cd_path_mod: StringProperty(
        name="Path to general texture folder of the mod",
        description="If provided plugin will auto load textures from this folder"
    )

    car_path_mod: StringProperty(
        name="Path to car texture folder of the mod",
        description="If provided plugin will auto load textures from this folder"
    )

    def execute(self, context):
        from . import import_cdp3d
        keywords = self.as_keywords(ignore=("filter_glob",
                                            ))

        return import_cdp3d.load(self, context, **keywords)

class ExportCDCCA(bpy.types.Operator, ExportHelper):
    bl_idname = "export_scene.crashday_cca"
    bl_label = 'Export CCA'

    filename_ext = ".txt"
    filter_glob:StringProperty(
            default="*.txt",
            options={'HIDDEN'},
            )

    def execute(self, context):
        from . import export_cdp3d

        keywords = self.as_keywords(ignore=("filter_glob",
                                            "check_existing",
                                            ))

        return export_cdp3d.save_cca(self, context, **keywords)

class ExportCDP3D(bpy.types.Operator, ExportHelper):
    bl_idname = "export_scene.crashday_p3d"
    bl_label = 'Export P3D'

    filename_ext = ".p3d"
    filter_glob:StringProperty(
            default="*.p3d",
            options={'HIDDEN'},
            )

    use_selection: BoolProperty(
            name="Selection Only",
            description="Export selected objects only",
            default=False,
            )

    use_mesh_modifiers: BoolProperty(
            name="Apply Mesh Modifiers",
            description="Apply modifiers",
            default=True,
            )

    enable_corona: BoolProperty(
            name = "Enable Corona",
            description="Enables corona effect for every exported lamp",
            default=False,
            )

    enable_flares: BoolProperty(
            name = "Enable Lens Flares",
            description="Enables lens flares for every exported lamp",
            default=True,
            )

    enable_environment: BoolProperty(
            name = "Light Up Environment",
            description="Static lamps will light up environemnt around",
            default=True,
            )

    use_empty_for_floor_level: BoolProperty(
        name = "Use empty 'floor_level' object to define floor level",
        default=True,
    )

    lower_top_bound: FloatProperty(
            name = "Lower Top Bound",
            default = 0.0,
    )

    lift_bottom_bound: FloatProperty(
            name = "Lift Bottom Bound",
            default = 0.0,
    )

    export_log: BoolProperty(
            name = "Export Log",
            description = "Create a log file of export process with useful data",
            default=False,
            )

    def execute(self, context):
        from . import export_cdp3d

        keywords = self.as_keywords(ignore=("filter_glob",
                                            "check_existing",
                                            ))

        return export_cdp3d.save(self, context, **keywords)


# Add to a menu
def menu_func_export(self, context):
    self.layout.operator(ExportCDP3D.bl_idname, text="Crashday Model(.p3d)")
    self.layout.operator(ExportCDCCA.bl_idname, text="Crashday Carinfo Pos(.txt)")


def menu_func_import(self, context):
    self.layout.operator(ImportCDP3D.bl_idname, text="Crashday Model(.p3d)")
    self.layout.operator(ImportCDCCA.bl_idname, text="Crashday Carinfo(.cca)")


def register():
    bpy.utils.register_class(ExportCDP3D)
    bpy.utils.register_class(ExportCDCCA)
    bpy.utils.register_class(ImportCDP3D)
    bpy.utils.register_class(ImportCDCCA)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportCDP3D)
    bpy.utils.unregister_class(ExportCDCCA)
    bpy.utils.unregister_class(ImportCDP3D)
    bpy.utils.unregister_class(ImportCDCCA)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
