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

from . import export_cdp3d
from . import import_cdp3d


if 'bpy' in locals():
    import importlib
    importlib.reload(import_cdp3d)
    importlib.reload(export_cdp3d)

class IMPORT_OT_cdcca(bpy.types.Operator, ImportHelper):
    bl_idname       = 'import_scene.cdcca'
    bl_label        = 'Import CCA'
    bl_description  = 'Import Crashday RE .cca file for positions'
    bl_options      = {'UNDO'}

    filename_ext    = '.cca'
    filter_glob     : StringProperty(default='*.cca', 
                                     options={'HIDDEN'})

    def execute(self, context):
        from . import import_cdp3d
        keywords = self.as_keywords(ignore=('filter_glob',))

        return import_cdp3d.load_cca(self, context, **keywords)

class IMPORT_OT_cdp3d(bpy.types.Operator, ImportHelper):
    bl_idname       = 'import_scene.cdp3d'
    bl_label        = 'Import P3D'
    bl_description  = 'Import Crashday RE .p3d model'
    bl_options      = {'UNDO'}

    filename_ext    = '.p3d'
    filter_glob     : StringProperty(default='*.p3d', 
                                     options={'HIDDEN'})

    use_edge_split_modifier : BoolProperty(
        name        = 'Use EdgeSplit, remove doubles',
        default     = True
    )

    remove_doubles_distance : FloatProperty(
        name        = 'Remove doubles distance',
        default     = 0.00001
    )

    cd_path         : StringProperty(
        name        = 'Path to general texture folder',
        description = 'If provided plugin will auto load textures from this folder'
    )

    car_path        : StringProperty(
        name        = 'Path to a car texture folder',
        description = 'If provided plugin will auto load textures from this folder'
    )

    cd_path_mod     : StringProperty(
        name        = 'Path to general texture folder of the mod',
        description = 'If provided plugin will auto load textures from this folder'
    )

    car_path_mod    : StringProperty(
        name        = 'Path to car texture folder of the mod',
        description = 'If provided plugin will auto load textures from this folder'
    )

    def execute(self, context):
        from . import import_cdp3d
        keywords = self.as_keywords(ignore=('filter_glob',))

        return import_cdp3d.load(self, context, **keywords)

class EXPORT_OT_cdcca(bpy.types.Operator, ExportHelper):
    bl_idname       = 'export_scene.cdcca'
    bl_label        = 'Export CCA'
    bl_description  = 'Export Crashday RE .ссa positions into text file'

    filename_ext    = '.cca'
    filter_glob     : StringProperty(default='*.txt',
                                     options={'HIDDEN'})

    def execute(self, context):
        from . import export_cdp3d
        keywords = self.as_keywords(ignore=('filter_glob',
                                            'check_existing',
                                            ))

        return export_cdp3d.save_cca(self, context, **keywords)

class EXPORT_OT_cdp3d(bpy.types.Operator, ExportHelper):
    bl_idname       = 'export_scene.cdp3d'
    bl_label        = 'Export P3D'
    bl_description  = 'Export Crashday RE .p3d model'

    filename_ext    = '.p3d'
    filter_glob     : StringProperty(default='*.p3d',
                                     options={'HIDDEN'})

    use_selection   : BoolProperty(
        name        = 'Selection Only',
        description = 'Export selected objects only',
        default     = False
    )

    use_mesh_modifiers: BoolProperty(
        name        = 'Apply Mesh Modifiers',
        description = 'Apply modifiers',
        default     = True
    )

    use_empty_for_floor_level: BoolProperty(
        name        = 'Use empty \'floor_level\' object to define floor level',
        default     = True
    )

    bbox_mode       : EnumProperty(
        name        = 'Bounding box mode',
        description = 'Bounding box defines area in which collisions will be detected. Meshes outside this box will have no collisions.',
        items       = (
            ('MAIN',    'Main mesh',    'Calculate bounding box using main mesh sizes. This is default makep3d behaviour.'),
            ('ALL',     'All meshes',   'Calculate bounding box using all meshes. Everything will be collidable.')
        ),
        default     = 'MAIN'
    )

    force_main_mesh : BoolProperty(
        name        = 'Force main mesh',
        description = 'If no main mesh was found, try finding a substite mesh and use it as main.',
        default     = False
    )

    export_log: BoolProperty(
        name        = 'Export Log',
        description = 'Create a log file of export process with useful data',
        default     = False
    )

    def execute(self, context):
        from . import export_cdp3d

        keywords = self.as_keywords(ignore=('filter_glob',
                                            'check_existing',
                                            ))

        return export_cdp3d.save(self, context, **keywords)