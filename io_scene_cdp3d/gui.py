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

if "bpy" in locals():
    import importlib
    if "import_cdp3d" in locals():
        importlib.reload(import_cdp3d)
    if "export_cdp3d" in locals():
        importlib.reload(export_cdp3d)

class IMPORT_OT_cdcca(bpy.types.Operator, ImportHelper):
    bl_idname       = "import_scene.cdcca"
    bl_label        = 'Import CCA'
    bl_description  = 'Import Crashday RE .cca file for positions'
    bl_options      = {'UNDO'}

    filename_ext    = ".cca"
    filter_glob     : StringProperty(default="*.cca", 
                                     options={'HIDDEN'})

    def execute(self, context):
        from . import import_cdp3d
        keywords = self.as_keywords(ignore=("filter_glob"))

        return import_cdp3d.load_cca(self, context, **keywords)

class IMPORT_OT_cdp3d(bpy.types.Operator, ImportHelper):
    bl_idname       = "import_scene.cdp3d"
    bl_label        = 'Import P3D'
    bl_description  = 'Import Crashday RE .p3d model'
    bl_options      = {'UNDO'}

    filename_ext    = ".p3d"
    filter_glob     : StringProperty(default="*.p3d", 
                                     options={'HIDDEN'})

    use_edge_split_modifier : BoolProperty(
        name        = "Use EdgeSplit, remove doubles",
        default     = True
    )

    remove_doubles_distance : FloatProperty(
        name        = "Remove doubles distance",
        default     = 0.00001
    )

    cd_path         : StringProperty(
        name        = "Path to general texture folder",
        description = "If provided plugin will auto load textures from this folder"
    )

    car_path        : StringProperty(
        name        = "Path to a car texture folder",
        description = "If provided plugin will auto load textures from this folder"
    )

    cd_path_mod     : StringProperty(
        name        = "Path to general texture folder of the mod",
        description = "If provided plugin will auto load textures from this folder"
    )

    car_path_mod    : StringProperty(
        name        = "Path to car texture folder of the mod",
        description = "If provided plugin will auto load textures from this folder"
    )

    def execute(self, context):
        from . import import_cdp3d
        keywords = self.as_keywords(ignore=("filter_glob"))

        return import_cdp3d.load(self, context, **keywords)

class EXPORT_OT_cdcca(bpy.types.Operator, ExportHelper):
    bl_idname       = "export_scene.cdcca"
    bl_label        = 'Export CCA'
    bl_description  = 'Export Crashday RE .ссa positions into text file'

    filename_ext    = ".cca"
    filter_glob     : StringProperty(default="*.txt",
                                     options={'HIDDEN'})

    def execute(self, context):
        from . import export_cdp3d
        keywords = self.as_keywords(ignore=("filter_glob",
                                            "check_existing",
                                            ))

        return export_cdp3d.save_cca(self, context, **keywords)

class EXPORT_OT_cdp3d(bpy.types.Operator, ExportHelper):
    bl_idname       = "export_scene.cdp3d"
    bl_label        = 'Export P3D'
    bl_description  = 'Export Crashday RE .p3d model'

    filename_ext    = ".p3d"
    filter_glob     : StringProperty(default="*.p3d",
                                     options={'HIDDEN'})

    use_selection   : BoolProperty(
        name        = "Selection Only",
        description = "Export selected objects only",
        default     = False
    )

    use_mesh_modifiers: BoolProperty(
        name        = "Apply Mesh Modifiers",
        description = "Apply modifiers",
        default     = True
    )

    enable_corona: BoolProperty(
        name        = "Enable Corona",
        description = "Enables corona effect for every exported lamp",
        default     = False
    )

    enable_flares: BoolProperty(
        name        = "Enable Lens Flares",
        description = "Enables lens flares for every exported lamp",
        default     = True
    )

    enable_environment: BoolProperty(
        name        = "Light Up Environment",
        description = "Static lamps will light up environemnt around",
        default     = True
    )

    use_empty_for_floor_level: BoolProperty(
        name        = "Use empty 'floor_level' object to define floor level",
        default     = True
    )

    export_log: BoolProperty(
        name        = "Export Log",
        description = "Create a log file of export process with useful data",
        default     = False
    )

    def execute(self, context):
        from . import export_cdp3d

        keywords = self.as_keywords(ignore=("filter_glob",
                                            "check_existing",
                                            ))

        return export_cdp3d.save(self, context, **keywords)

class MATERIAL_PT_p3d_materials(bpy.types.Panel):
    bl_idname      = "MATERIAL_PT_p3d_materials"
    bl_label       = "CDRE - Material"
    bl_space_type  = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context     = "material"

    def draw(self, context):
        if not context.material or not context.material.cdp3d:
            return

        layout = self.layout
        settings = context.material.cdp3d

        layout.prop(settings, "material_type", text="Material Type")


class DATA_PT_p3d_lights(bpy.types.Panel):
    bl_idname      = "DATA_PT_p3d_lights"
    bl_label       = "CDRE - Light"
    bl_space_type  = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context     = "data"

    def draw(self, context):
        if not context.light.cdp3d:
            return
        
        layout = self.layout
        settings = context.light.cdp3d

        layout.prop(context.light, 'color')
        layout.prop(context.light, 'energy', text='Range')

        layout.prop(settings, 'corona')
        layout.prop(settings, 'lens_flares')
        layout.prop(settings, 'lightup_environment')

        

class CDP3DMaterialProps(bpy.types.PropertyGroup):
    
    material_type : bpy.props.EnumProperty(
        name        = 'Material Type',
        items       = (
            ('FLAT', 'Flat', 'Flat shading'),
            ('FLAT_METAL', 'Flat Metal', 'Flat shading for metals?'),
            ('GOURAUD', 'Gouraud', 'Smooth shading'),
            ('GOURAUD_METAL', 'Gouraud Metal', 'Smooth shading for metals?'),
            ('GOURAUD_METAL_ENV', 'Gouraud Metal Env', 'Smooth shading for environment metals'),
            ('SHINING', 'Shining', 'Shining material. Used for glowing signs, makes colors shinier.')
        ),
        default     = 'GOURAUD'
    )

    def register():
        bpy.types.Material.cdp3d = bpy.props.PointerProperty(type=CDP3DMaterialProps)

class CDP3DLightProps(bpy.types.PropertyGroup):
    
    corona          : bpy.props.BoolProperty(
        name        = 'Enable Corona',
        default     = True,
        description = "Enable corona effect for this light"
    )

    lens_flares     : bpy.props.BoolProperty(
        name        = 'Enable Lens Flares',
        default     = True,
        description = "Enable lens flares for this light"
    )

    lightup_environment : bpy.props.BoolProperty(
        name        = 'Enable Environment Lighting',
        default     = True,
        description = "Should this lamp lightup environment (only works for tiles)"
    )

    def register():
        bpy.types.Light.cdp3d = bpy.props.PointerProperty(type=CDP3DLightProps)