from . binary_parser import *
from enum import Enum

def int_to_color(value):
    return (((value >> 16) & 255)/255.0, ((value >> 8) & 255)/255.0, (value & 255)/255.0)

class P3DMaterial(Enum):
    FLAT = 0,
    FLAT_METAL = 1,
    GOURAUD = 2,
    GOURAUD_METAL = 3,
    GOURAUD_METAL_ENV = 4,
    SHINING = 5

class P3DTextureInfo:
    texture_start = 0
    num_flat = 0
    num_flat_metal = 0
    num_gouraud = 0
    num_gouraud_metal = 0
    num_gouraud_metal_env = 0
    num_shining = 0

    def __str__(self):
        return 'tex info: {} {} {} {} {} {} {}'.format(
            self.texture_start, self.num_flat, self.num_flat_metal,
            self.num_gouraud, self.num_gouraud_metal, self.num_gouraud_metal_env,
            self.num_shining)

class P3DLight:
    name = ""
    pos = [0.0, 0.0, 0.0]
    range = 1.0
    color = 255

    show_corona = True
    show_lens_flares = True
    Lightup_environment = True

    def __str__(self):
        formated_pos = ["{0:0.2f}".format(i) for i in self.pos]
        return '''{}\nrange: {:.2f} color: {}\ncorona {} flares {} environment {}\npos: {}\n'''.format(
            self.name[0] if type(self.name) is tuple else self.name, 
            self.range, int_to_color(self.color), 
            self.show_corona, self.show_lens_flares, self.Lightup_environment,
            formated_pos
        )

class P3DPolygon:
    texture = ""
    material = 0

    p1 = 0
    u1 = 0.0
    v1 = 0.0

    p2 = 0
    u2 = 0.0
    v2 = 0.0

    p3 = 0
    u3 = 0.0
    v3 = 0.0

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

class P3DMesh:
    name = ""
    flags = 0
    pos = [0.0, 0.0, 0.0]

    length = 0.0
    height = 0.0
    depth = 0.0

    #this is not in the default p3d format
    materials_used = []

    texture_infos = []

    num_vertices = 0
    vertices = []

    num_polys = 0
    polys = []

    def __str__(self):
        formated_pos = ["{0:0.2f}".format(i) for i in self.pos]
        # for p in self.polys:
        #     print(p)
        return '''{}\nflags: {} vertices: {} polys: {}
pos: {}\nsize: {:.2f} {:.2f} {:.2f} \n'''.format(
            self.name[0] if type(self.name) is tuple else self.name, 
            self.flags, self.num_vertices, self.num_polys,
            formated_pos, 
            self.length, self.height, self.depth
        )

class P3D:
    length = 0.0
    height = 0.0
    depth = 0.0

    num_textures = 0
    textures = []

    num_lights = 0
    lights = []

    num_meshes = 0
    meshes = []

    user_data_size = 0
    user_data = ""

    def __str__(self):
        print("\n{} textures:".format(self.num_textures))
        for i in self.textures:
            print(i[0] if type(i) is tuple else i)

        print("\n{} lights:".format(self.num_lights))
        for i in self.lights:
            print(i)
        
        print("\n{} meshes:".format(self.num_meshes))
        for i in self.meshes:
            print(i)
        return "model size: {:.2f} {:.2f} {:.2f}\n{} lights, {} meshes, {} textures\n".format(self.length, self.height, self.depth, self.num_lights, self.num_meshes, self.num_textures)

    def load(self, file):
        file.read(4)
        self.length = read_float(file)
        self.height = read_float(file)
        self.depth = read_float(file)

        #texture list
        file.read(7)
        self.num_textures = read_byte(file)
        self.textures = []
        for i in range(self.num_textures):
            self.textures.append("")
            self.textures[i] = read_null_string(file)

        #lights list
        file.read(10)
        self.num_lights = read_short(file)
        self.lights = []
        for i in range(self.num_lights):
            self.lights.append(P3DLight())
            self.lights[i].name = read_null_string(file)
            self.lights[i].pos = read_vector(file)
            self.lights[i].range = read_float(file)
            self.lights[i].color = read_int(file)

            self.lights[i].show_corona = read_byte(file)
            self.lights[i].show_lens_flares = read_byte(file)
            self.lights[i].Lightup_environment = read_byte(file)

        #meshes list
        file.read(10)
        self.num_meshes = read_short(file)
        self.meshes = []
        for i in range(self.num_meshes):
            self.meshes.append(P3DMesh())
            #submesh
            file.read(11)
            self.meshes[i].name = read_null_string(file)

            self.meshes[i].flags = read_uint(file)
            self.meshes[i].pos = read_vector(file)

            self.meshes[i].length = read_float(file)
            self.meshes[i].height = read_float(file)
            self.meshes[i].depth = read_float(file)

            self.meshes[i].texture_infos = []
            for ti in range(self.num_textures):
                self.meshes[i].texture_infos.append(P3DTextureInfo())
                self.meshes[i].texture_infos[ti].texture_start = read_short(file)
                self.meshes[i].texture_infos[ti].num_flat = read_short(file)
                self.meshes[i].texture_infos[ti].num_flat_metal = read_short(file)
                self.meshes[i].texture_infos[ti].num_gouraud = read_short(file)
                self.meshes[i].texture_infos[ti].num_gouraud_metal = read_short(file)
                self.meshes[i].texture_infos[ti].num_gouraud_metal_env = read_short(file)
                self.meshes[i].texture_infos[ti].num_shining = read_short(file)

            self.meshes[i].num_vertices = read_short(file)
            self.meshes[i].vertices = []
            for v in range(self.meshes[i].num_vertices):
                self.meshes[i].vertices.append(read_vector(file))

            self.meshes[i].num_polys = read_short(file)
            self.meshes[i].polys = []
            for p in range(self.meshes[i].num_polys):
                self.meshes[i].polys.append(P3DPolygon())
                self.meshes[i].polys[p].p1 = read_short(file)
                self.meshes[i].polys[p].u1 = read_float(file)
                self.meshes[i].polys[p].v1 = 1.0 - read_float(file)

                self.meshes[i].polys[p].p3 = read_short(file)
                self.meshes[i].polys[p].u3 = read_float(file)
                self.meshes[i].polys[p].v3 = 1.0 - read_float(file)

                self.meshes[i].polys[p].p2 = read_short(file)
                self.meshes[i].polys[p].u2 = read_float(file)
                self.meshes[i].polys[p].v2 = 1.0 - read_float(file)

            #at this point we have read everything but we need to fill
            #texture and materials of every polygon from the packed data
            #of the p3d model
            self.meshes[i].materials_used = []
            for ji, j in enumerate(self.meshes[i].texture_infos):
                polys_in_tex = j.texture_start

                for n in range(j.num_flat):
                    if((P3DMaterial.FLAT, self.textures[ji]) not in self.meshes[i].materials_used):
                        self.meshes[i].materials_used.append((P3DMaterial.FLAT, self.textures[ji]))
                    self.meshes[i].polys[polys_in_tex + n].material = P3DMaterial.FLAT
                    self.meshes[i].polys[polys_in_tex + n].texture = self.textures[ji]

                polys_in_tex += j.num_flat

                for n in range(j.num_flat_metal):
                    if((P3DMaterial.FLAT_METAL, self.textures[ji]) not in self.meshes[i].materials_used):
                        self.meshes[i].materials_used.append((P3DMaterial.FLAT_METAL, self.textures[ji]))
                    self.meshes[i].polys[polys_in_tex + n].material = P3DMaterial.FLAT_METAL
                    self.meshes[i].polys[polys_in_tex + n].texture = self.textures[ji]

                polys_in_tex += j.num_flat_metal

                for n in range(j.num_gouraud):
                    if((P3DMaterial.GOURAUD, self.textures[ji]) not in self.meshes[i].materials_used):
                        self.meshes[i].materials_used.append((P3DMaterial.GOURAUD, self.textures[ji]))
                    self.meshes[i].polys[polys_in_tex + n].material = P3DMaterial.GOURAUD
                    self.meshes[i].polys[polys_in_tex + n].texture = self.textures[ji]

                polys_in_tex += j.num_gouraud

                for n in range(j.num_gouraud_metal):
                    if((P3DMaterial.GOURAUD_METAL, self.textures[ji]) not in self.meshes[i].materials_used):
                        self.meshes[i].materials_used.append((P3DMaterial.GOURAUD_METAL, self.textures[ji]))
                    self.meshes[i].polys[polys_in_tex + n].material = P3DMaterial.GOURAUD_METAL
                    self.meshes[i].polys[polys_in_tex + n].texture = self.textures[ji]

                polys_in_tex += j.num_gouraud_metal

                for n in range(j.num_gouraud_metal_env):
                    if((P3DMaterial.GOURAUD_METAL_ENV, self.textures[ji]) not in self.meshes[i].materials_used):
                        self.meshes[i].materials_used.append((P3DMaterial.GOURAUD_METAL_ENV, self.textures[ji]))
                    self.meshes[i].polys[polys_in_tex + n].material = P3DMaterial.GOURAUD_METAL_ENV
                    self.meshes[i].polys[polys_in_tex + n].texture = self.textures[ji]

                polys_in_tex += j.num_gouraud_metal_env    

                for n in range(j.num_shining):
                    if((P3DMaterial.SHINING, self.textures[ji]) not in self.meshes[i].materials_used):
                        self.meshes[i].materials_used.append((P3DMaterial.SHINING, self.textures[ji]))
                    self.meshes[i].polys[polys_in_tex + n].material = P3DMaterial.SHINING
                    self.meshes[i].polys[polys_in_tex + n].texture = self.textures[ji]

        file.read(8)
        self.user_data_size = read_int(file)

    def save(self, file):
        write_string(file, b"P3D2")
        write_float(file, self.length)
        write_float(file, self.height)
        write_float(file, self.depth)

        #texture list
        write_string(file, b"TEX")
        write_uint(file, 1337)
        write_byte(file, self.num_textures)
        for i in range(self.num_textures):
            write_null_string(file, sanitise_string(self.textures[i]))

        #lights list
        write_string(file, b"LIGHTS")
        write_uint(file, 1337)
        write_short(file, self.num_lights)
        for i in range(self.num_lights):
            write_null_string(file, sanitise_string(self.lights[i].name))
            write_vector(file, self.lights[i].pos)
            write_float(file, self.lights[i].range)
            write_int(file, self.lights[i].color)

            write_byte(file, self.lights[i].show_corona)
            write_byte(file, self.lights[i].show_lens_flares)
            write_byte(file, self.lights[i].Lightup_environment)

        #meshes list
        write_string(file, b"MESHES")
        write_uint(file, 1337)
        write_short(file, self.num_meshes)
        for i in range(self.num_meshes):
            write_string(file, b"SUBMESH")
            write_uint(file, 1337)
            write_null_string(file, sanitise_string(self.meshes[i].name))

            write_uint(file, self.meshes[i].flags)
            write_vector(file, self.meshes[i].pos)

            write_float(file, self.meshes[i].length)
            write_float(file, self.meshes[i].height)
            write_float(file, self.meshes[i].depth)

            for ti in range(self.num_textures):
                write_short(file, self.meshes[i].texture_infos[ti].texture_start)
                write_short(file, self.meshes[i].texture_infos[ti].num_flat)
                write_short(file, self.meshes[i].texture_infos[ti].num_flat_metal)
                write_short(file, self.meshes[i].texture_infos[ti].num_gouraud)
                write_short(file, self.meshes[i].texture_infos[ti].num_gouraud_metal)
                write_short(file, self.meshes[i].texture_infos[ti].num_gouraud_metal_env)
                write_short(file, self.meshes[i].texture_infos[ti].num_shining)

            write_short(file, self.meshes[i].num_vertices)
            for v in range(self.meshes[i].num_vertices):
                write_vector(file, self.meshes[i].vertices[v])

            write_short(file, self.meshes[i].num_polys)
            for p in range(self.meshes[i].num_polys):
                write_short(file, self.meshes[i].polys[p].p1)
                write_float(file, self.meshes[i].polys[p].u1)
                write_float(file, 1.0 - self.meshes[i].polys[p].v1)

                write_short(file, self.meshes[i].polys[p].p3)
                write_float(file, self.meshes[i].polys[p].u3)
                write_float(file, 1.0 - self.meshes[i].polys[p].v3)

                write_short(file, self.meshes[i].polys[p].p2)
                write_float(file, self.meshes[i].polys[p].u2)
                write_float(file, 1.0 - self.meshes[i].polys[p].v2)


        write_string(file, b"USER")
        write_uint(file, 1337)
        write_int(file, 0)
            