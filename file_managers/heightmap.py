import Image
import numpy


class Heightmap(object):

    def __init__(self, data, resize=(256, 256), obj_vertical_scale=0.01):
        self.jpg_output_size = resize
        self.obj_vertical_scale = obj_vertical_scale
        self.data = data
        self._jpg = None
        self._obj = None

    def get_jpg(self):
        if self._jpg:
            return self._jpg

        data = numpy.array(self.data)
        m = data.max()
        if m <= 1:
            m = 255.0
        rescaled = (255.0 / m * (data - data.min())).astype(numpy.uint8)
        img = Image.fromarray(rescaled)
        if self.jpg_output_size:
            img = img.resize(self.jpg_output_size, Image.ANTIALIAS)
        self._jpg = img
        return img

    def chunks(self, l, n):
        matrix = []
        for i in xrange(0, len(l), n):
            matrix.append(l[i:i+n])
        return matrix

    def get_matrix(self):
        img = self.get_jpg()
        data = list(img.getdata())
        matrix = self.chunks(data, img.size[0])
        return matrix

    def get_obj(self):
        if self._obj:
            return self._obj

        content = ""
        content += "# OBJ file\n"

        # vertices
        for x in range(0, len(self.data)):
            for y in range(0, len(self.data[0])):
                h = float(self.data[x][y])*self.obj_vertical_scale
                content += "v %d %d %.4f\n" % (x, h, y)
            content += "\n"

        # triangles
        len_row = len(self.data[0])
        for index in range(0, len(self.data)*len_row - len_row - len(self.data) + 1):
            if index % len_row != 0:
                indices = [index, index+1, index+len_row+1, index+len_row]
                content += "# square: %s\n" % ", ".join([i.__str__() for i in indices])
                content += "f %d %d %d\n" % (indices[0], indices[1], indices[3])  # top left of square
                content += "f %d %d %d\n\n" % (indices[1], indices[3], indices[2])  # bottom right of square

        self._obj = content
        return content

    def write_jpg(self, filepath):
        pass

    def write_obj(self, filepath):
        pass