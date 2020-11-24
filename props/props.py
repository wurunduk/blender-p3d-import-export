import bpy

class CDP3DMaterialProps(bpy.types.PropertyGroup):
    use_texture     : bpy.props.BoolProperty (
        name        = 'Try using texture name',
        description = 'If a texture is found, use texture name for material name',
        default     = True
    )

    material_name   : bpy.props.StringProperty (
        name        = 'Texture Name',
        description = 'Name of the .tga or .dds texture to be used',
        default     = 'colwhite'
    )

    material_type   : bpy.props.EnumProperty(
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
        name        = 'Enable Corona (dont press in 2020)',
        description = 'Enable corona effect for this light',
        default     = True
    )

    lens_flares     : bpy.props.BoolProperty(
        name        = 'Enable Lens Flares',
        description = 'Enable lens flares for this light',
        default     = True
    )

    lightup_environment : bpy.props.BoolProperty(
        name        = 'Enable Environment Lighting',
        description = 'Should this lamp lightup environment (only works for tiles)',
        default     = True
    )

    def register():
        bpy.types.Light.cdp3d = bpy.props.PointerProperty(type=CDP3DLightProps)

class CDP3DMeshProps(bpy.types.PropertyGroup):
    flags           : bpy.props.EnumProperty(
        name        = 'Flags',
        description = 'Flags set for this mesh.',
        options     = {'ENUM_FLAG'},
        items       = (
            ('MAIN', 'Main',
            'Main mesh',
            1 << 0),
            ('VIS', 'Visible',
            'Is visible', 
            1 << 1),
            ('TRACE', 'Tracing',
            'Used to detect bullet hits, maybe shadows? This is used for cars',
            1 << 2),
            ('COLL', 'Collision',
            'Is collision shape? This is used for cars',
            1 << 3),
            ('NOLOD', 'LOD 1 aka normal mesh',
            'Level of detail 1. Used for default looking meshes',
            1 << 4),
            ('LOD0', 'LOD 0',
            'Level of detail 0. Used for best looking mesh up-close',
            1 << 5),
            ('LOD2', 'LOD 2',
            'Level of detail 2. Used for the first worse looking mesh',
            1 << 6),
            ('LOD3', 'LOD 3',
            'Level of detail 3. Used for the second worst looking mesh',
            1 << 7),
            ('LOD4', 'LOD 4',
            'Level of detail 4. Used for the worst looking mesh',
            1 << 8),
            ('SUB0', 'SUBMESH LOD 0',
            '??????????????????????',
            1 << 9),
            ('SUB2', 'SUBMESH LOD 2',
            '??????????????????????',
            1 << 10),
            ('SUB3', 'SUBMESH LOD 3',
            '??????????????????????',
            1 << 11),
            ('SUB4', 'SUBMESH LOD 4',
            '??????????????????????',
            1 << 12),
            ('DET', 'Detachable',
            'Object can be lost from the car',
            1 << 13),
            ('BRG', 'Breakable glass',
            '',
            1 << 14),
            ('BRP', 'Breakable plastic',
            '',
            1 << 15),
            ('BRW', 'Breakable wood',
            '',
            1 << 16),
            ('BRM', 'Breakable metal',
            '',
            1 << 17),
            ('BRE', 'Breakable explosive',
            '',
            1 << 18),
            ('LIPL', 'License place',
            '',
            1 << 19),
            ('HDL', 'Headlights',
            '',
            1 << 20),
            ('BRL', 'Brakelights',
            '',
            1 << 21),
            ('DMG', 'Damaged version',
            'This object appears when some other object is getting damaged',
            1 << 22),
            ('NOCL', 'No collision',
            'This object has no collisions with cars',
            1 << 23),
        ),
        default     = {'VIS'}
    )

    def register():
        bpy.types.Mesh.cdp3d = bpy.props.PointerProperty(type=CDP3DMeshProps)