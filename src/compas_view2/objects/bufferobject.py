from compas.utilities import flatten

from ..buffers import make_index_buffer, make_vertex_buffer

from .object import Object


class BufferObject(Object):
    """Object for displaying COMPAS mesh data structures.
    """

    default_color_points = [0.2, 0.2, 0.2]
    default_color_lines = [0.4, 0.4, 0.4]
    default_color_frontfaces = [0.8, 0.8, 0.8]
    default_color_backfaces = [0.8, 0.8, 0.8]

    def __init__(self, data, name=None, is_selected=False, show_points=False,
                 show_lines=False, show_faces=False, linewidth=1, pointsize=10):
        super().__init__(data, name=name, is_selected=is_selected)
        self._data = data
        self.show_points = show_points
        self.show_lines = show_lines
        self.show_faces = show_faces
        self.linewidth = linewidth
        self.pointsize = pointsize

    def make_buffer_from_data(self, data):
        positions, colors, elements = data
        return {
                'positions': make_vertex_buffer(list(flatten(positions))),
                'colors': make_vertex_buffer(list(flatten(colors))),
                'elements': make_index_buffer(list(flatten(elements))),
                'n': len(positions)
            }

    def update_buffer_from_data(self, data):
        pass

    def make_buffers(self):
        if hasattr(self, '_points_data'):
            self._points_buffer = self.make_buffer_from_data(self._points_data())
        if hasattr(self, '_lines_data'):
            self._lines_buffer = self.make_buffer_from_data(self._lines_data())
        if hasattr(self, '_frontfaces_data'):
            self._frontfaces_buffer = self.make_buffer_from_data(self._frontfaces_data())
        if hasattr(self, '_backfaces_data'):
            self._backfaces_buffer = self.make_buffer_from_data(self._backfaces_data())

    def init(self):
        self.make_buffers()

    def draw(self, shader):
        shader.enable_attribute('position')
        shader.enable_attribute('color')
        shader.uniform1i('is_selected', self.is_selected)
        if hasattr(self, "_points_buffer") and self.show_points:
            shader.bind_attribute('position', self._points_buffer['positions'])
            shader.bind_attribute('color', self._points_buffer['colors'])
            shader.draw_points(size=self.pointsize, elements=self._points_buffer['elements'], n=self._points_buffer['n'])
        if hasattr(self, "_lines_buffer") and self.show_lines:
            shader.bind_attribute('position', self._lines_buffer['positions'])
            shader.bind_attribute('color', self._lines_buffer['colors'])
            shader.draw_lines(width=self.linewidth, elements=self._lines_buffer['elements'], n=self._lines_buffer['n'])
        if hasattr(self, "_frontfaces_buffer") and self.show_faces:
            shader.bind_attribute('position', self._frontfaces_buffer['positions'])
            shader.bind_attribute('color', self._frontfaces_buffer['colors'])
            shader.draw_triangles(elements=self._frontfaces_buffer['elements'], n=self._frontfaces_buffer['n'])
        if hasattr(self, "_backfaces_buffer") and self.show_faces:
            shader.bind_attribute('position', self._backfaces_buffer['positions'])
            shader.bind_attribute('color', self._backfaces_buffer['colors'])
            shader.draw_triangles(elements=self._backfaces_buffer['elements'], n=self._backfaces_buffer['n'])
        shader.uniform1i('is_selected', 0)
        shader.disable_attribute('position')
        shader.disable_attribute('color')

    def draw_instance(self, shader):
        shader.enable_attribute('position')
        shader.uniform1i('is_instance_mask', 1)
        shader.uniform3f('instance_color', self.instance_color)
        if self.show_points:
            shader.bind_attribute('position', self._points_buffer['positions'])
            shader.draw_points(size=self.pointsize, elements=self._points_buffer['elements'], n=self._points_buffer['n'])
        if self.show_lines:
            shader.bind_attribute('position', self._lines_buffer['positions'])
            shader.draw_lines(width=self.linewidth, elements=self._lines_buffer['elements'], n=self._lines_buffer['n'])
        if self.show_faces:
            shader.bind_attribute('position', self._frontfaces_buffer['positions'])
            shader.draw_triangles(elements=self._frontfaces_buffer['elements'], n=self._frontfaces_buffer['n'])
            shader.bind_attribute('position', self._backfaces_buffer['positions'])
            shader.draw_triangles(elements=self._backfaces_buffer['elements'], n=self._backfaces_buffer['n'])
        shader.uniform1i('is_instance_mask', 0)
        shader.uniform3f('instance_color', [0, 0, 0])
        shader.disable_attribute('position')
