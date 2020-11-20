import bpy

class CDP3DMaterialProps(bpy.types.PropertyGroup):
    material_name   : bpy.props.StringProperty (
        name        = 'Texture Name',
        default     = 'colwhite',
        description = 'Name of the .tga or .dds texture to be used'
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
        name        = 'Enable Corona(dont press in 2020)',
        default     = True,
        description = 'Enable corona effect for this light'
    )

    lens_flares     : bpy.props.BoolProperty(
        name        = 'Enable Lens Flares',
        default     = True,
        description = 'Enable lens flares for this light'
    )

    lightup_environment : bpy.props.BoolProperty(
        name        = 'Enable Environment Lighting',
        default     = True,
        description = 'Should this lamp lightup environment (only works for tiles)'
    )

    def register():
        bpy.types.Light.cdp3d = bpy.props.PointerProperty(type=CDP3DLightProps)

class CDP3DMeshProps(bpy.types.PropertyGroup):
    collisions      : bpy.props.BoolProperty(
        name        = 'Enable Collisions',
        default     = True,
        description = 'Enable collisions on this mesh. Only parts which are inside tile bbox will be collidable.'
    )

    def register():
        bpy.types.Mesh.cdp3d = bpy.props.PointerProperty(type=CDP3DMeshProps)