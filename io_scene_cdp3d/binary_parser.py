import struct

def transform_pos(value):
    return (value[0], value[2], value[1])

def sanitise_string(string):
    return string.encode("ASCII", "replace")

def read_byte(file):
    return struct.unpack('<B', file.read(struct.calcsize('B')))[0]

def read_short(file):
    return struct.unpack('<h', file.read(struct.calcsize('h')))[0]

def read_int(file):
    return struct.unpack('<i', file.read(struct.calcsize('i')))[0]

def read_uint(file):
    return struct.unpack('<I', file.read(struct.calcsize('I')))[0]

def read_float(file):
    return struct.unpack('<f', file.read(struct.calcsize('f')))[0]

def read_vector(file):
    return transform_pos([float(v) for v in struct.unpack('<3f', file.read(struct.calcsize('3f')))])

def read_null_string(file):
    string = b''
    while True:
        char = struct.unpack('<c', file.read(1))[0]
        if char == b'\x00':
            break
        string += char
    return str(string, "utf-8", "replace")


def write_byte(file, value):
    file.write(struct.pack("<B", value))

def write_short(file, value):
    file.write(struct.pack("<h", value))

def write_int(file, value):
    file.write(struct.pack("<i", value))

def write_uint(file, value):
    file.write(struct.pack("<I", value))

def write_float(file, value):
    file.write(struct.pack("<f", value))

def write_vector(file, value):
    value = transform_pos(value)
    file.write(struct.pack('<3f', value[0], value[1], value[2]))

def write_null_string(file, value):
    binary_format = "<%ds" % (len(value) + 1)
    file.write(struct.pack(binary_format, value))

def write_string(file, value):
    binary_format = "<%ds" % (len(value))
    file.write(struct.pack(binary_format, value))