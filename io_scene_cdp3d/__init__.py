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
    "blender": (2, 80, 0),
    "location": "File > Import-Export",
    "version": (2, 0, 0),
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



class ImportCDP3D(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.crashday_p3d"
    bl_label = 'Import P3D'
    bl_options = {'UNDO'}

    filename_ext = ".p3d"
    filter_glob: StringProperty(default="*.p3d", options={'HIDDEN'})

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
        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            ))

        return import_cdp3d.load(self, context, **keywords)


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

    enable_corona: BoolProperty(
            name = "Enable corona",
            description="Enables corona effect for every exported lamp",
            default=False,
            )

    enable_flares: BoolProperty(
            name = "Enable lens flares",
            description="Enables lens flares for every exported lamp",
            default=True,
            )

    enable_environment: BoolProperty(
            name = "Light up environment",
            description="Static lamps will light up environemnt around",
            default=True,
            )

    center_objects_to_origin: BoolProperty(
            name = "Center object verticies to origin",
            description = """Moves every vertex so the center of the mesh will be the same at 0,0,0\n
            This is the default behaviour of makep3d. If you have any physics bugs in-game, check this""",
            default=True,
            )

    def execute(self, context):
        from . import export_cdp3d

        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            "check_existing",
                                            ))

        return export_cdp3d.save(self, context, **keywords)


# Add to a menu
def menu_func_export(self, context):
    self.layout.operator(ExportCDP3D.bl_idname, text="Crashday (.p3d)")


def menu_func_import(self, context):
    self.layout.operator(ImportCDP3D.bl_idname, text="Crashday (.p3d)")


def register():
    bpy.utils.register_class(ExportCDP3D)
    bpy.utils.register_class(ImportCDP3D)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportCDP3D)
    bpy.utils.unregister_class(ImportCDP3D)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
