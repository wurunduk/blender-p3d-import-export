import struct

# TODO:
# - add error checking for struct reading\writing
# - this is some terrible OOP like code which is terrible and only decreases redability. Burn this with fire and don't you dare copy it to somewhere else

def rf(file, format):
    answer = struct.unpack(format, file.read(struct.calcsize(format)))
    return answer[0] if len(answer) == 1 else answer

def rf_str(file):
    string = b''
    while True:
        char = struct.unpack('<c', file.read(1))[0]
        if char == b'\x00':
            break
        string += char
    return str(string, 'utf-8', 'replace')

def wf(file, format, *args):
    file.write(struct.pack(format, *args))

def wf_str(file, st):
    wf(file, '<%ds' % (len(st)+1), st.encode('ASCII', 'replace'))

class TextureInfo:
    def __init__(self):
        self.texture_start = 0
        self.num_flat = 0
        self.num_flat_metal = 0
        self.num_gouraud = 0
        self.num_gouraud_metal = 0
        self.num_gouraud_metal_env = 0
        self.num_shining = 0

    def __str__(self):
        return 'tex info: {} {} {} {} {} {} {}'.format(
            self.texture_start, self.num_flat, self.num_flat_metal,
            self.num_gouraud, self.num_gouraud_metal, self.num_gouraud_metal_env,
            self.num_shining)

    def read(self, file):
        (self.texture_start,
        self.num_flat,
        self.num_flat_metal,
        self.num_gouraud,
        self.num_gouraud_metal,
        self.num_gouraud_metal_env,
        self.num_shining) = rf(file, '<7H')

    def write(self, file):
        wf(file, '<7H',
            self.texture_start,
            self.num_flat,
            self.num_flat_metal,
            self.num_gouraud,
            self.num_gouraud_metal,
            self.num_gouraud_metal_env,
            self.num_shining
            )

class Light:
    def __init__(self):
        self.name = 'light'
        self.pos = [0.0, 0.0, 0.0]
        self.range = 1.0
        self.color = 255

        self.show_corona = True
        self.show_lens_flares = True
        self.lightup_environment = True

    def __str__(self):
        formated_pos = ['{0:0.2f}'.format(i) for i in self.pos]
        return '''{}\nrange: {:.2f}, color: #{:x}\ncorona {}, flares {}, environment {}\npos: {}\n'''.format(
            self.name[0] if type(self.name) is tuple else self.name,
            self.range, self.color,
            self.show_corona, self.show_lens_flares, self.lightup_environment,
            formated_pos
        )

    def read(self, file):
        self.name = rf_str(file)

        (self.pos[0], self.pos[2], self.pos[1],
        self.range, self.color,
        self.show_corona, self.show_lens_flares,
        self.lightup_environment) = rf(file, '<4fi3B')

    def write(self, file):
        wf_str(file, self.name.lower())
        wf(file, '<4fi3B', self.pos[0], self.pos[2], self.pos[1],
        self.range, self.color, self.show_corona,
        self.show_lens_flares, self.lightup_environment)

class Polygon:
    def __init__(self):
        self.texture = ''
        self.material = 0

        self.p1 = 0
        self.u1 = 0.0
        self.v1 = 0.0

        self.p2 = 0
        self.u2 = 0.0
        self.v2 = 0.0

        self.p3 = 0
        self.u3 = 0.0
        self.v3 = 0.0

    def __str__(self):
        return str(self.__class__) + ': ' + str(self.__dict__)

    def read(self, file):
        (self.p1, self.u1, self.v1,
        self.p3, self.u3, self.v3,
        self.p2, self.u2, self.v2
        ) = rf(file, '<H2fH2fH2f')

        self.v1 = 1.0 - self.v1
        self.v2 = 1.0 - self.v2
        self.v3 = 1.0 - self.v3

    def write(self, file):
        wf(file, '<H2fH2fH2f',
        self.p1, self.u1, 1.0 - self.v1,
        self.p3, self.u3, 1.0 - self.v3,
        self.p2, self.u2, 1.0 - self.v2
        )

class Mesh:
    def __init__(self):
        self.name = 'mesh'
        self.flags = 0
        self.pos = [0.0, 0.0, 0.0]

        self.length = 0.0
        self.height = 0.0
        self.depth = 0.0

        #this is not in the default p3d format
        self.materials_used = []

        self.texture_infos = []

        self.num_vertices = 0
        self.vertices = []

        self.num_polys = 0
        self.polys = []

    def __str__(self):
        formated_pos = ['{0:0.2f}'.format(i) for i in self.pos]
        return '''Mesh: {}\nflags: {}, vertices: {}, polys: {}
pos: {}\nsize: {:.2f} {:.2f} {:.2f} \n'''.format(
            self.name[0] if type(self.name) is tuple else self.name,
            self.flags, self.num_vertices, self.num_polys,
            formated_pos,
            self.length, self.height, self.depth
        )

    def read(self, file, textures, num_textures):
        def r(format):
            return rf(file, format)

        self.name = rf_str(file)

        (self.flags,
        self.pos[0], self.pos[2], self.pos[1],
        self.length, self.height,
        self.depth) = rf(file, '<i6f')

        self.texture_infos = []
        for i in range(num_textures):
            tex_info = TextureInfo()
            tex_info.read(file)
            self.texture_infos.append(tex_info)

        self.num_vertices = r('<H')
        self.vertices = []
        for v in range(self.num_vertices):
            vp = r('<3f')
            self.vertices.append((vp[0], vp[2], vp[1]))

        self.num_polys = r('<H')
        self.polys = []
        for p in range(self.num_polys):
            poly = Polygon()
            poly.read(file)
            self.polys.append(poly)

        #at this point we have read everything but we need to fill
        #texture and materials of every polygon from the packed data
        #of the p3d model
        self.materials_used = []
        for ji, j in enumerate(self.texture_infos):
            polys_in_tex = j.texture_start

            def add_material_type(name, amount, polys_in_tex):
                for n in range(amount):
                    if((name, textures[ji]) not in self.materials_used):
                        self.materials_used.append((name, textures[ji]))
                    self.polys[polys_in_tex + n].material = name
                    self.polys[polys_in_tex + n].texture = textures[ji]

                return polys_in_tex + amount

            polys_in_tex = add_material_type('FLAT', j.num_flat, polys_in_tex)
            polys_in_tex = add_material_type('FLAT_METAL', j.num_flat_metal, polys_in_tex)
            polys_in_tex = add_material_type('GOURAUD', j.num_gouraud, polys_in_tex)
            polys_in_tex = add_material_type('GOURAUD_METAL', j.num_gouraud_metal, polys_in_tex)
            polys_in_tex = add_material_type('GOURAUD_METAL_ENV', j.num_gouraud_metal_env, polys_in_tex)
            polys_in_tex = add_material_type('SHINING', j.num_shining, polys_in_tex)

    def write(self, file):
        def w(format, *args):
            wf(file, format, *args)

        def w_str(st):
            wf_str(file, st)

        file.write(b'SUBMESH')
        w('<I', 1337)
        w_str(self.name.lower())

        w('<I6f', self.flags,
        self.pos[0], self.pos[2], self.pos[1],
        self.length, self.height, self.depth
        )

        for ti in self.texture_infos:
            ti.write(file)

        if self.num_vertices != len(self.vertices):
            print('Counted num_vertices differs from actual amount of vertices! Report this error!')
            self.num_vertices = len(self.vertices)
        w('<H', self.num_vertices)
        for v in self.vertices:
            w('<3f', v[0], v[2], v[1])

        if self.num_polys != len(self.polys):
            print('Counted num_polys differs from actual amount of polys! Report this error!')
            self.num_polys = (self.polys)
        w('<H', self.num_polys)
        for p in self.polys:
            p.write(file)

class P3D:
    def __init__(self):
        self.length = 0.0
        self.height = 0.0
        self.depth = 0.0

        self.num_textures = 0
        self.textures = []

        self.num_lights = 0
        self.lights = []

        self.num_meshes = 0
        self.meshes = []

        self.user_data_size = 0
        self.user_data = ''

    def __str__(self):
        print('\n{} textures:'.format(self.num_textures))
        for i in self.textures:
            print(i[0] if type(i) is tuple else i)

        print('\n{} lights:'.format(self.num_lights))
        for i in self.lights:
            print(i)

        print('\n{} meshes:'.format(self.num_meshes))
        for i in self.meshes:
            print(i)
        return 'model size: {:.2f} {:.2f} {:.2f}\n{} lights, {} meshes, {} textures\n'.format(
            self.length, self.height, self.depth, self.num_lights,
            self.num_meshes, self.num_textures)

    def read(self, file):
        def r(format):
            return rf(file, format)

        def r_str():
            return rf_str(file)

        # P3D2 signature
        file.read(4)

        self.length = r('<f')
        self.height = r('<f')
        self.depth = r('<f')

        # texture list
        # TEX + 4 bytes size signature
        file.read(7)
        self.num_textures = r('<B')
        for i in range(self.num_textures):
            tex_name = r_str()
            if tex_name.endswith('.tga'):
                tex_name = tex_name[0:-4]
            self.textures.append(tex_name)

        # lights list
        # LIGHTS + 4 bytes size signature
        file.read(10)

        self.num_lights = r('<H')
        for i in range(self.num_lights):
            p = Light()
            p.read(file)
            self.lights.append(p)

        # meshes list
        # MESHES + 4 bytes size signature
        file.read(10)
        self.num_meshes = r('<H')
        self.meshes = []
        for i in range(self.num_meshes):
            # SUBMESH + 4 bytes size signature
            file.read(11)
            p = Mesh()
            p.read(file, self.textures, self.num_textures)
            self.meshes.append(p)

        file.read(8)
        self.user_data_size = r('<i')

    def write(self, file):
        def w(format, *args):
            wf(file, format, *args)

        def w_str(st):
            wf_str(file, st)

        file.write(b'P3D\x02')

        w('<3f', self.length, self.height, self.depth)

        # texture list
        file.write(b'TEX')
        w('<I', 1337)
        w('<B', self.num_textures)
        if self.num_textures != len(self.textures):
            print('Counted num_textures differs from actual amount of textures! Report this error!')
            self.num_textures = len(self.textures)
        for tex in self.textures:
            tn = tex + '.tga'
            w_str(tn.lower())

        # lights list
        file.write(b'LIGHTS')
        w('<I', 1337)
        w('<H', self.num_lights)
        if self.num_lights != len(self.lights):
            print('Counted num_lights differs from actual amount of lights! Report this error!')
            self.num_lights = len(self.lights)
        for light in self.lights:
            light.write(file)

        # meshes list
        file.write(b'MESHES')
        w('<I', 1337)
        w('<H', self.num_meshes)
        if self.num_meshes != len(self.meshes):
            print('Counted num_meshes differs from actual amount of meshes! Report this error!')
            self.num_meshes = len(self.meshes)
        for m in self.meshes:
            m.write(file)

        file.write( b'USER')
        w('<I', 1337)
        w('<i', 0)
