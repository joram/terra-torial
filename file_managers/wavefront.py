
class Obj(object):

    def __init__(self, data):
        self.data = data

    def write_obj(self, filepath, vertical_scale=0.01):
        with open(filepath, 'w') as f:
            f.write("# OBJ file\n")

            # vertices
            for x in range(0, len(self.data)):
                for y in range(0, len(self.data[0])):
                    h = float(self.data[x][y])*vertical_scale
                    f.write("v %d %d %.4f\n" % (x, h, y))
                f.write("\n")

            # triangles
            len_row = len(self.data[0])
            for index in range(0, len(self.data)*len_row - len_row - len(self.data) + 1):
                if index % len_row != 0:
                    indices = [index, index+1, index+len_row+1, index+len_row]
                    f.write("# square: %s\n" % ", ".join([i.__str__() for i in indices]))
                    f.write("f %d %d %d\n" % (indices[0], indices[1], indices[3]))  # top left of square
                    f.write("f %d %d %d\n\n" % (indices[1], indices[3], indices[2]))  # bottom right of square